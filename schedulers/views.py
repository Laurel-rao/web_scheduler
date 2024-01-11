import time
import traceback
from threading import Thread

import smtplib
from email.mime.text import MIMEText

from apscheduler.jobstores.base import JobLookupError

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from logs.log import logger
from .job_handler import ApiJobHandler, ScriptJobHandler, CommonJobHandler
from .models import DateSchedulers, CronSchedulers, IntervalSchedulers, Email, \
    AbstractJob, ScriptJob, CommonJob, ApiJob
import json
from django.db.models import Q
from .en_de import decrypt_p
from .exchange_mail import ExchangeEmail
# Create your views here.

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from .tools import write_job_log

JOB_MODELS = {
    "0": ScriptJob,
    "1": ApiJob,
    "2": CommonJob,
}

# 定义以线程方式执行任务，最多20个线程同时执行

executors = {
    'default': ThreadPoolExecutor(20)  # 最多20个线程同时执行
}

jobstores = {
    "default": DjangoJobStore(),
}
tz = pytz.timezone('Asia/Shanghai')

# scheduler = BackgroundScheduler(timezone=tz, executors=executors)
scheduler = BackgroundScheduler(timezone=tz, executors=executors, jobstores=jobstores)
scheduler.start()


@csrf_exempt
def login_web(request):
    errors = []
    account = None
    password = None
    if request.method == 'POST':
        if not request.POST.get('account'):
            errors.append('请输入帐户！Please Enter account！')
        else:
            account = request.POST.get('account')
        if not request.POST.get('password'):
            errors.append('请输入密码！Please Enter password！')
        else:
            password = request.POST.get('password')
        if account is not None and password is not None:
            user = authenticate(username=account, password=password)
            if user is not None:
                if user.is_active:
                    if user.is_authenticated:  # 判断用户是否通过认证
                        # request.user: 可以在模版中直接调用
                        login(request, user)
                        return redirect("/")
                else:
                    errors.append('账户已被禁用，请核实~！')
            else:
                errors.append('用户名或密码错误，请确认~！')
                # 非post登录请求，跳转到登录页面！
    return render(request, 'login.html', {'errors': errors})


def logout_view(request):
    logout(request)
    return redirect("/login")
    # Redirect to a success page


@login_required
def index(request):
    return render(request, 'index.html')


def update_next_time(cur_job_id, job_dict):
    cur_model = job_dict.get("cur_model")
    job_id = job_dict['id']
    job_next_time = scheduler.get_job(cur_job_id).next_run_time
    cur_model.objects.filter(id=job_id).update(next_time=job_next_time)


def handler(cur_job_id, job_dict, username):
    job_handlers = {
        "0": ScriptJobHandler,
        "1": ApiJobHandler,
        "2": CommonJobHandler,
    }
    job_id = job_dict['id']
    job_type = job_dict['type']
    write_job_log(job_type, job_id, msg="start")
    ObjHandler = job_handlers.get(job_type)
    if not ObjHandler:
        error_msg = "job_type error %s" % job_type
        write_job_log(job_type, job_id, msg=error_msg, level="1")
    else:
        try:
            ObjHandler(job_dict, username)
        except:
            error_msg = "UnException Error: %s" % traceback.format_exc()
            write_job_log(job_type, job_id, msg=error_msg, level="1")
    write_job_log(job_type, job_id, msg="end")
    t = Thread(target=update_next_time, args=(cur_job_id, job_dict))
    t.setDaemon(True)
    t.start()




def send_email(str_content, username, ReceiversEmail):
    req = {
        'code': 1,  # 1为成功，0为失败
        'msg': 'Ok'
    }

    # 设置服务器所需信息
    # 邮箱服务器地址
    email = Email.objects.get(author__username=username)
    # 邮箱服务器
    mail_host = email.EmailServer
    # 邮箱用户名
    mail_user = email.SendEmailUser
    # 密码(部分邮箱为授权码)
    mail_pass = decrypt_p(email.SendEmailPsd)
    # 邮件发送方邮箱地址
    sender = email.SendEmailAdd
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = ReceiversEmail.split('|')
    # 邮件内容设置
    content = str_content
    # 判断是否为exchange邮箱，如果是调用exchange邮箱发送方式
    EmailType = email.EmailType
    if EmailType == '1':
        try:
            exchange_email = ExchangeEmail(mail_user, mail_pass, mail_host, sender)
            for receiver in receivers:
                exchange_email.send_email(receiver, '网页监控消息', content)
            print('success')
            return req
        except Exception as e:
            req['code'] = 0
            req['msg'] = str(traceback.format_exc())
            logger.error('email-error1 %s' % e)  # 打印错误
            return req
    elif EmailType == '2':
        # 邮件主题
        message = MIMEText(content, 'plain', 'utf-8')
        message['Subject'] = '网页监控消息'
        # 发送方信息
        message['From'] = sender
        # 接受方信息
        message['To'] = receivers[0]

        # 登录并发送邮件
        try:
            # 使用非加密方式访问邮箱
            # smtpObj = smtplib.SMTP()
            # smtpObj.connect(mail_host, 25)
            # 使用ssl加密 访问邮箱
            smtpObj = smtplib.SMTP_SSL(mail_host, 465)
            # 登录到服务器
            smtpObj.login(mail_user, mail_pass)
            # 发送
            smtpObj.sendmail(
                sender, receivers, message.as_string())
            # 退出

            smtpObj.quit()
            return req
        except smtplib.SMTPException as e:
            req['code'] = 0
            req['msg'] = str(traceback.format_exc())
            logger.error('email-error2 %s' % traceback.format_exc())  # 打印错误
            return req


def email_test(request):
    req = {
        'code': 1,  # 1为成功，0为失败
        'msg': ''
    }
    username = request.user.username
    try:
        email_obj = Email.objects.filter(author__username=username)
        if not list(email_obj):
            req['code'] = 0
            req['msg'] = "请先在后台登记邮件信息"
            return JsonResponse(req)
        ReceiversEmail = email_obj.first().ReceiversEmail
        if email_obj:
            str_content = '网页：http://www.baidu.com  \n' + '检测到关键内容：\n' + \
                          '>>> 关键字：测试    匹配到内容如下：\n' + '测试内容…… \n\n'
            req = send_email(str_content, username, ReceiversEmail)
            return JsonResponse(req)
        else:
            req['code'] = 0
            req['msg'] = '尚未配置邮件告警，请在后台管理中进行配置。'
            return JsonResponse(req)
    except Exception as e:
        req['code'] = 0
        req['msg'] = str(e)
        return JsonResponse(req)


######## todo 任务创建/处理 ########

# def

def startup_jobs(**kwargs):
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'msg': ''
    }
    try:
        job_dict = kwargs
        username = kwargs['username']
        trigger = kwargs['trigger']
        cur_model = kwargs['cur_model']
        ID = kwargs['id']
        str_type = kwargs['type']
        cur_job_id = "job_id_%s_%s" % (ID, str_type)

        if trigger == 'date':
            date_schedulers = DateSchedulers.objects.get(id=kwargs.get('DateSchedulers', kwargs.get("DateSchedulers_id")))
            datetime = date_schedulers.datetime
            trigger_args = {"trigger": trigger, "run_date": datetime}
        elif trigger == 'interval':
            interval_schedulers = IntervalSchedulers.objects.get(id=kwargs.get('IntervalSchedulers', kwargs.get("IntervalSchedulers_id")))
            weeks = interval_schedulers.weeks
            days = interval_schedulers.days
            hours = interval_schedulers.hours
            minutes = interval_schedulers.minutes
            seconds = interval_schedulers.seconds
            start_date = interval_schedulers.start_date
            trigger_args = {"trigger": "interval",
                            "weeks": weeks, "days": days, "hours": hours, "minutes": minutes,
                            "seconds": seconds, "start_date": start_date
                            }
        elif trigger == 'cron':
            cron_schedulers = CronSchedulers.objects.get(id=kwargs.get('CronSchedulers', kwargs.get("CronSchedulers_id")))
            year = cron_schedulers.year
            month = cron_schedulers.month
            day = cron_schedulers.day
            week = cron_schedulers.week
            day_of_week = cron_schedulers.day_of_week
            hour = cron_schedulers.hour
            minute = cron_schedulers.minute
            second = cron_schedulers.second

            trigger_args = {"trigger": "cron",
                            "year": year, "month": month, "day": day, "week": week, "day_of_week": day_of_week,
                            "hour": hour, "minute": minute, "second": second
                            }
        else:
            raise ValueError("参数错误 %s" % trigger)
        scheduler.add_job(handler, **trigger_args, id=cur_job_id, args=[cur_job_id, job_dict, username],
                          replace_existing=True)
        time.sleep(1)
        job = scheduler.get_job(cur_job_id)
        if job:
            next_time = job.next_run_time
            cur_model.objects.filter(id=ID).update(job_id=cur_job_id, enable='0', next_time=next_time)
        else:
            # todo 任务已经失效，已执行完毕或者超过当前时间 enable = 2
            cur_model.objects.filter(id=ID).update(job_id='', enable='2', next_time=None)
            req.update({"code": 0, "msg": "已执行完毕或者超过当前时间"})
        return req
    except Exception as e:
        req['code'] = 0
        req['msg'] = str(traceback.format_exc())
        return req


def stop_job(cur_model, job_id, str_type):
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'msg': ''
    }
    try:
        cur_job_id = "job_id_%s_%s" % (job_id, str_type)
        try:
            scheduler.pause_job(cur_job_id)
        except JobLookupError:
            cur_model.objects.filter(id=job_id).update(job_id="", enable='2', next_time=None)
        else:
            cur_model.objects.filter(id=job_id).update(job_id=cur_job_id, enable='1', next_time=None)
        return req
    except Exception as e:
        req['code'] = 0
        req['msg'] = str(traceback.format_exc())
        return req


def get_all_job_model():
    # 查询所有任务类
    from django.apps import apps
    all_models = apps.get_models()
    job_models = []
    for model in all_models:
        for i in model.__bases__:
            if i.__name__ == AbstractJob.__name__:
                job_models.append(model)
    return job_models


def get_job_list(request, username):
    jobs_list = []
    job_models = get_all_job_model()
    for job_model in job_models:
        # 权限查询
        filters = {}
        if not request.user.is_superuser:
            filters.update({"author__username": username})
        job_objs = job_model.objects.filter(**filters).values()
        jobs_list.extend(job_objs)
    for i in jobs_list:
        i['datetime'] = utc_to_utc8(i['datetime'])
        if i['next_time']:
            i['next_time'] = utc_to_utc8(i['next_time'])
    return jobs_list


def get_job(request):
    """获取所有任务信息"""
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'username': '',
        'msg': ''
    }
    if not request.user.is_authenticated:
        return HttpResponse(content="Forbidden Access", status=403)
    username = request.user.username
    try:
        jobs_list = get_job_list(request, username)
        req['data'] = jobs_list
        req['username'] = request.user.username
    except Exception as e:
        req['code'] = 0
        req['msg'] = '获取任务信息异常，具体异常为：' + str(e)
    return JsonResponse(req)


def utc_to_utc8(utc_time):
    """django默认使用的utc时间，即便在setting中更改了时区也不是对数据库中保存的时间进行调整，
    只是在前端显示时依据设置的时区显示时间。由于前后端分离了，在前端显示时间字段时候也需进行时间显示上的调整。
    该功能就是将数据库中保存的时间进行转换，然后在提供给前端显示。
    """
    try:
        utc_time = str(utc_time).split('.')[0]
        if '+' in utc_time:
            utc_time = utc_time.split('+')[0]
        # 将字符串转换为时间数组
        utc_time = time.strptime(utc_time, "%Y-%m-%d %H:%M:%S")
        # 将时间数组转换为时间戳
        utc_time = time.mktime(utc_time)
        # 将时间戳转换为东八区的时间戳
        beijing_time = utc_time + 8 * 60 * 60
        # 将时间戳进行格式化即可
        timeArray = time.localtime(beijing_time)
        new_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return new_time
    except Exception as e:
        print('utc_trans_error:' + str(e))


@csrf_exempt
def query_job(request):
    """查询任务信息"""
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'username': '',
        'msg': ''
    }
    username = request.user.username
    print(request.user.is_authenticated)
    if not request.user.is_authenticated:
        return HttpResponse(content="Forbidden Access", status_code=403)
    try:
        data = json.loads(request.body.decode('utf-8'))
        jobs_list = []
        job_models = get_all_job_model()
        for job_model in job_models:
            # 权限查询
            filters = {}
            if not request.user.is_superuser:
                filters.update({"author__username": username})
            job_objs = job_model.objects.filter(
                Q(name__icontains=data['inputstr']) |
                Q(trigger__icontains=data['inputstr']), **filters).values()
            jobs_list.extend(job_objs)
        for i in jobs_list:
            i['datetime'] = utc_to_utc8(i['datetime'])
            if i['next_time']:
                i['next_time'] = utc_to_utc8(i['next_time'])
        req['data'] = jobs_list
        req['username'] = request.user.username
    except Exception as e:
        req['code'] = 0
        req['msg'] = '查询任务信息异常，具体异常为：' + str(e)
    return JsonResponse(req)


def get_model_by_type(job_type):
    return JOB_MODELS.get(job_type)


@csrf_exempt
def modify_jobs(request):
    """用于启动和停止任务"""
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'msg': ''
    }
    username = request.user.username
    try:
        data = json.loads(request.body.decode('utf-8'))
        ID = data['job_id']
        str_type = data['type']
        cur_model = get_model_by_type(str_type)
        job_dict = model_to_dict(cur_model.objects.get(id=ID))
        option = data['option']
        if option == 'startup':
            req = startup_jobs(cur_model=cur_model, username=username, **job_dict)
        elif option == 'stop':
            req = stop_job(cur_model, ID, str_type)
        jobs_list = get_job_list(request, username)
        req['data'] = jobs_list
        return JsonResponse(req)
    except Exception as e:
        req['code'] = 0
        req['msg'] = '查询任务信息异常，具体异常为：' + str(e)
        logger.error(traceback.format_exc())
        return JsonResponse(req)

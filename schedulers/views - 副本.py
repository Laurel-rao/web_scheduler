import time
import pytz
import requests
import urllib3
import smtplib
from email.mime.text import MIMEText

from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from requests import RequestException

from .models import SchedulersJob, DateSchedulers, CronSchedulers, IntervalSchedulers, Email, SchedulersJob2
import json
from django.db.models import Q
import logging
import re
from .en_de import decrypt_p


# Create your views here.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
tz = pytz.timezone('Asia/Shanghai')
scheduler = BackgroundScheduler(timezone=tz)
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


def more_page(web_url, pattern, base_url, str_keywords, trigger, job_id, str_type, username):
    # https://weain.mil.cn/tzgg/list.shtml
    try:
        # 添加头部信息
        web_url_list = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        urllib3.disable_warnings()
        response = requests.get(web_url, headers=headers, verify=False)
        # 进行状态码判断，是否正确读取到网页
        if response.status_code == 200:
            matchObj = re.findall(pattern, response.content.decode())
            # today = str(datetime.date.today() - datetime.timedelta(days=1)).replace('-', '')
            for i in matchObj:
                web_url_list.append(base_url + i)
            monitor_one_page(web_url_list, str_keywords, trigger, job_id, str_type, username)
    except RequestException as e:
        logger.warning("页面监控测序异常~！异常代码为：" + str(e))


# 监控单个页面
def monitor_one_page(web_url_list, str_keywords, trigger, job_id, str_type, username):
    try:
        # 添加头部信息
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        urllib3.disable_warnings()
        keywords = []
        error_list = []
        str_content = ''
        for web_url in web_url_list:
            response = requests.get(web_url, headers=headers, verify=False)

            # 进行状态码判断，是否正确读取到网页
            logger.info("Start monitor………………………………………………\\n监控网址为：" + str(web_url) + '\\n关键字为：' + str_keywords)
            if response.status_code == 200:

                keywords_list = str_keywords.split('|')
                for i in keywords_list:
                    match_dict = dict()
                    if i in response.content.decode():
                        pattern = '>([^<]*' + i + '[^<]+)'
                        # keywords.append(i)
                        matchObj = re.findall(pattern, response.content.decode())
                        texts_list = []
                        for text in matchObj:
                            texts_list.append(text)
                        if texts_list:
                            match_dict = {
                                'web_url': web_url,
                                'keyword': i,
                                'texts': texts_list
                            }
                            keywords.append(match_dict)
            else:
                error_list.append(web_url)
        if keywords:
            for i in keywords:
                str_content = str_content + '网页：' + i['web_url'] + '  \n' + '检测到关键内容：\n' + \
                               '>>> 关键字：' + i['keyword'] + '    匹配到内容如下：\n' + '\n'.join(i['texts']) + '\n\n'
        for e in error_list:
            str_content = str_content + '网页：' + e['web_url'] + '  \n' + '无法访问，请确认~!!：\n\n'
        logger.info(keywords)
        send_email(str_content, username)
        if trigger != 'cron':
            if str_type == 'one':
                SchedulersJob.objects.filter(id=job_id).update(enable='2', next_time=None)
            else:
                SchedulersJob2.objects.filter(id=job_id).update(enable='2', next_time=None)
        else:
            if str_type == 'one':
                job = scheduler.get_job('job_id_' + str(job_id) + '_' + str_type)
                next_time = job.next_run_time
                SchedulersJob.objects.filter(id=job_id).update(next_time=next_time)
            else:
                job = scheduler.get_job('job_id_' + str(job_id) + '_' + str_type)
                next_time = job.next_run_time
                SchedulersJob2.objects.filter(id=job_id).update(next_time=next_time)
        logger.info("monitor Finish~!")
    except RequestException as e:
        logger.warning("页面监控测序异常~！异常代码为：" + str(e))
        # str_keywords = "页面监控测序异常~！异常代码为：" + str(e)
    # finally:
    #     send_email(str_keywords, username)


def send_email(str_content, username):
    req = {
        'code': 1,  # 1为成功，0为失败
        'msg': ''
    }

    # 设置服务器所需信息
    # 163邮箱服务器地址
    email = Email.objects.get(author__username=username)
    mail_host = email.EmailServer
    # 163用户名
    mail_user = email.SendEmailUser
    # 密码(部分邮箱为授权码)
    mail_pass = decrypt_p(email.SendEmailPsd)
    # 邮件发送方邮箱地址
    sender = email.SendEmailAdd
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = email.ReceiversEmail.split('|')

    # 设置email信息
    # 邮件内容设置
    # str_keywords = ''
    # for i in keywords:
    #     str_keywords = str_keywords + '>>> 关键字：' + i['keyword'] + '    匹配到内容如下：\n' + '\n'.join(i['texts']) + '\n\n'
    content = str_content
    message = MIMEText(content, 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = '网页监控消息'
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        # smtpObj = smtplib.SMTP()
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        # 连接到服务器
        # smtpObj.connect(mail_host, 25)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        print('success')
        return req
    except smtplib.SMTPException as e:
        req['code'] = 0
        req['msg'] = str(e)
        print('email-error', e)  # 打印错误
        return req


def email_test(request):
    req = {
        'code': 1,  # 1为成功，0为失败
        'msg': ''
    }
    username = request.user.username
    try:
        email_obj = Email.objects.filter(author__username=username)
        if email_obj:
            str_content = '网页：http://www.baidu.com  \n' + '检测到关键内容：\n' + \
                           '>>> 关键字：测试    匹配到内容如下：\n' + '测试内容…… \n\n'
            req = send_email(str_content, username)
            return JsonResponse(req)
        else:
            req['code'] = 0
            req['msg'] = '尚未配置邮件告警，请在后台管理中进行配置。'
            return JsonResponse(req)
    except Exception as e:
        req['code'] = 0
        req['msg'] = str(e)
        return JsonResponse(req)


def startup_jobs(**kwargs):
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'msg': ''
    }
    try:
        username = kwargs['username']
        web_url = kwargs['web_url']
        keywords = kwargs['keywords']
        trigger = kwargs['trigger']
        ID = kwargs['id']
        str_type = kwargs['type']
        if trigger == 'date':
            date_schedulers = DateSchedulers.objects.get(id=kwargs['DateSchedulers'])
            datetime = date_schedulers.datetime
            if str_type == 'one':
                web_url_list = [web_url]
                scheduler.add_job(monitor_one_page, 'date', run_date=datetime, id='job_id_' + str(ID) + '_' + str_type,
                                  args=[web_url_list, keywords, trigger, ID, str_type, username])
            else:
                pattern = kwargs['pattern']
                base_url = kwargs['base_url']
                scheduler.add_job(more_page, 'date', run_date=datetime, id='job_id_' + str(ID) + '_' + str_type,
                                  args=[web_url, pattern, base_url, keywords, trigger, ID, str_type, username])
        elif trigger == 'interval':
            interval_schedulers = IntervalSchedulers.objects.get(id=kwargs['IntervalSchedulers'])
            weeks = interval_schedulers.weeks
            days = interval_schedulers.days
            hours = interval_schedulers.hours
            minutes = interval_schedulers.minutes
            seconds = interval_schedulers.seconds
            start_date = interval_schedulers.start_date
            if str_type == 'one':
                scheduler.add_job(monitor_one_page, 'interval',
                                  weeks=weeks, days=days, hours=hours, minutes=minutes,
                                  seconds=seconds, start_date=start_date, id='job_id_' + str(ID) + '_' + str_type,
                                  args=[web_url, keywords, trigger, ID, str_type, username])
            else:
                pattern = kwargs['pattern']
                base_url = kwargs['base_url']
                scheduler.add_job(more_page, 'interval',
                                  weeks=weeks, days=days, hours=hours, minutes=minutes,
                                  seconds=seconds, start_date=start_date, id='job_id_' + str(ID) + '_' + str_type,
                                  args=[web_url, pattern, base_url, keywords, trigger, ID, str_type, username])
        elif trigger == 'cron':
            cron_schedulers = CronSchedulers.objects.get(id=kwargs['CronSchedulers'])
            year = cron_schedulers.year
            month = cron_schedulers.month
            day = cron_schedulers.day
            week = cron_schedulers.week
            day_of_week = cron_schedulers.day_of_week
            hour = cron_schedulers.hour
            minute = cron_schedulers.minute
            second = cron_schedulers.second
            if str_type == 'one':
                scheduler.add_job(monitor_one_page, 'cron',
                                  year=year, month=month, day=day, week=week, day_of_week=day_of_week,
                                  hour=hour, minute=minute, second=second, id='job_id_' + str(ID) + '_' + str_type,
                                  args=[web_url, keywords, trigger, ID, str_type, username])
            else:
                pattern = kwargs['pattern']
                base_url = kwargs['base_url']
                scheduler.add_job(more_page, 'cron',
                                  year=year, month=month, day=day, week=week, day_of_week=day_of_week,
                                  hour=hour, minute=minute, second=second, id='job_id_' + str(ID) + '_' + str_type,
                                  args=[web_url, pattern, base_url, keywords, trigger, ID, str_type, username])
        time.sleep(1)
        job = scheduler.get_job('job_id_' + str(ID) + '_' + str_type)
        if job:
            next_time = job.next_run_time
            if str_type == 'one':
                SchedulersJob.objects.filter(id=ID).update(job_id='job_id_' + str(ID) + '_' + str_type, enable='0',
                                                           next_time=next_time)
            else:
                SchedulersJob2.objects.filter(id=ID).update(job_id='job_id_' + str(ID) + '_' + str_type, enable='0',
                                                            next_time=next_time)
        else:
            if str_type == 'one':
                SchedulersJob.objects.filter(id=ID).update(job_id='', enable='2')
            else:
                SchedulersJob2.objects.filter(id=ID).update(job_id='', enable='2')
        return req
    except Exception as e:
        req['code'] = 0
        req['msg'] = e
        return req


def stop_job(job_id, str_type):
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'msg': ''
    }
    try:
        scheduler.pause_job('job_id_' + str(job_id) + '_' + str_type)
        if str_type == 'one':
            SchedulersJob.objects.filter(id=job_id).update(job_id='job_id_' + str(job_id) + '_' + str_type, enable='1',
                                                           next_time=None)
        else:
            SchedulersJob2.objects.filter(id=job_id).update(job_id='job_id_' + str(job_id) + '_' + str_type, enable='1',
                                                            next_time=None)
        return req
    except Exception as e:
        req['code'] = 0
        req['msg'] = e
        return req


def get_job(request):
    """获取所有任务信息"""
    req = {
        'code': 1,  # 1为成功，0为失败
        'data': None,
        'username': '',
        'msg': ''
    }
    username = request.user.username
    try:
        if request.user.is_superuser:
            # 使用ORM获取所有任务信息，values的作用为：将结果转换为字典形式
            obj_jobs = SchedulersJob.objects.all().values()
            # 把结果转换为标准的list类型
            jobs_list = list(obj_jobs)
            obj_jobs2 = SchedulersJob2.objects.all().values()
            jobs_list = jobs_list + list(obj_jobs2)
        else:
            # 使用ORM获取所有任务信息，values的作用为：将结果转换为字典形式
            obj_jobs = SchedulersJob.objects.filter(author__username=username).values()
            # 把结果转换为标准的list类型
            jobs_list = list(obj_jobs)
            obj_jobs2 = SchedulersJob2.objects.filter(author__username=username).values()
            jobs_list = jobs_list + list(obj_jobs2)
        for i in jobs_list:
            i['datetime'] = utc_to_utc8(i['datetime'])
            if i['next_time']:
                i['next_time'] = utc_to_utc8(i['next_time'])
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
    try:
        data = json.loads(request.body.decode('utf-8'))
        if request.user.is_superuser:
            # 使用ORM查询任务信息，values的作用为：将结果转换为字典形式
            obj_jobs = SchedulersJob.objects.filter(
                Q(name__icontains=data['inputstr']) |
                Q(web_url__icontains=data['inputstr']) |
                Q(keywords__icontains=data['inputstr']) |
                Q(trigger__icontains=data['inputstr']) |
                Q(remarks__icontains=data['inputstr'])
            ).values()
            # 把结果转换为标准的list类型
            jobs_list = list(obj_jobs)
            obj_jobs2 = SchedulersJob2.objects.filter(
                Q(name__icontains=data['inputstr']) |
                Q(web_url__icontains=data['inputstr']) |
                Q(keywords__icontains=data['inputstr']) |
                Q(trigger__icontains=data['inputstr']) |
                Q(remarks__icontains=data['inputstr'])).values()
            jobs_list = jobs_list + list(obj_jobs2)
        else:
            # 使用ORM查询任务信息，values的作用为：将结果转换为字典形式
            obj_jobs = SchedulersJob.objects.filter(author__username=username and (
                Q(name__icontains=data['inputstr']) |
                Q(web_url__icontains=data['inputstr']) |
                Q(keywords__icontains=data['inputstr']) |
                Q(trigger__icontains=data['inputstr']) |
                Q(remarks__icontains=data['inputstr']))
            ).values()
            # 把结果转换为标准的list类型
            jobs_list = list(obj_jobs)
            obj_jobs2 = SchedulersJob2.objects.filter(author__username=username and (
                Q(name__icontains=data['inputstr']) |
                Q(web_url__icontains=data['inputstr']) |
                Q(keywords__icontains=data['inputstr']) |
                Q(trigger__icontains=data['inputstr']) |
                Q(remarks__icontains=data['inputstr']))).values()
            jobs_list = jobs_list + list(obj_jobs2)
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
        email_obj = Email.objects.filter(author__username=username)
        if not email_obj:
            req['code'] = 0
            req['msg'] = '尚未配置邮件告警，请在后台管理中进行配置。'
            return JsonResponse(req)
        else:
            data = json.loads(request.body.decode('utf-8'))
            ID = data['job_id']
            str_type = data['type']
            # 使用ORM查询任务信息
            if str_type == 'one':
                job_dict = model_to_dict(SchedulersJob.objects.get(id=ID))
            else:
                job_dict = model_to_dict(SchedulersJob2.objects.get(id=ID))
            option = data['option']
            if option == 'startup':
                if job_dict['job_id']:
                    scheduler.resume_job('job_id_' + str(ID) + '_' + str_type)
                    job = scheduler.get_job('job_id_' + str(ID) + '_' + str_type)
                    next_time = job.next_run_time
                    if str_type == 'one':
                        SchedulersJob.objects.filter(id=ID).update(enable='0', next_time=next_time)
                    else:
                        SchedulersJob2.objects.filter(id=ID).update(enable='0', next_time=next_time)
                else:
                    req = startup_jobs(username=username, **job_dict)
            elif option == 'stop':
                req = stop_job(ID, str_type)
            if request.user.is_superuser:
                # 使用ORM获取所有任务信息，values的作用为：将结果转换为字典形式
                obj_jobs = SchedulersJob.objects.all().values()
                # 把结果转换为标准的list类型
                jobs_list = list(obj_jobs)
                obj_jobs2 = SchedulersJob2.objects.all().values()
                jobs_list = jobs_list + list(obj_jobs2)
            else:
                # 使用ORM获取所有任务信息，values的作用为：将结果转换为字典形式
                obj_jobs = SchedulersJob.objects.filter(author__username=username).values()
                # 把结果转换为标准的list类型
                jobs_list = list(obj_jobs)
                obj_jobs2 = SchedulersJob2.objects.filter(author__username=username).values()
                jobs_list = jobs_list + list(obj_jobs2)
            for i in jobs_list:
                i['datetime'] = utc_to_utc8(i['datetime'])
                if i['next_time']:
                    i['next_time'] = utc_to_utc8(i['next_time'])
            req['data'] = jobs_list
            return JsonResponse(req)
    except Exception as e:
        req['code'] = 0
        req['msg'] = '查询任务信息异常，具体异常为：' + str(e)
        return JsonResponse(req)

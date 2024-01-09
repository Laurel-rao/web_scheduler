from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.


class DateSchedulers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, verbose_name='触发器名称')
    datetime = models.DateTimeField(verbose_name='开始时间')
    author = models.ForeignKey(User, related_name='date_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '3、特定的时间点触发器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class IntervalSchedulers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, verbose_name='触发器名称')
    weeks = models.IntegerField(verbose_name='间隔周数', blank=True, null=True, default=0)
    days = models.IntegerField(verbose_name='间隔天数', blank=True, null=True, default=0)
    hours = models.IntegerField(verbose_name='间隔小时数', blank=True, null=True, default=0)
    minutes = models.IntegerField(verbose_name='间隔分钟数', blank=True, null=True, default=0)
    seconds = models.IntegerField(verbose_name='间隔秒数', blank=True, null=True, default=0)
    start_date = models.DateTimeField(verbose_name='开始日期', blank=True, null=True)
    author = models.ForeignKey(User, related_name='interval_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '4、固定时间间隔触发器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CronSchedulers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, verbose_name="触发器名称")
    year = models.CharField(max_length=50, verbose_name='年份(2020)', blank=True, null=True)
    month = models.CharField(max_length=50, verbose_name='月份(1-12)', blank=True, null=True)
    day = models.CharField(max_length=50, verbose_name='日期(1-31)', blank=True, null=True)
    week = models.CharField(max_length=50, verbose_name='周数(1-53)', blank=True, null=True)
    day_of_week = models.CharField(max_length=50, verbose_name='工作日(0-6)；0为周一', blank=True, null=True)
    hour = models.CharField(max_length=50, verbose_name='小时(0-23)', blank=True, null=True)
    minute = models.CharField(max_length=50, verbose_name='分钟(0-59)', blank=True, null=True)
    second = models.CharField(max_length=50, verbose_name='秒数(0-59)', blank=True, null=True)
    author = models.ForeignKey(User, related_name='cron_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '5、特定时间周期性地触发器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class JobLog(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name="内容", default="")
    level = models.CharField(verbose_name="等级", max_length=10, default="0", blank=True)
    job_id = models.IntegerField(verbose_name="任务ID", null=False)
    type = models.CharField(choices=settings.TYPES, verbose_name='类型', max_length=10)
    datetime = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    class Meta:
        verbose_name = '任务执行日志'
        verbose_name_plural = verbose_name


# todo 添加自定义 模型
class AbstractJob(models.Model):
    TRIGGER = (
        ('date', '特定的时间点触发器'),
        ('interval', '固定时间间隔触发器'),
        ('cron', '特定时间周期性地触发器'),
    )
    STATUS = (
        ('0', '启用'),
        ('1', '停用'),
        ('2', '失效'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, verbose_name='任务名称')
    trigger = models.CharField(choices=TRIGGER, max_length=10, verbose_name='触发器类型')
    DateSchedulers = models.OneToOneField(DateSchedulers, on_delete=models.CASCADE
                                          , verbose_name='特定的时间点触发器', blank=True, null=True)
    IntervalSchedulers = models.OneToOneField(IntervalSchedulers, on_delete=models.CASCADE
                                              , verbose_name='固定时间间隔触发器', blank=True, null=True)
    CronSchedulers = models.OneToOneField(CronSchedulers, on_delete=models.CASCADE, verbose_name='特定时间周期性地触发器'
                                          , blank=True, null=True)
    datetime = models.DateTimeField(verbose_name='创建时间', auto_now=True)
    next_time = models.DateTimeField(verbose_name='下次执行时间', blank=True, null=True)
    job_id = models.CharField(max_length=50, verbose_name='任务id', blank=True, null=True, default='')
    enable = models.CharField(choices=STATUS, max_length=5, verbose_name='当前状态', default=1)
    ReceiversEmail = models.CharField(verbose_name='接受方邮件地址(多个用 | 分开)', max_length=200)
    remarks = models.TextField(verbose_name='备注', blank=True, null=True)

    class Meta:
        abstract = True


class ScriptJob(AbstractJob):
    SCRIPTS = (
        # ('0', 'java'),
        ('1', 'python'),
        # ('2', 'js'),
        # ('3', "bash")
    )
    script_type = models.CharField(choices=SCRIPTS, max_length=10, verbose_name="语言类型", default="1")
    script_content = models.TextField(verbose_name="脚本内容", null=False, blank=False)
    script_timeout = models.IntegerField(verbose_name="执行超时时间(s)", default=300)
    author = models.ForeignKey(User, related_name='script_job_author', on_delete=models.CASCADE, verbose_name='用户')
    type = models.CharField(choices=settings.TYPES, verbose_name='类型', max_length=10, default="0")

    class Meta:
        verbose_name = '脚本执行任务'
        verbose_name_plural = verbose_name


class ApiJob(AbstractJob):
    METHODS = (
        ('GET', 'GET'),
        ('PUT', 'PUT'),
        ('POST', 'POST'),
        ('DELETE', "DELETE"),
        ('PATCH', "PATCH")
    )
    url = models.CharField(max_length=255, verbose_name='网址', blank=False, null=False)
    method = models.CharField(choices=METHODS, max_length=10, verbose_name="方法", blank=False, null=False, default="GET")
    params = models.TextField(verbose_name="命令行参数, json格式", default="", blank=True)
    json_data = models.TextField(verbose_name="post application/json 请求参数", default="", blank=True)
    form_data = models.TextField(verbose_name="post form 请求参数", default="", blank=True)
    headers = models.TextField(verbose_name="请求头 json格式", default="", blank=True)
    verify = models.BooleanField(verbose_name="忽略 https 校验", default=False)
    author = models.ForeignKey(User, related_name='api_job_author', on_delete=models.CASCADE, verbose_name='用户')
    type = models.CharField(choices=settings.TYPES, verbose_name='类型', max_length=10, default="1")

    class Meta:
        verbose_name = 'HTTP API执行任务'
        verbose_name_plural = verbose_name


class CommonJob(AbstractJob):
    path = models.CharField(max_length=1024, verbose_name="模块路径", null=False, blank=False,
                            default="path1/path2/path3.func1")
    params = models.TextField(verbose_name="参数, json格式", blank=True, default="")
    author = models.ForeignKey(User, related_name='common_job_author', on_delete=models.CASCADE, verbose_name='用户')
    type = models.CharField(choices=settings.TYPES, verbose_name='类型', max_length=10, default="2")

    class Meta:
        verbose_name = '通用执行任务'
        verbose_name_plural = verbose_name


class Email(models.Model):
    EMAIL_TYPE = (
        ('1', 'Exchange邮箱'),
        ('2', '其他邮箱'),
    )
    id = models.AutoField(primary_key=True)
    EmailType = models.CharField(choices=EMAIL_TYPE, max_length=10, verbose_name='邮箱类型', default=2)
    EmailServer = models.CharField(verbose_name='邮箱服务器地址', max_length=50)
    SendEmailAdd = models.EmailField(verbose_name='发送方邮件地址')
    SendEmailUser = models.CharField(verbose_name='发送方邮件账户', max_length=50)
    SendEmailPsd = models.CharField(verbose_name='发送放邮件密码', max_length=100)
    ReceiversEmail = models.CharField(verbose_name='接受方邮件地址(仅用于邮件测试)', max_length=200)
    author = models.ForeignKey(User, related_name='email_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '6、邮件告警配置'
        verbose_name_plural = verbose_name

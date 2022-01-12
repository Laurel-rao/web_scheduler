from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone

# Create your models here.


class DateSchedulers(models.Model):
    name = models.CharField(max_length=25, verbose_name='触发器名称')
    datetime = models.DateTimeField(verbose_name='开始时间')
    author = models.ForeignKey(User, related_name='date_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '3、特定的时间点触发器'
        verbose_name_plural = verbose_name

    def __str__(self):
            return self.name


class IntervalSchedulers(models.Model):
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


class SchedulersJob(models.Model):
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
    OneOrMore = (
        ('1', '单页爬取'),
        ('2', '多页爬取'),
    )
    name = models.CharField(max_length=25, verbose_name='任务名称')
    web_url = models.CharField(max_length=200, verbose_name='网址')
    keywords = models.CharField(max_length=100, verbose_name='关键字(多个用 | 分开)')
    islazyload = models.BooleanField(verbose_name='是否为懒加载网站', default=False)
    mask_keys = models.CharField(max_length=100, verbose_name='存放招标信息的关键字(多个用 | 分开)', blank=True, null=True)
    url_key = models.CharField(max_length=100, verbose_name='存放详细页网址的关键字', blank=True, null=True)
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
    islogin = models.BooleanField(verbose_name='是否需要登录', default=False)
    login_url = models.CharField(max_length=200, verbose_name='登录地址', blank=True, null=True)
    username_input = models.CharField(max_length=200, verbose_name='用户名输入框的XPath', blank=True, null=True)
    username_text = models.CharField(max_length=200, verbose_name='登录用户名', blank=True, null=True)
    password_input = models.CharField(max_length=200, verbose_name='密码输入框的XPath', blank=True, null=True)
    password_text = models.CharField(max_length=200, verbose_name='登录密码', blank=True, null=True)
    login_button = models.CharField(max_length=200, verbose_name='提交按钮的XPath', blank=True, null=True)
    oneormore = models.CharField(choices=OneOrMore, max_length=5, verbose_name='单页爬取/多页爬取', default=1)
    nextbutton = models.CharField(max_length=200, verbose_name='下一页按钮的名称', blank=True, null=True)
    pagenum = models.IntegerField(verbose_name='爬取页数', blank=True, null=True)
    remarks = models.TextField(verbose_name='备注', blank=True, null=True)
    type = models.CharField(verbose_name='类型', default='one', max_length=10)
    author = models.ForeignKey(User, related_name='job_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '1、通用单页面定时爬虫任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SchedulersJob2(models.Model):
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
    OneOrMore = (
        ('1', '单页爬取'),
        ('2', '多页爬取'),
    )
    name = models.CharField(max_length=25, verbose_name='任务名称')
    web_url = models.CharField(max_length=200, verbose_name='网址')
    keywords = models.CharField(max_length=100, verbose_name='关键字(多个用 | 分开)')
    pattern = models.CharField(max_length=100, verbose_name='正则表达式模式')
    base_url = models.CharField(max_length=100, verbose_name='根网址')
    selector = models.CharField(max_length=100, verbose_name='指定区域selector', blank=True, null=True)
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
    islogin = models.BooleanField(verbose_name='是否需要登录', default=False)
    login_url = models.CharField(max_length=200, verbose_name='登录地址', blank=True, null=True)
    username_input = models.CharField(max_length=200, verbose_name='用户名输入框的XPath', blank=True, null=True)
    username_text = models.CharField(max_length=200, verbose_name='登录用户名', blank=True, null=True)
    password_input = models.CharField(max_length=200, verbose_name='密码输入框的XPath', blank=True, null=True)
    password_text = models.CharField(max_length=200, verbose_name='登录密码', blank=True, null=True)
    login_button = models.CharField(max_length=200, verbose_name='提交按钮的XPath', blank=True, null=True)
    oneormore = models.CharField(choices=OneOrMore, max_length=5, verbose_name='单页爬取/多页爬取', default=1)
    nextbutton = models.CharField(max_length=200, verbose_name='下一页按钮的名称', blank=True, null=True)
    pagenum = models.IntegerField(verbose_name='爬取页数', blank=True, null=True)
    remarks = models.TextField(verbose_name='备注', blank=True, null=True)
    type = models.CharField(verbose_name='类型', default='two', max_length=10)
    author = models.ForeignKey(User, related_name='Job2_author', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = '2、二级页面定时爬虫任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Email(models.Model):
    EMAIL_TYPE = (
        ('1', 'Exchange邮箱'),
        ('2', '其他邮箱'),
    )
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


# Generated by Django 3.1.4 on 2021-03-12 07:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CronSchedulers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='触发器名称')),
                ('year', models.CharField(blank=True, max_length=50, null=True, verbose_name='年份(2020)')),
                ('month', models.CharField(blank=True, max_length=50, null=True, verbose_name='月份(1-12)')),
                ('day', models.CharField(blank=True, max_length=50, null=True, verbose_name='日期(1-31)')),
                ('week', models.CharField(blank=True, max_length=50, null=True, verbose_name='周数(1-53)')),
                ('day_of_week', models.CharField(blank=True, max_length=50, null=True, verbose_name='工作日(0-6)')),
                ('hour', models.CharField(blank=True, max_length=50, null=True, verbose_name='小时(0-23)')),
                ('minute', models.CharField(blank=True, max_length=50, null=True, verbose_name='分钟(0-59)')),
                ('second', models.CharField(blank=True, max_length=50, null=True, verbose_name='秒数(0-59)')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cron_author', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '5、特定时间周期性地触发器',
                'verbose_name_plural': '5、特定时间周期性地触发器',
            },
        ),
        migrations.CreateModel(
            name='DateSchedulers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='触发器名称')),
                ('datetime', models.DateTimeField(verbose_name='开始时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='date_author', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '3、特定的时间点触发器',
                'verbose_name_plural': '3、特定的时间点触发器',
            },
        ),
        migrations.CreateModel(
            name='IntervalSchedulers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='触发器名称')),
                ('weeks', models.IntegerField(blank=True, default=0, null=True, verbose_name='间隔周数')),
                ('days', models.IntegerField(blank=True, default=0, null=True, verbose_name='间隔天数')),
                ('hours', models.IntegerField(blank=True, default=0, null=True, verbose_name='间隔小时数')),
                ('minutes', models.IntegerField(blank=True, default=0, null=True, verbose_name='间隔分钟数')),
                ('seconds', models.IntegerField(blank=True, default=0, null=True, verbose_name='间隔秒数')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='开始日期')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interval_author', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '4、固定时间间隔触发器',
                'verbose_name_plural': '4、固定时间间隔触发器',
            },
        ),
        migrations.CreateModel(
            name='SchedulersJob2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='任务名称')),
                ('web_url', models.CharField(max_length=200, verbose_name='网址')),
                ('keywords', models.CharField(max_length=100, verbose_name='关键字(多个用 | 分开)')),
                ('pattern', models.CharField(max_length=100, verbose_name='正则表达式模式')),
                ('base_url', models.CharField(max_length=100, verbose_name='根网址')),
                ('trigger', models.CharField(choices=[('date', '特定的时间点触发器'), ('interval', '固定时间间隔触发器'), ('cron', '特定时间周期性地触发器')], max_length=10, verbose_name='触发器类型')),
                ('datetime', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('next_time', models.DateTimeField(blank=True, null=True, verbose_name='下次执行时间')),
                ('job_id', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='任务id')),
                ('enable', models.CharField(choices=[('0', '启用'), ('1', '停用'), ('2', '失效')], default=1, max_length=5, verbose_name='当前状态')),
                ('ReceiversEmail', models.CharField(max_length=200, verbose_name='接受方邮件地址(多个用 | 分开)')),
                ('islogin', models.BooleanField(default=False, verbose_name='是否需要登录')),
                ('username_input', models.CharField(blank=True, max_length=200, null=True, verbose_name='用户名输入框的XPath')),
                ('password_input', models.CharField(blank=True, max_length=200, null=True, verbose_name='密码输入框的XPath')),
                ('login_button', models.CharField(blank=True, max_length=200, null=True, verbose_name='提交按钮的XPath')),
                ('oneormore', models.CharField(choices=[('1', '单页爬取'), ('2', '多页爬取')], default=1, max_length=5, verbose_name='单页爬取/多页爬取')),
                ('nextbutton', models.CharField(blank=True, max_length=100, null=True, verbose_name='下一页按钮的XPath')),
                ('pagenum', models.IntegerField(blank=True, null=True, verbose_name='爬取页数')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('type', models.CharField(default='two', max_length=10, verbose_name='类型')),
                ('CronSchedulers', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulers.cronschedulers', verbose_name='特定时间周期性地触发器')),
                ('DateSchedulers', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulers.dateschedulers', verbose_name='特定的时间点触发器')),
                ('IntervalSchedulers', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulers.intervalschedulers', verbose_name='固定时间间隔触发器')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Job2_author', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '2、二级页面定时爬虫任务',
                'verbose_name_plural': '2、二级页面定时爬虫任务',
            },
        ),
        migrations.CreateModel(
            name='SchedulersJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='任务名称')),
                ('web_url', models.CharField(max_length=200, verbose_name='网址')),
                ('keywords', models.CharField(max_length=100, verbose_name='关键字(多个用 | 分开)')),
                ('trigger', models.CharField(choices=[('date', '特定的时间点触发器'), ('interval', '固定时间间隔触发器'), ('cron', '特定时间周期性地触发器')], max_length=10, verbose_name='触发器类型')),
                ('datetime', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('next_time', models.DateTimeField(blank=True, null=True, verbose_name='下次执行时间')),
                ('job_id', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='任务id')),
                ('enable', models.CharField(choices=[('0', '启用'), ('1', '停用'), ('2', '失效')], default=1, max_length=5, verbose_name='当前状态')),
                ('ReceiversEmail', models.CharField(max_length=200, verbose_name='接受方邮件地址(多个用 | 分开)')),
                ('islogin', models.BooleanField(default=False, verbose_name='是否需要登录')),
                ('login_url', models.CharField(blank=True, max_length=200, null=True, verbose_name='登录地址')),
                ('username_input', models.CharField(blank=True, max_length=200, null=True, verbose_name='用户名输入框的XPath')),
                ('password_input', models.CharField(blank=True, max_length=200, null=True, verbose_name='密码输入框的XPath')),
                ('login_button', models.CharField(blank=True, max_length=200, null=True, verbose_name='提交按钮的XPath')),
                ('oneormore', models.CharField(choices=[('1', '单页爬取'), ('2', '多页爬取')], default=1, max_length=5, verbose_name='单页爬取/多页爬取')),
                ('nextbutton', models.CharField(blank=True, max_length=100, null=True, verbose_name='下一页按钮的XPath')),
                ('pagenum', models.IntegerField(blank=True, null=True, verbose_name='爬取页数')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('type', models.CharField(default='one', max_length=10, verbose_name='类型')),
                ('CronSchedulers', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulers.cronschedulers', verbose_name='特定时间周期性地触发器')),
                ('DateSchedulers', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulers.dateschedulers', verbose_name='特定的时间点触发器')),
                ('IntervalSchedulers', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulers.intervalschedulers', verbose_name='固定时间间隔触发器')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_author', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '1、通用单页面定时爬虫任务',
                'verbose_name_plural': '1、通用单页面定时爬虫任务',
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EmailServer', models.CharField(max_length=50, verbose_name='邮箱服务器地址')),
                ('SendEmailAdd', models.EmailField(max_length=254, verbose_name='发送方邮件地址')),
                ('SendEmailUser', models.CharField(max_length=50, verbose_name='发送方邮件账户')),
                ('SendEmailPsd', models.CharField(max_length=100, verbose_name='发送放邮件密码')),
                ('ReceiversEmail', models.CharField(max_length=200, verbose_name='接受方邮件地址(仅用于邮件测试)')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_author', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '6、邮件告警配置',
                'verbose_name_plural': '6、邮件告警配置',
            },
        ),
    ]
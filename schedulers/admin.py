from django.contrib import admin
from .models import *
from .en_de import encrypt_p
from .forms import EmailForm


# Register your models here.


class APIJobAdmin(admin.ModelAdmin):
    exclude = ('next_time', 'author', 'type')
    """设置列表可显示的字段"""
    list_display = ('name', 'DateSchedulers', 'IntervalSchedulers', 'CronSchedulers'
                    , 'author',)
    '''设置过滤选项'''
    list_filter = ('name', 'trigger')
    '''每页显示条目数'''
    list_per_page = 10
    '''设置可编辑字段'''
    # list_editable = ('status',)
    '''按发布日期排序'''
    ordering = ('-datetime',)

    def get_queryset(self, request):
        # 用于后台数据依据用户做隔离，用户只能看到自己创建的数据，管理员可以看到全部
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 此处user为当前model的related object的related object， 正常的外键只要filter(user=request.user)
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()


class CommonJobAdmin(admin.ModelAdmin):
    exclude = ('next_time', 'author', 'type')
    """设置列表可显示的字段"""
    list_display = ('name', 'DateSchedulers', 'IntervalSchedulers', 'CronSchedulers'
                    , 'author',)
    '''设置过滤选项'''
    list_filter = ('name', 'trigger')
    '''每页显示条目数'''
    list_per_page = 10
    '''设置可编辑字段'''
    # list_editable = ('status',)
    '''按发布日期排序'''
    ordering = ('-datetime',)

    def get_queryset(self, request):
        # 用于后台数据依据用户做隔离，用户只能看到自己创建的数据，管理员可以看到全部
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 此处user为当前model的related object的related object， 正常的外键只要filter(user=request.user)
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()


class DateSchedulersAdmin(admin.ModelAdmin):
    exclude = ('author',)
    list_display = ('name', 'datetime', 'author',)
    '''设置过滤选项'''
    list_filter = ('name',)

    def get_queryset(self, request):
        # 用于后台数据依据用户做隔离，用户只能看到自己创建的数据，管理员可以看到全部
        qs = super(DateSchedulersAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 此处user为当前model的related object的related object， 正常的外键只要filter(user=request.user)
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()


class IntervalSchedulersAdmin(admin.ModelAdmin):
    exclude = ('author',)
    list_display = ('name', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'start_date', 'author',)
    '''设置过滤选项'''
    list_filter = ('name',)

    def get_queryset(self, request):
        # 用于后台数据依据用户做隔离，用户只能看到自己创建的数据，管理员可以看到全部
        qs = super(IntervalSchedulersAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 此处user为当前model的related object的related object， 正常的外键只要filter(user=request.user)
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()


class CronSchedulersAdmin(admin.ModelAdmin):
    exclude = ('author',)
    list_display = ('name', 'year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second', 'author',)
    '''设置过滤选项'''
    list_filter = ('name',)

    def get_queryset(self, request):
        # 用于后台数据依据用户做隔离，用户只能看到自己创建的数据，管理员可以看到全部
        qs = super(CronSchedulersAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 此处user为当前model的related object的related object， 正常的外键只要filter(user=request.user)
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()


class EmailAdmin(admin.ModelAdmin):
    # 设置密码字段在admin后台，输入和显示的时候为*
    form = EmailForm
    list_display = ('EmailServer', 'SendEmailAdd', 'SendEmailUser', 'ReceiversEmail', 'author',)

    def get_queryset(self, request):
        # 用于后台数据依据用户做隔离，用户只能看到自己创建的数据，管理员可以看到全部
        qs = super(EmailAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 此处user为当前model的related object的related object， 正常的外键只要filter(user=request.user)
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.SendEmailPsd = encrypt_p(request.POST['SendEmailPsd'])
        obj.save()


# todo 添加任务任务日志页面， 用户管理界面

admin.site.register(ApiJob, APIJobAdmin)
admin.site.register(CommonJob, CommonJobAdmin)
admin.site.register(ScriptJob, CommonJobAdmin)
admin.site.register(DateSchedulers, DateSchedulersAdmin)
admin.site.register(IntervalSchedulers, IntervalSchedulersAdmin)
admin.site.register(CronSchedulers, CronSchedulersAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(JobLog, admin.ModelAdmin)


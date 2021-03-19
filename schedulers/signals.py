from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.forms import model_to_dict

from .models import *
from .views import scheduler, startup_jobs


@receiver(post_save, sender=DateSchedulers, dispatch_uid="DateSchedulers_post_save")
def date_schedulers_saved(sender, instance, **kwargs):
    if kwargs['created'] is False:
        #  当触发器修改时间后，对应的任务也需更新
        DateSchedulers_obj = instance
        job_list = list(SchedulersJob.objects.filter(DateSchedulers=DateSchedulers_obj.id).values())
        if not job_list:
            job_list = list(SchedulersJob2.objects.filter(DateSchedulers=DateSchedulers_obj.id).values())
        if job_list:
            if job_list[0]['job_id'] and job_list[0]['enable'] == '0':
                scheduler.remove_job(job_list[0]['job_id'])
            if job_list[0]['type'] == 'one':
                SchedulersJob.objects.filter(id=job_list[0]['id']).update(job_id='', enable='1', next_time=None)
            else:
                SchedulersJob2.objects.filter(id=job_list[0]['id']).update(job_id='', enable='1', next_time=None)


@receiver(post_save, sender=IntervalSchedulers, dispatch_uid="IntervalSchedulers_post_save")
def interval_schedulers_saved(sender, instance, **kwargs):
    if kwargs['created'] is False:
        #  当触发器修改时间后，对应的任务也需更新
        IntervalSchedulers_obj = instance
        job_list = list(SchedulersJob.objects.filter(IntervalSchedulers=IntervalSchedulers_obj.id).values())
        if not job_list:
            job_list = list(SchedulersJob2.objects.filter(IntervalSchedulers=IntervalSchedulers_obj.id).values())
        if job_list:
            if job_list[0]['job_id'] and job_list[0]['enable'] == '0':
                scheduler.remove_job(job_list[0]['job_id'])
            if job_list[0]['type'] == 'one':
                SchedulersJob.objects.filter(id=job_list[0]['id']).update(job_id='', enable='1', next_time=None)
            else:
                SchedulersJob2.objects.filter(id=job_list[0]['id']).update(job_id='', enable='1', next_time=None)


@receiver(post_save, sender=CronSchedulers, dispatch_uid="CronSchedulers_post_save")
def cron_schedulers_saved(sender, instance, **kwargs):
    if kwargs['created'] is False:
        #  当触发器修改时间后，对应的任务也需更新
        CronSchedulers_obj = instance
        job_list = list(SchedulersJob.objects.filter(CronSchedulers=CronSchedulers_obj).values())
        if not job_list:
            job_list = list(SchedulersJob2.objects.filter(CronSchedulers=CronSchedulers_obj).values())
        if job_list:
            if job_list[0]['job_id'] and job_list[0]['enable'] == '0':
                scheduler.remove_job(job_list[0]['job_id'])
            if job_list[0]['type'] == 'one':
                SchedulersJob.objects.filter(id=job_list[0]['id']).update(job_id='', enable='1', next_time=None)
            else:
                SchedulersJob2.objects.filter(id=job_list[0]['id']).update(job_id='', enable='1', next_time=None)


@receiver(post_delete, sender=SchedulersJob, dispatch_uid="SchedulersJob_post_delete")
def schedulers_job_post_delete(sender, instance, **kwargs):
    # 后台删除任务时，scheduler真实任务一并移除。
    job_id = instance.job_id
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)

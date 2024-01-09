import traceback

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from logs.log import logger
from .models import *
# from .views import get_all_job_model, startup_jobs, stop_job
from .views import scheduler, get_all_job_model, startup_jobs, stop_job


@receiver(post_save, sender=DateSchedulers, dispatch_uid="DateSchedulers_post_save")
def date_schedulers_saved(sender, instance, **kwargs):
    logger.debug("date run", kwargs)
    if kwargs['created'] is False:
        #  当触发器修改时间后，对应的任务也需更新
        for model in get_all_job_model():
            for job_dict in model.objects.filter(IntervalSchedulers=instance.id, enable="0", trigger="date").values():
                req = startup_jobs(cur_model=model, username="", **job_dict)
                logger.debug(req)


@receiver(post_save, sender=IntervalSchedulers, dispatch_uid="IntervalSchedulers_post_save")
def interval_schedulers_saved(sender, instance, **kwargs):
    print("interval run", kwargs)
    if kwargs['created'] is False:
        #  当触发器修改时间后，对应的任务也需更新
        for model in get_all_job_model():
            for job_dict in model.objects.filter(IntervalSchedulers=instance.id, enable="0", trigger="interval").values():
                req = startup_jobs(cur_model=model, username="", **job_dict)
                logger.debug(req)


@receiver(post_save, sender=CronSchedulers, dispatch_uid="CronSchedulers_post_save")
def cron_schedulers_saved(sender, instance, **kwargs):
    logger.debug("cron run", kwargs)

    if kwargs['created'] is False:
        #  当触发器修改时间后，对应的任务也需更新
        for model in get_all_job_model():
            for job_dict in model.objects.filter(IntervalSchedulers=instance.id, enable="0", trigger="cron").values():
                req = startup_jobs(cur_model=model, username="", **job_dict)
                logger.debug(req)



# @receiver(post_delete, sender=, dispatch_uid="SchedulersJob_post_delete")
# def schedulers_job_post_delete(sender, instance, **kwargs):
#     # 后台删除任务时，scheduler真实任务一并移除。
#     job_id = instance.job_id
#     job = scheduler.get_job(job_id)
#     if job:
#         scheduler.remove_job(job_id)

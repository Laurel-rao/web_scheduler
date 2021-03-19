# 每次启动时scheduler中也将被自动清空（因为报错在内存中）。为此需同时将数据库中相依的任务信息做调整
from schedulers.models import SchedulersJob


def clear_job():
    print('clear_job')
    jobs_obj = SchedulersJob.objects.all()
    for i in jobs_obj:
        if i.enable != '0':
            SchedulersJob.objects.filter(id=i.id).update(next_time=None, job_id='', enable='1')
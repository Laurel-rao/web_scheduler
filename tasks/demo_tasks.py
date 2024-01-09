import random

from schedulers.tools import write_job_log


def run(*args, **kwargs):
    print(args, kwargs)
    data = random.random()
    job_type = kwargs.get("job_type")
    job_id = kwargs.get("job_id")
    write_job_log(job_type, job_id, "测试运行 %s" % data)
    return "done"

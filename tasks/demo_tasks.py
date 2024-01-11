import random

from schedulers.tools import write_job_log
from schedulers.views import send_email


def run(*args, **kwargs):
    print(args, kwargs)
    data = random.random()
    job_type = kwargs.get("job_type")
    job_id = kwargs.get("job_id")
    recv_email = kwargs.get("recv_email")
    req = send_email("测试发送", "admin", recv_email)
    write_job_log(job_type, job_id, "邮件发送结果 %s" % req)
    write_job_log(job_type, job_id, "测试运行 %s" % data)
    return "done"

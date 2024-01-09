import traceback

from logs.log import logger
from schedulers.models import JobLog


def write_job_log(job_type, job_id, msg, level="0"):
    try:
        if level == "0":
            logger.debug(f"job debug {job_type} {job_id} level:{level}: {msg}")
        else:
            logger.error(f"job error {job_type} {job_id} level:{level}: {msg}")
        job_log = JobLog(content=msg, level=level, job_id=job_id, type=job_type)
        job_log.save()
    except:
        logger.error("error %s" % traceback.format_exc())

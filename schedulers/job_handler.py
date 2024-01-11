import importlib
import json
import sys
import threading
import time
import traceback
from io import StringIO
from threading import Thread

import requests

from logs.log import logger
from schedulers.tools import write_job_log


class JobHandler:
    def __init__(self, job_dict, username, *args, **kwargs):
        self.job_dict = job_dict
        self.job_id = job_dict['id']
        self.job_type = job_dict['type']
        self.username = username
        self.open()
        self.run()
        self.close()

    def close(self):
        pass

    def open(self):
        pass

    def run(self):
        pass

    def parse(self, content):
        if content:
            return json.loads(content)
        else:
            return {}


def capture_print_output(func):
    # 创建一个用于捕获输出的StringIO对象
    output = StringIO()
    sys.stdout = output

    # 调用函数，并将输出捕获到StringIO对象中
    msg = ""
    try:
        func()
    except Exception as e:
        msg = str(e)

    # 重置sys.stdout，恢复原有的输出方式
    sys.stdout = sys.__stdout__

    # 获取捕获到的输出内容
    output_string = output.getvalue() + msg

    # 关闭StringIO对象
    output.close()

    # 返回输出内容
    return output_string


def execute_with_timeout(func, args, timeout_seconds):
    thread = threading.Thread(target=func, args=args)  # 创建一个线程执行函数
    thread.start()  # 启动线程
    thread.join(timeout_seconds)  # 等待线程执行完成或超时
    if thread.is_alive():  # 如果线程仍在运行，则超时
        # thread.join()  # 等待线程正常结束
        raise TimeoutError("RuntimeError timeout %s" % timeout_seconds)


class ScriptJobHandler(JobHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

    def run(self):
        script_content = self.job_dict.get("script_content")
        script_timeout = float(self.job_dict.get("script_timeout"))
        try:
            def func():
                execute_with_timeout(exec, (script_content,), script_timeout)
            result = capture_print_output(func)
        except Exception as e:
            msg = f"Error %s" % traceback.format_exc()
            logger.error(msg)
        else:
            msg = f"result: {result}"

        write_job_log(self.job_type, self.job_id, msg=msg)


class ApiJobHandler(JobHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

    def run(self):
        method = self.job_dict.get("method")
        url = self.job_dict.get("url")
        verify = self.job_dict.get("verify")
        headers = self.parse(self.job_dict.get("headers"))
        json_data = self.parse(self.job_dict.get("json_data"))
        form_data = self.parse(self.job_dict.get("form_data"))
        params = self.parse(self.job_dict.get("params"))
        try:
            resp = requests.request(method, url, headers=headers, json=json_data, data=form_data, params=params,
                                    verify=verify)
        except Exception as e:
            msg = f"Error %s" % traceback.format_exc()
            logger.error(msg)
        else:
            msg = f"code: {resp.status_code}, headers: {resp.headers}, content: {resp.text}"

        write_job_log(self.job_type, self.job_id, msg=str(msg))


def execute_function(path, params):
    # 将路径切分为模块路径和函数名
    module_path, function_name = path.rsplit('.', 1)
    # path1/path2/path3.func1
    try:
        # 动态导入模块
        module_path = module_path.replace("/", ".")
        module = importlib.import_module(module_path)

        # 获取函数对象
        function = getattr(module, function_name)

        # 执行函数
        return function(**params)

    except ImportError:
        logger.error("无法导入模块")
        raise

    except AttributeError:
        logger.error("未找到函数")
        raise


class CommonJobHandler(JobHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

    def run(self):
        path = self.job_dict.get("path")
        params = self.parse(self.job_dict.get("params"))
        params.update({"job_id": self.job_id, "job_type": "2", "recv_email": self.job_dict.get("ReceiversEmail")})
        try:
            result = execute_function(path, params)
        except Exception as e:
            msg = f"Error %s" % traceback.format_exc()
            logger.error(msg)
            level = 1
        else:
            level = 0
            msg = f"result: {result}"

        write_job_log(self.job_type, self.job_id, msg=msg, level=level)

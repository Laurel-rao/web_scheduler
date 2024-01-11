# web_scheduler

## Introduce

A scheduler task project, base on apscheduler + django , design three types of job.
    - API Task(http, https)
    - Script Task (execute raw python code)
    - General Task (Call a customize function)
  
Compare to APScheduler, this project build a website that you can operated on browser.
    - In case, something wrong in the job, you can view the job log on website.
    - Use Django + APScheduler to build some API make us easier to control it.
    - use vue framework and django admin , build our website page.
So, just for sure, you can create a issue to make your idea to be true.  
  
## Structure

- python 3.8.5
- django 4.0+
- vue 2.6.5

## Getting started

### Run as normal service
#### 1. build you environment

1. install python , 3.8.5 will be perfect, use virtual environment that provide a clean place.
2. install the requirements, `pip install -r requirements.txt`
3. init django environment
    1. modify you database setting, `web_scheduler/settings.py`, default is sqlite3
        ```
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
       ```
    2. make connection with database
        1. `python manage.py makemigrations`
        2. `python manage.py migrate`
    3. create a superuser
        1. `python manage.py createsuperuser`

#### 2. run it
1. open in your browser http://127.0.0.1:8000
    - `python manage.py 0.0.0.0:8000`
   
   
### Run from docker container

- 

### Run as Docker-compose

```

git pull https://github.com/Laurel-rao/web_scheduler.git
docker-compose up -d

```
- open it `http://127.0.0.1:8000`
- admin/admin



#### 系统界面截图
1.  前端截图
![输入图片说明](https://images.gitee.com/uploads/images/2021/0319/112213_791d44bd_1419487.png "1616124103(1).png")

2.  后端截图
![输入图片说明](https://images.gitee.com/uploads/images/2021/0319/112521_21e348a7_1419487.png "1616124147(1).png")


#### 软件架构
前端为：vue2+element+无需 nodejs
后端为：python3.8.5+django 3.8


#### 安装教程

1.  系统中完成python3安装后，使用`pip install -r requirements.txt`指令完成后端所需python库的安装。（注：建议使用`virtualenv`等）
2.  环境搭建完成后，使用`python3 manage.py makemigrations`以及`python3 manage.py migrate`指令完成数据库初始化。如出现报错，可先将admin.py中最后一行的clear_job()注释掉，待数据库构建完成后再解除注释即可。
3.  使用`python3 manage.py createsuperuser`指令完成后端管理员账号的创建, 默认账户名密码 admin admin, 可自行切换到 mysql 后重新创建
4.  直接使用`python3 manage.py runserver 0.0.0.0:8000`启动。

#### 基本使用说明

1.  系统启动后，访问`http:\\127.0.0.1\admin`（地址依据实际情况替换）进入后端，完成`邮件告警配置`以及`定时任务和相应触发器`的配置。（定时任务创建时需暂不启动）
2.  访问搭建后的前端地址，在前端界面可以看到所有定时任务清单，并且可以控制启动和停止。
3.  点击定时任务后的`启动`按钮，可以启动任务，双击任务可以看到明细，包括下次执行任务的时间等。
4.  启动后的任务，相依的按钮将变更为`停止`。点击后，相依的定时任务将被为暂停。重新点击启动可以恢复。但如果设定的执行时间已过，则按钮将会变为禁止状态，显示为`失效`
5.  触发器对任务是一对多的关系。修改触发器时间，会对所有应用该触发器的任务产生影响
6.  已配置数据库保存任务
7.  建议在后端配置完`邮件告警配置`后，在前端点击`邮件测试`按钮，测试邮件发送是否正常。


#### 任务类型说明

##### 脚本任务
- 可通过执行 python 代码，执行相应任务

##### API 访问任务
- 可通过http / https 访问网络请求任务

##### 通用函数任务
- 通过自行编写函数代码，然后输入函数位置，执行相应任务

#### 参与贡献

1.  Fork 本仓库1. 这里是列表文本
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)

# web_scheduler

#### 介绍
功能：基于python+APScheduler的定时任务管理系统，目前定时执行的任务为获取指定网页的源码并与关键字比对，若比对通过则发送邮件通知。
开发语言及框架为：
前端为：vue+element
后端为：python+django

#### 系统界面截图
1.  前端截图
![输入图片说明](https://images.gitee.com/uploads/images/2021/0319/112213_791d44bd_1419487.png "1616124103(1).png")

2.  后端截图
![输入图片说明](https://images.gitee.com/uploads/images/2021/0319/112521_21e348a7_1419487.png "1616124147(1).png")


#### 软件架构
前端为：vue+element
后端为：python+django


#### 安装教程

1.  系统中完成python3安装后，使用`pip install -r requirements.txt`指令完成后端所需python库的安装。（注：建议使用`virtualenv`等）
2.  环境搭建完成后，使用`python3 manage.py makemigrations`以及`python3 manage.py migrate`指令完成数据库初始化。如出现报错，可先将admin.py中最后一行的clear_job()注释掉，待数据库构建完成后再解除注释即可。
3.  使用`python3 manage.py createsuperuser`指令完成后端管理员账号的创建
4.  直接使用`python3 manage.py runserver 0.0.0.0:8000`启动。

#### 基本使用说明

1.  系统启动后，访问`http:\\127.0.0.1\admin`（地址依据实际情况替换）进入后端，完成`邮件告警配置`以及`定时任务和相应触发器`的配置。（定时任务创建时需暂不启动）
2.  访问搭建后的前端地址，在前端界面可以看到所有定时任务清单，并且可以控制启动和停止。
3.  点击定时任务后的`启动`按钮，可以启动任务，双击任务可以看到明细，包括下次执行任务的时间等。
4.  启动后的任务，相依的按钮将变更为`停止`。点击后，相依的定时任务将被为暂停。重新点击启动可以恢复。但如果设定的执行时间已过，则按钮将会变为禁止状态，显示为`失效`
5.  每条任务与触发器是一对一的关系。修改触发器时间，仅会对指定任务产生影响，`修改时间后，任务将停止，需要重新启动`
6.  如果后端服务停止后重启，则原先的已启动的任务都将重置，需重新点击开启，`如果已超过计划执行时间，该任务将变为失效状态`
7.  建议在后端配置完`邮件告警配置`后，在前端点击`邮件测试`按钮，测试邮件发送是否正常。

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

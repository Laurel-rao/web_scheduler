const app = new Vue({
        el: "#app",
        data: {
            activeIndex: "1",
            pageJobs: [], //分页后当前页的学生
            tableData: [],
            baseURL: "/",
            inputstr: "", //输入的查询条件
            name: "123",

            //分页相关的变量
            total: 0, //数据的总行数
            currentPage: 1, //当前所在页
            pagesize: 10, //每页显示多少行
            // 日志数据分页查询
            curLogPage: 1,
            ticking: false,
            //弹出框表单
            dialogVisible: false,
            // 任务日志弹出框
            jobLogDialogVisible: false,
            text_logs: "",
            text_log_objs: [],
            //启动、停用按钮相关
            job_id: "",
            option: "",
            type: "",
            timeout: null,
            // 运行限流函数
            logRefresh: null,
            jobLogTitle: "任务日志",
            isRefreshLog: true,
            refreshLogGap: 5,
            refreshLogLength: 30,
            //任务明细相关
            job_detailed: {
                name: '',
                web_url: '',
                keywords: '',
                trigger: '',
                datetime: '',
                next_time: '',
                enable: '',
                remarks: '',
                type: '',
            },
            trigger: {
                'date': '特定的时间点触发器',
                'interval': '固定时间间隔触发器',
                'cron': '特定时间周期性地触发器'
            },
            status: {
                '0': '已启动',
                '1': '已停止',
                '2': '已失效',
            },
        },
        mounted() {
            //自动加载数据
            this.getAllJobs();
            setInterval(() => {
                this.getAllJobs(false)
            }, 15000)
            window.addEventListener('beforeunload', e => this.beforeunloadHandler(e))

        },
        destroyed() {
            window.removeEventListener('beforeunload', e => this.beforeunloadHandler(e))
        },
        methods: {
            beforeunloadHandler(e) {
                console.log('刷新或关闭');
                // let that = this;
                // axios
                //   .get(that.baseURL + "logout/")
            },
            //获取所有任务信息
            getAllJobs: function (info = true) {
                //使用Axios实现Ajax的请求
                //记录this 属性
                let that = this;
                axios
                    .get(that.baseURL + "jobs/")
                    .then(function (response) {
                        if (response.data.code === 1) {
                            //把数据给tableData
                            that.tableData = response.data.data;
                            that.name = response.data.username;
                            //获取返回数据的总行数
                            that.total = response.data.data.length;
                            //获取当前页的数据
                            that.getPageJobs();
                            //提示
                            if (info === true) {
                                that.$message({
                                    message: "数据加载成功~！",
                                    type: "success",
                                });
                            }
                        } else {
                            that.$message.error(response.data.msg);
                        }
                    })
                    .catch(function (error) {
                        console.log(error);
                    });
            },
            //获取当前页的jobs数据
            getPageJobs() {
                //清空pageJobs中的数据
                this.pageJobs = [];
                //获取当前页的数据
                for (
                    let i = (this.currentPage - 1) * this.pagesize;
                    i < this.total;
                    i++
                ) {
                    //遍历数据添加到pageJobs中
                    this.pageJobs.push(this.tableData[i]);
                    //判断是否达到一页的要求
                    if (this.pageJobs.length === this.pagesize) break;
                }
            },

            //分页时修改每页的数据
            handleSizeChange(size) {
                //修改当前每页数据行数
                this.pagesize = size;
                //数据重新分页
                this.getPageJobs();
            },

            //调整当前的页码
            handleCurrentChange(PageNum) {
                //修改当前的页码
                this.currentPage = PageNum;
                //数据重新分页
                this.getPageJobs();
            },

            //实现任务信息的查询
            query_job() {
                //使用Ajax请求-->post-->传递inputstr
                if (this.inputstr === '') {
                    this.getAllJobs();
                } else {
                    let that = this;
                    //开始Ajax的请求
                    axios
                        .post(that.baseURL + "jobs/query", {
                            inputstr: that.inputstr
                        })
                        .then(function (response) {
                            console.log(response);
                            if (response.data.code === 1) {
                                //把数据给tableData
                                that.tableData = response.data.data;
                                //获取返回数据的总行数
                                that.total = response.data.data.length;
                                //获取当页的数据
                                that.getPageJobs();
                                //提示
                                that.$message({
                                    message: "数据加载成功~！",
                                    type: "success",
                                });
                            } else {
                                that.$message.error(response.data.msg);
                            }
                        })
                        .catch(function (error) {
                            console.log(error);
                        });
                }
            },
            //数据刷新功能
            refresh() {
                this.getAllJobs();
            },
            //双击单元格显示任务明细
            cell_dblclick(row) {
                this.job_detailed.name = row.name;
                this.job_detailed.web_url = row.web_url;
                this.job_detailed.keywords = row.keywords;
                this.job_detailed.trigger = this.trigger[row.trigger];
                this.job_detailed.datetime = row.datetime;
                this.job_detailed.next_time = row.next_time;
                this.job_detailed.enable = this.status[row.enable];
                this.job_detailed.remarks = row.remarks
                this.job_detailed.type = row.type
                this.dialogVisible = true;
            },
            // 限流
            runOnce(target, delay = 500) {
                let last = 0;
                return function (...args) {
                    const now = Date.now();
                    if (now - last >= delay) {
                        target.apply(this, args);
                        last = now;
                    }
                };
            },
            updateLog(that, row, init = false) {
                axios.get(that.baseURL + "api/job_log/", {
                    params: {
                        job_id: row.id,
                        type: row.type,
                        page: 1,
                        page_size: this.refreshLogLength
                    }
                }).then(function (response) {
                    if (response.status === 200) {
                        //把数据给tableData
                        let results = response.data.results;
                        let new_arr = [...that.text_log_objs, ...results];
                        that.text_log_objs = Array.from(new Set(new_arr.map(obj => obj.id))).map(id => new_arr.find(obj => obj.id === id));
                        results = that.text_log_objs.sort((v1, v2) => v1.id > v2.id ? 1 : -1)
                        that.text_logs = results.map(value => {
                            return `${value.datetime} ${value.id} level:${value.level} : ${value.content}`
                        }).join("\n") + "\n\n\n\n";
                        if (init === true) {
                            const gap = 20;
                            let thisInterval = setInterval(() => {
                                const el = document.getElementById("myLogTextarea")
                                el.scrollTop = el.scrollTop + gap;
                                if (el.scrollHeight - el.clientHeight - el.scrollTop <= gap) {
                                    el.scrollTop = el.scrollHeight;
                                    clearInterval(thisInterval)
                                }
                            }, 50)
                        } else {
                            const el = document.getElementById("myLogTextarea")
                            el.scrollTop = el.scrollHeight;
                        }

                    } else {
                        that.$message.error(response.data.toString());
                    }
                })
                    .catch(function (error) {
                        that.$message.error(error.toString());
                    })
            },
            logClick(row) {
                this.job_detailed = {
                    "name": row.name,
                    "id": row.id,
                    "type": row.type,
                }
                this.text_log_objs = [];
                this.jobLogTitle = `任务日志 ${row.name} 任务id: ${row.id}`
                this.text_logs = row.name + "\n" + row.id + "\n" + row.type;
                //开始Ajax的请求
                var that = this;
                this.updateLog(that, row, true);
                if (this.isRefreshLog === true) {
                    clearInterval(this.logRefresh)
                    this.logRefresh = setInterval(() => this.updateLog(that, row), this.refreshLogGap * 1000);
                }
                this.jobLogDialogVisible = true;
            }
            ,
            updateLogParam(e) {
                console.log("run ", e)
                if (this.isRefreshLog === false) {
                    clearInterval(this.logRefresh)
                } else {
                    var that = this;
                    clearInterval(this.logRefresh)
                    this.logRefresh = setInterval(() => this.updateLog(that, this.job_detailed), this.refreshLogGap * 1000);
                }
            }
            ,
            refreshLog() {
                var that = this;
                this.updateLog(that, this.job_detailed)
            }
            ,
            closeJobLog() {
                clearInterval(this.logRefresh);
                this.jobLogDialogVisible = false;
                this.text_log_objs = [];
            }
            ,
//点击操作按钮完成相应的任务的启动和停止
            handleClick(row) {
                this.job_id = row.id;
                this.type = row.type;
                if (row.enable === '0') {
                    this.option = 'stop';
                } else if (row.enable === '1') {
                    this.option = 'startup';
                } else if (row.enable === '2') {
                    this.option = 'startup';
                }
                //使用Ajax请求-->post-->传递inputstr
                let that = this;
                //开始Ajax的请求
                axios
                    .post(that.baseURL + "jobs/modify", {
                        job_id: that.job_id,
                        option: that.option,
                        type: that.type,
                    })
                    .then(function (response) {
                        console.log(response);
                        if (response.data.code === 1) {
                            //把数据给tableData
                            that.tableData = response.data.data;
                            //获取返回数据的总行数
                            that.total = response.data.data.length;
                            //获取当页的数据
                            that.getPageJobs();
                            //提示
                            that.$message({
                                message: "工单更新成功~！",
                                type: "success",
                            });
                        } else {
                            that.$message.error(response.data.msg);
                        }
                    })
                    .catch(function (error) {
                        console.log(error);
                    });
            }
            ,
//邮件测试按钮功能
            test_email() {
                //使用Axios实现Ajax的请求
                //记录this 属性
                let that = this;
                axios
                    .get(that.baseURL + "email/test")
                    .then(function (response) {
                        if (response.data.code === 1) {
                            that.$message({
                                message: "测试邮件已发送，请确认查收~！",
                                type: "success",
                            });
                        } else {
                            that.$message.error(response.data.msg);
                        }
                    })
                    .catch(function (error) {
                        console.log(error);
                    });
            }
            ,
//导航栏选择事件
            handleSelect(key, row = null) {
                if (key == 2) {
                    window.open(this.baseURL + 'admin/', '_blank')
                } else if (key == 3) {
                    window.open(this.baseURL + 'logout/', '_parent')
                } else if (key == 0) {
                    const models = {
                        "0": "scriptjob",
                        "1": "apijob",
                        "2": "commonjob",
                    }
                    const model = models[row.type]
                    window.open(this.baseURL + 'admin/schedulers/' + model + '/' + row.id + '/change/', '_blank')
                }
            }
            ,
        },
    })
;

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

    //弹出框表单
    dialogVisible: false,

    //启动、停用按钮相关
    job_id: "",
    option: "",
    type: "",

    //任务明细相关
    job_detailed:{
      name:'',
      web_url:'',
      keywords:'',
      trigger:'',
      datetime:'',
      next_time:'',
      enable:'',
      remarks:'',
    },
    trigger:{
      'date': '特定的时间点触发器',
      'interval': '固定时间间隔触发器',
      'cron': '特定时间周期性地触发器'
    },
    status:{
      '0': '已启动',
      '1': '已停止',
      '2': '已失效',
    },
  },
  mounted() {
    //自动加载数据
    this.getAllJobs();
    window.addEventListener('beforeunload', e => this.beforeunloadHandler(e))
  },
  destroyed() {
    window.removeEventListener('beforeunload', e => this.beforeunloadHandler(e))
  },
  methods: {
    beforeunloadHandler(e){
    console.log('刷新或关闭');
      let that = this;
      axios
        .get(that.baseURL + "logout/")
  },
    //获取所有任务信息
    getAllJobs: function () {
      //使用Axios实现Ajax的请求
      //记录this 属性
      let that = this;
      axios
        .get(that.baseURL + "jobs/")
        .then(function (response) {
          if (response.data.code === 1) {
            console.log(response);
            //把数据给tableData
            that.tableData = response.data.data;
            that.name = response.data.username;
            console.log(that.name);
            //获取返回数据的总行数
            that.total = response.data.data.length;
            //获取当前页的数据
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
        if (this.pageJobs.lenth === this.pagesize) break;
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
      if (this.inputstr === ''){
        this.getAllJobs();
      }else {
        let that = this;
      //开始Ajax的请求
      axios
        .post(that.baseURL + "jobs/query", {
          inputstr: that.inputstr
        })
        .then(function (response) {
          console.log(response);
          if(response.data.code === 1){
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
          }else{
            that.$message.error(response.data.msg);
          }
        })
        .catch(function (error) {
          console.log(error);
        });
      }
    },

    //数据刷新功能
    refresh(){
      this.getAllJobs();
    },

    //双击单元格显示任务明细
    cell_dblclick(row){
      this.dialogVisible = true;
      this.job_detailed.name = row.name;
      this.job_detailed.web_url = row.web_url;
      this.job_detailed.keywords = row.keywords;
      this.job_detailed.trigger = this.trigger[row.trigger];
      this.job_detailed.datetime = row.datetime;
      this.job_detailed.next_time = row.next_time;
      this.job_detailed.enable = this.status[row.enable];
      this.job_detailed.remarks = row.remarks
    },

    //点击操作按钮完成相应的任务的启动和停止
    handleClick(row){
      console.log(row);
      this.job_id = row.id;
      this.type = row.type;
      if (row.enable === '0'){
        this.option = 'stop';
      }else if(row.enable === '1'){
        this.option = 'startup';
      }
      console.log(this.job_id);
      console.log(this.option);
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
           if(response.data.code === 1){
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
           }else{
             that.$message.error(response.data.msg);
           }
         })
         .catch(function (error) {
           console.log(error);
         });
    },

    //邮件测试按钮功能
    test_email(){
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
      
    },

    //导航栏选择事件
    handleSelect(key){
      console.log(key);
      // this.activeIndex = key;
      if(key == 2){
        window.open(this.baseURL + 'admin/', '_blank')
      }else if(key ==3){
        window.open(this.baseURL + 'logout/', '_parent')
      }
    },
  },
});

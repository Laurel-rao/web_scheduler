# import json
# import re
# import time
#
# import requests
# import urllib3
# from bs4 import BeautifulSoup
# from django.forms import model_to_dict
# from requests import RequestException
# from selenium import webdriver
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ec
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
#
# from logs.log import logger
# from schedulers.views import scheduler, send_email
#
#
# def get_browser():
#     chrome_options = webdriver.ChromeOptions()
#     # 使用headless无界面浏览器模式
#     chrome_options.add_argument('--headless')  # 增加无界面选项。代码测试无误后可去除注释
#     chrome_options.add_argument('--disable-gpu')  # 如果不加这个选项，有时定位会出现问题
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--ignore-certificate-errors')  # 处理ssl证书错误问题
#     chrome_options.add_argument("--disable-blink-features")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
#     chrome_options.add_argument('--user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
#                                 '(KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.39')
#     # 不加载图片
#     prefs = {
#         'profile.default_content_setting_values': {
#             'images': 2,
#         }
#     }
#     chrome_options.add_experimental_option('prefs', prefs)
#     # driver = webdriver.Chrome(options=chrome_options)
#     driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)
#     return driver
#
# def more_page(web_url, kwargs):
#     pattern = kwargs['pattern']
#     base_url = kwargs['base_url']
#     str_keywords = kwargs['keywords']
#     trigger = kwargs['trigger']
#     job_id = kwargs['id']
#     str_type = kwargs['type']
#     username = kwargs['username']
#     ReceiversEmail = kwargs['ReceiversEmail']
#     oneormore = kwargs['oneormore']
#     nextbutton = kwargs['nextbutton']
#     pagenum = kwargs['pagenum']
#     islogin = kwargs['islogin']
#     username_input = kwargs['username_input']
#     password_input = kwargs['password_input']
#     username_text = kwargs['username_text']
#     password_text = kwargs['password_text']
#     login_button = kwargs['login_button']
#     login_url = kwargs['login_url']
#     browser = get_browser()
#     if islogin:
#         browser.get(login_url)
#         WebDriverWait(browser, 10).until(ec.visibility_of_element_located((By.XPATH, username_input)))
#         browser.find_element_by_xpath(username_input).send_keys(username_text)
#         browser.find_element_by_xpath(password_input).send_keys(password_text)
#         browser.find_element_by_xpath(login_button).click()
#         time.sleep(3)
#
#     try:
#         web_url_list = []
#         logger.info('进入多页面模块：' + web_url)
#         browser.get(web_url)
#         time.sleep(3)
#         # 获取访问cookie
#         c = browser.get_cookies()
#         cookies = {}
#         # 获取cookie中的name和value,转化成requests可以使用的形式
#         for cookie in c:
#             cookies[cookie['name']] = cookie['value']
#
#         # 判断是否需要读取多页
#         islazyload = False
#         mask_keys = ''
#         url_key = ''
#         if oneormore == '1':
#             # 获取当前页面的源码并断言
#             pageSource = browser.page_source
#             matchObj = re.findall(pattern, pageSource)
#             for i in matchObj:
#                 web_url_list.append(base_url + i)
#             monitor_one_page(web_url_list, str_keywords, trigger, job_id, str_type, username, ReceiversEmail, cookies,
#                              islazyload, mask_keys, url_key)
#         elif oneormore == '2':
#             if nextbutton == '' or nextbutton is None:
#                 WebDriverWait(browser, 20).until(ec.visibility_of_element_located((By.PARTIAL_LINK_TEXT, '下一页')))
#             else:
#                 WebDriverWait(browser, 20).until(ec.visibility_of_element_located((By.PARTIAL_LINK_TEXT, nextbutton)))
#             p = pagenum
#             while p > 0:
#                 try:
#                     pageSource = browser.page_source
#                     matchObj = re.findall(pattern, pageSource)
#                     for i in matchObj:
#                         web_url_list.append(base_url + i)
#                     # print(nextbutton)
#                     if nextbutton == '' or nextbutton is None:
#                         browser.find_element_by_partial_link_text("下一页").click()
#                         WebDriverWait(browser, 20).until(
#                             ec.visibility_of_element_located((By.PARTIAL_LINK_TEXT, '下一页')))
#                     else:
#                         browser.find_element_by_partial_link_text(nextbutton).click()
#                         WebDriverWait(browser, 20).until(
#                             ec.visibility_of_element_located((By.PARTIAL_LINK_TEXT, nextbutton)))
#                     p = p - 1
#                 except NoSuchElementException:
#                     break
#             monitor_one_page(web_url_list, str_keywords, trigger, job_id, str_type, username, ReceiversEmail, cookies,
#                              islazyload, mask_keys, url_key)
#         browser.quit()
#     except Exception as e:
#         logger.warning("页面监控测序异常~！异常代码为：" + str(e))
#
#
# def get_cookie(login_url, username_input, username_text, password_input, password_text, login_button):
#     browser = get_browser()
#     browser.get(login_url)
#     WebDriverWait(browser, 10).until(ec.visibility_of_element_located((By.XPATH, username_input)))
#     browser.find_element_by_xpath(username_input).send_keys(username_text)
#     browser.find_element_by_xpath(password_input).send_keys(password_text)
#     browser.find_element_by_xpath(login_button).click()
#     time.sleep(3)
#     c = browser.get_cookies()
#     cookies = {}
#     # 获取cookie中的name和value,转化成requests可以使用的形式
#     for cookie in c:
#         cookies[cookie['name']] = cookie['value']
#     browser.quit()
#     return cookies
#
#
# # 监控单个页面
# def monitor_one_page(web_url_list, str_keywords, trigger, job_id, str_type, username, ReceiversEmail, cookies,
#                      islazyload, mask_keys, url_key):
#     cookies = cookies
#     job_dict = {}
#     job_dict = model_to_dict(SchedulersJob2.objects.get(id=job_id))
#     if str_type == 'one':
#         job_dict = model_to_dict(SchedulersJob.objects.get(id=job_id))
#         if job_dict['islogin']:
#             username_input = job_dict['username_input']
#             password_input = job_dict['password_input']
#             username_text = job_dict['username_text']
#             password_text = job_dict['password_text']
#             login_button = job_dict['login_button']
#             login_url = job_dict['login_url']
#             cookies = get_cookie(login_url, username_input, username_text, password_input, password_text, login_button)
#     try:
#         # 添加头部信息
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
#         }
#         requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
#         s = requests.session()
#         s.keep_alive = False  # 关闭多余连接
#         urllib3.disable_warnings()
#         keywords = []
#         error_list = []
#         str_content = ''
#
#         logger.info('进入单页面模块：')
#         # 判断是否为单页面任务且是懒加载网站
#         if str_type == 'one' and islazyload:
#             response = requests.get(web_url_list[0], headers=headers, verify=False, cookies=cookies)
#             if response.status_code == 200:
#                 response_list = json.loads(response.content)
#                 mask_keys_list = mask_keys.split('|')
#                 keywords_list = str_keywords.split('|')
#                 for i in response_list:
#                     for keyword in keywords_list:
#                         texts_list = []
#                         for mask_key in mask_keys_list:
#                             if keyword in i[mask_key]:
#                                 texts_list.append(i[mask_key])
#                         if texts_list:
#                             match_dict = {
#                                 'web_url': i[url_key],
#                                 'keyword': keyword,
#                                 'texts': texts_list
#                             }
#                             keywords.append(match_dict)
#             else:
#                 error_list.append(web_url_list[0])
#         else:  # 非懒加载网站
#             for web_url in web_url_list:
#                 print(web_url)
#                 response = requests.get(web_url, headers=headers, verify=False, cookies=cookies)
#
#                 # 进行状态码判断，是否正确读取到网页
#                 logger.info("Start monitor………………………………………………\\n监控网址为：" + str(web_url) + '\\n关键字为：' + str_keywords)
#                 if response.status_code == 200:
#                     web_content = ""
#                     response.encoding = response.apparent_encoding
#                     # 因为网站使用的不是通用的utf-8格式，而是gzip或gb2312等，所以要让它判断解码格式
#
#                     if job_dict['selector']:
#                         html = BeautifulSoup(response.text, 'lxml')
#                         # 获取到的网页信息需要进行解析，使用lxml解析器，其实默认的解析器就是lxml，但是这里会出现警告提示，方便你对其他平台移植
#                         content = html.select(job_dict['selector'])
#                         # 将复制好的选择器信息放进select方法中，将获取到的内容作为tag形式放入一个列表中
#                         # print(content[0].get_text())
#                         if len(content) == 0:
#                             web_content = response.text
#                         else:
#                             web_content = str(content[0])
#                         # 输出这个列表中第一个内容，就是我们要获得的信息
#                     else:
#                         web_content = response.text
#
#                     keywords_list = str_keywords.split('|')
#                     for i in keywords_list:
#                         match_dict = dict()
#                         if i in web_content:
#                             pattern = '>([^<]*' + i + '[^<]+)'
#                             # keywords.append(i)
#                             matchObj = re.findall(pattern, web_content)
#                             texts_list = []
#                             for text in matchObj:
#                                 texts_list.append(text)
#                             if texts_list:
#                                 match_dict = {
#                                     'web_url': web_url,
#                                     'keyword': i,
#                                     'texts': texts_list
#                                 }
#                                 keywords.append(match_dict)
#                 else:
#                     error_list.append(web_url)
#         if keywords:
#             for i in keywords:
#                 str_content = str_content + '网页：' + i['web_url'] + '  \n' + '检测到关键内容：\n' + \
#                               '>>> 关键字：' + i['keyword'] + '    匹配到内容如下：\n' + '\n'.join(i['texts']) + '\n\n'
#         for e in error_list:
#             str_content = str_content + '网页：' + e['web_url'] + '  \n' + '无法访问，请确认~!!：\n\n'
#         # logger.info(keywords)
#         if str_content == '':
#             str_content = '网页：' + job_dict['web_url'] + '  当前查询时间点：' + time.strftime("%m/%d/%Y %H:%M") + '，暂无无匹配项~！'
#         send_email(str_content, username, ReceiversEmail)
#         if trigger != 'cron':
#             if str_type == 'one':
#                 SchedulersJob.objects.filter(id=job_id).update(enable='2', next_time=None)
#             else:
#                 SchedulersJob2.objects.filter(id=job_id).update(enable='2', next_time=None)
#         else:
#             if str_type == 'one':
#                 job = scheduler.get_job('job_id_' + str(job_id) + '_' + str_type)
#                 next_time = job.next_run_time
#                 SchedulersJob.objects.filter(id=job_id).update(next_time=next_time)
#             else:
#                 job = scheduler.get_job('job_id_' + str(job_id) + '_' + str_type)
#                 next_time = job.next_run_time
#                 SchedulersJob2.objects.filter(id=job_id).update(next_time=next_time)
#         logger.info("monitor Finish~!")
#     except RequestException as e:
#         logger.warning("页面监控测序异常~！异常代码为：" + str(e))
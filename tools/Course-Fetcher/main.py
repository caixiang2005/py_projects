from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from collections import defaultdict
import time
import json
import os

# 1. 配置选项
options = Options()

# 2. 打开浏览器
driver = webdriver.Chrome(options=options)

driver.get('https://cas.ncjti.edu.cn/cas/login?service=https%3A%2F%2Fmy.ncjti.edu.cn%2F')

# 读取项目配置文件
cur_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(cur_dir,"config.json")
with open(config_path,'r',encoding='utf-8') as f:
    config = json.load(f)

wait = WebDriverWait(driver, 10)


username = wait.until(
    ec.visibility_of_element_located((By.ID,'username'))
)
username.send_keys(config["USERNAME"])


password = wait.until(
    ec.visibility_of_element_located((By.ID,'ppassword'))
)
password.send_keys(config["PASSWORD"])

# 点击登录
login_button = wait.until(
    ec.visibility_of_element_located((By.ID,'dl'))
)
login_button.click()

# 等待课表里面的所有 p 标签加载完毕
wait.until(
    ec.visibility_of_all_elements_located(
        (By.XPATH, ".//dl[@class='week']//p")
    )
)

# 等待课表加载
schedule_table = wait.until(
    ec.visibility_of_element_located((By.XPATH,"//div[@class = 'schedule-table']"))
)
# time.sleep(3)
# 等待表格信息加载出来



# 每一周内的信息
all_dls = schedule_table.find_elements(By.XPATH,'.//dl')
# dl
    # dt -> 星期几
    # dd -> 当天的课程
        # p -> 课程名以及上课地点

d = defaultdict(list)
for i in range(1,len(all_dls)):
    dl = all_dls[i]
    week = dl.find_element(By.TAG_NAME, 'dt').text.strip()
    # print(week,end='')
    all_dds = dl.find_elements(By.XPATH,'./dd')
    for v in all_dds:

        # 这里处理上第几节课
        inf = v.get_attribute("class").split(' ')
        start_time = int(inf[0][-1])
        continue_time = int(inf[-1][-1])
        
        d[week].append(start_time)
        d[week].append(continue_time)
        inf = v.text.split("\n")
        course_name = inf[0]
        location = inf[-1]
        d[week].append(course_name)
        d[week].append(location)

print(d['星期一'])
# [开始的节数，上几节，上什么课，上课地点]


# 关闭浏览器
driver.quit()
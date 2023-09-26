# -*- coding: utf-8 -*-
# @Time    : 2023/6/16 17:10
# @Author  : SZPU Qxz
# @File    : main.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import pymongo
import time
browser=webdriver.Chrome()
wait=WebDriverWait(browser,10)#初始化WebDriverWait对象
client=pymongo.MongoClient('localhost',27017)
mongo=client.cnki
collection=mongo.papers
def searcher(keyword):
    browser.get('https://www.cnki.net/')#知网
    browser.maximize_window()
    time.sleep(2)
    #定位id属性"搜索"
    input=wait.until(
        EC.presence_of_element_located((By.ID,'txt_SearchText'))
    )
    input.send_keys(keyword)#输入需要的文本
    wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME,'search-btn'))).click()
    time.sleep(3)
    #定位每页文章的篇数列表并且点击
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR,'[class="icon icon-sort"]'))).click()
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR,'#id_grid_display_num ul li'))
    )[2].click()
    time.sleep(3)
    parse_page()
def parse_page():
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, '.result-table-list tbody tr')
        )
    )
    html=browser.page_source
    soup=BeautifulSoup(html,'lxml')
    items=soup.select('.result-table-list tbody tr')
    for i in range(0,len(items)):
        item=items[i]
        detail=item.select('td')
        paper={
            'index':detail[0].text.strip(),
            'title': detail[1].text.strip(),
            'author': detail[2].text.strip(),
            'resource': detail[3].text.strip(),
            'time': detail[4].text.strip(),
            'database': detail[5].text.strip(),
        }
        print(paper)
        data_storage(paper)
def data_storage(paper):
    try:
        collection.insert_one(paper)
    except:
        print('错误Error',paper)
def next_page():
    try:
        page_next=wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR,'#Page_next_top')
            )
        )
    except TimeoutException:#超时异常
        return False
    else:
        page_next.click()
        return True
if __name__=='__main__':
    keyword='Python'
    searcher(keyword)
    while True:
        flag=next_page()
        time.sleep(5)
        if flag:
            parse_page()
            continue
        else:
            break
    browser.close()






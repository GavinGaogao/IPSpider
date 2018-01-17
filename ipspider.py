import os
from pprint import pprint
import csv
from collections import Counter
import json
import time
from bs4 import BeautifulSoup
import requests
from pyquery import PyQuery as pq
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


def csv_save(data, path, header=None):
    """
    将数据data，保存为.csv文件，注意在写入的时候，
    open函数中newline=''，才能保证隔行没有空行
    header:当写入的数据不想保留第一行header的时候，
    可以不传人header
    """

    with open(path, "w", encoding="utf-8", newline='') as f:
        f_csv = csv.writer(f)
        if header:
            f_csv.writerow(header)
        f_csv.writerows(data)


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class IPSpider(Model):
    """
    ip地址网站爬虫类
    """

    def __init__(self):
        self.iplist = []
        self.ip_file_path = "data/ip_locate.csv"
        self.file_header = ['ip', 'city', 'carrier']
        self.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                          '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }

    def ip_from_urls(self, url, ip):
        r = requests.get(url, headers=self.headers)
        page = r.content
        e = pq(page)
        data = e(".ul1").find("li").text()
        ipdata = data.split(" ")[0]
        ip_locate = ipdata[5:]
        ip_company = data.split(" ")[2]
        ip_info = [ip, ip_locate, ip_company]
        self.iplist.append(ip_info)

    def save_ipinfo(self):
        csv_save(self.iplist, self.ip_file_path, header=self.file_header)


def analyze_salary(filepath):
    data = pd.read_csv(filepath)
    chengshi = []
    city_salary = []
    salary = []
    citys = data['city']
    pro_counter_list = []
    provinces = []
    for location in citys:
        c = location[0:2]
        provinces.append(c)
    # 将列表中重复出现的身份都去掉，利用set可以做到，然后再转换为list
    provinces_uniq = list(set(provinces))
    pro_num = len(provinces_uniq)
    num = len(citys)
    for j in range(0, pro_num):
        pro = provinces_uniq[j]
        pro_counter = 0
        for i in range(0, num - 1):
            a = citys.ix[i]
            if a.find(pro) != -1:
                pro_counter = pro_counter + 1
        pro_counter_list.append(pro_counter)

    fig, ax = plt.subplots()
    # 设置柱状宽度
    bar_width = 0.25
    # 下面两句配置，为了防止中文出现乱码
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # 设置透明度
    opacity = 1
    rects1 = plt.bar(provinces_uniq, pro_counter_list, bar_width, alpha=opacity, color='green')
    plt.xlabel('Province')
    plt.ylabel('Count')
    plt.title('The number of times each identity IP appears')
    # 设置X坐标标签旋转90度，更加美观
    plt.xticks(rotation=90)
    # plt.ylim(0, 5)
    # plt.legend()
    plt.tight_layout()
    plt.show()


def main():

    iplist = pd.read_csv("ip.csv")
    ips = iplist["ip"]

    url = "http://www.ip138.com/ips138.asp?ip={}&action=2"
    # ips = ['61.186.251.202', '61.186.251.212']
    num = len(ips)
    urls = [url.format(ip) for ip in ips]
    ipspider = IPSpider()
    for i in range(0, num):
        ipspider.ip_from_urls(urls[i], ips[i])
    ipspider.save_ipinfo()
    analyze_salary("data/ip_locate.csv")


if __name__ == "__main__":
    main()

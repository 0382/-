#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#---------------------------------------
# author     : 0.382
# data       : 2018-04-05
# description: 使用 selenium 来抓取中国作物种质量资源信息网上的数据的程序
# environment: Windows 10, python3.5
#---------------------------------------

from selenium import webdriver
from urllib import request, parse
import re
import time
import codecs
import os
import json

URL = "http://www.cgris.net/query/do.php#油料作物,大豆"  #你可以通过更换网址来替换抓取的页面

#在当前目录下新建一个这个作物类型的文件夹
url_title = re.search(r'#([\s\S]+)?,([\s\S]+)', URL)
url_title1 = url_title.group(1)
url_title2 = url_title.group(2)
crop_type = url_title1 + url_title2
os.system('md {0}'.format(crop_type))

#打开Edge()，这个傻逼网站似乎通过Chrome和Firefox都会使一个javascript出错而不能识别网址
driver = webdriver.Edge()
driver.get(URL)
driver.implicitly_wait(20)

#点击学名，嗯，这是我自己的需求
xueming = driver.find_element_by_id("items_学名")
xueming.click()

#点击选择所有的选项
checks = driver.find_elements_by_name("学名")
for check in checks:
	check.click()

#确认并关闭
#由于试了很多方法都找不到这个元素，只好暴力搜索了，由于单次操作，不费时间
guanbi = driver.find_elements_by_tag_name('div')
for ele in guanbi:
	if ele.text == '确认并关闭':
		ele.click()
		break

#点击查询，实际上一般查找到有三个按钮，我们需要最后一个
chaxun = driver.find_elements_by_class_name('divbutton')
for ele in chaxun:
	if ele.text == '查询':
		ele.click()
		break

#开始抓数据
index_number = int(input('现在你看到有多少条目，请输入小于等于这个条目数的数值，将会抓取从头开始到你输入的条目数：'))

def get_one_crop(unify_id, crop_type_list):
	#只好用post来了
	post_url="http://www.cgris.net/query/o.php"
	headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
	data={
		"p": unify_id,
		"croptype": crop_type_list,
		"action": "item",
		"_": None
	}
	data = parse.urlencode(data).encode('utf-8')
	req = request.Request(post_url, headers=headers, data=data)
	html = request.urlopen(req).read().decode('unicode_escape')

	#json文件保存数据，其实本来得到的就是json文件
	filename = crop_type + '\\{0}.json'.format(unify_id)
	fp = codecs.open(filename,'w','utf-8')
	fp.write(html)

page_number = 0
flag = 'flag'
while page_number <= index_number:
	#页面信息
	page = driver.page_source
	page_number = int(re.search(r'<span id="hehecurrent">([0-9]+)</span>', page).group(1))
	print(page_number)

	#统一编号，作物的统一编号是完全不同的，以此可以作为数据不重复的保证
	unify_id = ''
	unify_ids = re.findall(r'<td class="cap">统一编号</td><td>([\s\S]+?)</td>', page)
	if unify_ids == None:
		pass
	else:
		for uni_id in unify_ids:
			if '<' not in uni_id:
				unify_id = uni_id
				break

	#下一页操作，如果新的统一编号还没有刷新出来，就不翻页
	#由于文件会覆盖，重复写入也没关系
	if flag != unify_id:
		flag = unify_id
		next_page = driver.find_element_by_id('nexthehe')
		next_page.click()
	elif page_number == index_number:
		page_number += 1
	else:
		pass

	#抓数据
	crop_type_list = '["{0}","{1}"]'.format(url_title1, url_title2)
	get_one_crop(unify_id, crop_type_list)

#关闭浏览器
driver.close()
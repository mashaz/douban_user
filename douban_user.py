# -*- coding:utf-8 -*-
#!/usr/bin/env python

__auther__ = 'xiaohuahu94@gmail.com'
'''
爬某小组用户信息  todo:断点续爬
'''
import requests
from bs4 import BeautifulSoup
import urllib,urllib2
import re
import os
import sys,time
import csv
reload(sys)
sys.setdefaultencoding('utf-8')   # note
requests.adapters.DEFAULT_RETRIES = 5 
def Login():  
	'''
	他娘的 搞死我了
	'''
	f = open('cookies.txt','r')
	cookies = {}
	for line in f.read().split(','):
		name,value = line.strip().split('=',1)
		cookies[name] = value
	return cookies
def GetUserNumber():

	group_url = 'https://www.douban.com/group/blabla/members'
	response = requests.get(group_url)
	soup = BeautifulSoup(response.content)
	s = soup.findAll('span',attrs={'class','count'}) # notes:bs4查找指定属性标签
	re_mumber = re.compile(r'[0-9]{1,9}')
	mumber_sum = re.findall(re_mumber,str(s)).pop()
	print '本小组共有用户%s人'%(mumber_sum)
	return mumber_sum

def GetAllList():
	group_url = 'https://www.douban.com/group/blabla/members?start='
	start_item = 10000
	people_list = []
	while(1):
		print 'GetList : get the %d one'%(start_item)
		url = group_url + str(start_item)
		response = requests.get(url)
		re_people  = re.compile(r'https://www\.douban\.com/people/[a-zA-Z0-9]{1,20}/')
		some_people_list = re.findall(re_people,response.content)
		people_list.extend(some_people_list)
		#print people_list
		start_item += 35
		if start_item > 20000: 
			# start_item == GetUserNumber()  had:100=info100.txt
			people_list = list(set(people_list))
			return people_list
			break
def SaveInfo():
	cookies = Login()
	count = 0
	people_list = GetAllList()
	cfile = file('info1.csv','ab+')
	w = csv.writer(cfile)
	w.writerow(['NAME','ID','ADDR','DATE','FOLLOWER'])
	cfile.close()
	while(people_list != []):
		address_flag = 1
		time.sleep(1)
		people_url = people_list.pop()
		headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36' }
		try:
			response = requests.get(people_url,headers=headers,cookies=cookies)
			soup = BeautifulSoup(response.content)
			
			follower = soup.findAll('p',attrs={'class','rev-link'})[0].contents[0].contents[0]
			follower = str(follower)
			
			re_flwer = re.compile(r'[0-9]{1,9}')
			fl_list = re_flwer.findall(follower)
			follower = str(fl_list.pop())
     
			#follower = follower[len(follower)-13:len(follower)]
	        #加上这句便乱码
	
			user_info = soup.findAll('div',attrs={'class','user-info'}) 
			user_info =  str(user_info)[1:len(str(user_info))-1]
			user_info_soup = BeautifulSoup(str(user_info))
			try:
				user_address = user_info_soup.select('a')[0].contents[0]   # note:
				user_address = str(user_address)
			except Exception,ee:
				address_flag = 0
			user_id = user_info_soup.findAll('div',attrs={'class','pl'})[0].contents[0]
			user_id = str(user_id)
			user_date = user_info_soup.findAll('div',attrs={'class','pl'})[0].contents[2]
			user_date = str(user_date)
	
			user_name = soup.select('h1')[0].contents[0]
			user_name = str(user_name).rstrip().strip().replace(' ','') 
			'''
			上句是删除空格 但最前面仍有空行存在
			'''
			info = []
			if address_flag == 1:
				info = [user_name,user_id,user_address,user_date,follower]
			else:
				info = [user_name,user_id,'Unknown',user_date,follower]
			
			cfile = file('info1.csv','ab+')
			writer = csv.writer(cfile)
			writer.writerow(info)
			cfile.close()
			count += 1
			print count
		except Exception,e:
			count += 1
			print 'failed'+str(e)
			print people_url
			print count

if __name__ =='__main__':
	Login()
	SaveInfo()



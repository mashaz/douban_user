# -*- coding:utf-8 -*-
#!/usr/bin/env python

__auther__ = 'xiaohuahu94@gmail.com'

import requests
from bs4 import BeautifulSoup
import urllib,urllib2
import re
import os
import sys,time
import csv
from pymongo import MongoClient

reload(sys)

sys.setdefaultencoding('utf-8')  
requests.adapters.DEFAULT_RETRIES = 5 

def connect_to_mongo():
	"""
	return collections
	"""
	client = MongoClient('127.0.0.1',27017)
	db = client['douban']
	coll_user = db['user']
	coll_url = db['profile_url']
	return coll_user, coll_url  # collection equals table in sqlite

def login():  

	f = open('cookies.txt','r')
	cookies = {}
	for line in f.read().split(','):
		name,value = line.strip().split('=',1)
		cookies[name] = value
	return cookies

def get_user_number():

	group_url = 'https://www.douban.com/group/blabla/members'
	response = requests.get(group_url)
	soup = BeautifulSoup(response.content,'html5lib')
	s = soup.findAll('span',attrs={'class','count'}) # notes:bs4查找指定属性标签
	re_mumber = re.compile(r'[0-9]{1,9}')
	mumber_sum = re.findall(re_mumber,str(s)).pop()
	print '本小组共有用户%s人'%(mumber_sum)
	return mumber_sum

def get_all_list():

	group_url = 'https://www.douban.com/group/blabla/members?start='
	start_item = 0
	people_list = []
	while(1):
		time.sleep(2)
		print '获取成员profile : 第 %d 个'%(start_item)
		url = group_url + str(start_item)
		try:
			response = requests.get(url, timeout=60)
			re_people  = re.compile(r'https://www\.douban\.com/people/[a-zA-Z0-9]{1,20}/')
			some_people_list = re.findall(re_people,response.content)
		except:
			continue
		people_list.extend(some_people_list)
		#print people_list
		start_item += 35
		if start_item > 50000: 
			people_list = list(set(people_list))
			return people_list
			break

def save_profile_url(people_list):

	conn = sqlite3.connect('user.db')
	conn.text_factory = str
	lid = 1
	for link in people_list:
			sqlite_insert(conn, 'url', {
					'lid': lid,
					'link': link,
					'status': 0
					})
			lid += 1
	conn.commit()
	conn.close()

def save_info():

	cookies = login()
	count = 0
	# people_list = get_all_list()
	# save_profile_url(people_list)

	coll_user, coll_url = connect_to_mongo()
	cursor = coll_url.find({"status" : 0 })
	people_list = []
	for document in cursor:
		people_list.append(document['url']) 

	# return 0 # del

	while(people_list != []):
		address_flag = 1
		time.sleep(2)
		people_url = people_list.pop()
		headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36' }
		try:
			response = requests.get(people_url,headers=headers,cookies=cookies)
			soup = BeautifulSoup(response.content,'html5lib')
			# print soup
			follower = soup.findAll('p',attrs={'class','rev-link'})[0].contents[0].contents[0]
			follower = str(follower)
			
			re_flwer = re.compile(r'[0-9]{1,9}')
			fl_list = re_flwer.findall(follower)
			follower = str(fl_list.pop())
     
			#follower = follower[len(follower)-13:len(follower)]
	        #加上这句便乱码
	
			user_info = soup.findAll('div',attrs={'class','user-info'})
			user_info_soup = user_info[0]
			# user_info =  str(user_info)[1:len(str(user_info))-1]
			#user_info_soup = BeautifulSoup(str(user_info[0]),'html5lib')
			#print user_info_soup
			try:
				user_address = user_info_soup.select('a')[0].contents[0] # note:
				
				user_address = unicode(user_address).strip().replace(' ','') 
				
			
			except Exception,ee:
				address_flag = 0
			user_id = user_info_soup.findAll('div',attrs={'class','pl'})[0].contents[0]
			user_id = str(user_id)
			user_date = user_info_soup.findAll('div',attrs={'class','pl'})[0].contents[2].lstrip().rstrip('')
			user_date = str(user_date).strip().replace(' ','').rstrip(u'加入')
			
			user_name = soup.select('h1')[0].contents[0]
			user_name = str(user_name).rstrip().strip().replace(' ','') 
			
			info = []
			if address_flag == 1:
				info = [user_name,user_id,user_address,user_date,follower]
			else:
				info = [user_name,user_id,'Unknown',user_date,follower]
			
			result = coll_user.insert_one(
				{
					'username': info[0],
					'uid': info[1],
					'location': info[2],
					'joined_date': info[3],
					'follower_sum': info[4],
				})
			
			print info[0],' is saved.'

			"""fix status"""
			coll_url.update({'url':people_url} , {"$set":{"status":1}})

			print coll_url.find({"url":people_url}).next()
			
			count += 1
			print count
			print '-------------------------------------------------'
		except Exception,e:
			count += 1
			print 'failed '+str(e)
			coll_url.update({'url':people_url} , {"$set":{"status":1}})
			print coll_url.find({"url":people_url}).next()
			print count
			print '-------------------------------------------------'
if __name__ =='__main__':
	f = login()
	save_info()



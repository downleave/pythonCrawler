import requests
from lxml import etree
from PIL import Image
from selenium import webdriver
import os
import time
import json

def login(browser):
	loginPage = 'http://wiki.klub11.com/index.php?s=/home/item/pwd/item_id/2'
	browser.get(loginPage)
	v_code = input('请输入验证码:')
	return submitLoginForm(v_code,browser)

def submitLoginForm(v_code, browser):
	browser.find_element_by_xpath('//input[@name="password"]').send_keys("pf1q78rc")
	browser.find_element_by_xpath('//input[@name="v_code"]').send_keys(v_code)
	browser.find_element_by_xpath('//button[@class="golddot_btn"]').click()
	return browser

def getUrls(browser):
	#获取多个接口url
	urls = browser.find_elements_by_xpath("//p/strong[text()='请求URL：']/../following-sibling::ul[1]/li/code")
	if len(urls) == 0:
		urls = browser.find_elements_by_xpath("//strong[text()='请求URL：']/following-sibling::ul[1]/li/code")
	return urls

def  getTypes(browser):
	apitypes = browser.find_elements_by_xpath("//p/strong[text()='请求方式：']/../following-sibling::ul[1]/li")
	return apitypes

def getParams(browser,num):
	params = {}
	params['name'] = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[1]"%(num))
	params['require'] = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[2]"%(num))
	params['type'] = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[3]"%(num))
	params['description'] = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[4]"%(num))
	return params

def getJsonParams(browser,fldname,num):
	jsonParams = {}
	jsonParams['name'] = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[1]"%(fldname,num))
	jsonParams['require'] = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[2]"%(fldname,num))
	jsonParams['type'] = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[3]"%(fldname,num))
	jsonParams['description'] = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[4]"%(fldname,num))
	return 	jsonParams

def getList(browser, urls, apitypes):
	apiList = []
	for index,url in enumerate(urls):
		tmp = {}
		tmp['url'] = url.text
		tmp['type'] = apitypes[index].text
		tmp['params'] = []

		num = index + 1
		
		params = getParams(browser,num)

		i = 1;
		for key,param_name in enumerate(params['name']):
			#遍历父级
			tmp_param = {}
			tmp_param['id'] = i
			tmp_param['pid'] = 0
			tmp_param['fieldname'] = params['name'][key].text
			tmp_param['require'] = params['require'][key].text
			tmp_param['type'] = params['type'][key].text		
			tmp_param['description'] = params['description'][key].text
			tmp['params'].append(tmp_param)
			
			#如果有json，则遍历json相关参数
			if(tmp_param['type'] == 'json'):
				pid = i
				i = i + 1
				jsonParams = getJsonParams(browser,params['name'][key].text,num)
				for key2,content_param_name in enumerate(jsonParams['name']):
					tmp_param = {}
					tmp_param['id'] = i
					tmp_param['pid'] = pid
					tmp_param['fieldname'] = jsonParams['name'][key2].text
					tmp_param['require'] = jsonParams['require'][key2].text
					tmp_param['type'] = jsonParams['type'][key2].text		
					tmp_param['description'] = jsonParams['description'][key2].text
					tmp['params'].append(tmp_param)
					i = i + 1
			else:
				i = i + 1
		apiList.append(tmp)
	return apiList

def writeJson(apiList,nextpage):
	if len(apiList):
		apiList = json.dumps(apiList)
		path = '%s.json'%(nextpage)
		fo = open(path, "w")
		fo.write(apiList)
		fo.close()

def crawlWiki(browser, nextpage='2'):
	browser.get('http://wiki.klub11.com/index.php?s=/2&page_id=' + nextpage)

	#切换iframe
	browser.switch_to.frame("page-content")

	#获取页面所有请求url
	urls = getUrls(browser)

	#获取页面所有请求方式
	apitypes = getTypes(browser)
		
	#根据url和apitypes来再去爬出对应的参数，并重组成dict
	apiList = getList(browser, urls, apitypes)
	
	#将apiList转成json并写入文件
	writeJson(apiList,nextpage)

def browserInit():
	chromedriver = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe"
	os.environ["webdriver.chrome.driver"] = chromedriver
	return webdriver.Chrome(chromedriver)

def writeCookie(browser):
	cookie = browser.get_cookies()
	cookie = json.dumps(cookie)
	path = 'cookie.json'
	fo = open(path, "w")
	fo.write(cookie)
	fo.close()

def readCookie(browser):
	#要先访问一下才能add_cookie
	loginPage = 'http://wiki.klub11.com/index.php?s=/home/item/pwd/item_id/2'
	browser.get(loginPage)
	fo = open('cookie.json', 'r')
	cookie = fo.read()
	cookie = json.loads(cookie)
	browser.add_cookie(cookie[0])
	# 尝试是否登录成功
	browser.get('http://wiki.klub11.com/index.php?s=/2&page_id=2')
	browser.switch_to.frame("page-content")
	check_is_login = browser.find_elements_by_xpath("//h3[text()='会员资料创建和变动']")
	if len(check_is_login):
		return True
	return False

browser = browserInit()
if readCookie(browser) == False:
	browser = login(browser)
	writeCookie(browser)
# for i in range(2,20):
# 	crawlWiki(browser,str(i))
# 	time.sleep(2)
crawlWiki(browser,'2')
browser.quit()
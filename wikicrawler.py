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

def writeJson(browser, nextpage='2'):
	browser.get('http://wiki.klub11.com/index.php?s=/2&page_id=' + nextpage)
	# time.sleep(2)

	#切换iframe
	browser.switch_to.frame("page-content")

	#获取多个接口url
	urls = browser.find_elements_by_xpath("//p/strong[text()='请求URL：']/../following-sibling::ul[1]/li/code")
	apitypes = browser.find_elements_by_xpath("//p/strong[text()='请求方式：']/../following-sibling::ul[1]/li")
		
	apiList = []
	for index,url in enumerate(urls):
		tmp = {}
		tmp['url'] = url.text
		tmp['type'] = apitypes[index].text
		tmp['params'] = []

		num = index + 1

		params_name = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[1]"%(num))
		params_require = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[2]"%(num))
		params_type = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[3]"%(num))
		params_description = browser.find_elements_by_xpath("(//p/strong[text()='请求方式：'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[4]"%(num))

		i = 1;
		for key,param_name in enumerate(params_name):
			#遍历父级
			tmp_param = {}
			tmp_param['id'] = i
			tmp_param['pid'] = 0
			tmp_param['fieldname'] = params_name[key].text
			tmp_param['require'] = params_require[key].text
			tmp_param['type'] = params_type[key].text		
			tmp_param['description'] = params_description[key].text
			tmp['params'].append(tmp_param)
			
			#如果有json，则遍历json相关参数
			if(tmp_param['type'] == 'json'):
				pid = i
				i = i + 1
				content_params_name = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[1]"%(params_name[key].text,num))
				content_params_require = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[2]"%(params_name[key].text,num))
				content_params_type = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[3]"%(params_name[key].text,num))
				content_params_description = browser.find_elements_by_xpath("(//ul/li[text()='%s参数说明'])[%s]/../following-sibling::div[1]/table/tbody/tr/td[4]"%(params_name[key].text,num))
				for key2,content_param_name in enumerate(content_params_name):
					tmp_param = {}
					tmp_param['id'] = i
					tmp_param['pid'] = pid
					tmp_param['fieldname'] = content_params_name[key2].text
					tmp_param['require'] = content_params_require[key2].text
					tmp_param['type'] = content_params_type[key2].text		
					tmp_param['description'] = content_params_description[key2].text
					tmp['params'].append(tmp_param)
					i = i + 1
			else:
				i = i + 1
		apiList.append(tmp)
	if len(apiList):
		apiList = json.dumps(apiList)
		path = '%s.json'%(nextpage)
		fo = open(path, "w")
		fo.write(apiList)
		fo.close()

	# browser.quit()

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
	return True;

browser = browserInit()
if readCookie(browser) == False:
	browser = login(browser)
	writeCookie(browser)
# for i in range(2,20):
# 	writeJson(browser,str(i))
# 	time.sleep(2)
writeJson(browser,'96')
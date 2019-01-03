import requests
from lxml import etree
from PIL import Image
from selenium import webdriver
import os
import time
import json

def login(browser):
	loginPage = 'http://wiki.klub11.com/index.php?s=/home/item/pwd/item_id/%s'%(crawltarget)
	browser.get(loginPage)
	v_code = input('请输入验证码:')
	return submitLoginForm(v_code,browser)

def submitLoginForm(v_code, browser):
	fo = open('password.json', 'r')
	password = fo.read()
	browser.find_element_by_xpath('//input[@name="password"]').send_keys(password)
	browser.find_element_by_xpath('//input[@name="v_code"]').send_keys(v_code)
	browser.find_element_by_xpath('//button[@class="golddot_btn"]').click()
	return browser

def getUrls(browser):
	#获取多个接口url
	urls = browser.find_elements_by_xpath("//p/strong[text()='请求URL：']/../following-sibling::ul[1]/li[1]/code")
	if len(urls) == 0:
		urls = browser.find_elements_by_xpath("//strong[text()='请求URL：']/following-sibling::ul[1]/li[1]/code")
	return urls

def getTypes(browser):
	apitypes = browser.find_elements_by_xpath("//p/strong[text()='请求方式：']/../following-sibling::ul[1]/li")
	return apitypes

def getDescription(browser):
	descriptions = browser.find_elements_by_xpath("//p/strong[text()='请求URL：']/../preceding-sibling::ul[1]/li/ul/li/a")
	if len(descriptions) == 0:
		descriptions = browser.find_elements_by_xpath("//p/strong[text()='请求URL：']/../preceding-sibling::ul[1]/li")
	if len(descriptions) == 0:
		descriptions = browser.find_elements_by_xpath("//strong[text()='请求URL：']/preceding-sibling::ul[1]/li/ul/li/a")
	if len(descriptions) == 0:
		descriptions = browser.find_elements_by_xpath("//strong[text()='请求URL：']/preceding-sibling::ul[1]/li")
	return descriptions	

def getParams(browser,num,requesttype):
	#先获取最近的div的table
	divNum = 1
	if len(requesttype) == 0:
		strongtext = '请求URL：'
	else:
		strongtext = '请求方式：'
	paramNames = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[1]"%(strongtext,num,divNum))
	paramRequire = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[2]"%(strongtext,num,divNum))
	paramType = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[3]"%(strongtext,num,divNum))
	paramDescription = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[4]"%(strongtext,num,divNum))
	
	resultName = []
	resultRequire = []
	resultType = []
	resultDescription = []
	#检查是否带有apiKey\interfaceId\timestamp\sign
	for key,name in enumerate(paramNames):
		if name.text == 'apiKey' or name.text == 'interfaceId' or name.text == 'timestamp' or name.text == 'sign':
			continue
		resultName.append(paramNames[key])
		resultRequire.append(paramRequire[key])
		resultType.append(paramType[key])
		resultDescription.append(paramDescription[key])
	#第一个div除了基本参数什么都没有，所以要直接再找第二个
	#直接再找下一个div的table
	if len(resultName) == 0:
		divNum = divNum + 1
		resultName = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[1]"%(strongtext,num,divNum))
		resultRequire = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[2]"%(strongtext,num,divNum))
		resultType = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[3]"%(strongtext,num,divNum))
		resultDescription = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[4]"%(strongtext,num,divNum))
		if len(resultDescription) == 0:
			params = {}
			return params

	params = {}
	params['name'] = resultName
	params['require'] = resultRequire
	params['type'] = resultType
	params['description'] = resultDescription
	params['divNum'] = divNum
	return params

def get2ndParams(browser,num,divNum,requesttype):
	params = {}
	if len(requesttype) == 0:
		strongtext = '请求URL：'
	else:
		strongtext = '请求方式：'
	#判断接下来是否还有参数
	secondParamsTitle = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/following-sibling::p[1]/strong"%(strongtext,num,divNum))
	if len(secondParamsTitle) == 0:
		return params
	#判断是否是POST参数
	if 'POST' in secondParamsTitle[0].text:
		divNum = divNum+1
		resultName = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[1]"%(strongtext,num,divNum))
		resultRequire = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[2]"%(strongtext,num,divNum))
		resultType = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[3]"%(strongtext,num,divNum))
		resultDescription = browser.find_elements_by_xpath("(//p/strong[text()='%s'])[%s]/../following-sibling::div[%s]/table/tbody/tr/td[4]"%(strongtext,num,divNum))
		params['name'] = resultName
		params['require'] = resultRequire
		params['type'] = resultType
		params['description'] = resultDescription
	return params


def getJsonParams(browser,fldname,num):
	jsonParams = {}
	jsonParams['name'] = browser.find_elements_by_xpath("(//ul/li[contains(text(),'%s')])[%s]/../following-sibling::div[1]/table/tbody/tr/td[1]"%(fldname,num))
	jsonParams['require'] = browser.find_elements_by_xpath("(//ul/li[contains(text(),'%s')])[%s]/../following-sibling::div[1]/table/tbody/tr/td[2]"%(fldname,num))
	jsonParams['type'] = browser.find_elements_by_xpath("(//ul/li[contains(text(),'%s')])[%s]/../following-sibling::div[1]/table/tbody/tr/td[3]"%(fldname,num))
	jsonParams['description'] = browser.find_elements_by_xpath("(//ul/li[contains(text(),'%s')])[%s]/../following-sibling::div[1]/table/tbody/tr/td[4]"%(fldname,num))
	if len(jsonParams['name']) == 0:
		jsonParams['name'] = browser.find_elements_by_xpath("//td[text()='%s']/../../../../following-sibling::div[1]/table/tbody/tr/td[1]"%(fldname))
		jsonParams['require'] = browser.find_elements_by_xpath("//td[text()='%s']/../../../../following-sibling::div[1]/table/tbody/tr/td[2]"%(fldname))
		jsonParams['type'] = browser.find_elements_by_xpath("//td[text()='%s']/../../../../following-sibling::div[1]/table/tbody/tr/td[3]"%(fldname))
		jsonParams['description'] = browser.find_elements_by_xpath("//td[text()='%s']/../../../../following-sibling::div[1]/table/tbody/tr/td[4]"%(fldname))
		if len(jsonParams['description']) == 0:
			return {}
	return 	jsonParams

def getCategory(browser):
	#先判断是否三级接口
	category = browser.find_elements_by_xpath("//li[@class='active']/../..")
	if len(category) == 0 :
		return ''
	if category[0].get_attribute('class') == 'third-child-catalog':
		#是三级接口
		category = browser.find_element_by_xpath("//li[@class='active']/../../../preceding-sibling::a[1]")
	else:
		#非三级接口
		category = browser.find_element_by_xpath("//li[@class='active']/../preceding-sibling::a[1]")

	result = 0
	# return 1 if category.get_attribute('title') == '微信接口' else 0
	if category.get_attribute('title') == '微信接口':
		result = 1
	elif category.get_attribute('title') == 'CRM+ 大陆同步接口':
		result = 2
	elif category.get_attribute('title') == 'CRM+ HK同步接口':
		result = 3
	return result

def getPrefix(browser):
	#先判断是否三级接口
	category = browser.find_elements_by_xpath("//li[@class='active']/../..")
	if len(category) == 0 :
		return ''
	if category[0].get_attribute('class') == 'third-child-catalog':
		#是三级接口,取父级作为前缀
		prefix = browser.find_element_by_xpath("//li[@class='active']/../preceding-sibling::a[1]")
		prefix = prefix.get_attribute('title')
	else:
		#非三级接口,取自己作为前缀
		prefix = browser.find_element_by_xpath("//li[@class='active']/a")
		prefix = prefix.text
	return prefix

#递归获取JsonParams
def recursionJsonParams(result,tmp_param,i,num):
	#如果有json，则遍历json相关参数
	if(tmp_param['type'] == 'json'):
		pid = i
		i = i + 1
		jsonParams = getJsonParams(browser,tmp_param['fieldname'],num)
		if len(jsonParams) == 0:
			return i
		for key2,content_param_name in enumerate(jsonParams['name']):
			tmp_param = {}
			tmp_param['id'] = i
			tmp_param['pid'] = pid
			tmp_param['fieldname'] = jsonParams['name'][key2].text
			tmp_param['require'] = 1 if jsonParams['require'][key2].text == '是' else 0
			tmp_param['type'] = jsonParams['type'][key2].text		
			try:
			    tmp_param['description'] = jsonParams['description'][key2].text
			except:
			    tmp_param['description'] = ''
			result.append(tmp_param)
			i = recursionJsonParams(result,tmp_param,i,num)
	else:
		i = i + 1
	return i

def formatParams(browser, params, num):
	result = []
	if len(params) == 0:
		return result
	i = 1;
	for key,param_name in enumerate(params['name']):
		#遍历父级
		tmp_param = {}
		tmp_param['id'] = i
		tmp_param['pid'] = 0
		tmp_param['fieldname'] = params['name'][key].text
		tmp_param['require'] = 1 if params['require'][key].text == '是' else 0
		tmp_param['type'] = params['type'][key].text
		tmp_param['description'] = params['description'][key].text
		result.append(tmp_param)

		#递归获取JsonParams
		i = recursionJsonParams(result,tmp_param,i,num)
	return result

def getList(browser, urls, apitypes, descriptions, category, prefix):
	apiList = []
	for index,url in enumerate(urls):
		tmp = {}
		tmp['url'] = url.text
		tmp['category'] = category
		if len(apitypes) > 0 :
			tmp['type'] = apitypes[index].text
		else:
			tmp['type'] = ''

		if len(descriptions) > 0 :
			tmp['description'] = prefix + '-' + descriptions[index].text
		else:
			tmp['description'] = ''

		tmp['params'] = []
		tmp['secondParams'] = []

		num = index + 1
		
		params = getParams(browser,num,tmp['type'])
		if len(params) != 0:
			divNum = params['divNum']
		else:
			divNum = 1
			
		secondParams = get2ndParams(browser,num,divNum,tmp['type'])

		tmp['params'] = formatParams(browser, params, num)

		if len(secondParams) != 0:
			tmp['secondParams'] = formatParams(browser, secondParams, num)

		apiList.append(tmp)
	return apiList

def writeJson(apiList,nextpage):
	if len(apiList):
		apiList = json.dumps(apiList)
		basepath = '../wikijson%s/'%(crawltarget)
		path = basepath+'%s.json'%(nextpage)
		fo = open(path, "w")
		fo.write(apiList)
		fo.close()

def crawlWiki(browser, nextpage='2'):
	browser.get('http://wiki.klub11.com/index.php?s=/%s&page_id='%(crawltarget) + nextpage)

	category = getCategory(browser)
	if category == 3:
		#香港接口不同步
		return False
	prefix = getPrefix(browser)

	#切换iframe test
	browser.switch_to.frame("page-content")

	#获取页面所有请求url
	urls = getUrls(browser)

	#获取页面所有请求方式
	apitypes = getTypes(browser)

	#获取页面所有请求描述
	descriptions = getDescription(browser)
		
	#根据url和apitypes来再去爬出对应的参数，并重组成dict
	apiList = getList(browser, urls, apitypes, descriptions, category, prefix)
	
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
	loginPage = 'http://wiki.klub11.com/index.php?s=/home/item/pwd/item_id/%s'%(crawltarget)
	browser.get(loginPage)
	fo = open('cookie.json', 'r')
	cookie = fo.read()
	cookie = json.loads(cookie)
	browser.add_cookie(cookie[0])
	# 尝试是否登录成功
	browser.get('http://wiki.klub11.com/index.php?s=/%s&page_id=2'%(crawltarget))
	# browser.switch_to.frame("page-content")
	check_is_login = browser.find_elements_by_xpath("//a[@class='show_cut_title']")
	if len(check_is_login):
		return True
	return False

#供应商开发平台 2
#丰泽同步接口 4
crawltarget = '4'
browser = browserInit()
if readCookie(browser) == False:
	browser = login(browser)
	writeCookie(browser)
# for i in range(23,200):
# 	crawlWiki(browser,str(i))
crawlWiki(browser,'143')
browser.quit()
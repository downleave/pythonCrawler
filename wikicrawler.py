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
	time.sleep(2)

	#切换iframe
	browser.switch_to.frame("page-content")

	#获取多个接口url
	urls = browser.find_elements_by_xpath("//p/strong[text()='请求URL：']/../following-sibling::ul[1]/li/code")
	for url in urls:
		print('url:',url.text)

	#获取请求方式
	apitypes = browser.find_elements_by_xpath("//p/strong[text()='请求方式：']/../following-sibling::ul[1]/li")
	for apitype in apitypes:
		print('apitype:',apitype.text)

	params = browser.find_elements_by_xpath("//ul/li[text()='content参数说明']/../following-sibling::div[1]/table/tbody/tr/td[1]")

	for param in params:
		print('param:',param.text)

	browser.quit()

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
writeJson(browser)
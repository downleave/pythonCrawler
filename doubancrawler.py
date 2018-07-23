import requests
from lxml import etree
from PIL import Image
import os

def login():
	loginPage = 'https://accounts.douban.com/login';
	session = requests.session();
	response = session.get(loginPage)
	if isCaptcha(response):
		path = downloadCaptcha(response)
		showCaptcha(path)
		captchaSolution = input('根据打开的图片输入验证码:')
		capthaID = getCaptchaID(response)
	else:
		print('无验证码')
		captchaSolution = ''
		capthaID = ''
	return submitLoginForm(captchaSolution,capthaID,session)

def isCaptcha(response):
	text = etree.HTML(response.text).xpath('//div[@class="item item-captcha"]/label/text()')
	if not text:
		return False
	return True

def downloadCaptcha(response):
	imgUrl = etree.HTML(response.text).xpath('//img[@id="captcha_image"]/@src')[0]
	captha = requests.get(imgUrl)
	path = 'captha.jpg'
	with open(path, 'wb') as file:
		file.write(captha.content)
		file.close()
	return path

def getCaptchaID(response):
	return etree.HTML(response.text).xpath('//input[@name="captcha-id"]/@value')[0]

def showCaptcha(path):
	im = Image.open(path)
	im.show()

def submitLoginForm(captchaSolution, captchaId, session):
	formdata = {
		"source": "None",
		"redir": "https://www.douban.com",
		"form_email": "",# 输入你的豆瓣账号
		"form_password": "",# 输入你的密码
		"captcha-solution": captchaSolution,
		"captcha-id": captchaId,
		"login": "登录",
	}
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"}
	response = session.post('https://accounts.douban.com/login', headers = headers, data = formdata)
	if response.status_code == 200:
		print('登录成功')
	else:
		print('登录失败')
	return session

def writeFollowers(session, nextpage = ''):
	response 	= session.get('https://www.douban.com/contacts/rlist' + nextpage)
	response 	= etree.HTML(response.text)
	followerList 	= response.xpath('//ul[@class="user-list"]/li/div/h3/a[1]/text()')
	detailUrlList = response.xpath('//ul[@class="user-list"]/li/div/h3/a[1]/@href')

	file = 'follow.txt'

	if not os.path.exists(file):
 		fileobj = os.open(file, os.O_CREAT|os.O_RDWR|os.O_APPEND)
	else:
		fileobj = os.open(file, os.O_RDWR|os.O_APPEND)

	for index,url in enumerate(detailUrlList):
		followerDetailResponse = etree.HTML(session.get(url).text)
		location = followerDetailResponse.xpath('//div[@class="basic-info"]/div/a/text()')
		if not location:
			location = ''
		else:
			location = location[0]
		writeStr = followerList[index] + ' ' + location + '\r\n'
		os.write(fileobj, bytes(writeStr, 'UTF-8'))

	print('分页信息写入成功')

	nextpage = response.xpath('//span[@class="next"]/a/@href')
	if nextpage:
		writeFollowers(session, nextpage[0])

session = login()
writeFollowers(session)
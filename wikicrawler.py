import requests
from lxml import etree
from PIL import Image
import os

def login():
	loginPage = 'http://wiki.klub11.com/index.php?s=/home/item/pwd/item_id/2';
	session = requests.session()
	response = session.get(loginPage)
	path = downloadCaptcha(response,session)
	showCaptcha(path)
	v_code = input('根据打开的图片输入验证码:')
	return submitLoginForm(v_code,session)

def downloadCaptcha(response,session):
	imgUrl = 'http://wiki.klub11.com/Public/verifyCode.php';
	captha = session.get(imgUrl)
	path = 'captha.jpg'
	with open(path, 'wb') as file:
		file.write(captha.content)
		file.close()
	return path

def showCaptcha(path):
	im = Image.open(path)
	im.show()

def submitLoginForm(v_code, session):
	formdata = {
		"item_id": "2",
		"password": "pf1q78rc",
		"refer_url": "",
		"v_code": v_code,
	}
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"}
	response = session.post('http://wiki.klub11.com/index.php?s=/home/item/pwd/item_id/2', headers = headers, data = formdata)
	if response.status_code == 200:
		print('登录成功')
	else:
		print('登录失败')
	return session

# def writeFollowers(session, nextpage = ''):
# 	response 	= session.get('https://www.douban.com/contacts/rlist' + nextpage)
# 	response 	= etree.HTML(response.text)
# 	followerList 	= response.xpath('//ul[@class="user-list"]/li/div/h3/a[1]/text()')
# 	detailUrlList = response.xpath('//ul[@class="user-list"]/li/div/h3/a[1]/@href')

# 	file = 'follow.txt'

# 	if not os.path.exists(file):
#  		fileobj = os.open(file, os.O_CREAT|os.O_RDWR|os.O_APPEND)
# 	else:
# 		fileobj = os.open(file, os.O_RDWR|os.O_APPEND)

# 	for index,url in enumerate(detailUrlList):
# 		followerDetailResponse = etree.HTML(session.get(url).text)
# 		location = followerDetailResponse.xpath('//div[@class="basic-info"]/div/a/text()')
# 		if not location:
# 			location = ''
# 		else:
# 			location = location[0]
# 		writeStr = followerList[index] + ' ' + location + '\r\n'
# 		os.write(fileobj, bytes(writeStr, 'UTF-8'))

# 	print('分页信息写入成功')

# 	nextpage = response.xpath('//span[@class="next"]/a/@href')
# 	if nextpage:
# 		writeFollowers(session, nextpage[0])

def writeJson(session, nextpage='4'):
	# response = session.get('http://wiki.klub11.com/index.php?s=/2&page_id=' + nextpage)
	response = session.get('http://wiki.klub11.com/index.php?s=/home/page/index/page_id/' + nextpage)
	print(response.text)
	response = etree.HTML(response.text)
	# 接口中文名字
	page_title = response.xpath('//h3[@id="page_title"]/text()')[0]
	print(page_title)

	urls = response.xpath('//li/code')
	print(urls)
	exit()


session = login()
writeJson(session)
#writeFollowers(session)
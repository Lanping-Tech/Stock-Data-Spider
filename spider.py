from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import time
import json
import pandas as pd
import schedule

import os
from tqdm import tqdm
import threading

def fake_refresh(driver):
	driver.execute_script(
	"""
	(function () {
		var y = 0;
		var step = 100;
		window.scroll(0, 0);

		function f() {
		if (y < (document.body.scrollHeight)/5) {
			y += step;
			window.scroll(0, y);
			setTimeout(f, 100);
		} else {
			window.scroll(0, 0);   //滑动到顶部
			document.title += "scroll-done";
		}
		}
		setTimeout(f, 1000);
	})();
	"""
	)
	sleep(5)

class SimpleThread(threading.Thread):

    def __init__(self,func,args={}):
        super(SimpleThread,self).__init__()
        self.func = func # 执行函数
        self.args = args # 执行参数，其中包含切分后的数据块，字典类型

    def run(self):
        self.result = self.func(**self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def get_driver():
	# PROXY="182.84.144.68:3256"
	# webdriver.DesiredCapabilities.CHROME['proxy'] = {
    # "httpProxy": PROXY,
    # "ftpProxy": PROXY,
    # "sslProxy": PROXY,
    # "proxyType": "MANUAL",

	# }

	webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True
	chrome_options = Options()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-dev-shm-usage')
	chrome_options.add_argument('--disable-gpu')
	# chrome_options.add_argument("window-size=1024,768")
	# chrome_options.add_argument('--ignore-certificate-errors')
	# chrome_options.add_argument('--ignore-ssl-errors')
	# chrome_options.add_argument("--proxy-server={}".format('27.40.124.240:9999'))
	

	chrome_driver = 'config/chromedriver-win.exe'  #chromedriver的文件位置
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = chrome_driver)
	driver.delete_all_cookies()
	return driver

def text_format(text):
	text = text.replace(' ','')
	text = text.replace('\n','')
	text = text.replace('\r','')
	text = text.replace('查看PDF原文','')
	text = text.replace('查看原文','')
	text = text.replace('[点击]','')
	text = text.replace('提示：本网不保证其真实性和客观性，一切有关该股的有效信息，以交易所的公告为准，敬请投资者注意风险。','')
	return text

def get_base_info(driver, stock_id, record):
	if record['comment_url'].startswith('/news,{}'.format(stock_id)):
		comment_url = 'http://guba.eastmoney.com'+record['comment_url']
		driver.get(comment_url)
		soup = BeautifulSoup(driver.page_source, "html.parser")
		if soup.select('#zwconttbt'):
			record['title'] = text_format(soup.select('#zwconttbt')[0].get_text())
			time_str = soup.select('#zwconttb > div.zwfbtime')[0].get_text().split(' ')
			record['time'] = time_str[1]+' '+time_str[2]
			record['content'] = text_format(soup.select('#zwconbody > div')[0].get_text())
			return record
		else:
			return {}
	else:
		return {}

def get_all_urls(stock_id, page_id):
	save_path = os.path.join('comment',stock_id)
	driver = get_driver()
	driver.maximize_window()
	sleep(1)
	base_url = 'http://guba.eastmoney.com/list,{}_{}.html'.format(stock_id,page_id)
	driver.get(base_url)
	# driver.maximize_window()
	soup = BeautifulSoup(driver.page_source, "html.parser")
	items = soup.select('#articlelistnew > div')
	records = []
	for item in items:
		if item.get('class')[0] == 'articleh':
			record = {}
			record['read'] = item.select('span.l1.a1')[0].get_text()
			record['subcomments'] = item.select('span.l2.a2')[0].get_text()
			record['comment_url'] = item.select('span.l3.a3 > a')[0].get('href') #.split(',')[-1].split('.')[0]
			print(record)
			record = get_base_info(driver, stock_id, record)
			if record:
				record['comment_id'] = record['comment_url'].split(',')[-1].split('.')[0]
				# writelog('comment-url-{}.log'.format(stock_id),str(record))
				json2file(save_path, record)
				records.append(record)
	driver.quit()
	return records


def get_data(stock_id):
	if not os.path.exists(os.path.join('comment',stock_id)):
		os.makedirs(os.path.join('comment',stock_id))
	driver = get_driver()

	driver.get('http://guba.eastmoney.com/list,{}.html'.format(stock_id))
	driver.maximize_window()
	sleep(1)

	soup = BeautifulSoup(driver.page_source, "html.parser")
	
	page_num = soup.select('#articlelistnew > div.pager > span > span > span:nth-child(1) > span')[0].get_text()
	# record = get_base_info(driver, stock_id, {'read': '30', 'subcomments': '0', 'comment_url': '/news,000983,1086997925.html'})
	# print(record)
	driver.quit()
	records = []
	# threads = []
	# for i in range(int(page_num)):
	# 	t = SimpleThread(get_all_urls, {'stock_id':stock_id,'page_id':i+1})
	# 	threads.append(t)
	# for i in range(int(page_num)):  
	# 	threads[i].start()
	# for i in range(int(page_num)):
	# 	threads[i].join()
	# 	records.extend(threads[i].get_result())

	total_num = 0
	for i in range(int(page_num)):
		page_id = i+1
		print(page_id)
		
		rs = get_all_urls(stock_id, page_id)
		# records.extend(rs)
		total_num = total_num+len(rs)

	print('编号：{}，共计{}页, {}条记录。'.format(stock_id, page_num, total_num))

def json2file(save_path, record):
	with open(os.path.join(save_path, record['comment_id']+'.json'),"w",encoding='utf-8') as f:
		json.dump(record,f,ensure_ascii=False)

def main():
	if not os.path.exists('comment'):
		os.makedirs('comment')
	get_data('000983')

def writelog(file_name, log):
	with open(file_name, mode='a',encoding='utf-8') as filename:
		filename.write(log)
		filename.write('\n') # 换行

if __name__ == "__main__":
	main()
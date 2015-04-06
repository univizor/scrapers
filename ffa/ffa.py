import re
import sys
import subprocess
import os

import requests
import bs4
from slugify import slugify

URL_BASE = 'http://www.ffa.uni-lj.si/'
URL_START = URL_BASE + 'knjiznica/diplome-magisteriji-in-doktorati/'

DL_DIR = os.environ.get('SCRAPER_TMP_DOC') or '/mnt/univizor/download/'

EXTs = {
	'application/pdf': 'pdf',
}

class Thesis(dict):
	def __hash__(self):
		return hash(self['url'])

	def get_filename(self, ext):
		return '{}_{}.{}'.format(
			slugify(self['author'])[:20],
			slugify(self['title'])[:30],
			ext
		)

	def download(self):
		r = requests.get(self['url'], stream=True)
		try:
			
			ext = re.findall(r'filename=.*',
							 r.headers['Content-Disposition'])[0].split('=')[1].split('.')[-1]
		except:
			ct = r.headers.get('content-type')
			if ct not in EXTs:
				print('Failed url:', self['url'])
				return False
			ext = EXTs[ct]
		local_filename = (DL_DIR + self.get_filename(ext))
		if os.path.exists(local_filename):
			return
		with open(local_filename, 'wb') as f:
			f.write(r.content)
		self.filename = local_filename
		return True

	def store_meta(self):
		command = u'./push2db.py "{}" "{}" "{}" "{}" "{}" "{}" "{}"'.format(
			self.filename,
			self.source,
			self['url'],
			self['author'],
			self['title'],
			self['year'],
			self['school']
		)
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		out = p.stdout.read()
		p.communicate()
		if p.returncode > 0:
			print out

def extract_links(response_html):
	url_list = set()
	soup = bs4.BeautifulSoup(response_html)
	for item in soup.select('.tx_sevenpack-title a'):
		try:
			url_list.add(URL_BASE + item['href'])
		except:
			print ('Failed', item)
			pass
	url_next = None
	for item in soup.select('.tx_sevenpack-navi_page_selection a'):
		if item['title'] == 'Naslednja stran':
			url_next = URL_BASE + item['href']
	return url_list, url_next

def extract_content(response_html):
	thesis = Thesis()
	thesis.source = 'FFA'
	thesis['school'] = 'UL, Fakulteta za farmacijo'
	
	soup = bs4.BeautifulSoup(response_html).select('.tx_sevenpack-single_view')[0]
	for item in soup.select('table.tx_sevenpack-single_item tr'):
		if not item.select('th') or not item.select('td'):
			continue
		key = item.select('th')[0].get_text()
		value = item.select('td')[0].get_text()
		if 'URL do' in key:
			thesis['url'] = value
		elif 'Naslov:' in key:
			thesis['title'] = value
		elif 'Leto:' in key:
			thesis['year'] = value
		elif 'Avtor(ji):' in key:
			thesis['author'] = value.split(', ')[0]
	
	if 'url' in thesis and thesis.download():
		thesis.store_meta()
			
if __name__ == '__main__':
	page_url = sys.argv[-1] if len(sys.argv) > 1 else URL_START
	while page_url:
		print ('Scraping', page_url)
		response = requests.get(page_url)

		url_list, page_url = extract_links(response.content.decode('utf-8'))
		for url in url_list:
			response = requests.get(url)
			extract_content(response.content.decode('utf-8'))
		

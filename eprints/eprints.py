import re
import json
import os
import subprocess

import requests
import bs4
from slugify import slugify

DL_DIR = '/mnt/univizor/download/'

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
		if 'url' not in self:
			return False
		r = requests.get(self['url'], stream=True)
		try:
			ext = re.findall(r'filename=.*',
							 r.headers['Content-Disposition'])[0].split('=')[1].split('.')[-1]
		except:
			print('Failed url:', self['url'])
			return False
		local_filename = (DL_DIR + self.get_filename(ext))
		if os.path.exists(local_filename):
			return
		with open(local_filename, 'wb') as f:
			f.write(r.content)
		self.filename = local_filename
		return True

	def get_meta(self):
		return json.dumps({
			key: val for key, val in self.items()
			if key not in ('author', 'title', 'year', 'school', )
		})
	
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
			exit(1)

def get_url_list(y, url_base):
	url_list = set()
	url = '{}view/year/{}.html'.format(url_base, y)
	response = requests.get(url)
	content = response.content.decode('utf-8')
	soup = bs4.BeautifulSoup(content)
	for item in soup.select('.ep_view_page_view_year p'):
		try:
			url = item.select('a')[0]['href']
			if re.match(r'{}\d+/'.format(url_base), url):
				url_list.add(url)
		except:
			pass
	if len(url_list) == 0:
		start = 0
		while True:
			try:
				ind_url = content.index(url_base, start)
				ind_url_num = ind_url + len(url_base)
				ind_url_end = content.index('/', ind_url_num)
				if content[ind_url_num:ind_url_end].isdigit():
					url_list.add(content[ind_url:ind_url_end])
				start = ind_url_end + 1
			except ValueError:
				break
			
			
	print url_list
	return url_list

def extract(url, source, school=None):
	response = requests.get(url)
	soup = bs4.BeautifulSoup(response.content.decode('utf-8'))

	thesis = Thesis()
	thesis.source = source
	if school:
		thesis['school'] = school

	thesis['keywords'] = []

	thesis['title'] = soup.select('h1')[0].get_text()
	for bar in soup.select('.ep_summary_content_main'):
		thesis['year'] = re.findall(r'[0-9]{4}', bar.get_text())[0]
		break
	
	for author in soup.select('.ep_summary_content .person_name'):
		thesis['author'] = author.get_text()
		break
	for anchor in soup.select('table a'):
		if 'Download' in anchor.get_text():
			thesis['url'] = anchor['href']
			break
	for row in soup.select('table table tr'):
		if not row.select('th'):
			continue
		row_header = row.select('th')[0].get_text()
		if 'Item Type:' in row_header or 'Tip vnosa:' in row_header:
			row_content = row.select('td')[0].get_text()
			if 'Thesis' not in row_content and 'Delo' not in row_content:
				return # lets break
		if 'ne besede:' in row_header or 'Keywords:' in row_header:
			thesis['keywords'] = [
				elt.encode('utf-8') for elt in row.select('td')[0].get_text().split(', ')
			]
	
	if thesis.download():
		thesis.store_meta()
	

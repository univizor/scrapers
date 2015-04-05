import re
import sys
import json
import os

import requests
import bs4
from slugify import slugify

URL_BASE = 'http://eprints.fri.uni-lj.si/'
YEARS = range(1983, 2016)
DL_DIR = './docs/'

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
			print('Failed url:', self['url'])
			return False
		local_filename = (DL_DIR + self.get_filename(ext))
		if os.path.exists(local_filename):
			return
		with open(local_filename, 'wb') as f:
			f.write(r.content)
		return True

	def store_meta(self):
		local_filename = DL_DIR + self.get_filename('json')
		with open(local_filename, 'w') as f:
			f.write(json.dumps(self))

def get_url_list(y):
	url_list = set()
	url = '{}view/year/{}.html'.format(URL_BASE, y)
	response = requests.get(url)
	soup = bs4.BeautifulSoup(response.content.decode('utf-8'))
	for item in soup.select('.ep_view_page_view_year p'):
		try:
			url = item.select('a')[0]['href']
			if re.match(r'{}\d+/'.format(URL_BASE), url):
				url_list.add(url)
		except:
			pass
	return url_list

def extract(url):
	response = requests.get(url)
	soup = bs4.BeautifulSoup(response.content.decode('utf-8'))
	thesis = Thesis()

	thesis['keywords'] = []

	thesis['title'] = soup.select('h1')[0].get_text()
	for author in soup.select('.ep_summary_content .person_name'):
		thesis['author'] = author.get_text()
		break
	for anchor in soup.select('table a'):
		if 'Download' in anchor.get_text():
			thesis['url'] = anchor['href']
			break
	for row in soup.select('table tr'):
		if not row.select('th'):
			continue
		row_header = row.select('th')[0].get_text()
		if 'ne besede:' in row_header or 'Keywords:' in row_header:
			thesis['keywords'] = row.select('td')[0].get_text().split(', ')
			break
	
	if thesis.download():
		thesis.store_meta()
	
			
if __name__ == '__main__':
	start = YEARS.index(int(sys.argv[-1]) if len(sys.argv) > 1 else YEARS[0])
	for year in YEARS[start:]:
		print ('Scraping year', year)
		for thesis_url in get_url_list(year):
			try:
				extract(thesis_url)
			except:
				raise

import re
import sys
import json
import os

import requests
import bs4
from slugify import slugify

CATEGORIES = {
	'sl': 'kat1=jezik&kat2=1060&',
	'en': 'kat1=jezik&kat2=1033&',
}

URL_BASE = 'https://repozitorij.uni-lj.si/'
URI_LIST = '{base}Brskanje2.php?{category}page={page}' # this is just the slovenian list, TODO: english
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

def extract(response_html):
	item_list = set()
	soup = bs4.BeautifulSoup(response_html)
	for item in soup.select('table.ZadetkiIskanja .Besedilo'):
		thesis = Thesis()
		thesis['keywords'] = []
		for a in item.select('a'):
			if 'stl0=KljucneBesede' in a['href']:
				thesis['keywords'].append(a.get_text())
			elif 'stl0=Avtor' in a['href']:
				thesis['author'] = a.get_text()
			elif 'Dokument.php' in a['href']:
				thesis['url'] = URL_BASE + a['href']
			elif 'IzpisGradiva.php?id=30689&lang=slv':
				thesis['title'] = a.get_text()
		if thesis.download():
			thesis.store_meta()
			item_list.add(thesis)
	return item_list


if __name__ == '__main__':
	page = int(sys.argv[-1]) if len(sys.argv) > 1 else 1
	category = sys.argv[-2] if len(sys.argv) > 2 else 'sl'
	thesis_set = set([])
	while True:
		url = URI_LIST.format(base=URL_BASE, page=page, category=CATEGORIES[category])
		print ('Scraping', url)
		response = requests.get(url)
		new_items = extract(response.content.decode('utf-8'))
		if not (new_items - thesis_set):
			break
		thesis_set |= new_items
		page += 1

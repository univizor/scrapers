import re
import sys
import subprocess
import os

import requests
import bs4
from slugify import slugify

CATEGORIES = {
	'sl': 'kat1=jezik&kat2=1060&',
	'en': 'kat1=jezik&kat2=1033&',
}

URL_META = 'https://repozitorij.uni-lj.si/Export.php?id={id}&lang=slv'
URL_BASE = 'https://repozitorij.uni-lj.si/'
URI_LIST = '{base}Brskanje2.php?{category}page={page}' # this is just the slovenian list, TODO: english

#DL_DIR = './docs/'
DL_DIR = os.environ.get('SCRAPER_TMP_DOC') or '/mnt/univizor/download/'

SKIP = (
	'FRI', # FRI
	'PEF', # Pedagoska
	'FGG', # Gradbenistvo
	'FFA', # Farmacija
)
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
			exit(1)

def extract_one(item):
	thesis = Thesis()
	thesis.source = 'RUL'
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

	thesis_id = thesis['url'].split('Dokument.php?id=')[-1].split('&')[0]

	meta = bs4.BeautifulSoup(requests.get(URL_META.format(id=thesis_id)).content.decode('utf-8'))
	thesis_type = meta.select('vrstagradiva')
	if not thesis_type:
		return
	thesis_type = thesis_type[0].get_text()
	if 'delo/naloga' not in thesis_type and ' delo' not in thesis_type:
		return
	org = meta.select('organizacija')[0]
	if org['kratica'] in SKIP:
		return
	org_text = org.get_text()
	thesis['year'] = meta.select('letoizida')[0].get_text()
	thesis['school'] = 'UL, ' + org_text
	return thesis

def extract(response_html):
	item_list = set()
	soup = bs4.BeautifulSoup(response_html)
	for item in soup.select('table.ZadetkiIskanja .Besedilo'):
		try:
			thesis = extract_one(item)
			if not thesis:
				continue
			if thesis.download():
				thesis.store_meta()
				item_list.add(thesis)
		except:
			raise
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
		if new_items and not (new_items - thesis_set):
			# if we got new items and they are all in the thesis set, then we stop
			break
		thesis_set |= new_items
		page += 1

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cobiss.py [LETO VRSTA UDK]

"""

import sys, os, re, subprocess
import urllib
import requests
import bs4
from slugify import slugify


# http://cobiss4.izum.si/scripts/cobiss?ukaz=SFRM&mode=5&id=1504303287585446
# http://home.izum.si/cobiss/obvestila_novosti/dokumenti/Dodatek_G.pdf

URL_REQ = 'http://www.cobiss.si/scripts/cobiss'
URL_SEARCH = 'http://cobiss4.izum.si/scripts/cobiss?ukaz=SFRM&mode=5&id={}'
URL_ADVSEARCH = 'http://cobiss6.izum.si/scripts/cobiss?ukaz=SFRM&id={}'
URL_GETID = 'http://www.cobiss.si/scripts/cobiss?ukaz=getid&lani=si'

VRSTA = {
	'm': 'doktorska disertacija',
	'm2': 'magistrsko delo', 
	'm3': 'specialisticno delo',
	'm4': 'habilitacijsko delo', 
	'm5': 'diplomsko delo',
	'm6': 'višješolska diplomska naloga', 
	'm7': 'maturitetna naloga',
	'mb11': 'diplomsko delo/naloga (1. stopnja bolonjskega študija)', 
	'mb12': 'zaključna naloga (1. stopnja bolonjskega študija)', 
	'mb13': 'delo diplomskega projekta/projektno delo (1. stopnja bolonjskega študija)',
	'mb14': 'delo diplomskega seminarja/zaključno seminarsko delo/naloga (1. stopnja bolonjskega študija)',
	'mb15': 'dramaturško delo (1. stopnja bolonjskega študija)',
	'mb16': 'delo zaključne refleksije študija (1. stopnja bolonjskega študija)',
	'mb21': 'diplomsko delo/naloga (2. stopnja bolonjskega študija)',
	'mb22': 'magistrsko delo/naloga (bolonjski študij)',
	'mb31': 'doktorsko delo/naloga (bolonjski študij)',
}
VRSTAs = [
	'm', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7',
	'mb11', 'mb12', 'mb13', 'mb14', 'mb15', 'mb16', 'mb21', 'mb22', 'mb31',
]

DL_DIR = os.environ.get('SCRAPER_TMP_DOC') or '/mnt/univizor/download/'

LETOs = range(1980, 2016)

#3-101 - 3-128 - ul
#3-201 - 3-222 - umb
#3-301 - 3-303 - up
#3-401 - 3-419  - others
#3-500 - ung

SCHOOLS = {
	'UL': range(101, 129),
	'UMB': range(201, 223),
	'UP': range(301, 304),
	'others': range(401, 420),
	'UNG': [500]
}

EXTs = {
	'application/pdf': 'pdf',
}

HEADERS = {
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Language': 'en-US,en;q=0.8,sl;q=0.6,en-GB;q=0.4,de;q=0.2',
	'Accept-Encoding': 'gzip, deflate',
	'Content-Type': 'application/x-www-form-urlencoded',
	'Origin': 'http://cobiss6.izum.si',
	'Cache-Control': 'max-age=0',
}

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


class Thesis(dict):
	def __hash__(self):
		return hash(self['url'])

	def get_filename(self, ext):
		return '{}_{}.{}'.format(
			slugify(self['author'])[:20],
			slugify(self['title'])[:30],
			ext
		)

	def force_download(self):
		if '.pdf' not in self['url']:
			return False
		ext = self['url'].split('.')[-1]
		local_filename = (DL_DIR + self.get_filename(ext))
		self.filename = local_filename

		if 'https://' in self['url']:
			cmd = "curl -3 {} > {}".format(self['url'], local_filename)
		else:
			cmd = "curl {} > {}".format(self['url'], local_filename)
		status = subprocess.call(cmd, shell=True)
		return status == 0

	def download(self):
		try:
			r = requests.get(self['url'], stream=True)
		except requests.exceptions.SSLError:
			self['url'] = self['url'].replace('http://', 'https://')
			return self.force_download()
		try:
			
			ext = re.findall(r'filename=.*',
							 r.headers['Content-Disposition'])[0].split('=')[1].split('.')[-1]
		except:
			ct = r.headers.get('content-type')
			if ct not in EXTs:
				return self.force_download()
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

def store_and_download(thesis, retry=0):
	if retry >= 3:
		exit(1)
	try:
		if thesis.download():
			thesis.store_meta()
	except ValueError:
		print 'Download failed for url (', retry, ')', thesis['url']
		store_and_download(thesis, retry=(retry+1))
			
def find_content(soup, school, leto):
	content_found = False
	one_page = soup.select('#nolist-full')
	if one_page and one_page[0].get('class', ['NO'])[0] == 'record':
		thesis = Thesis()
		thesis['school'] = school
		thesis['year'] = leto
		thesis.source = 'cobiss'
			
		for tr in one_page[0].select('tr'):
			th = tr.select('th')[0]
			td = tr.select('td')[0]
			col = th.get_text()
			if col == 'Avtor':
				thesis['author'] = td.get_text().strip()
			if col == 'Naslov':
				thesis['title'] = td.get_text().strip()
			if col == 'URL':
				try:
					thesis['url'] = td.select('a')[0]['href']
				except:
					return True
		print thesis['url'], thesis['school'],
		store_and_download(thesis)
		return True

	for row in soup.select('#nolist-full tr'):
		columns = row.select('td')
		if not columns:
			continue
		content_found = True
		try:
			thesis = Thesis()
			thesis['school'] = school
			thesis['year'] = leto
			thesis.source = 'cobiss'
			thesis['author'] = columns[2].get_text()
			thesis['title'] = columns[3].get_text().split(' : ')[0]
			thesis['url'] = columns[8].select('a')[0]['href']
		except:
			thesis = Thesis()
			thesis.source = 'cobiss'
			thesis['school'] = school
			thesis['year'] = leto
			thesis['author'] = columns[3].get_text()
			thesis['title'] = columns[4].get_text().split(' : ')[0]
			thesis['url'] = columns[9].select('a')[0]['href']

		if 'cobiss4.izum.si/scripts/cobiss' in thesis['url']:
			continue
		store_and_download(thesis)
	return content_found

def get_school(soup, school_id):
	for b in soup('b'):
		b_text = b.get_text()
		if school_id in b_text:
			return b_text.split('(')[1][:-1]
	return '[unknown]'

def extract(sid, leto, vrsta, school, print_info='-'):
	print 'Extracting links for', leto, vrsta, school, '({})'.format(print_info), 'with sid', sid

	data = {
		'ukaz': 'SEAR',
		'ID': sid,
		'keysbm': '',

		'PF1': 'PY',
		'SS1': leto,
		'OP1': 'AND',

		'PF2': 'CC',
		'SS2': '"{}"'.format(vrsta),
		'OP2': 'AND',

		'PF3': 'FC',
		'SS3': '"{}"'.format(school),
		'OP3': 'AND',

		'PF4': 'KW',
		'SS4': '',
		'lan': '',
		'mat': '51',
		'eac': '1',
		'find': 'isci',	
	}

	url = URL_SEARCH.format(sid)
	data = 'ukaz=SEAR&ID={}&keysbm=&PF1=PY&SS1={}&OP1=AND&PF2=CC&SS2=%22{}%22&OP2=AND&PF3=FC&SS3=%22{}%22&OP3=AND&PF4=KW&SS4=&lan=&mat=51&eac=1&find=isci'.format(sid, leto, vrsta, school)
	resp = requests.post(url, data=data, headers=HEADERS)
	
	with open('test.html', 'w') as fd:
		fd.write(resp.content)
	
	soup = bs4.BeautifulSoup(resp.content)

	school_name = get_school(soup, school)

	content_found = find_content(soup, school_name, leto)

	try:
		if 'tevilo najdenih zapisov: 0' in soup.select('body div.main div.iright b')[0].get_text():
			print 'NIC ZADETKOV'
			return get_id(soup)
	except:
		pass
	
	if not content_found:
		sid = get_id()
		print 'Retry ... '
		return extract(sid, leto, vrsta, school, print_info=print_info)
	else:
		next_page(sid, school_name, leto, 1)
		return get_id(soup)

def next_page(sid, school_name, leto, page=1):
	url='http://cobiss4.izum.si/scripts/cobiss?ukaz=DIRE&' + urllib.urlencode({
		'id': sid,
		'dfr': 1 + page * 10, # 1, 11, 21 : page,
		'pgg': '10',
		'sid': '20',
	})
	print 'page', sid, school_name, page, 'url:', url
	resp = requests.get(url, headers=HEADERS)
	soup = bs4.BeautifulSoup(resp.content)

	content_found = find_content(soup, school_name, leto)
	if content_found:
		next_page(sid, school_name, leto, page + 1)
	
def get_id(soup=None):
	if soup:
		for item in soup('input'):
			if item['name'] == 'ID':
				return item['value']
	else:
		soup = bs4.BeautifulSoup(requests.get(URL_GETID).content)
		for a in soup('a'):
			if a.get('title') == 'Iskanje':
				url = a['href']
				return get_id(bs4.BeautifulSoup(requests.get(url).content)) 
	return None
	

def iterate(args):
	SCHOOL_LIST = ['UL', 'UMB', 'UP', 'others', 'UNG']
	first_itr = True
	leto, vrsta = 0, 0
	school1, school2 = 0, SCHOOLS['UL'][0]
	if args:
		leto, vrsta, school1, school2 = LETOs.index(int(args[0])), VRSTAs.index(args[1]), SCHOOL_LIST.index(args[2]), SCHOOLS[args[2]].index(int(args[3]))
	sid = get_id()
	for l in LETOs[leto:]:
		for v in first_itr and VRSTAs[vrsta:] or VRSTAs:
			for s1 in first_itr and SCHOOL_LIST[school1:] or SCHOOL_LIST:
				for s2 in first_itr and SCHOOLS[s1][school2:] or SCHOOLS[s1]:
					sid = extract(sid, l, v, '3-' + str(s2), print_info=s1)
					first_itr = False
					
			# for u in first_itr and UDKs[udk:] or UDKs:
			# 	sid = extract(sid, l, v, u)
			# 	first_itr = False
if __name__ == '__main__':
	iterate(sys.argv[1:])


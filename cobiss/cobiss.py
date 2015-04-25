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

def extract(sid, leto, vrsta, school):
	print 'Extracting links for', leto, vrsta, school, 'with sid', sid

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
	content_found = False
	for row in soup.select('#nolist-full tr'):
		content_found = True
		columns = row.select('td')
		if not columns:
			continue
		try:
			thesis = Thesis()
			thesis.source = 'cobiss'
			thesis['author'] = columns[2].get_text()
			thesis['title'] = columns[3].get_text().split(' : ')[0]
			thesis['url'] = columns[8].select('a')[0]['href']
		except:
			thesis = Thesis()
			thesis.source = 'cobiss'
			thesis['author'] = columns[3].get_text()
			thesis['title'] = columns[4].get_text().split(' : ')[0]
			thesis['url'] = columns[9].select('a')[0]['href']

		if 'cobiss4.izum.si/scripts/cobiss' in thesis['url']:
			continue
		print thesis['title']
	try:
		if 'tevilo najdenih zapisov: 0' in soup.select('body div.main div.iright b')[0].get_text():
			print 'NIC ZADETKOV'
			return get_id(soup)
	except:
		pass
	
	if not content_found:
		sid = get_id()
		print 'Retry ... '
		return extract(sid, leto, vrsta, school)
	else:
		#print soup.select('.content .nic9')#[2].get_text() #soup.select('.content .nic9 b')#[0].get_text()
		# pages
		url='http://cobiss4.izum.si/scripts/cobiss?ukaz=DIRE&' + urllib.urlencode({
			'sid': sid,
			'dfr': '', # 1, 11, 21 : page,
			'pgg': '10',
			'sid': '20',
		})
		# print soup.select('.content .nic9')
		return get_id(soup)

def set_commands(sid):
	return get_id(bs4.BeautifulSoup(requests.get(URL_ADVSEARCH.format(sid)).content))
	
def get_id(soup=None):
	soup = soup or bs4.BeautifulSoup(requests.post(URL_REQ, data={
		'base': '99999',
		'command': 'SEARCH',
		'srch': 'test',
		'x': '13',
		'y': '9',
	}).content.decode('utf-8'))
	for item in soup('input'):
		if item['name'] == 'ID':
			return soup and set_commands(item['value']) or item['value']
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
					sid = extract(sid, l, v, '3-' + str(s2))
					first_itr = False
					
			# for u in first_itr and UDKs[udk:] or UDKs:
			# 	sid = extract(sid, l, v, u)
			# 	first_itr = False
if __name__ == '__main__':
	iterate(sys.argv[1:])


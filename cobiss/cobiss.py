#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cobiss.py [LETO VRSTA UDK]

"""

import sys, os, re, subprocess

import requests
import bs4
from slugify import slugify

# http://cobiss4.izum.si/scripts/cobiss?ukaz=SFRM&mode=5&id=1504303287585446
# http://home.izum.si/cobiss/obvestila_novosti/dokumenti/Dodatek_G.pdf

URL_REQ = 'http://www.cobiss.si/scripts/cobiss'
URL_SEARCH = 'http://cobiss4.izum.si/scripts/cobiss?ukaz=SFRM&mode=5&id={}'

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

LETOs = [
	1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015
]

UDKs = ['001', '001', '002', '003', '004', '005', '006', '007', '008', '01', '015', '016', '02', '022', '023', '026', '027', '028', '030', '050', '06', '061', '069', '070', '09', '091', '093', '097', '1', '1', '1', '10', '11', '11', '11', '12', '13', '133', '14', '14', '14', '141', '15', '16', '16', '165', '17', '17', '18', '19', '2', '2', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '2008', '21', '22', '23', '23', '24', '24', '25', '255', '257', '258', '259', '26', '27', '271', '272', '28', '29', '3', '3', '303', '304', '305', '305', '308', '311', '314', '316', '32', '321', '322', '323', '324', '325', '326', '327', '328', '329', '33', '330', '331', '332', '334', '336', '338', '339', '34', '341', '342', '343', '344', '346', '347', '348', '349', '35', '351', '352', '353', '354', '36', '364', '366', '368', '37', '371', '373', '374', '376', '377', '378', '39', '391', '392', '393', '393', '394', '394', '395', '396', '397', '398', '4', '5', '5', '502', '504', '51', '510', '511', '512', '514', '517', '52', '520', '521', '523', '524', '524', '528', '53', '531', '532', '533', '534', '535', '536', '536', '537', '539', '54', '542', '543', '544', '546', '547', '55', '552', '553', '556', '56', '57', '572', '574', '575', '576', '577', '578', '579', '58', '581', '582', '59', '591', '6', '60', '602', '604', '608', '61', '611', '612', '613', '614', '615', '616', '617', '618', '62', '621', '622', '623', '624', '625', '628', '629', '63', '630', '631', '632', '633', '635', '636', '637', '638', '639', '64', '640', '641', '654', '655', '656', '657', '658', '659', '66', '661', '662', '663', '664', '665', '666', '667', '669', '674', '675', '676', '677', '678', '681', '684', '687', '69', '69', '691', '691', '692', '692', '693', '694', '696', '697', '7', '7', '71', '71', '712', '719', '719', '719', '72', '72', '725', '726', '727', '728', '73', '730', '737', '74', '744', '746', '747', '75', '76', '766', '77', '778', '78', '781', '782', '782', '783', '783', '784', '784', '785', '785', '791', '792', '797', '798', '798', '799', '799', '8', '80', '808', '81', '811', '82', '821', '9', '902', '908', '91', '911', '912', '913', '929', '930']

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

def extract(sid, leto, vrsta, udk):
	print 'Extracting links for', leto, vrsta, udk
	resp = requests.post(URL_SEARCH.format(sid), data={
		'ukaz': 'SEAR',
		'ID': sid,
		'keysbm': '',
		'PF1': 'PY',
		'SS1': leto,
		'OP1': 'AND',
		'PF2': 'CC',
		'SS2': vrsta,
		'OP2': 'AND',
		'PF3': 'UC',
		'SS3': '"' + udk + '"',
		'OP3': 'AND',
		'PF4': 'KW',
		'SS4': '',
		'lan': 'slv',
		'mat': '51',
		'eac': '1',
		'find': 'isci',	
	})
	soup = bs4.BeautifulSoup(resp.content.decode('utf-8'))
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
		print thesis
	if not content_found:
		sid = get_id()
		print 'Retry', leto, vrsta, udk, 'with sid', sid
		extract(sid, leto, vrsta, udk)
	else:
		return get_id(soup)

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
			return item['value']
	return None
	

def iterate(args):
	first_itr = True
	leto, vrsta, udk = 0, 0, 0
	if args:
		leto, vrsta, udk = LETOs.index(int(args[0])), VRSTAs.index(args[1]), UDKs.index(args[2])
	sid = get_id()
	for l in LETOs[leto:]:
		for v in first_itr and VRSTAs[vrsta:] or VRSTAs:
			for u in first_itr and UDKs[udk:] or UDKs:
				sid = extract(sid, l, v, u)
				print sid
				first_itr = False
if __name__ == '__main__':
	iterate(sys.argv[1:])


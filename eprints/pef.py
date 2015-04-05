import sys

import eprints

URL_BASE = 'http://pefprints.pef.uni-lj.si/'
YEARS = range(2000, 2016)
DL_DIR = './docs/'

			
if __name__ == '__main__':
	start = YEARS.index(int(sys.argv[-1]) if len(sys.argv) > 1 else YEARS[0])
	for year in YEARS[start:]:
		print ('Scraping year', year)
		for thesis_url in eprints.get_url_list(year, URL_BASE):
			try:
				eprints.extract(thesis_url, 'PEF', 'UL, Pedagoska fakulteta')
			except:
				raise


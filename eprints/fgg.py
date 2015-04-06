import sys

import eprints2 as eprints

URL_BASE = 'http://drugg.fgg.uni-lj.si/'
YEARS = range(1990, 2016)
DL_DIR = './docs/'

			
if __name__ == '__main__':
	start = YEARS.index(int(sys.argv[-1]) if len(sys.argv) > 1 else YEARS[0])
	for year in YEARS[start:]:
		print ('Scraping year', year)
		for thesis_url in eprints.get_url_list(year, URL_BASE):
			try:
				eprints.extract(thesis_url, 'FGG', 'UL, Fakulteta za gradbenistvo in geodezijo')
			except:
				print ('Url faild, fix manually: ', thesis_url)
				pass # continue if there are errors


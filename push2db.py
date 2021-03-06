#!/usr/bin/env python2
"""push2db.py

Usage:
	./push2db.py DOC_PATH SOURCE URL AUTHOR TITLE YEAR SCHOOL [META]

Example:
	./push2db.py something.pdf FRI www 'Someone' 'Something' 2015 'Faculty of Computer and Information Science'

Meta information is read from stdin because it can contain just about anything.
    
"""
import sys
import os

import MySQLdb as mdb
import settings

SQL_INSERT = u"INSERT INTO docDB (url, avtor, naslov, leto, fakulteta, data, filename) VALUES (%s, %s, %s, %s, %s, %s, '');"
SQL_UPDATE_FILENAME = u"UPDATE docDB SET filename=%s WHERE id = %s;"
SQL_EXISTS = u"SELECT * FROM docDB WHERE url = %s;"

def push(path, source, *fields):
	conn = mdb.connect(settings.DB_HOST, settings.DB_USER,
					   settings.DB_PASS, settings.DB_DATABASE,
					   charset='utf8')
	with conn:
		cur = conn.cursor()

		cur.execute(SQL_EXISTS, (fields[0], ))
		if len(cur.fetchall()):
			os.remove(path)
			return
		
		cur.execute(SQL_INSERT, fields)
		doc_id = cur.lastrowid
		filename = '{}.{}'.format(doc_id, path.split('.')[-1])
		new_path = os.path.join(settings.DOC_PATH, source, filename)
		try:
			os.rename(path, new_path)
			cur.execute(SQL_UPDATE_FILENAME, (new_path, doc_id))
		except:
			print path, '->', new_path
			raise
	

if __name__ == '__main__':
	print sys.argv
	filename, source, url, author, title, year, school = sys.argv[1:8]
	meta = '{}'
	if len(sys.argv) > 8:
		meta = sys.argv[8]
	push(os.path.expanduser(filename), source, url, author.decode('utf-8'), title.decode('utf-8'), year, school.decode('utf-8'), meta)

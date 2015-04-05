#!/usr/bin/env python2
"""push2db.py

Usage:
	./push2db.py DOC_PATH SOURCE URL AUTHOR TITLE YEAR SCHOOL [META]

Meta information is read from stdin because it can contain just about anything.
    
"""
import sys
import os

import MySQLdb as mdb

import settings

SQL_INSERT = "INSERT INTO docDB (url, avtor, naslov, leto, fakulteta, data, filename) VALUES (%s, %s, %s, %s, %s, %s, '');"
SQL_UPDATE_FILENAME = "UPDATE docDB SET filename=%s WHERE id = %s;"

def push(path, source, *fields):
	conn = mdb.connect(settings.DB_HOST, settings.DB_USER, settings.DB_PASS, settings.DB_DATABASE)
	with conn:
		cur = conn.cursor()
		cur.execute(SQL_INSERT, fields)
		doc_id = cur.lastrowid
		filename = '{}.{}'.format(doc_id, path.split('.')[-1])
		os.rename(path, os.path.join(settings.DOC_PATH, source, filename))
		cur.execute(SQL_UPDATE_FILENAME, (filename, doc_id))
	

if __name__ == '__main__':
	print sys.argv
	filename, source, url, author, title, year, school = sys.argv[1:8]
	meta = '{}'
	if len(sys.argv) > 8:
		meta = sys.argv[8]
	push(os.path.expanduser(filename), source, url, author, title, year, school, meta)

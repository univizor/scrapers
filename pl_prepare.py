#!/usr/bin/env python2
"""prepare.py

Usage:
	cat list.txt | ./prepare.py DOC_DIR SOURCE ALT_SCHOOL

Example:
	cat docs/dkum.list | ./pl_prepare.py docs/ dkum "Fakulteta za naravoslovje in matematiko" 

Script fixes file extensions and pushes files with meta to docDB
"""
import sys
import subprocess
import os
import re

EXTs = {
	'application/pdf': 'pdf',
	'application/msword': 'doc',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
}

CMD_MIME = "fl=`file -bi %s | egrep -o '.*;'`; echo ${fl::-1}"
DOC_DIR = sys.argv[1]

def get_file(fname):
	p = subprocess.Popen(CMD_MIME % (fname, ), shell=True, executable='/bin/bash', stdout=subprocess.PIPE)
	mimetype = p.stdout.read().strip()
	p.communicate()
	if p.returncode > 0:
		return None
	return EXTs.get(mimetype)
	
def push(filename, source, url, author, title, year, school):
	command = u'./push2db.py "{}" "{}" "{}" "{}" "{}" "{}" "{}"'.format(
		filename,
		source,
		url,
		author,
		title,
		year,
		school
	)
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	out = p.stdout.read()
	p.communicate()
	if p.returncode > 0:
		print out

if __name__ == '__main__':
	source = sys.argv[2]
	alt_school = sys.argv[3] # 'Fakulteta za naravoslovje in matematiko'
	for line in sys.stdin.readlines():
		segments = line.decode('utf-8').strip().split('\t')
		if len(segments) == 5:
			title, author, year, url, filename = segments
			school = alt_school
		elif len(segments) == 9:
			thesis_type, _, school, title, _, author, year, url, filename = segments
		else:
			thesis_type, _, school, title, author, year, url, filename = segments
		school = 'UM, ' + school

		filename = os.path.join(DOC_DIR, filename)
		if not os.path.exists(filename):
			continue
		ext = get_file(filename)
		if not ext:
			continue
		new_filename = re.sub('\w+$', ext, filename)
		if filename != new_filename:
			os.rename(filename, new_filename)
			filename = new_filename
		push(filename, source, url, author, title, year, school)

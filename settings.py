import os

# export DB_HOST='localhost'; export DB_USER='dev'; export DB_PASS='dev'; export DB_NAME='univizor'; export DOC_PATH='./docs/'; 

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_DATABASE = os.environ['DB_NAME']

DOC_PATH = os.environ.get('DOC_PATH') or '/mnt/univizor/download/'

# Univizor Scrapers

[List of all entities (Google Document)](https://docs.google.com/spreadsheets/d/1LdW-V_vTOMh38zqivm0EAIiUXhTjtd6kKb3iXUDRyto/edit#gid=0)

# Installation

## How to run scraper?

1. ... write here dude!

## Database

Dumping latest structure on production.

    mysqldump -d -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > $DB_NAME.sql

Loading database localy.

    mysql -h <host> -u <username> -p < univizor.sql

## Python

    mkvirtualenv --no-site-packages univizor
    workon univizor
    pip install --upgrade -r requirements.txt

# Pipeline

## Output
PDF file

> This repository is deprecated. Working on rewrite,... - Oto

# Univizor Scrapers

[List of all entities (Google Document)](https://docs.google.com/spreadsheets/d/1LdW-V_vTOMh38zqivm0EAIiUXhTjtd6kKb3iXUDRyto/edit#gid=0)

# Installation

## How to run scraper?

| Scraper       | Command                                        
|---------------|------------------------------------------------
| [vsvo](vsvo/) | `cd vsvo; ruby vsvo.rb > ./vsvo.log 2>&1`      
| [ung](ung/)   | `cd ung; ruby ung-library.rb > ./ung.log 2>&1` 
| [gea](gea/)   | `cd gea; ruby gea-college.rb > ./gea.log 2>&1` 

(*) gea: set REDOWNLOAD=true in gea-college.rb to fetch again

## Database

Dumping latest structure on production.

    mysqldump -d -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME \
    --skip-comments --skip-add-drop-table > $DB_NAME.sql

Loading database localy.

    mysql -h <host> -u <username> -p < univizor.sql

## Python

    mkvirtualenv --no-site-packages univizor
    workon univizor
    pip install --upgrade -r requirements.txt

# Pipeline

## Output
PDF file

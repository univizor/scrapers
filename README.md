# Univizor Scrapers

[List of all entities (Google Document)](https://docs.google.com/spreadsheets/d/1LdW-V_vTOMh38zqivm0EAIiUXhTjtd6kKb3iXUDRyto/edit#gid=0)

| Entity      | Language | Owner      |
|-------------|----------|------------|
| [up](up/)   | Perl     | @igzebedze |
| [mb](mb/)   | Perl     | @igzebedze |
| [ung](ung/) | Perl     | @igzebedze |

# Installation

## Python

    mkvirtualenv --no-site-packages univizor
    workon univizor
    pip install --upgrade -r requirements.txt

# Pipeline

## Output
1. PDF file
2. JSON file with meta information: **author**, **title**, **keywords**, **year**, **university/faculty/school**, **url**

#!/bin/bash

four_days_ago=$(date -d "4 days ago" +"%Y-%m-%d") 
one_day_ago=$(date -d "1 days ago" +"%Y-%m-%d") 

/home/malte/repos/wikidiary/bin/wiki_pipeline.sh $four_days_ago
/home/malte/repos/wikidiary/bin/wiki_pipeline.sh $one_day_ago

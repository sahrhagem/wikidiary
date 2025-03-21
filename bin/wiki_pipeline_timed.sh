#!/bin/bash

three_days_ago=$(date -d "3 days ago" +"%Y-%m-%d") 

/home/malte/repos/wikidiary/bin/wiki_pipeline.sh $three_days_ago

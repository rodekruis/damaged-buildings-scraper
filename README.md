# damaged-buildings-scraper

Start with district_scraper.py. It takes the provinces.csv (output of https://hasartespit.csb.gov.tr/query/cities transformed to csv) and queries all the district codes and then writes them to districts.csv.

Then run neighborhood_scraper.py. It takes districts.csv, queries the neighborhood codes and writes them to neighborhoods.csv.

Then the real scraping starts with scraper.py. It takes neighborhoods.csv and scrapes all data for one province. Set the province by changing the index of ilIds on line 11 (should be below 21 atm as there are 21 provinces partly assessed currently).

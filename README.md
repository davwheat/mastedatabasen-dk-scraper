# Mastedatabasen.dk scraper

Simple Python tool to scrape Mastedatabasen.dk of all antenna locations across the country, along with their associated operators.

## What's Mastedatabasen.dk

Mastedatabasen.dk is the official database of existing and planned antenna positions in Denmark and was established to create greater transparency with the placement of antennas across the country.

[Learn more (Danish only)](https://mastedatabasen.dk/viskort/ContentPages/About.aspx)

## Usage

### Install pip requirements

```
pip install -r requirements.txt
```

### Run scraper

This will automatically begin scraping Mastedatabasen.dk for all in-use sites across Denmark. This might take about 10 mins on fast connections due to server performance and paging limitations.

```
python ./scraper.py
```

### Run metadata fetcher

By default, for some reason, Mastedatabasen doesn't include operator info within API requests for multiple points. Instead, detailed info about every point must be requested separately, site-by-site.

With Mastedatabasen currently having approx. 50,000 sites, and an average of 1.5s per request, this can take upwards of 13 hours to complete.

The script will automatically read the output from the `scraper.py` script (`sites_current.json`) and load it into memory, then beginning to fetch operator info. When complete, it will output to `sites_current_with_operator.json`. It will also save to this file every 25 requests in case of network issues.

```
python ./metadata_fetcher.py
```

#### In case of errors...

Due to the autosave functionality, not much progress should be lost.

1. Make a backup of `sites_current.json`
2. Delete `sites_current.json`
3. Rename `sites_current_with_operator.json` to `sites_current.json`
4. Re-run `python ./metadata_fetcher.py`

The script should inform you that only X sites require operator info, while Y sites have been loaded into the script.

## License

The MIT license covers the all content within this repository, **except** any `json` files containing data from Mastedatabasen.dk. The content within these remain the copyright of the Danish Energy Agency (Energistyrelsen).

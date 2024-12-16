# Canyon County Parcel Scraper

## Introduction

Many counties in Idaho still do not offer an open data portal with address information. In many cases this is not due to technological limitations, but a simple lack of desire to publish the data. However, I find this information invaluable for personal research. As such, I decided to build a scraper for the Canyon County Assessor's map.

This is equal parts a demonstration of my coding ability, a demonstration of my drive to solve real problems, and a protest against the closed nature of many municipal datasets with immense public utility.

A secondary motive is to detect data entry errors, which can be reported to county assessors.

## Functionality

This program scrapes parcel geometry from an ArcGIS server using its REST API and outputs it in GeoJSON format. It is designed to generate only address data, so it queries only the relevant columns; for Canyon County, these are `SiteAddress` and `SiteCity`. It then applies postprocessing to convert the addresses to a more readable format.

## Usage

This is a proof-of-concept at the moment, so no usage support will be provided. Currently, the script is run with a single, unnamed argument specifying the minimum number of parcels to try to scrape.

## Requirements

The scraper uses [**Requests**](https://docs.python-requests.org/en/latest/index.html) to get paginated parcel features and [**Shapely**](https://shapely.readthedocs.io/en/stable/manual.html) to get centroids from geometry.

## To dos

There is a huge number of edge cases yet to be handled. Some cases are so close to the edge that they're probably not even represented in this dataset. Below are the ones I've noticed looking at the output from scraping the entire parcel layer:

* Handle fractional addresses (currently interpreted as part of street name)
* Handle unit types (e.g., Suite, No, Unit, Trlr)
  * Currently, these are wrongly expanded as directionals as "Southte" and "Northo"
* Handle unit numbers represented as address suffixes (e.g., 398 A)
* Handle multiple highway numbers (e.g., Highway 20/26)
* Lowercase prepositions (e.g., "Of", "And") in street names.
* Handle sequential suffixes (e.g., 10th Ave Cir)
* Handle "Avenue X"-style names
* Handle infixes (e.g., Mtn)

My end goal is to develop a framework to scrape parcel address information from other county assessor sites in Idaho, which will necessitate additional considerations.

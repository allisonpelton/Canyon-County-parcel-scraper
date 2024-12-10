# Canyon County Parcel Scraper

## Introduction

Many counties in Idaho still do not offer an open data portal with address information. In many cases this is not due to technological limitations, but a simple lack of desire to publish the data. However, I find this information invaluable for personal research. As such, I decided to build a scraper for the Canyon County Assessor's map.

This is equal parts a demonstration of my coding ability, a demonstration of my drive to solve real problems, and a protest against the closed nature of many municipal datasets with immense public utility.

## Functionality

This program scrapes parcel geometry from an ArcGIS server using its REST API and outputs it in GeoJSON format. It is designed to generate only address data, so it queries only the relevant columns `SiteAddress` and `SiteCity`. It then applies postprocessing to convert the addresses to a more readable format.

## Requirements

The scraper uses [**Requests**](https://docs.python-requests.org/en/latest/index.html) to get paginated parcel features and [**Shapely**](https://shapely.readthedocs.io/en/stable/manual.html) to get centroids from geometry.

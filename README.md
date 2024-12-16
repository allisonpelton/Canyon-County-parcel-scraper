# Owyhee County Parcel Scraper

## Information

Idaho's largest county. Home to the most remote cabin in the lower 48, at 45 Ranch.

## Format

Parcel address info is provided in a single field, `Situs`. It comes in the format `{NUMBER} {STREET},( {UNIT},) {CITY} {ST}, {ZIP}`. A few parcels only have the number and street and a few others have two spaces between the state and ZIP code instead of a comma followed by a space.

## Issues

### Street grids

The numbered street grids of both Marsing and Homedale use directionals inconsistently. This is reflected in the variety of street name representations in the database. In Marsing, North–South avenues take both a pre and postdirectional (except for 9th Avenue), while East–West streets take only a postdirectional. In Homedale, all numbered streets (going North–South) take both a predirectional and postdirectional. Such addresses are few enough to not merit a programmatic fix, i.e., you will need to clean this up manually.

### Missing suffixes

A handful of roads are missing their "Road" suffix. This could be fixed in processing but there are few enough such addresses to merit doing so.

### Minor data entry errors

As per usual, there are a few dozen data entry errors that require manual correction. Some ZIP codes are wrong, some city names and street names are misspelled, etc.

### City name, postcodes

The city listed in the dataset is not always the approved postal city. Postal city and ZIP code should always match one of the following.

| City name | ZIP code |
| ---------- | -------- |
| Bruneau | 83604 |
| Buhl* | 83316 |
| Grand View | 83624 |
| Hammett | 83627 |
| Homedale | 83628 |
| Marsing | 83639 |
| Melba | 83641 |
| Owyhee, Nevada† | 89832 |
| Rogerson | 83302 |
| South Mountain† | 97910 |

\*Not present in the dataset due to missing fields

†ZIP code originates outside Idaho

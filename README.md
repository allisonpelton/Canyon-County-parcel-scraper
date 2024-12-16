# Boise County Parcel Scraper

## Information

Confusingly does not contain the City of Boise.

## Format

Address information is presented in two fields, `ANMPROPAD1` and `ANMPROPAD2`. `ANMPROPAD1` contains the address number and street name, and if applicable, the unit, while `ANMPROPAD=2` contains the city, state, and ZIP code (albeit in ZIP+4 format).

## Issues

### Data entry errors

The ZIP codes are a mess. In some areas, they're wrong more often than they're right.

### City name, postcodes

| City name | ZIP code |
| ---------- | -------- |
| Banks | 83602 |
| Boise | 83716 |
| Garden Valley | 83622 |
| Horseshoe Bend | 83629 |
| Idaho City | 83631 |
| Lowman | 83637 |
| Placerville | 83666 |
| Sweet | 83670 |

With the addition of Avimor Boise County Phase 1, there are now Eagle addresses as well. While Avimor is incorporated into Eagle, its postal addresses continue to be based in Boise 83714. As of December 2024, the USPS does not report these addresses, so the correct code and city cannot be determined.

### Poorly delineated unit info

There is no way to systematically disambiguate street name from unit due to the lack of a separator. Manual clean-up is required.

### Undocumented symbol usage

Some parcel addresses contain a lone plus sign after the road name. The meaning is unclear. They must be filtered out.
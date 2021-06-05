# UT Building Scraper
## Description
Web scrape UT buildings' information across all sites from [The University of Texas at Austin Facilities Services](https://utdirect.utexas.edu/apps/campus/buildings/nlogon/facilities/?_ga=2.227999700.871646062.1622874639-448752207.1598189041).

## Installation
Recommended installation is to install from GitHub using `pip` Version Control System installation within a virtual environment.
Follow these steps to create and activate a virtual environment, and install this package:
```
python -m venv env
source env/bin/activate
python -m pip install git+https://github.com/kingsleynweye/ut_building_scraper.git
```

## Usage
See the Command Line Interface help for instructions:
```
python -m ut_building_scraper -h
```

To get the data for in-code use or storage, make use of the `Scraper` class.
```python
from ut_building_scraper.scrape import Scrape

data = Scraper.building_information()
```

The result is a `pd.dataFrame` with `site_name`, `site_abbreviation`, `building_name`, `building_abbreviation`, `building_number`, `address`, `floors`, `gross_square_feet`, `occupied_since` and `building_image_urls` columns.
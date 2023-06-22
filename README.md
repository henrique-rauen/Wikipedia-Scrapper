# Wikipedia scraper
This project requests a list of world leaders from the API availble at https://country-leaders.onrender.com and scrap the first paragraph from their respective wikipedia entries.
## Installation
This program requires python 3.10.4. Included in this repository is a requirements.txt file which includes the requirements. In order to install them you can run ```python -m pip install requirements.txt``` Make sure to do so in a virtual environment to avoid conflicts. 
## Usage
Run ```leaders_scrapper.py```. The program will print in the terminal the leaders names and a short introduction. The full data will be written to a file called ```leaders.json``` according to the following pattern::
```py
{"us" : [
	{
	first_name: "George",
	"last_name: "Washington",
	"wikipedia_url": "https://www.wikipedia.com/Geor...",
	"short_introduction" : "George Washington was....",
	"start_mandate": "",
	"end_mandate" : "",
	"date_of_birth": "",
	"date_of_death": "",
	"id": ""
	},
	{
	first_name: "George",
	"last_name: "Washington",
	"wikipedia_url": "https://www.wikipedia.com/Geor...",
	"short_introduction" : "George Washington was....",
	"start_mandate": "",
	"end_mandate" : "",
	"date_of_birth": "",
	"date_of_death": "",
	"id": ""
	},
	...	
	]
"ru" : [
	...
	]
}```

## Made by Henrique Rauen
This program was done in ~11 hours as part of the junior data analyst course @ becode.
Jun 2023

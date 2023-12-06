
from playwright.sync_api import sync_playwright
import time
from sys import argv, exit, platform
from openai import OpenAI


import os
client=OpenAI()
quiet = False
if len(argv) >= 2:
	if argv[1] == '-q' or argv[1] == '--quiet':
		quiet = True
		print(
			"Running in quiet mode (HTML and other content hidden); \n"
			+ "exercise caution when running suggested commands."
		)
allprompts=[]

objective = "go to amazon, search for men's tshirt and click on the first result. Click on Add to cart."

convcontext="""
Convert the given paragraph into stepwise instructions seperated by commas. Each instruction should be indivisible into smaller instructions. Here are some examples:
============================
EXAMPLE 1:
PARA="Go to amazon then search for men's tshirt and click on the first result. Click on Add to cart."
RESPONSE="Go to amazon, search for men's tshirt, click on the first result, click on add to cart"
============================
============================
EXAMPLE 2:
PARA="Go to Google. Type “chocolate chip cookie recipe” into the search bar.
Press Enter or click the search icon.
Scroll down and click on a recipe that looks appealing.
Follow the instructions on the website for the recipe."
RESPONSE="Go to Google, type “chocolate chip cookie recipe” into the search bar, press Enter or click the search icon, Scroll down, click on a recipe that looks appealing, follow the instructions on the website for the recipe"
============================
============================
EXAMPLE 3:
PARA="
Go to a news website like BBC News or CNN.
Scroll through the homepage to find headlines that interest you.
Click on a news article to read it.
Navigate back to the homepage, then choose another article or exit the site."
RESPONSE="Go to a news website like BBC News or CNN, scroll through the homepage to find headlines that interest you, click on a news article to read it, navigate back to the homepage, choose another article or exit the site"
============================
============================
EXAMPLE 4:
PARA="Visit an online bookstore like Amazon or Barnes & Noble.
Use the search bar to type the name of the book you’re looking for.
Press Enter or click the search icon.
Browse through the search results and click on the book you are interested in.
Read the book description, reviews, and pricing information provided."
RESPONSE="Visit an online bookstore like Amazon or Barnes & Noble, use the search bar to type the name of the book you’re looking for, press Enter or click the search icon, browse through the search results, click on the book you are interested in, read the book description, reviews, and pricing information provided"
============================
============================
EXAMPLE 5:
PARA="Visit a weather forecasting website like weather.com or AccuWeather.
Enter your city or ZIP code into the search bar on the site.
Press Enter or click the search/magnifying glass icon.
View the weather forecast displayed for your area."
RESPONSE="Visit a weather forecasting website like weather.com or AccuWeather, enter your city or ZIP code into the search bar, press Enter or click the search/magnifying glass icon, view the weather forecast displayed for your area"
============================


Now, convert the given paragraph into stepwise instructions by completing the text:
PARA="$para1"
RESPONSE=
	"""
convcontext=convcontext.replace("$para1",objective)
cmdintermediate = client.chat.completions.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": convcontext}])

print(cmdintermediate)
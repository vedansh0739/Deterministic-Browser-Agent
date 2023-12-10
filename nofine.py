#!/usr/bin/env python3
#
# natbot.py
#
# Set OPENAI_API_KEY to your API key, and then run this from a terminal.
#
from crawler import Crawler
from playwright.sync_api import sync_playwright
import time
from sys import argv, exit, platform
from openai import OpenAI

import re
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



allprompts.append("""
You are an agent controlling a browser. You are given:

	(1) an objective that you are trying to achieve
	(2) the URL of your current web page
	(3) a simplified text description of what's visible in the browser window (more on that below)

You can issue these commands:
	SCROLL UP - scroll up one page
	SCROLL DOWN - scroll down one page
	CLICK X - click on a given element. You can only click on links, buttons, and inputs!
	TYPE X "TEXT" - type the specified text into the input with id X
	TYPESUBMIT X "TEXT" - same as TYPE above, except then it presses ENTER to submit the form

The format of the browser content is highly simplified; all formatting elements are stripped.
Interactive elements such as links, inputs, buttons are represented like this:

		<link id=1>text</link>
		<button id=2>text</button>
		<input id=3>text</input>

Images are rendered as their alt text like this:

		<img id=4 alt=""/>

Based on your given objective, issue whatever command you believe will get you closest to achieving your goal.

Don't try to interact with elements that you can't see.

The following part of the prompt along with the following three prompts consists of examples. Starting from after the next three prompts you are supposed to reply with the appropriate commands:

EXAMPLE 1:
==================================================
CURRENT BROWSER CONTENT:
------------------
<link id=1>About</link>
<link id=2>Store</link>
<link id=3>Gmail</link>
<link id=4>Images</link>
<link id=5>(Google apps)</link>
<link id=6>Sign in</link>
<img id=7 alt="(Google)"/>
<textarea id=8 alt="Search"></textarea>
<button id=9>(Search by voice)</button>
<button id=10>(Google Search)</button>
<button id=11>(I'm Feeling Lucky)</button>
<link id=12>Advertising</link>
<link id=13>Business</link>
<link id=14>How Search works</link>
<link id=15>Carbon neutral since 2007</link>
<link id=16>Privacy</link>
<link id=17>Terms</link>
<text id=18>Settings</text>
------------------
OBJECTIVE: Search Amazon
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "Amazon"
==================================================

""")
allprompts.append("""
EXAMPLE 2:
==================================================
CURRENT BROWSER CONTENT:
------------------
<link id=1>Skip to main content</link>
<link id=2>Turn off continuous scrolling</link>
<link id=3>Accessibility help</link>
<link id=4>Accessibility feedback</link>
<link id=5 title="Go to Google Home" alt="Google"/>
<textarea id=6 search Search/>
<button id=7 Clear/>
<button id=8 Search by voice/>
<button id=9 Search by image/>
<button id=10 aria-label="Search"/>
<link id=12 aria-label="Google apps"/>
<link id=13 aria-label="Sign in">Sign in</link>
<link id=16>Shopping</link>
<link id=17>News</link>
<link id=18>Books</link>
<link id=19>Images</link>
<link id=27>Shop online at Amazon India - Great deals on Amazon Amazon.in https://www.amazon.in</link>
<img id=28/>
<img id=31/>
<link id=38>Mobiles & Accessories</link>
<link id=40>Home & Kitchen</link>
<link id=42>Electronics & accessories</link>
<link id=44>Deals on Fashion & beauty</link>
<link id=48>Amazon.in Amazon.in https://www.amazon.in</link>
<link id=53>Women's fashion</link>
<link id=56>Home & Kitchen</link>
<link id=58>Great Indian Festival 2023</link>
<link id=60>Mobile Phones</link>
<link id=62>More results from amazon.in »</link>
<button id=64 Share/>
<link id=67 aria-label="Images search for Amazon.com"/>
<link id=68>amazon.in</link>
<link id=71>Wikipedia</link>
<link id=72>CEO</link>
<link id=74>Andy Jassy</link>
<link id=76>Trending</link>
<link id=77>Stock price</link>
<link id=79>AMZN</link>
<link id=84>Disclaimer</link>
<link id=85>Founder</link>
<link id=87>Jeff Bezos</link>
<link id=88>President</link>
<link id=90>Andy Jassy</link>
<link id=91>Founded</link>
<link id=94>Bellevue, Washington, United States</link>
<link id=95>CFO</link>
<link id=97>Brian T. Olsavsky</link>
<link id=98>Mascot</link>
<link id=100>Peccy</link>
<link id=101>Subsidiaries</link>
<link id=103>Audible</link>
<link id=105>Amazon India</link>
<link id=107>Amazon Web Services</link>
<link id=109>MORE</link>
<link id=110>Disclaimer</link>
<link id=112>LinkedIn</link>
<link id=113>Instagram</link>
<link id=114>Facebook</link>
<link id=115>Twitter</link>
<link id=116>People also search for</link>
<link id=117>View 10+ more</link>
<link id=118 aria-label="Rakuten" title="Rakuten" alt="Rakuten"/>
<link id=119 aria-label="eBay" title="eBay" alt="eBay"/>
<link id=120 aria-label="SHEIN" title="SHEIN" alt="SHEIN"/>
<link id=121 aria-label="Zalando" title="Zalando" alt="Zalando"/>
------------------
OBJECTIVE: Click on the link to the Amazon website 
CURRENT URL: https://www.google.com/search?q=amazon&sca
YOUR COMMAND: 
CLICK 27
==================================================
""")
allprompts.append("""
EXAMPLE 3:
==================================================
CURRENT BROWSER CONTENT:
------------------

------------------
OBJECTIVE: Search for men's tshirts
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "Amazon"
==================================================
""")
allprompts.append("""
EXAMPLE 4:
==================================================
CURRENT BROWSER CONTENT:
------------------

------------------
OBJECTIVE: Search Amazon
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "Amazon"
==================================================
""")


prompt_template="""
The current browser content, objective, and current URL follow. Reply with your next command to the browser.

CURRENT BROWSER CONTENT:
------------------
$browser_content
------------------

OBJECTIVE: $objective
CURRENT URL: $url
YOUR COMMAND:
"""

black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "script", "style", "path", "svg", "br", "::marker",])



if (
	__name__ == "__main__"
):
	
	

	def print_help():
		print(
			"(g) to visit url\n(u) scroll up\n(d) scroll down\n(c) to click\n(t) to type\n" +
			"(h) to view commands again\n(r/enter) to run suggested command\n(o) change objective"
		)

	def get_gpt_command(objective, url, previous_command, browser_content):
		prompt = prompt_template
		prompt = prompt.replace("$objective", objective)
		prompt = prompt.replace("$url", url)

		prompt = prompt.replace("$browser_content", browser_content)
		response = client.chat.completions.create(model="gpt-3.5-turbo-16k",messages=[{"role": "user", "content": prompt}])
		return response.choices[0].message.content

	def run_cmd(cmd):
		cmd = cmd.split("\n")[0]

		if cmd.startswith("SCROLL UP"):
			_crawler.scroll("up")
		elif cmd.startswith("SCROLL DOWN"):
			_crawler.scroll("down")
		elif cmd.startswith("CLICK"):
			commasplit = cmd.split(",")
			id = commasplit[0].split(" ")[1]
			_crawler.click(id)
		elif cmd.startswith("TYPE"):
			spacesplit = cmd.split(" ")
			id = spacesplit[1]
			text = spacesplit[2:]
			text = " ".join(text)
			# Strip leading and trailing double quotes
			text = text[1:-1]

			if cmd.startswith("TYPESUBMIT"):
				text += '\n'
			_crawler.type(id, text)

		time.sleep(2)

	objective = "go to amazon, click on the amazon link, search for men's tshirt and click on the first result. Click on Add to cart."
	print("\nWelcome to natbot! What is your objective?")
	i = input()
	if len(i) > 0:
		objective = i

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
	
	cmdintermediate = client.chat.completions.create(
	    model="gpt-3.5-turbo-1106",
	    messages=[{"role": "user", "content": convcontext}],
	    temperature=0,
		seed=12345,
	    frequency_penalty=-2.0,
	    presence_penalty=-2.0
	)

	cmdarray = cmdintermediate.choices[0].message.content.split(',')
	
	#loop to feed context
	for currprompt in allprompts:
		garbageresponse=client.chat.completions.create(
	    model="gpt-3.5-turbo-1106",
	    messages=[{"role": "user", "content": currprompt}],
	    temperature=0,
		seed=12345,
	    frequency_penalty=-2.0,
	    presence_penalty=-2.0
	)
		print(f"{garbageresponse}")# temperature=0,frequency_penalty=-2.0, presence_penalty=-2.0,  don't alter top_p
	
	
 
 
	_crawler = Crawler()
	gpt_cmd = ""
	prev_cmd = ""
	_crawler.go_to_page("google.com")
	try:
		for currcmd in cmdarray:#individual steps fed into gpt with each iteration
			browser_content = _crawler.crawl()
			
   
   
			url1=_crawler.page.url[:50]
			prev_cmd = gpt_cmd
			gpt_cmd = get_gpt_command(currcmd, url1, prev_cmd, browser_content)
			gpt_cmd = gpt_cmd.strip()

			if not quiet:
				print("URL: " + url1)
				print("Objective: " + objective)
				print("----------------\n" + browser_content + "\n----------------\n")
			if len(gpt_cmd) > 0:
				print("Suggested command: " + gpt_cmd)


			command = input()
			if command == "r" or command == "":
				run_cmd(gpt_cmd)
			elif command == "g":
				url = input("URL:")
				_crawler.go_to_page(url)
			elif command == "u":
				_crawler.scroll("up")
				time.sleep(1)
			elif command == "d":
				_crawler.scroll("down")
				time.sleep(1)
			elif command == "c":
				id = input("id:")
				_crawler.click(id)
				time.sleep(1)
			elif command == "t":
				id = input("id:")
				text = input("text:")
				_crawler.type(id, text)
				time.sleep(1)
			elif command == "o":
				objective = input("Objective:")
			else:
				print_help()
	except KeyboardInterrupt:
		print("\n[!] Ctrl+C detected, exiting gracefully.")
		exit(0)
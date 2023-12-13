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
sysmes="""
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
DOWNLOAD - download the webpage

The format of the browser content is highly simplified; all formatting elements are stripped.
Interactive elements such as links, inputs, buttons are represented like this:

    <link id=1>text</link>
    <button id=2>text</button>
    <input id=3>text</input>

Images are rendered as their alt text like this:

    <img id=4 alt=""/>

Based on your given objective, issue whatever command you believe will get you closest to achieving your goal.

Don't try to interact with elements that you can't see.

     """
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

usermes="""
The current browser content, objective, and current URL follow. Reply with your next command to the browser.

CURRENT BROWSER CONTENT:
------------------
$browser_content
------------------

OBJECTIVE: $objective
CURRENT URL: $url
YOUR COMMAND:"""

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
		prompt=usermes
		prompt = prompt.replace("$objective", objective)
		prompt = prompt.replace("$url", url)
		prompt = prompt.replace("$browser_content", browser_content)
  
	
		response = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-1106:personal::8V3JKQCi",
  messages=[
    {"role": "system", "content":sysmes },
    {"role": "user", "content": prompt}
  ],
	temperature=0.2,
	seed=12345,
	frequency_penalty=-1.0,
	presence_penalty=-1.0
  
)
		return response.choices[0].message.content

	def run_cmd(cmd):
		cmd = cmd.split("\n")[0]

		if cmd.startswith("SCROLL UP"):
			_crawler.scroll("up")
		elif cmd.startswith("SCROLL DOWN"):
			_crawler.scroll("down")
		elif cmd.startswith("DOWNLOAD"):
			_crawler.download()
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

	objective = "type codecademy in the search box, click search, click on the link that leads to codecademy.com, then click on catalog, then python, then click on cheatsheets, then click on build a machine learning model with Python, then print the cheatsheet"
	print("\nPlease state all steps that you want the automated browser to perform. All steps should be indivisible into smaller steps, so don't miss a single step:\n")
	i = input()
	if len(i) > 0:
		objective = i

	convcontext="""
Convert the given paragraph into stepwise instructions seperated by two semicolons ;;. Each instruction should be indivisible into smaller instructions. Here are some examples:
============================
EXAMPLE 1:
PARA="Go to amazon then search for men's tshirt and click on the first result. Click on Add to cart."
RESPONSE="Go to amazon;; search for men's tshirt;; click on the first result;; click on add to cart"
============================
============================
EXAMPLE 2:
PARA="Go to Google. Type “chocolate chip cookie recipe” into the search bar.
Press Enter or click the search icon.
Scroll down and click on a recipe that looks appealing.
Follow the instructions on the website for the recipe."
RESPONSE="Go to Google;; type “chocolate chip cookie recipe” into the search bar;; press Enter or click the search icon;; Scroll down;; click on a recipe that looks appealing;; follow the instructions on the website for the recipe"
============================
============================
EXAMPLE 3:
PARA="
Go to a news website like BBC News or CNN.
Scroll through the homepage to find headlines that interest you.
Click on a news article to read it.
Navigate back to the homepage, then choose another article or exit the site."
RESPONSE="Go to a news website like BBC News or CNN;; scroll through the homepage to find headlines that interest you;; click on a news article to read it;; navigate back to the homepage;; choose another article or exit the site"
============================
============================
EXAMPLE 4:
PARA="Visit an online bookstore like Amazon or Barnes & Noble.
Use the search bar to type the name of the book you’re looking for.
Press Enter or click the search icon.
Browse through the search results and click on the book you are interested in.
Read the book description, reviews, and pricing information provided."
RESPONSE="Visit an online bookstore like Amazon or Barnes & Noble;; use the search bar to type the name of the book you’re looking for;; press Enter or click the search icon;; browse through the search results;; click on the book you are interested in;; read the book description;; reviews;; and pricing information provided"
============================
============================
EXAMPLE 5:
PARA="Visit a weather forecasting website like weather.com or AccuWeather.
Enter your city or ZIP code into the search bar on the site.
Press Enter or click the search/magnifying glass icon.
View the weather forecast displayed for your area."
RESPONSE="Visit a weather forecasting website like weather.com or AccuWeather;; enter your city or ZIP code into the search bar;; press Enter or click the search/magnifying glass icon;; view the weather forecast displayed for your area"
============================


Now, convert the given paragraph into stepwise instructions by completing the text:
PARA="$para1"
RESPONSE=
	"""
	convcontext=convcontext.replace("$para1",objective)
	
	cmdintermediate = client.chat.completions.create(
	    model="gpt-3.5-turbo-1106",
	    messages=[{"role": "user", "content": convcontext}],
	    temperature=0.2,
		seed=12345,
	    frequency_penalty=-1.0,
	    presence_penalty=-1.0
	)

	cmdarray = cmdintermediate.choices[0].message.content.split(';;')
	
	print(cmdarray)
	
 
 
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


			print("URL: " + url1)
			print("Current Command: " + currcmd)
			if len(gpt_cmd) > 0:
				print("Suggested command: " + gpt_cmd)
			print("----------------\n" + browser_content + "\n----------------\n")
			


			command = ""
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
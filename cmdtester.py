# QUICKLY GET A DOM SNAPSHOT OF ANY URL AND DISPLAY IT, THAT'S IT
# !/usr/bin/env python3
#
# natbot.py
#
# Set OPENAI_API_KEY to your API key, and then run this from a terminal.
#
import sys
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



black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "script", "style", "path", "svg", "br", "::marker",])


if (
	__name__ == "__main__"
):
	_crawler = Crawler()
	

	def print_help():
		print(
			"(g) to visit url\n(u) scroll up\n(d) scroll down\n(c) to click\n(t) to type\n" +
			"(h) to view commands again\n(r/enter) to run suggested command\n(o) change objective"
		)

	

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
	print("\nWelcome to cmdtester!")


	
	
	
	
	
	gpt_cmd = ""
	prev_cmd = ""
	_crawler.go_to_page("wsj.com")
	while True:
		try:

			browser_content = _crawler.crawl()


	# Replace matched patterns with an empty string

			url1=_crawler.page.url[:50]
			prev_cmd = gpt_cmd
			print("URL: " + url1)
			print("Objective: " + objective)
			print("----------------\n" + browser_content + "\n----------------\n")
			if len(gpt_cmd) > 0:
				print("Suggested command: " + gpt_cmd)
				
		

			print('enter a char:')
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
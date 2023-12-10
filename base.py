# THE SECOND ONE WHERE WE TRIED TO SPLIT THE PROMPT
# 
# !/usr/bin/env python3
#
# natbot.py
#
# Set OPENAI_API_KEY to your API key, and then run this from a terminal.
#
import re

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
prompt_template=[None] * 5
prompt_template[0] = """
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
You always start on Google; you should submit a search query to Google that will take you to the best page for
achieving your objective. And then interact with that page to achieve your objective.

If you find yourself on Google and there are no search results displayed yet, you should probably issue a command 
like "TYPESUBMIT 7 "search query"" to get to a more useful page.

Then, if you find yourself on a Google search results page, you might issue the command "CLICK 24" to click
on the first link in the search results. (If your previous command was a TYPESUBMIT your next command should
probably be a CLICK.)

Once you are on the restaurant web page, scroll down to get a better view. Then issue the necessary commands.

Don't try to interact with elements that you can't see.

The following part of this prompt and the next prompt need to be taken into consideration as they consist of the necessary 4 Examples that will be required for decision making.
Here are the Examples:

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
OBJECTIVE: Find a 2 bedroom house for sale in Anchorage AK for under $750k
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "anchorage redfin"
==================================================

EXAMPLE 2:
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
OBJECTIVE: Make a reservation for 4 at Dorsia at 8pm
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "dorsia nyc opentable"
=================================================="""

prompt_template[1]="""EXAMPLE 3:
==================================================
CURRENT BROWSER CONTENT:
------------------
<button id=1>For Businesses</button>
<button id=2>Mobile</button>
<button id=3>Help</button>
<button id=4 alt="Language Picker">EN</button>
<link id=5>OpenTable logo</link>
<button id=6 alt ="search">Search</button>
<text id=7>Find your table for any occasion</text>
<button id=8>(Date selector)</button>
<text id=9>Sep 28, 2022</text>
<text id=10>7:00 PM</text>
<text id=11>2 people</text>
<textarea id=12 alt="Location, Restaurant, or Cuisine"></textarea> 
<button id=13>Let’s go</button>
<text id=14>It looks like you're in Peninsula. Not correct?</text> 
<button id=15>Get current location</button>
<button id=16>Next</button>
------------------
OBJECTIVE: Make a reservation for 4 for dinner at Dorsia in New York City at 8pm
CURRENT URL: https://www.opentable.com/
YOUR COMMAND: 
TYPESUBMIT 12 "dorsia new york city"
==================================================

EXAMPLE 4:
==================================================
PART OF CURRENT BROWSER CONTENT:
------------------
<link id=0/>
<link id=1>Skip to main content</link>
<link id=2 aria-label="Amazon.in">.in</link>
<link id=3>Delivering to Mumbai 400072
                 
                   Update location</link>
<input id=5 text Search Amazon.in Search Amazon.in>men's tshirt</input>
<link id=6 aria-label="Choose a language for shopping.">EN</link>
<link id=7>Hello, sign in Account & Lists</link>
<link id=8>Returns & Orders</link>
<link id=9 aria-label="0 items in cart">0 
        Cart</link>
<link id=10 aria-label="Open Menu">All</link>
<link id=11>Fresh</link>
<link id=12>Amazon miniTV</link>
<link id=13>Sell</link>
<link id=14>Best Sellers</link>
<link id=15>Today's Deals</link>
<link id=16>Mobiles</link>
<link id=17>Customer Service</link>
<link id=18>Electronics</link>
<link id=19>New Releases</link>
<link id=20>Prime</link>
<link id=21>Home & Kitchen</link>
<link id=22>Gift Ideas</link>
<link id=23>Fashion</link>
<link id=24>Amazon Pay</link>
<link id=25>Computers</link>
<link id=26>Books</link>
<link id=27>Beauty & Personal Care</link>
<link id=28>Coupons</link>
<link id=29>Toys & Games</link>
<link id=30>Home Improvement</link>
<link id=31>Gift Cards</link>
<link id=32>Sports, Fitness & Outdoors</link>
<link id=33>Health, Household & Personal Care</link>
<link id=34>Grocery & Gourmet Foods</link>
<link id=35>Car & Motorbike</link>
<link id=36>Baby</link>
<link id=37>Subscribe & Save</link>
<link id=38>Video Games</link>
<link id=39>Audible</link>
<link id=40>Pet Supplies</link>
<link id=41>AmazonBasics</link>
<link id=42>Kindle eBooks</link>
<link id=43 aria-label="New Launches from Mobile, Electronics & more" alt="New Launches from Mobile, Electronics & more"/>
<link id=44/>
<link id=50 aria-label="Sponsored ad from Red Tape. "Stylish T-shirts for Men by Red Tape." Shop Red Tape."/>
<link id=51/>
<link id=52>Stylish T-shirts for Men by Red Tape Stylish T-shirts for Men by Red Tape</link>
<link id=53>Shop Red  Tape</link>
<link id=54 aria-label="Go to detail page for "Red Tape Men T-Shirt." Eligible for Prime."/>
<link id=55 alt="Red Tape Men T-Shirt"/>
<link id=56>Red Tape Men T-Shirt Red Tape Men T-Shirt</link>
<link id=57 aria-label="Rated 3.5 out of 5 stars by 12 reviews. Go to review section.">3.5 out of 5 stars.   12</link>
<link id=58 aria-label="Go to detail page for "Red Tape Polo T-Shirt for Men | Comfortable & Breathable." Eligible for Prime."/>
<link id=59 alt="Red Tape Polo T-Shirt for Men | Comfortable & Breathable"/>
<link id=60>Red Tape Polo T-Shirt for Men | Comfortable & Breathable Red Tape Polo T-Shirt for Men | Comfortable & Breathable</link>
<link id=61 aria-label="Rated 3.7 out of 5 stars by 16 reviews. Go to review section.">3.7 out of 5 stars.   16</link>
<link id=62/>
<img id=64/>
<link id=67 alt="Sponsored Ad - DAMENSCH Men’s Fluid Cotton Lycra Full T- Shirt"/>
<link id=68>+3 colors/patterns</link>
<link id=69 aria-label="View Sponsored information or leave ad feedback">Sponsored</link>
<link id=71>Men’s Fluid Cotton Lycra Full T- Shirt</link>
<link id=72>5.0 out of 5 stars</link>
<link id=73>1</link>
<link id=74>₹1,200 ₹ 1,200   M.R.P:  ₹1,290 ₹1,290</link>
<link id=78 alt="Sponsored Ad - Damensch Men Regular Fit T-Shirt"/>
<link id=79>+2 colors/patterns</link>
<link id=80 aria-label="View Sponsored information or leave ad feedback">Sponsored</link>
<link id=82>Men Regular Fit T-Shirt</link>
<link id=83>4.6 out of 5 stars</link>
<link id=84>17</link>
<link id=85>₹1,403 ₹ 1,403   M.R.P:  ₹1,990 ₹1,990</link>
<link id=88 alt="Sponsored Ad - DAMENSCH Men’s Fluid Cotton Full T-Shirt"/>
<link id=89>+5 colors/patterns</link>
<link id=90 aria-label="View Sponsored information or leave ad feedback">Sponsored</link>
<link id=92>Men’s Fluid Cotton Full T-Shirt</link>
<link id=93>4.4 out of 5 stars</link>
<link id=94>25</link>
<link id=95>₹1,356 ₹ 1,356   M.R.P:  ₹1,490 ₹1,490</link>
<link id=99 alt="Sponsored Ad - XYXX Men 100% Cotton Polo Tshirt"/>
<link id=100>+7 colors/patterns</link>
<link id=101 aria-label="View Sponsored information or leave ad feedback">Sponsored</link>
<link id=103>Men 100% Cotton Polo Tshirt</link>
<link id=104>4.1 out of 5 stars</link>
<link id=105>238</link>
<link id=107>₹549 ₹ 549   M.R.P:  ₹699 ₹699</link>
<link id=112 title="tab to go back to filtering menu">Go back to filtering menu</link>
<link id=113 title="tab to skip to main search results">Skip to main search results</link>
<link id=115 type="checkbox">Get It Today</link>
<link id=116 type="checkbox">Get It by Tomorrow</link>
<link id=117 type="checkbox">Get It in 2 Days</link>
<link id=119>Men's T-Shirts & Polos</link>
<link id=120>Men's T-Shirts</link>
<link id=121>Men's Polos</link>
<link id=122>Baby Clothing</link>
<link id=124 aria-label="4 Stars & Up">4 Stars & Up 
       & Up</link>
<link id=125 aria-label="3 Stars & Up">3 Stars & Up 
       & Up</link>
<link id=126 aria-label="2 Stars & Up">2 Stars & Up 
       & Up</link>
<link id=127 aria-label="1 Star & Up">1 Star & Up 
       & Up</link>
<link id=129 type="checkbox">EYEBOGLER</link>
<link id=130 type="checkbox">Allen Solly</link>
<link id=131 type="checkbox">Van Heusen</link>
<link id=132 type="checkbox">Amazon Brand - Symbol</link>
<link id=133 type="checkbox">LEOTUDE</link>
<link id=134 type="checkbox">BULLMER</link>
<link id=135 type="checkbox">Lux Cozi</link>
<link id=136 aria-label="See more, Brand">See more</link>
<link id=138>Under ₹300</link>
<link id=139>₹300 - ₹500</link>
<link id=140>₹500 - ₹1,000</link>
<link id=141>₹1,000 - ₹1,500</link>
<link id=142>Over ₹1,500</link>
<input id=144 text Min/>
<input id=146 text Max/>
<link id=149>All Discounts</link>
<link id=150>Today's Deals</link>
<link id=152 type="checkbox">Top Brands</link>
<link id=153 type="checkbox">Made for Amazon</link>
<link id=154 type="checkbox">Premium Brands</link>
<link id=156 type="checkbox">Asymmetric Neck</link>
------------------
OBJECTIVE: Go to amazon, search for men's tshirt and click on the first result. Click on Add to cart.Go to cart. Then buy it.
CURRENT URL: https://www.amazon.in/s?k=men%27s+tshirt
YOUR COMMAND: 
CLICK 54
=================================================="""

prompt_template[2]="""The current browser content, objective, and current URL follow. Reply with your next command to the browser.The command generated should be of the exact fashion as it was in the previous examples that were in the previous 2 prompts.

CURRENT BROWSER CONTENT:
------------------
$browser_content
------------------

OBJECTIVE: $objective
CURRENT URL: $url
YOUR COMMAND:
"""

black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "script", "style", "path", "svg", "br", "::marker",])

class Crawler:
	def __init__(self):
		self.browser = (
			sync_playwright()
			.start()
			.chromium.launch(
				headless=False,
			)
		)

		self.page = self.browser.new_page()
		self.page.set_viewport_size({"width": 1280, "height": 1080})

	def go_to_page(self, url):
		self.page.goto(url=url if "://" in url else "http://" + url)
		self.client = self.page.context.new_cdp_session(self.page)
		self.page_element_buffer = {}

	def scroll(self, direction):
		if direction == "up":
			self.page.evaluate(
				"(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop - (window.innerHeight/2);"
			)
		elif direction == "down":
			self.page.evaluate(
				"(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop + (window.innerHeight/2);"
			)

	def click(self, id):
		# Inject javascript into the page which removes the target= attribute from all links
		js = """
		links = document.getElementsByTagName("a");
		for (var i = 0; i < links.length; i++) {
			links[i].removeAttribute("target");
		}
		"""
		self.page.evaluate(js)

		element = self.page_element_buffer.get(int(id))
		if element:
			x = element.get("center_x")
			y = element.get("center_y")
			
			self.page.mouse.click(x, y)
   
		else:
			print("Could not find element")

	def type(self, id, text):
		self.click(id)
		self.page.keyboard.type(text)

	def enter(self):
		self.page.keyboard.press("Enter")

	def crawl(self):
		page = self.page
		page_element_buffer = self.page_element_buffer
		start = time.time()

		page_state_as_text = []

		device_pixel_ratio = page.evaluate("window.devicePixelRatio")
		if platform == "darwin" and device_pixel_ratio == 1:  # lies
			device_pixel_ratio = 2

		win_scroll_x 		= page.evaluate("window.scrollX")
		win_scroll_y 		= page.evaluate("window.scrollY")
		win_upper_bound 	= page.evaluate("window.pageYOffset")
		win_left_bound 		= page.evaluate("window.pageXOffset") 
		win_width 			= page.evaluate("window.screen.width")
		win_height 			= page.evaluate("window.screen.height")
		win_right_bound 	= win_left_bound + win_width
		win_lower_bound 	= win_upper_bound + win_height
		document_offset_height = page.evaluate("document.body.offsetHeight")
		document_scroll_height = page.evaluate("document.body.scrollHeight")

#		percentage_progress_start = (win_upper_bound / document_scroll_height) * 100
#		percentage_progress_end = (
#			(win_height + win_upper_bound) / document_scroll_height
#		) * 100
		percentage_progress_start = 1
		percentage_progress_end = 2

		page_state_as_text.append(
			{
				"x": 0,
				"y": 0,
				"text": "[scrollbar {:0.2f}-{:0.2f}%]".format(
					round(percentage_progress_start, 2), round(percentage_progress_end)
				),
			}
		)

		tree = self.client.send(
			"DOMSnapshot.captureSnapshot",
			{"computedStyles": [], "includeDOMRects": True, "includePaintOrder": True},
		)
		strings	 	= tree["strings"]
		document 	= tree["documents"][0]
		nodes 		= document["nodes"]
		backend_node_id = nodes["backendNodeId"]
		attributes 	= nodes["attributes"]
		node_value 	= nodes["nodeValue"]
		parent 		= nodes["parentIndex"]
		node_types 	= nodes["nodeType"]
		node_names 	= nodes["nodeName"]
		is_clickable = set(nodes["isClickable"]["index"])

		text_value 			= nodes["textValue"]
		text_value_index 	= text_value["index"]
		text_value_values 	= text_value["value"]

		input_value 		= nodes["inputValue"]
		input_value_index 	= input_value["index"]
		input_value_values 	= input_value["value"]

		input_checked 		= nodes["inputChecked"]
		layout 				= document["layout"]
		layout_node_index 	= layout["nodeIndex"]
		bounds 				= layout["bounds"]

		cursor = 0
		html_elements_text = []

		child_nodes = {}
		elements_in_view_port = []

		anchor_ancestry = {"-1": (False, None)}
		button_ancestry = {"-1": (False, None)}

		def convert_name(node_name, has_click_handler):
			if node_name == "a":
				return "link"
			if node_name == "input":
				return "input"
			if node_name=="textarea":
				return "textarea"
			if node_name == "img":
				return "img"
			if (
				node_name == "button" or has_click_handler
			):  # found pages that needed this quirk
				return "button"
			else:
				return "text"

		def find_attributes(attributes, keys):
			values = {}

			for [key_index, value_index] in zip(*(iter(attributes),) * 2):
				if value_index < 0:
					continue
				key = strings[key_index]
				value = strings[value_index]

				if key in keys:
					values[key] = value
					keys.remove(key)

					if not keys:
						return values

			return values

		def add_to_hash_tree(hash_tree, tag, node_id, node_name, parent_id):
			parent_id_str = str(parent_id)
			if not parent_id_str in hash_tree:
				parent_name = strings[node_names[parent_id]].lower()
				grand_parent_id = parent[parent_id]

				add_to_hash_tree(
					hash_tree, tag, parent_id, parent_name, grand_parent_id
				)

			is_parent_desc_anchor, anchor_id = hash_tree[parent_id_str]

			# even if the anchor is nested in another anchor, we set the "root" for all descendants to be ::Self
			if node_name == tag:
				value = (True, node_id)
			elif (
				is_parent_desc_anchor
			):  # reuse the parent's anchor_id (which could be much higher in the tree)
				value = (True, anchor_id)
			else:
				value = (
					False,
					None,
				)  # not a descendant of an anchor, most likely it will become text, an interactive element or discarded

			hash_tree[str(node_id)] = value

			return value

		for index, node_name_index in enumerate(node_names):
	  #node_names=[3,5,75,65,23] where strings[3] will give element type of node 1
	  #don't worry about how parent array looks like
			node_parent = parent[index]
			node_name = strings[node_name_index].lower()

			is_ancestor_of_anchor, anchor_id = add_to_hash_tree(
				anchor_ancestry, "a", index, node_name, node_parent
			)

			is_ancestor_of_button, button_id = add_to_hash_tree(
				button_ancestry, "button", index, node_name, node_parent
			)

			try:
				cursor = layout_node_index.index(
					index
				)  # todo replace this with proper cursoring, ignoring the fact this is O(n^2) for the moment
			except:
				continue

			if node_name in black_listed_elements:
				continue

			[x, y, width, height] = bounds[cursor]
			x /= device_pixel_ratio
			y /= device_pixel_ratio
			width /= device_pixel_ratio
			height /= device_pixel_ratio

			elem_left_bound = x
			elem_top_bound = y
			elem_right_bound = x + width
			elem_lower_bound = y + height

			partially_is_in_viewport = (
				elem_left_bound < win_right_bound
				and elem_right_bound >= win_left_bound
				and elem_top_bound < win_lower_bound
				and elem_lower_bound >= win_upper_bound
			)

			if not partially_is_in_viewport:
				continue

			meta_data = []

			# inefficient to grab the same set of keys for kinds of objects but its fine for now
			element_attributes = find_attributes(
				attributes[index], ["type", "placeholder", "aria-label", "title", "alt"]
			)
			

			ancestor_exception = is_ancestor_of_anchor or is_ancestor_of_button
			ancestor_node_key = (
				None
				if not ancestor_exception
				else str(anchor_id)
				if is_ancestor_of_anchor
				else str(button_id)
			)
			ancestor_node = (
				None
				if not ancestor_exception
				else child_nodes.setdefault(str(ancestor_node_key), [])
			)

			if node_name == "#text" and ancestor_exception: # if it is a text inside an anchor or button then child_nodes[ancestor]=[{type:"type",value:"the text inside",},{.....} .....]
				text = strings[node_value[index]]
				if text == "|" or text == "•":
					continue
				ancestor_node.append({
					"type": "type", "value": text
				})
			else:
				if (
					node_name == "input" and element_attributes.get("type") == "submit"
				) or node_name == "button":
					node_name = "button"
					element_attributes.pop(
						"type", None
					)  # prevent [button ... (button)..]
				
				for key in element_attributes:
					if ancestor_exception:
 # if it is not a text inside an anchor or button then child_nodes[ancestor]=[{type:"attribute",key:"<key>",value:"<value>",},{.....} .....]
 # the problem here is that if we have an input/textarea that is non_exception, it's attributes will be stored in meta_data without the input/textarea word itself
						ancestor_node.append({
							"type": "attribute",
							"key":  key,
							"value": element_attributes[key]
						})
					else:
						meta_data.append(element_attributes[key])



			# print(f"||||{child_nodes}|||")
			# print(f"||||{meta_data}|||")
			# print()
			# time.sleep(0.2)

			element_node_value = None

			if node_value[index] >= 0:
				element_node_value = strings[node_value[index]]

				if element_node_value == "|": #commonly used as a seperator, does not add much context - lets save ourselves some token space
					continue
			elif (
				node_name == "input"
				and index in input_value_index
				and element_node_value is None
			):
				node_input_text_index = input_value_index.index(index)
				text_index = input_value_values[node_input_text_index]
				if node_input_text_index >= 0 and text_index >= 0:
					element_node_value = strings[text_index]


		
			
			if ancestor_exception and (node_name != "a" and node_name != "button"):
				continue

			elements_in_view_port.append(
				{
					"node_index": str(index),
					"backend_node_id": backend_node_id[index],
					"node_name": node_name,
					"node_value": element_node_value,
					"node_meta": meta_data,
					"is_clickable": index in is_clickable,
					"origin_x": int(x),
					"origin_y": int(y),
					"center_x": int(x + (width / 2)),
					"center_y": int(y + (height / 2)),
				}
			)

		# lets filter further to remove anything that does not hold any text nor has click handlers + merge text from leaf#text nodes with the parent
		elements_of_interest= []
		id_counter 			= 0

		for element in elements_in_view_port:
			node_index = element.get("node_index")
			node_name = element.get("node_name")
			node_value = element.get("node_value")
			is_clickable = element.get("is_clickable")
			origin_x = element.get("origin_x")
			origin_y = element.get("origin_y")
			center_x = element.get("center_x")
			center_y = element.get("center_y")
			meta_data = element.get("node_meta")

			inner_text = f"{node_value} " if node_value else ""
			meta = ""
			
			if node_index in child_nodes:
				
				for child in child_nodes.get(node_index):
					
					entry_type = child.get('type')
					entry_value= child.get('value')

					if entry_type == "attribute":
						entry_key = child.get('key')
						meta_data.append(f'{entry_key}="{entry_value}"')
					else:
						inner_text += f"{entry_value} "

			if meta_data:
				meta_string = " ".join(meta_data)
				meta = f" {meta_string}"

			if inner_text != "":
				inner_text = f"{inner_text.strip()}"

			converted_node_name = convert_name(node_name, is_clickable)

			# not very elegant, more like a placeholder
			if (
				(converted_node_name != "button" or meta == "")
				and converted_node_name != "link"
				and converted_node_name != "input"
				and converted_node_name != "img"
				and converted_node_name != "textarea"
			) and inner_text.strip() == "":
				continue

			page_element_buffer[id_counter] = element

			if inner_text != "": 
				elements_of_interest.append(
					f"""<{converted_node_name} id={id_counter}{meta}>{inner_text}</{converted_node_name}>"""
				)
			else:
				elements_of_interest.append(
					f"""<{converted_node_name} id={id_counter}{meta}/>"""
				)
			id_counter += 1

		print("Parsing time: {:0.2f} seconds".format(time.time() - start))
		return elements_of_interest

if (
	__name__ == "__main__"
):
	_crawler = Crawler()
	

	def print_help():
		print(
			"(g) to visit url\n(u) scroll up\n(d) scroll down\n(c) to click\n(t) to type\n" +
			"(h) to view commands again\n(r/enter) to run suggested command\n(o) change objective"
		)

	def get_gpt_command(objective, url, previous_command, browser_content):
	 
		
		prompt = prompt_template[2]
		prompt = prompt.replace("$objective", objective)
		prompt = prompt.replace("$url", url[:50])

		papa=client.chat.completions.create(
	    model="gpt-3.5-turbo-1106",
	    messages=[{"role": "user", "content": prompt_template[0]}],
	    temperature=0,
	    frequency_penalty=-2.0,
	    presence_penalty=-2.0)


		
		mumma = prompt.replace("$browser_content", browser_content)
		response=client.chat.completions.create(
	    model="gpt-3.5-turbo-1106",
	    messages=[{"role": "user", "content": prompt_template[1]}],
	    temperature=0,
	    frequency_penalty=-2.0,
	    presence_penalty=-2.0)
		
		prompt = prompt.replace("$browser_content", browser_content)
		response=client.chat.completions.create(
	    model="gpt-3.5-turbo-1106",
	    messages=[{"role": "user", "content": prompt}],
	    temperature=0,
	    frequency_penalty=-2.0,
	    presence_penalty=-2.0)
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

	objective = "go to amazon, search for men's tshirt and click on the first result. Click on Add to cart."
	print("\nWelcome to natbot! What is your objective?")
	i = input()
	if len(i) > 0:
		objective = i

	gpt_cmd = ""
	prev_cmd = ""
	_crawler.go_to_page("google.com")
	try:
		while True:
			browser_content = "\n".join(_crawler.crawl())
			pattern = r'<text\s.*?>.*?</text>\s*'

# Replace matched patterns with an empty string
			browser_content = re.sub(pattern, '', browser_content, flags=re.DOTALL)
			url1=_crawler.page.url[:40]
			prev_cmd = gpt_cmd
			gpt_cmd = get_gpt_command(objective, url1, prev_cmd, browser_content)
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
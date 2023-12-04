





#this is an attempt to include <input> in browser content so that typesubmit would be able to click on the input box first then type whatever it needs to type followed by \n
# 
# the prompt has also been made more deterministic
# 
# !/usr/bin/env python3
#
# natbot.py
#
# Set OPENAI_API_KEY to your API key, and then run this from a terminal.
#
import logging
from playwright.sync_api import sync_playwright
import time
from sys import argv, exit, platform
from openai import OpenAI
client = OpenAI()
import os

quiet = False
if len(argv) >= 2:
    if argv[1] == '-q' or argv[1] == '--quiet':
        quiet = True
        print(
            "Running in quiet mode (HTML and other content hidden); \n"
            + "exercise caution when running suggested commands."
        )

prompt_template ="""You are an agent controlling a browser. You are given:

(1) an objective that you are trying to achieve
(2) the URL of your current web page
(3) a description of what's visible in the browser window, including the text and its coordinates on the page

You can issue these commands:
    SCROLL UP - scroll up one page
    SCROLL DOWN - scroll down one page
    CLICK AT COORDINATES X,Y - click on a given element at the specified coordinates
    TYPE AT COORDINATES X,Y "TEXT" - type the specified text into an input field at the given coordinates
    TYPESUBMIT AT COORDINATES X,Y "TEXT" - same as TYPE, except then it presses ENTER to submit the form

The format of the browser content includes text and their corresponding coordinates:
    {
        "boundingPoly": {
            "vertices": [
                {"x": X1, "y": Y1},
                {"x": X2, "y": Y2},
                {"x": X3, "y": Y3},
                {"x": X4, "y": Y4}
            ]
        },
        "description": "Text"
    },
    // More text elements with their coordinates...

Based on your given objective, issue whatever command you believe will get you closest to achieving your goal.
You always start on Google; you should submit a search query to Google that will take you to the best page for achieving your objective. And then interact with that page to get closer to achieving your objective. Keep interacting until you achieve your objective.

If you find yourself on Google and there are no search results displayed yet, you should probably issue a command like "TYPESUBMIT AT COORDINATES X,Y "search query"", where X,Y are the coordinates of the search input box.

Then, if you find yourself on a Google search results page, you might issue the command "CLICK AT COORDINATES X,Y" to click on the first link in the search results.

Don't try to interact with elements that you can't see.

Here are some examples:

EXAMPLE 1:
==================================================
CURRENT BROWSER CONTENT:
------------------
{
    "boundingPoly": {"vertices": [{"x": 100, "y": 150}, {"x": 200, "y": 150}, {"x": 200, "y": 200}, {"x": 100, "y": 200}]},
    "description": "Search"
},
// More text elements with their coordinates...
------------------
OBJECTIVE: Find a 2 bedroom house for sale in Anchorage AK for under $750k
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT AT COORDINATES 150,175 "anchorage redfin"
================================================== 

EXAMPLE 2:
==================================================
CURRENT BROWSER CONTENT:
------------------
{
    "boundingPoly": {"vertices": [{"x": 100, "y": 150}, {"x": 200, "y": 150}, {"x": 200, "y": 200}, {"x": 100, "y": 200}]},
    "description": "Search"
},
// More text elements with their coordinates...
------------------
OBJECTIVE: Make a reservation for 4 at Dorsia at 8pm
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT AT COORDINATES 150,175 "dorsia nyc opentable"
==================================================

EXAMPLE 3:
==================================================
CURRENT BROWSER CONTENT:
------------------
{
    "boundingPoly": {"vertices": [{"x": 300, "y": 250}, {"x": 400, "y": 250}, {"x": 400, "y": 300}, {"x": 300, "y": 300}]},
    "description": "Location, Restaurant, or Cuisine"
},
// More text elements with their coordinates...
------------------
OBJECTIVE: Make a reservation for 4 for dinner at Dorsia in New York City at 8pm
CURRENT URL: https://www.opentable.com/
YOUR COMMAND: 
TYPESUBMIT AT COORDINATES 350,275 "dorsia new york city"
==================================================

The current browser content, objective, and current URL follow. Reply with your next command to the browser.

CURRENT BROWSER CONTENT:
------------------
$browser_content
------------------

OBJECTIVE: $objective
CURRENT URL: $url
PREVIOUS COMMAND: $previous_command
YOUR COMMAND:
"""

black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "script", "style", "path", "svg", "br", "::marker",])

class Crawler:
    def __init__(self):
        self.browser = (
            sync_playwright().start().chromium.launch(headless=False)
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
                "(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop - window.innerHeight;"
            )
        elif direction == "down":
            self.page.evaluate("(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop + window.innerHeight;")
    
    def click(self, x, y):
        self.page.mouse.click(x, y)

    def type(self, x, y, text):
        self.click(x, y)
        self.page.keyboard.type(text)

    def enter(self):
        self.page.keyboard.press("Enter")
    def crawl(self):
        page = self.page
        page_element_buffer = self.page_element_buffer
        start = time.time()

        page_state_as_text = []

        device_pixel_ratio = page.evaluate("window.devicePixelRatio")
        if platform == "darwin" and device_pixel_ratio == 1:  #lies
            device_pixel_ratio = 2

        win_scroll_x 		= page.evaluate("window.scrollX")
        win_scroll_y 		= page.evaluate("window.scrollY")
        win_upper_bound 	= page.evaluate("window.pageYOffset")
        win_left_bound 		= page.evaluate("window.pageXOffset") 
        win_width 			= page.evaluate("window.screen.width")
        win_height 			= page.evaluate("window.screen.height")
        win_right_bound 	= win_left_bound + win_width # stored in the form of CSS pixels
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
        backend_node_id = nodes["backendNodeId"]#the tree's documents' nodes'
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
        bounds 				= layout["bounds"]#values of elements are stored in the form of 
                              #CSS pixels,ie.1280 * 1080 MULTIPLIED BY device pixel ratio i.e. 2 which is basically the same as the physical device resolution (not the css resolution)
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
            if node_name == "img":
                return "img"
            if (
                node_name == "button" or has_click_handler
            ):  # found pages that needed this quirk
                return "button"
            else:
                return "text"

        #["id", "content", "class", "container"], ["type", "placeholder", "aria-label", "title", "alt"]
        def find_attributes(attributes, keys):
            values = {}

            for [key_index, value_index] in zip(*(iter(attributes),) * 2):
                
                if value_index < 0:
                    continue
                key = strings[key_index]
                value = strings[value_index]
                
                time.sleep(0.2)
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
                value = (True, node_id)# node_id=index
            elif (
                is_parent_desc_anchor
            ):  # reuse the parent's anchor_id (which could be much higher in the tree)
                value = (True, anchor_id)
            else:
                value = (
                    False,
                    None,
                )  # not a descendant of an anchor, most likely it will become text, an interactive element or discarded

            hash_tree[str(node_id)] = value # node_id=index

            return value

        for index, node_name_index in enumerate(node_names):
#node_names=[5,3,7,3,7,3], where node_names[0]=5=node_name_index; strings[node_name_index] is the name of the node
#parent=[77,52,54,22,44], where parent[0]=77=parent_id and string[node_names[parent_id]] is the name of the parent
#
#
#
#
#

            node_parent = parent[index] # parent[] is parallel to node_names[] and therefore also stores values- lets say x which will represent the html element type when used as strings[x]
            node_name = strings[node_name_index].lower()  #node name is the element, ie, div, link, button

            is_ancestor_of_anchor, anchor_id = add_to_hash_tree(
                anchor_ancestry, "a", index, node_name, node_parent # anchor_ancestry = {"-1": (False, None)}
            )
            
            is_ancestor_of_button, button_id = add_to_hash_tree(
                button_ancestry, "button", index, node_name, node_parent
            )

            try:
                cursor = layout_node_index.index(index)  # todo replace this with proper cursoring, ignoring the fact this is O(n^2) for the moment
                #cursor will now consist of index of the node if its bounds are available else the loop will continue 
            except:
                continue

            if node_name in black_listed_elements:
                continue

            [x, y, width, height] = bounds[cursor]
            #bounds cursor will give
            x /= device_pixel_ratio  #everything here is divided by 2 to convert the physical device resolution to the CSS resolution because this will be compared to the full viewport resolution which is of the form CSS
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
            ) # element_attributes will consist of {'aria-label': 'Google apps', 'title}
   
            

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
#child_nodes={'43':[],'454',[]} where 43 is a key of outermost clickable
            if node_name == "#text" and ancestor_exception:
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
                        ancestor_node.append({
                            "type": "attribute",
                            "key":  key,
                            "value": element_attributes[key]
                        })
                    else:
                        meta_data.append(element_attributes[key])

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

            # remove redudant elements
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
        return elements_of_interest #this is wrong as it doesn't have input and textarea
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
        prompt = prompt_template
        prompt = prompt.replace("$objective", objective)
        prompt = prompt.replace("$url", url[:100])
        prompt = prompt.replace("$previous_command", previous_command)
        prompt = prompt.replace("$browser_content", browser_content[:9000])
        response = client.chat.completions.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content


    def run_cmd(cmd):
        if cmd.startswith("CLICK AT COORDINATES"):
            # Extracts coordinates from the command and clicks at that location
            _, _, coordinates = cmd.partition("COORDINATES ")
            x, y = map(int, coordinates.split(","))
            _crawler.click(x, y)      
        elif cmd.startswith("TYPE AT COORDINATES"):
         # Extracts coordinates and text from the command and types at that location
         _, _, rest = cmd.partition("COORDINATES ")
         coordinates, text = rest.split('"', 1)
         x, y = map(int, coordinates.strip().split(","))
         text = text.strip('"')
         _crawler.type(x, y, text)     
        elif cmd.startswith("SCROLL UP"):
            # If the command is to scroll up
            _crawler.scroll("up")     
        elif cmd.startswith("SCROLL DOWN"):
            # If the command is to scroll down
            _crawler.scroll("down")       
        # Add additional command processing as needed
        # Example: elif cmd.startswith("SOME_OTHER_COMMAND"):     
        else:
            print(f"Unknown command: {cmd}")


    objective = "Make a reservation for 2 at 7pm at bistro vida in menlo park"
    print("\nWelcome to natbot! What is your objective?")
    i = input()
    if len(i) > 0:
        objective = i

    gpt_cmd = ""
    prev_cmd = ""
    _crawler.go_to_page("bing.com")
    try:
        while True:
            browser_content = "\n".join(_crawler.crawl())
            prev_cmd = gpt_cmd
            gpt_cmd = get_gpt_command(objective, _crawler.page.url, prev_cmd, browser_content)
            gpt_cmd = gpt_cmd.strip()

            if not quiet:
                print("URL: " + _crawler.page.url)
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
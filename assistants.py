from openai import OpenAI
client = OpenAI()
import json

def show_json(obj):
    display(json.loads(obj.model_dump_json()))
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-3.5-turbo-1106-preview",
)
show_json(assistant)  
    
    
    
# response = client.chat.completions.create(
#   model="gpt-3.5-turbo-1106",
#   seed=765,
#   temperature=0,
#   response_format={ "type": "json_object" },
#   messages=[
#     {"role": "user", "content": "give me concise list of two awesome things about lions in json format"}
#   ]
# )



from mailjet_rest import Client
import os
api_key = '****************************1234'
api_secret = '****************************abcd'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')
data = {
  'Messages': [
    {
      "From": {
        "Email": "onlyvedansh@gmail.com",
        "Name": "Vedansh"
      },
      "To": [
        {
          "Email": "onlyvedansh@gmail.com",
          "Name": "Vedansh"
        }
      ],
      "Subject": "Greetings from Mailjet.",
      "TextPart": "My first Mailjet email",
      "HTMLPart": "<h3>Dear passenger 1, welcome to <a href='https://www.mailjet.com/'>Mailjet</a>!</h3><br />May the delivery force be with you!",
      "CustomID": "AppGettingStartedTest"
    }
  ]
}
result = mailjet.send.create(data=data)
print (result.status_code)
print (result.json())

from sanic import Sanic
from sanic.response import json, text
import aiohttp
import asyncio
import async_timeout
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Sanic()


@app.route('/')
def hello():
    return "Hello World!"

api_key = os.environ.get('API_KEY')
api_url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze'
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': api_key,
}

body = {
    # Request parameters. All of them are optional.
    'visualFeatures': 'Categories,Description,Color',
    'language': 'en',
}
data = {}

@app.post('/api/image')
async def get(request):
    async with aiohttp.ClientSession(headers=headers) as session:  # with ke
        async with session.post(
          url=api_url,
          data=data
          ) as resp:
            json_res = await resp.json()
            if resp.status == 200:
                return json({
                    'data': json_res,
                    'status': 'ok'
                })
            else:
                return json({
                    'status': 'error',
                    'message': json_res
                })


if __name__ == '__main__':
    app.run()

"""
Distill actionable information from images

5,000 transactions, 20 per minute.
Endpoint: https://westcentralus.api.cognitive.microsoft.com/vision/v1.0

Key 1: a2ca988a92bd48a6a7e5ae1cca3109e7

Key 2: 6b4891983d5d4c12a96f796357789098
####################################

########### Python 3.6 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64, json

###############################################
#### Update or verify the following values. ###
###############################################

# Replace the subscription_key string value with your valid subscription key.
subscription_key = '13hc77781f7e4b19b5fcdd72a8df7156'

# Replace or verify the region.
#
# You must use the same region in your REST API call as you used to obtain your subscription keys.
# For example, if you obtained your subscription keys from the westus region, replace
# "westcentralus" in the URI below with "westus".
#
# NOTE: Free trial subscription keys are generated in the westcentralus region, so if you are using
# a free trial subscription key, you should not need to change this region.
uri_base = 'westcentralus.api.cognitive.microsoft.com'

headers = {
    # Request headers.
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

params = urllib.parse.urlencode({
    # Request parameters. All of them are optional.
    'visualFeatures': 'Categories,Description,Color',
    'language': 'en',
})

# Replace the three dots below with the URL of a JPEG image of a celebrity.
body = "{'url':'https://upload.wikimedia.org/wikipedia/commons/1/12/Broadway_and_Times_Square_by_night.jpg'}"

try:
    # Execute the REST API call and get the response.
    conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read()

    # 'data' contains the JSON data. The following formats the JSON data for display.
    parsed = json.loads(data)
    print ("Response:")
    print (json.dumps(parsed, sort_keys=True, indent=2))
    conn.close()

except Exception as e:
    print('Error:')
    print(e)
"""

import re
from uuid import uuid4
from random import randint
from sanic import Sanic
from sanic.response import json, text, html, redirect
from sanic.config import LOGGING
from aiohttp import ClientSession
from PIL import Image
import asyncio
from dev import live_reload
from utils import is_url
from json import dumps, loads
from db import store_team_data, get_access_token_by_team_id
from willow.plugins.pillow import PillowImage
from settings import *

app = Sanic()


def draw_googly(image_name, faces):
    imagepath = 'img/' + image_name
    for face in faces:
        portrait = Image.open(imagepath)
        rect = face['faceRectangle']
        print('rectangle:', rect)
        eye = Image.open('eye.png')
        eye.thumbnail((rect['width'] / 3, rect['height'] / 3))
        eye_size = eye.size[0]
        offset = int(eye_size / 2)
        eye_left_x = int(face['faceLandmarks']['pupilLeft']['x']) - offset
        eye_left_y = int(face['faceLandmarks']['pupilLeft']['y']) - offset
        eye_right_x = int(face['faceLandmarks']['pupilRight']['x']) - offset
        eye_right_y = int(face['faceLandmarks']['pupilRight']['y']) - offset
        # center it on face
        paste_position_left = eye_left_x, eye_left_y
        paste_position_right = eye_right_x, eye_right_y
        # last property is a mask
        portrait.paste(eye, paste_position_left, eye)
        portrait.paste(eye, paste_position_right, eye)
        # check if it has an alpha channel
        if 'A' in portrait.getbands():
            PillowImage(portrait).set_background_color_rgb(
                (255, 255, 255)).save_as_jpeg(imagepath)
        else:
            portrait.save(imagepath)
            if DEV == 'TRUE':
                print('showing portrait.')
                portrait.show()


def create_res(payload):
    return json({
        'status': 'success',
        'payload': payload
    })


def create_err(message):
    return json({
        'status': 'error',
        'message': message
    })


# serve any file in the /img folder
app.static('/img', './img')
# serve any static asset
app.static('/assets', './static/assets')
# map get requests from /support.html to static folder. (i.e. /support.html)
app.static('/', './static/index.html')
app.static('/privacy', './static/privacy.html')
app.static('/support', './static/support.html')
app.static('/success', './static/success.html')
app.static('/failure', './static/failure.html')


async def slack_user_req(token, user_id):
    slack_user_header = {'Content-type': 'application/x-www-form-urlencoded'}
    slack_user_api_url = 'https://slack.com/api/users.profile.get'
    slack_user_params = {
        'token': token,
        'user': user_id,
    }
    with ClientSession(
        headers=slack_user_header
    ) as session:
        async with session.post(
            url=slack_user_api_url,
            params=slack_user_params
        ) as resp:
            return resp

# list all users in slack team


async def slack_users_req(token):
    slack_user_header = {'Content-type': 'application/x-www-form-urlencoded'}
    slack_user_api_url = 'https://slack.com/api/users.list'
    slack_user_params = {
        'token': token,
    }
    with ClientSession(
        headers=slack_user_header
    ) as session:
        async with session.post(
            url=slack_user_api_url,
            params=slack_user_params
        ) as resp:
            return resp


async def slack_api_req(code):
    slack_oauth_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
    }
    slack_oauth_url = "https://slack.com/api/oauth.access"
    with ClientSession() as session:
        async with session.get(
            url=slack_oauth_url,
            params=slack_oauth_params,
        ) as resp:
            return resp

# when installing the slack app, this should redirect to this url, which -- if the user is authenticated, will trigger /redirect.


@app.get('/auth')
async def authorize(req):
    slack_oauth_url = 'https://slack.com/oauth/authorize?scope=commands,users:read,users.profile:read&client_id=' + CLIENT_ID
    return redirect(slack_oauth_url)


@app.get('/redirect')
async def auth_redirect(req):
    print('redirect Called!')
    if 'code' in req.raw_args:
        code = req.raw_args['code']
    else:
        return redirect('/failure')
    resp = await slack_api_req(code)
    if resp.status == 200:
        json_res = await resp.json()
        if json_res['ok']:
            print('RESPONSE OK!')
            team_id = json_res['team_id']
            team_name = json_res['team_name']
            access_token = json_res['access_token']
            db_res = await store_team_data(team_id, team_name, access_token)
            print(db_res)
            return redirect('/success')
        else:
            print('slack error', json_res['error'])
            return redirect('/failure')
    else:
        print('could not communicate with slack OAuth API.')
        return redirect('/failure')


def get_full_image_path(image_name):
    return IMAGE_SERVER_HOST + '/img/' + image_name


async def download_image(url):
    image_name = str(uuid4()) + '.jpg'
    image_path = 'img/' + image_name
    with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image = await resp.read()
                with open(image_path, 'wb') as fs_instance:
                    fs_instance.write(image)
                    return image_name


async def bing_image_search(keywords):
    bing_image_api_url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'
    bing_image_req_headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': API_KEY_BING,
    }
    bing_image_search_req_params = {
        'q': keywords,
        'encodingFormat': 'jpeg'
    }
    # with ke
    async with ClientSession(headers=bing_image_req_headers) as session:
        async with session.get(
            url=bing_image_api_url,
            params=bing_image_search_req_params
        ) as resp:
            json_res = await resp.json()
            if resp.status == 200:
                return json_res
            else:
                print('Bing image search error API Error:', json_res);
                return 'could not get image from bing image api.'


async def vision_api_req(url):
    vision_api_url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze'
    vision_api_req_headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': API_KEY_VISION,
    }
    vision_api_params = {
        'visualFeatures': 'Faces, Description',
    }
    # request body looks like: {data: { url: ... }}
    vision_api_req_body = {
        'url': url,  # mandatory
    }
    async with ClientSession(headers=vision_api_req_headers) as session:
        async with session.post(
            url=vision_api_url,
            params=vision_api_params,
            data=dumps(vision_api_req_body)
        ) as resp:
            json_res = await resp.json()
            json_res['sourceUrl'] = url
            if resp.status == 200:
                return json_res
            else:
                print(resp)
                raise Exception('could not get image from ms vision api.')


async def face_api_req(url):
    face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
    face_api_req_headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': API_KEY_FACE,
    }
    face_api_params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'true'
    }
    # request body looks like: {data: { url: ... }}
    face_api_req_body = {
        'url': url,
    }
    async with ClientSession(headers=face_api_req_headers) as session:
        async with session.post(
            url=face_api_url,
            params=face_api_params,
            data=dumps(face_api_req_body)
        ) as resp:
            json_res = await resp.json()
            # json_res['sourceUrl'] = url
            if resp.status == 200:
                return json_res
            else:
                print(resp)
                raise Exception('could not get image from face api.')


async def create_googly_from_url(url):
    print('creating googly from url:', url)
    image_name = await download_image(url)
    face_api_res = await face_api_req(url)
    if not face_api_res:
        print('face_api_res:', face_api_res)
        return False
    draw_googly(image_name, face_api_res)
    return get_full_image_path(image_name)


async def create_googly_from_kw(keyword):
    bing_image_search_res = await bing_image_search(keyword)
    # get random one
    img_results = bing_image_search_res['value']
    if not img_results:
        return 'Unable to get Bing image search result, maybe API is down.'
    # if there are more than 10 items, choose the top 10, otherwise choose a random one.
    last_index = len(img_results) - 1
    # if Dev is on, always take the first item (makes debugging eye pos. easier)
    rand_index = randint(0, 10) if last_index > 10 and DEV != 'TRUE' else 0
    url = img_results[rand_index]['thumbnailUrl']
    return await create_googly_from_url(url)


def create_slack_image_json_res(label, imageurl):
    return json({
        'parse': 'full',
        'response_type': 'in_channel',
        'text': label,
        'attachments': [
            {'image_url': imageurl}
        ],
        'unfurl_media': True
    })


@app.post('/api/debug')
async def get_image_debug(req):
    res = await vision_api_req(DEFAULTIMGURL)
    return create_res(res)


@app.post('/api/image')
async def get_image(req):
    body = req.json
    if 'keyword' not in body:
        return create_err('keyword not in body.')
    else:
        keyword = body['keyword']
        image_path_res = await create_googly_from_kw(keyword)
        if is_url(image_path_res):
            return create_res(image_path_res)
        else:
            return create_err(image_path_res)


async def post_image_to_slack(url, display_title, full_image_path):
    headers = {
        'Content-type': 'application/json'
    }
    body = {
        "parse": "full",
        "response_type": "in_channel",
        "attachments": [
            {
                "title": display_title + ' got Googly\'d!',
                "image_url": full_image_path
            }
        ],
        "unfurl_media": True,
        "unfurl_links": True

    }
    async with ClientSession(headers=headers) as session:
        async with session.post(
            url=url,
            data=dumps(body)
        ) as resp:
            resp = await resp.text()
            return resp


def find_user_id(keyword):
    keyword_clean = keyword.lstrip()
    # example: "<@U84AA8NET|melissahdunn>" -> U84AA8NE
    if keyword_clean[0] == '<':
        user_id_regex = re.compile(r"[^A-Za-z0-9\s]([UW][\d\s\w]*)")
        matches = re.findall(user_id_regex, keyword)
        if matches:
            return matches[0]


@app.post('/api/slack')
async def get_image_slack(req):
    print('slack endpoint hit!')
    print('url!', req.url)
    keyword = req.form.get('text')
    # check if req carries validation token
    verification_token = req.form.get('token')
    if verification_token != VERIFICATION_TOKEN:
        return json('Unauthorized: mismatched verification token.')
    response_url = req.form.get('response_url')
    team_id = req.form.get('team_id')
    print('team_id:', team_id)
    user_id = find_user_id(keyword)
    if user_id:
        print(keyword)
        print('hello!')
        access_token = await get_access_token_by_team_id(team_id)
        if not access_token:
            return json(
                'Unable to get your team\'s access token from the DB. \
                Try reinstalling Googly on your Slack workspace.'
            )
        resp = await slack_user_req(access_token, user_id)
        if resp.status == 200:
            json_res = await resp.json()
            print('slack response', json_res)
            if json_res['ok']:
                print(json(json_res))
                user = json_res['profile']
                display_name = (
                    '@' + user['display_name']) if user.get('display_name') else user['real_name']
                avatar_url = user.get('image_512') or user.get('image_192')
                if not avatar_url:
                    return json('No suitable width image in requested user\'s profile.')
                person_image_path = await create_googly_from_url(avatar_url)
                if not person_image_path:
                    return json('Unable to locate human face in image search result, please try again.')
            else:
                # token probably expired, or user unauthorized.
                return json(json_res)
        else:
            return json('Cannot fetch users on your team from slack API.')
    # create a closure (at this point, post image to slack
    # http://cheat.readthedocs.io/en/latest/python/asyncio.html
    # calling post_image_to_slack does not call it, but rather, returns a coroutine object
    if 'person_image_path' in locals():
        print('returning...', person_image_path)
        post_image = post_image_to_slack(
            response_url, display_name, person_image_path)
    else:
        keyword_image_path = await create_googly_from_kw(keyword)
        if not keyword_image_path:
            return json('Unable to locate human face in image search result, please try again.')
        print('returning...', keyword_image_path)
        post_image = post_image_to_slack(
            response_url, keyword, keyword_image_path)
    # create an event loop, (so runtime continues while post_image is running)
    asyncio.get_event_loop().create_task(post_image)
    # returns ok, even if an image does not return.
    return json('Googly\'d!')

print('DB_HOST:', DB_HOST)
if __name__ == '__main__':
    # name == 'main' i.e. only execute when this file is run as program (via python3 app),
    # and not if someone imports it as a module via 'import app';
    if DEV == 'TRUE':
        live_reload()
        # host should be 0.0.0.0 for docker ... can be accessed via 192.168.99.100
        if SSL_ENABLED == 'TRUE':
            print('SSL--> ON!')
            app.run(port=PORT, host=RAW_HOST, debug=True,
                    log_config=LOGGING, ssl=SSL)
        else:
            print('SSL--> OFF!')
            app.run(port=PORT, host=RAW_HOST, debug=True, log_config=LOGGING)
    else:
        print('Production')
        print('SSL', SSL)
        app.run(port=PORT, host=RAW_HOST, ssl=SSL, log_config=LOGGING)

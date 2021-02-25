# -*- coding: utf-8 -*-

"""
Bot to test Social Network API.

Will generate users and simulate their activities by creating posts and likes.
"""

import confuse
import json
import os
import random
import requests

project_root = os.path.dirname(os.path.abspath(__file__))
os.environ['SOCIO_NETWORK_BOTDIR'] = project_root
appConfig = confuse.Configuration('socio_network_bot')

base_url = appConfig['app']['base_url'].get()
endpoints = appConfig['app']['endpoints'].get()

with open(f'{project_root}/users_demo.json', mode='r', encoding='utf-8') as fp:
    demo_data = fp.read()

user_list = json.loads(demo_data)


def get_random_user(users):
    return users[random.randint(0, len(users)-1)]


def get_random_post(posts):
    return posts[random.randint(0, len(posts)-1)]


# 1. Create users
created_users = []
for i in range(appConfig['app']['number_of_users'].get()):
    user_data = get_random_user(user_list)
    user = requests.post(f"{base_url}{endpoints['create_user']}", data=user_data).json()
    created_users.append({
        'username': user_data.get('username'),
        'password': user_data.get('password'),
    })

# 2. Get tokens
for i, user in enumerate(created_users):
    created_users[i]['tokens'] = requests.post(f"{base_url}{endpoints['auth_user']}", data=user).json()

# 3. Create posts. All posts with the same text. Can be improved, but it's ok for testing purposes.
# For simplicity we are not checking auth state here to perform refresh request. We assume that access token is not exp.
text = """
Nunc nonummy metus. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Aenean commodo ligula eget dolor. 
Aenean commodo ligula eget dolor. Nunc nulla.
Ut tincidunt tincidunt erat. Fusce a quam. Fusce vulputate eleifend sapien. Aenean viverra rhoncus pede. Cras id dui.
Pellentesque ut neque. Phasellus leo dolor, tempus non, auctor et, hendrerit quis, nisi. Fusce risus nisl, viverra et, 
tempor et, pretium in, sapien. Sed augue ipsum, egestas nec, vestibulum et, malesuada adipiscing, dui. 
Pellentesque libero tortor, tincidunt et, tincidunt eget, semper nec, quam.
Nulla sit amet est. Quisque malesuada placerat nisl. Nam adipiscing. Pellentesque auctor neque nec urna. 
Praesent adipiscing.
Aenean vulputate eleifend tellus. Nullam accumsan lorem in dui. Vivamus quis mi. Aenean posuere, tortor sed cursus 
feugiat, nunc augue blandit nunc, eu sollicitudin urna dolor sagittis lacus..
"""
created_posts = []
for user in created_users:
    for i in range(appConfig['app']['max_posts_per_user'].get()):
        created_posts.append(requests.post(
            f"{base_url}{endpoints['create_post']}",
            data={'text': text},
            headers={'Authorization': f'Bearer {user.get("tokens").get("access")}'}
        ).json())

# 4. Like posts
for user in created_users:
    for i in range(appConfig['app']['max_likes_per_user'].get()):
        post = get_random_post(created_posts)
        requests.post(
            f"{base_url}{endpoints['like_post']}",
            data={'id': post.get('id')},
            headers={'Authorization': f'Bearer {user.get("tokens").get("access")}'}
        )

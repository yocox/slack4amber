#import urllib.request
import urllib
import json
from collections import namedtuple


SLACK_TOKEN = 'xoxp-11979191639-11979191655-11999522372-47a2833f03'

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)
def url2obj(u): return json2obj(urllib.urlopen(url).read().decode())

def g(api, **args):
    args['token'] = SLACK_TOKEN
    arg_str = urllib.urlencode(args)
    url = 'https://slack.com/api/%s?%s' % (api, arg_str)
    return json2obj(urllib.urlopen(url).read().decode())


class User:
    def __init__(self, name, img):
        self.name = name
        self.img = img

def create_uesr_dict(user_list):
    result = {}
    for u in user_list.members:
        result[u.id] = User(u.name, u.profile.image_48) 
    return result

users = g('users.list', pretty=1)
user_dict = create_uesr_dict(users)

print users.members[14]

channels = g('channels.list')

print channels.channels[0].id
print channels.channels[0].name

h = g('channels.history', channel='C0BUQESCT', count=5)

for m in h.messages:
    print user_dict[m.user].name, ':', m.text


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

def create_user_dict(user_list):
    result = {}
    for u in user_list.members:
        result[u.id] = User(u.name, u.profile.image_48) 
    return result

def create_channel_dict(channel_list):
    result = {}
    for c in channel_list.channels:
        result[c.name] = c.id
    return result

user_list = g('users.list', pretty=1)
user_dict = create_user_dict(user_list)

channel_list = g('channels.list')
channel_dict = create_channel_dict(channel_list)

print 'Uesr list'
for k, v in user_dict.iteritems():
    print '    %20s %20s' % (k, v.name)
print ''

print 'Channel list'
for k, v in channel_dict.iteritems():
    print '    %20s %20s' % (k, v)
print ''

h = g('channels.history', channel=channel_dict['general'], count=50)

for m in h.messages:
    print user_dict[m.user].name, ':', m.text


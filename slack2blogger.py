import urllib.request
import urllib.parse
#import urllib
import json
import datetime
from collections import namedtuple


SLACK_TOKEN = 'xoxp-11979191639-11979191655-11999522372-47a2833f03'

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)
def url2obj(u): return json2obj(urllib.urlopen(url).read().decode())

def g(api, **args):
    args['token'] = SLACK_TOKEN
    arg_str = urllib.parse.urlencode(args)
    url = 'https://slack.com/api/%s?%s' % (api, arg_str)
    return json2obj(urllib.request.urlopen(url).read().decode())

def j(api, **args):
    args['token'] = SLACK_TOKEN
    arg_str = urllib.parse.urlencode(args)
    url = 'https://slack.com/api/%s?%s' % (api, arg_str)
    return json.loads(urllib.request.urlopen(url).read().decode())


class User:
    def __init__(self, name, img):
        self.name = name
        self.img = img

def get_user_dict():
    """
    a dict {'user_id': 'user_name', ...}
    like   {'U282834': 'amber', ...}
    """
    user_list = g('users.list', pretty=1)    
    result = {}
    for u in user_list.members:
        result[u.id] = User(u.name, u.profile.image_48) 
    return result

def get_channel_dict():
    """
    a dict {'channel_id': 'chennel_name', ...}
    like   {'C324223422': 'gossip', ...}
    """
    channel_list = g('channels.list')
    result = {}
    for c in channel_list.channels:
        result[c.id] = c.name
    return result

def get_one_day_one_channel(year, month, day, channel):
    date = datetime.date(year, month, day)
    min_ts = datetime.datetime.combine(date, datetime.time.min).timestamp()
    max_ts = datetime.datetime.combine(date, datetime.time.max).timestamp()
    message_list = []

    while True:
        hist = j('channels.history',
                 channel=channel,
                 count=1000,
                 oldest=min_ts,
                 latest=max_ts,
                 inclusive=0)

        message_list.extend(hist['messages'])
        
        if hist['has_more']:
            max_ts = float(hist['messages'][-1]['ts'])
        else:
            break

    print('Channel "%s" %d messages' % (channel, len(message_list)))
    return message_list

def get_one_day(year, month, day, channel_list):
    result = {}
    for channel in channel_list:
        m_list = get_one_day_one_channel(year, month, day, channel)
        result[channel] = m_list
    return result

def get_and_write_one_day(year, month, day):
    channel_id_name_dict = get_channel_dict()
    channel_list = channel_id_name_dict.keys()
    fout = open('%d-%d-%d.txt' % (year, month, day), 'w', encoding='utf-8')
    channel_messages_dict = get_one_day(year, month, day, channel_list)
    json_str = json.dumps(channel_messages_dict, ensure_ascii=False, indent=2)
    fout.write(json_str)
    fout.close()

user_id_name_dict = get_user_dict()

get_and_write_one_day(2015, 10, 6)

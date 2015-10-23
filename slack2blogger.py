import re
import urllib.request
import urllib.parse
#import urllib
import json
import datetime
from collections import namedtuple


SLACK_TOKEN = 'xoxp-11979191639-11979191655-11999522372-47a2833f03'
URL_PATTERN = re.compile('<(https?://.*?)>')
USER_NAME_ID_PATTERN = re.compile('<.*?\|.*?>(.*)')

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
    result = {'USLACKBOT': User('slackbot', 'https://slack.global.ssl.fastly.net/66f9/img/slackbot_48.png')}
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

channel_id_name_dict = get_channel_dict()
user_id_name_dict = get_user_dict()
user_tag_raw_txt_map = {}
for k, v in user_id_name_dict.items():
    user_tag_raw_txt_map['<@%s>' % k] = '<div class="tag-user">@%s</div>' % v.name

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
    return json.loads(open('%04d-%02d-%02d.txt' % (year, month, day), encoding='utf-8').read())
    result = {}
    for channel in channel_list:
        m_list = get_one_day_one_channel(year, month, day, channel)
        result[channel] = m_list
    return result

def get_and_write_one_day_json(year, month, day):
    global user_id_name_dict
    global channel_id_name_dict

    print('Retrieving %04d/%02d/%02d' % (year, month, day))
    channel_list = channel_id_name_dict.keys()
    channel_messages_dict = get_one_day(year, month, day, channel_list)
    json_str = json.dumps(channel_messages_dict, ensure_ascii=False, indent=2)
    fout = open('%04d-%02d-%02d.txt' % (year, month, day), 'w', encoding='utf-8')
    fout.write(json_str)
    fout.close()

def format_msg_string(msg_txt):
    global user_tag_raw_txt_map
    for user_tag_raw_txt in user_tag_raw_txt_map:
        msg_txt = msg_txt.replace(user_tag_raw_txt, user_tag_raw_txt_map[user_tag_raw_txt])

    msg_txt = URL_PATTERN.sub('<a class="text-hyperlink" target="_blank" href="\\1">\\1</a>', msg_txt)
    msg_txt = USER_NAME_ID_PATTERN.sub('<div class="user-system-notify">\\1</div>', msg_txt)

    msg_txt = msg_txt.replace('\n', '<br>')
    return msg_txt

def convert_one_day_to_html(channel_messages_dict, year, month, day):
    global user_id_name_dict
    global channel_id_name_dict

    html ="""<html>
<head>
  <meta charset="UTF-8">
  <title>Sample document</title>
  <link rel="stylesheet" href="slack.css">
</head>
<body>
"""

    html += '<h1>%04d-%02d-%02d</h1>\n' % (year, month, day)
    for cid, messages in channel_messages_dict.items():
        html += '<h2>'
        html += channel_id_name_dict[cid]
        html += '</h2>\n\n'

        for msg in messages:
            html += '<div class="user-message">\n'

            user_name = user_id_name_dict[msg['user']].name
            user_image = user_id_name_dict[msg['user']].img
            msg_txt = format_msg_string(msg['text'])
            time_txt = datetime.datetime.fromtimestamp(float(msg['ts'])).strftime('%Y-%m-%d %H:%M:%S')

            html += '    <img class="user-image" src="' + user_image + '"/>\n'
            html += '    <div class="user-name">' + user_name + '</div>\n'
            html += '    <div class="time-stamp">' + time_txt + '</div>\n'
            html += '    <div class="messsage-text">' + msg_txt + '</div>\n'

            html += '</div>\n'

    html += "</body>\n</html>"
    return html

def get_and_write_one_day_html(year, month, day):
    global channel_id_name_dict

    print('Retrieving %04d/%02d/%02d' % (year, month, day))
    channel_list = channel_id_name_dict.keys()
    channel_messages_dict = get_one_day(year, month, day, channel_list)
    html_str = convert_one_day_to_html(channel_messages_dict, year, month, day)
    fout = open('%d-%d-%d.html' % (year, month, day), 'w', encoding='utf-8')
    fout.write(html_str)
    fout.close()

get_and_write_one_day_html(2015, 10, 17)

#get_and_write_one_day_json(2015, 10, 17)


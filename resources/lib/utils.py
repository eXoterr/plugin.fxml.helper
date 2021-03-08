import re
import cfscrape
import json
from urllib.parse import urlencode, urlparse
from uuid import getnode 
from defusedxml.cElementTree import fromstring
from xbmcaddon import Addon

def clear_styles(text):
    text = re.sub(r'(<style .?\>|.+<\/style>)|(<.*?>)', ' ', text, flags=re.S) 
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    text = text.replace('\r\n', '')
    return text

def get_mac():
    return ''.join(re.findall('..', '%012x' % getnode()))


def get_page(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return '{"title" : "youtube not supported"}'
    # if 'http://' not in url or 'https://' not in url:
    #     url = 'http://' + url
    if 'https://' in url:
        url = url.replace('https://', 'http://')
    scraper = cfscrape.create_scraper()
    if len(Addon().getSettingString('email')) > 0:
        page = scraper.get(url, params={"box_mac" : get_mac(), "box_user" : Addon().getSettingString('email')})
    else:
        page = scraper.get(url, params={"box_mac" : get_mac()})
    print(page.url)
    raw_page = page.text
    return [raw_page, page.url]

def get_stream(url, order, page_type):
    scraper = cfscrape.create_scraper()
    page = scraper.get(url, params={"box_mac" : get_mac()})
    raw_page = page.text
    if page_type == 'json':
        return json.loads(raw_page)['channels'][int(order)]['stream_url']
    elif page_type == 'xml':
        return fromstring(raw_page).findall('channel')[int(order)].find('stream_url').text

def do_search(url, request):
    if 'youtube.com' in url or 'youtu.be' in url:
        return '{"title" : "youtube not supported"}'
    # if 'http://' not in url or 'https://' not in url:
    #     url = 'http://' + url
    if 'https://' in url:
        url = url.replace('https://', 'http://')
    scraper = cfscrape.create_scraper()
    if len(Addon().getSettingString('email')) > 0:
        page = scraper.get(url, params={"search" : request, "box_mac" : get_mac(), "box_user" : Addon().getSettingString('email')})
    else:
        page = scraper.get(url, params={"search" : request, "box_mac" : get_mac()})
    raw_page = page.text
    return [raw_page, page.url]

def extract_msg_from_alert(msg):
    return re.split(r'alert\((.+)\)', msg)[1]

def fix_xml(xml_doc):
    #if '<?xml version="1.0"' not in xml_doc:
    return re.sub(r'(\s+\&\s+)|(\&nbsp;)|(\&gt;)|(\&copy;)|(\&quot;)|(\&rsquo;)', ' ', xml_doc)
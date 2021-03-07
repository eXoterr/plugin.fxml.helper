import re
import cfscrape
import json
from urllib.parse import urlencode, urlparse
from uuid import getnode 

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
    page = scraper.get(url, params={"box_mac" : get_mac()})
    print(page.url)
    raw_page = page.text
    return raw_page

def do_search(url, request):
    if 'youtube.com' in url or 'youtu.be' in url:
        return '{"title" : "youtube not supported"}'
    # if 'http://' not in url or 'https://' not in url:
    #     url = 'http://' + url
    if 'https://' in url:
        url = url.replace('https://', 'http://')
    scraper = cfscrape.create_scraper()
    page = scraper.get(url, params={"search" : request, "box_mac" : get_mac()})
    raw_page = page.text
    return raw_page

def extract_msg_from_alert(msg):
    return re.split(r'alert\((.+)\)', msg)[1]

def fix_xml(xml_doc):
    #if '<?xml version="1.0"' not in xml_doc:
    return re.sub(r'(\s+\&\s+)|(\&nbsp;)|(\&gt;)|(\&copy;)|(\&quot;)|(\&rsquo;)', ' ', xml_doc)
import re
from resources.lib import cfscrape
import json
from urllib.parse import urlencode, urlparse, quote_plus
from uuid import getnode 
from defusedxml.cElementTree import fromstring
from xbmcaddon import Addon
import requests
from xbmcgui import Dialog

def clear_styles(text):
    text = re.sub(r'(<style .?\>|.+<\/style>)|(<.*?>)', ' ', text, flags=re.S) 
    # text = text.replace('\n', '')
    # text = text.replace('\r', '')
    # text = text.replace('\r\n', '')
    text = text.replace('Установите Acestream или Torrserve', '') #fork-portal
    text = text.replace('Установите Ace Stream или Torrserve', '') #fork-portal
    text = re.sub(r' +', ' ', text)
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
    cookie = {"sid" : Addon().getSettingString('fork_cookie')}
    if Addon().getSettingBool('enable_proxy') == True:
        if Addon().getSettingInt('proxy_type') == 0:
            proxy_type = 'http'
        elif Addon().getSettingInt('proxy_type') == 1:
            proxy_type = 'socks4'
        elif Addon().getSettingInt('proxy_type') == 2:
            proxy_type = 'socks5'
        proxy = {proxy_type : Addon().getSettingString('proxy_url')}
    else:
        proxy = {}
    if len(Addon().getSettingString('email')) > 0:
        page = scraper.get(url, params={"box_mac" : get_mac(), "box_hardware" : "Kodi FXML Helper", "box_user" : Addon().getSettingString('email')}, cookies=cookie, proxies=proxy)
    else:
        page = scraper.get(url, params={"box_mac" : get_mac(), "box_hardware" : "Kodi FXML Helper"}, cookies=cookie, proxies=proxy)
    #print("requesting page: \""+page.url+"\"")
    raw_page = page.text
    return [raw_page, page.url, url]

def get_stream(url, order=0, page_type='', suborder=False, submenu=False):
    print("url is: ")
    print(url)
    scraper = cfscrape.create_scraper()
    if Addon().getSettingBool('enable_proxy') == True:
        if Addon().getSettingInt('proxy_type') == 0:
            proxy_type = 'http'
        elif Addon().getSettingInt('proxy_type') == 1:
            proxy_type = 'socks4'
        elif Addon().getSettingInt('proxy_type') == 2:
            proxy_type = 'socks5'
        proxy = {proxy_type : Addon().getSettingString('proxy_url')}
    else:
        proxy = {}
    if '{' in url:  
            res_raw = json.loads(url)
            resolutions = []
            for res in res_raw.keys():
                resolutions.append(res_raw[res])
            #print(type(resolutions[int(order)]))
            return resolutions[int(order)]['url']
    else:
        page = scraper.get(url, params={"box_mac" : get_mac(), "box_hardware" : "Kodi FXML Helper"}, proxies=proxy)
        raw_page = page.text
    if suborder != False:
        return json.loads(raw_page)['channels'][int(suborder)]['submenu'][int(order)]['stream_url']
    else:
        print("suborder is: "+str(suborder))
        if page_type == 'json':
            if 'channels' in json.loads(raw_page):
                return json.loads(raw_page)['channels'][int(order)]['stream_url']
            else:
                res_raw = json.loads(raw_page)
                resolutions = []
                for res in res_raw.keys():
                    resolutions.append(res_raw[res])
                #print(type(resolutions[int(order)]))
                return resolutions[int(order)]['url']
        elif page_type == 'xml':
            return fromstring(raw_page).findall('channel')[int(order)].find('stream_url').text
        elif page_type == "m3u":
            return url
        else:
            url = get_page(url)
            print(url)
            return url[0]
def do_search(url, request):
    if 'youtube.com' in url or 'youtu.be' in url:
        return '{"title" : "youtube not supported"}'
    # if 'http://' not in url or 'https://' not in url:
    #     url = 'http://' + url
    if 'https://' in url:
        url = url.replace('https://', 'http://')
    scraper = cfscrape.create_scraper()
    cookie = {"sid" : Addon().getSettingString('fork_cookie')}
    if Addon().getSettingBool('enable_proxy') == True:
        if Addon().getSettingInt('proxy_type') == 0:
            proxy_type = 'http'
        elif Addon().getSettingInt('proxy_type') == 1:
            proxy_type = 'socks4'
        elif Addon().getSettingInt('proxy_type') == 2:
            proxy_type = 'socks5'
        proxy = {proxy_type : Addon().getSettingString('proxy_url')}
    else:
        proxy = {}
    #print("requesting page: \""+page.url+"\"")
    if len(Addon().getSettingString('email')) > 0:
        page = scraper.get(url, params={"search" : request, "box_mac" : get_mac(), "box_hardware" : "Kodi FXML Helper", "box_user" : Addon().getSettingString('email')}, cookies=cookie, proxies=proxy)
    else:
        page = scraper.get(url, params={"search" : request, "box_mac" : get_mac(), "box_hardware" : "Kodi FXML Helper"}, cookies=cookie, proxies=proxy)
    raw_page = page.text
    return [raw_page, page.url, url]

def extract_msg_from_alert(msg):
    if re.match(r'alert\((.+)\)', msg):
        return re.split(r'alert\((.+)\)|cmd:info\((.+)\);', msg)[1]
    else:
        return re.split(r'alert\((.+)\)|cmd:info\((.+)\);', msg)[2]

def fix_xml(xml_doc):
    #if '<?xml version="1.0"' not in xml_doc:
    xml_doc = xml_doc.replace('</items></items>', '</items>')
    return re.sub(r'(\s+\&\s+)|(\&nbsp;)|(\&gt;)|(\&copy;)|(\&quot;)|(\&rsquo;)|(\<background-image\>.+\<\/background-image\>)|(\<typeList\>.+\<\/typeList\>)', ' ', xml_doc)

def correct_spaces(data):
    return data.replace('/', ' ')

def generate_static_url(item_type, url, url_type=0, order=0, page_type='json', subindex=False):
    if item_type == "stream":
        if subindex != False:
            url = f"plugin://plugin.fxml.helper/extract_and_play?order={order}&suborder_i={subindex}&submenu=True&url={url}&page_type={page_type}&url_type=0"
        else:
            url = f"plugin://plugin.fxml.helper/extract_and_play?order={order}&url={url}&page_type={page_type}&url_type=0"
    elif item_type == "magnet":
        url = f"plugin://plugin.fxml.helper/play_t?url_type={url_type}&hash={quote_plus(url)}&stream_id={order}"
    elif item_type == 'ace':
        url = f"plugin://plugin.fxml.helper/play?url={url_type}"
    return url

def get_warning(wid):
    if wid == "adult":
        return Addon().getLocalizedString(32080)

def colorize(text):
    if 'fhd' in text.lower():
        return f"[COLOR lime]{text}[/COLOR]"
    if 'hd' in text.lower():
        return f"[COLOR yellow]{text}[/COLOR]"
    if '4k' in text.lower():
        return f"[COLOR aqua]{text}[/COLOR]"
    if 'ads' in text.lower() or 'ad' in text.lower():
        return f"[COLOR orangered]{text}[/COLOR]"
    else:
        return text
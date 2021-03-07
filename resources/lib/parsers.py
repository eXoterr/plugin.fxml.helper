import cfscrape
import json
from resources.lib.utils import clear_styles, get_page, do_search, extract_msg_from_alert, fix_xml
import re
from defusedxml.ElementTree import parse, fromstring
from urllib.parse import urlencode, quote_plus

def parse_json(url, elements="", request=""):
    if url == 'submenu':
        print("elements---------=-")
        print(elements)

        parsed_page = json.loads(json.dumps(elements[0]))
    elif request != "":
        parsed_page = do_search(url, request)
    else:
        parsed_page = get_page(url)
    
    if '<items>' in parsed_page:
        parsed_page = parse_xml(parsed_page)
    elif '{' in parsed_page:
        parsed_page = json.loads(parsed_page)
    elif '#EXTM3U' in parsed_page:
        parsed_page = parse_m3u(parsed_page)

    # try:
    #     parsed_page = json.loads(parsed_page)
    # except json.JSONDecodeError:
    #     try:
    #         parsed_page = parse_xml(parsed_page)
    #     except:
    #         parsed_page = parse_m3u(parsed_page)

    final_data = []
    print(parsed_page)
    if 'channels' in parsed_page:
            
        #print(parse_elements)
        for channel in parsed_page['channels']:
            #print(channel)
            current_channel = {"poster" : ""}
            if 'description' in channel:
                current_channel.update({"desc" : clear_styles(channel['description'])})
            else:
                current_channel.update({"desc" : ""})
            if 'title' in channel:
                current_channel.update({"title" : clear_styles(channel['title'])})
            elif 'details' in channel and channel['details'] != False:
                if 'name' in channel['details']:
                    current_channel.update({"title" : clear_styles(channel['details']['name'])})
                elif 'title' in channel['details']:
                    current_channel.update({"title" : clear_styles(channel['details']['title'])})
                else:
                    current_channel.update({"title" : "No title"})
                if 'about' in channel['details']:
                    current_channel.update({"desc" : clear_styles(channel['details']['about'])})
                if 'poster' in channel['details']:
                    current_channel.update({"poster" : clear_styles(channel['details']['poster'])})
                if 'img' in channel['details']:
                    current_channel.update({"poster" : clear_styles(channel['details']['img'])})
                else:
                    current_channel.update({"poster" : ""})
            else:
                current_channel.update({"title" : "No title"})
            if 'playlist_url' in channel:
                if channel['playlist_url'] == 'submenu':
                    #print("submenu type is " + str(type(channel['submenu'])))
                    # print(type(channel['submenu']))
                    # print(channel['submenu'])
                    current_channel.update({"submenu" : {"channels" : channel['submenu']},  "url_type" : "submenu"})
                elif len(channel['playlist_url']) == 0:
                    current_channel.update({"url_type" : "alert", "msg" : clear_styles(channel['description'])})
                elif 'magnet:?xt=' in channel['playlist_url']:
                    current_channel.update({"url" : quote_plus(channel['playlist_url']), "url_type" : "magnet"})
                elif re.match(r'alert\((.+)\)', channel['playlist_url']) is not None:
                    current_channel.update({"url_type" : "alert", "msg" : extract_msg_from_alert(clear_styles(channel['playlist_url']))})
                else:
                    current_channel.update({"url" : channel['playlist_url'], "url_type" : "link"})
            elif 'details' in channel and channel['details'] != False and 'infohash' in channel['details']:
                current_channel.update({"url" : channel['details']['infohash'], "url_type" : "ace"})
            elif 'details' in parsed_page and parsed_page['details'] != False and 'magnet' in parsed_page['details']:
                current_channel.update({"url" : parsed_page['details']['magnet'], "url_type" : "magnet"})
                if 'details' in channel and channel['details'] != False and 'tor-1.1.77' in channel['details'] and 'id' in channel['details']['tor-1.1.77']:
                    current_channel.update({"stream_id" : channel['details']['tor-1.1.77']['id']})
            elif 'stream_url' in channel:
                if len(channel['stream_url']) == 0:
                    current_channel.update({"url_type" : "alert", "msg" : clear_styles(channel['description'])})
                elif '{' in channel['stream_url']:
                    streams = json.loads(channel['stream_url'])
                    streams_for_load = []
                    for quality in streams.keys():
                        streams_for_load.append({"title" : str(quality), "stream_url" : streams[str(quality)]['url']})
                    current_channel.update({"submenu" : {"channels" : streams_for_load},  "url_type" : "submenu"})
                elif channel['stream_url'] == 'md5hash':
                    if 'parser' in channel:
                        streams = json.loads(get_page(channel['parser']))
                        print(streams)
                        streams_for_load = []
                        for quality in streams.keys():
                            streams_for_load.append({"title" : str(quality), "stream_url" : streams[str(quality)]['url']})
                        current_channel.update({"submenu" : {"channels" : streams_for_load},  "url_type" : "submenu"})
                else:
                    current_channel.update({"url" : channel['stream_url'], "url_type" : "stream"})
            else:
                if 'description' in channel:
                    current_channel.update({"url_type" : "alert", "msg" : clear_styles(channel['description'])})
                else:
                    current_channel.update({"url_type" : "none"})
            if 'search_on' in channel:
                current_channel.update({"url_type" : "search"})
            if 'logo_30x30' in channel:
                current_channel.update({"icon" : channel['logo_30x30']})
            else:
                current_channel.update({"icon" : ""})

            final_data.append(current_channel)

        if 'next_page_url' in parsed_page and len(parsed_page['next_page_url']) > 0:
            final_data.append({"title" : "Next page >","icon" : "", "desc": "", "url" : parsed_page['next_page_url'], "url_type" : "link", "poster" : ""})

        print(final_data)
        return final_data


def parse_xml(page, submenu=False):

    # if submenu == True:
    #     xml_page = fromstring(page)
    #     channels = []
    #     for subelement in xmlpage.findall("submenu"):
    #         channels.append({subelement.tag : str(subelement.text)})
    #     print("-----channels----------")
    #     print(channels)
    #     return {"channels" : channels}

    xml_page = fromstring(page.encode())
    channels = []
    # for se in xml_page.findall('menu').findall("*"):
    #     print(se.tag)

    if xml_page.find('channel') is not None:
        for channel in xml_page.findall('channel'):
            current_channel = dict()
            for subelement in channel.findall("*"):
                #print(subelement.tag)
                if subelement.tag == "playlist_url" and str(subelement.text) == "submenu":
                    submenu_list = []
                    for element in channel.findall("submenu"):
                        submenu_dict = {}
                        for se in element.findall("*"):
                            submenu_dict.update({se.tag : clear_styles(str(se.text))})
                        submenu_list.append(submenu_dict)
                    print("submenu_dict ====")
                    print(submenu_list)
                    current_channel.update({"submenu" : submenu_list})
                else:
                    if subelement.tag != 'submenu':
                        #print(subelement.tag)
                        #print("is not submenu")
                        current_channel.update({subelement.tag : clear_styles(str(subelement.text))})
                if subelement.tag != 'submenu':
                    # print(subelement.tag)
                    # print("is not submenu")
                    current_channel.update({subelement.tag : clear_styles(str(subelement.text))})
            channels.append(current_channel)

    if xml_page.find('menu') is not None:
        for channel in xml_page.findall('menu'):
            current_channel = dict()
            for subelement in channel.findall("*"):
                #print(subelement.tag)
                if subelement.tag == "playlist_url" and str(subelement.text) == "submenu":
                    submenu_list = []
                    for element in channel.findall("submenu"):
                        submenu_dict = {}
                        for se in element.findall("*"):
                            submenu_dict.update({se.tag : clear_styles(str(se.text))})
                        submenu_list.append(submenu_dict)
                    print("submenu_dict ====")
                    print(submenu_list)
                    current_channel.update({"submenu" : submenu_list})
                else:
                    if subelement.tag != 'submenu':
                        #print(subelement.tag)
                        #print("is not submenu")
                        current_channel.update({subelement.tag : clear_styles(str(subelement.text))})
                if subelement.tag != 'submenu':
                    # print(subelement.tag)
                    # print("is not submenu")
                    current_channel.update({subelement.tag : clear_styles(str(subelement.text))})
            channels.append(current_channel)
        
    
            
    print("formed xml")
    print(channels)

    return {"channels" : channels}




            



    return {"channels" : channels}

def parse_m3u(playlist):
    playlist = re.sub(r'(#EXT.+\,)|(#EXT.+)', '', playlist)
    channels = []
    playlist_lines = playlist.splitlines()
    clean_lines = []
    for line in range(len(playlist_lines)):
        if playlist_lines[line] != '':
            clean_lines.append(playlist_lines[line])
    #print(len(clean_lines))
    for item in range(0, len(clean_lines) - 1, 2):
        if 'http://' in clean_lines[item+1] or 'https://' in clean_lines[item+1] or 'udp://' in clean_lines[item+1]:
            channels.append({"title" : clean_lines[item], "stream_url" : clean_lines[item+1]})
        else:
            channels.append({"title" : clean_lines[item+1], "stream_url" : clean_lines[item+2]})
        
    #print(channels)

    return {"channels" : channels}

def proceed_submenu(elements):
    pass
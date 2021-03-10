import routing
from xbmcgui import ListItem, Dialog, NOTIFICATION_INFO, NOTIFICATION_ERROR, NOTIFICATION_WARNING
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl
from xbmcaddon import Addon
from resources.lib.parsers import parse_json
from resources.lib.utils import get_page, get_stream, correct_spaces
import json
import sys
from xbmcvfs import translatePath
from xbmc import executebuiltin
from urllib.parse import quote_plus, unquote_plus
import os
import re


plugin = routing.Plugin() 

@plugin.route('/')
def index():

    listitem = ListItem("SpiderXML (search engine)")
    listitem.setArt({"icon" : "http://spiderxml.com/spidericon.png"})
    addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://spider.forkplayer.tv/search/?web=&onlyxml=1/", search=False), listitem=listitem, isFolder=True)
    
    listitem = ListItem("Forkplayer.tv Account")
    listitem.setArt({"icon" : "http://forkplayer.tv/favicon.ico"})
    addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://forkplayer.tv/xml/account.php?act=info/", search=False), listitem=listitem, isFolder=True)

    for i in range(1, 8):
        #print(Addon().getSettingString('menu'+str(i)))
        menu_item_json = Addon().getSettingString('menu'+str(i))
        if len(menu_item_json) > 0:
            menu_item = json.loads(menu_item_json)
            listitem = ListItem(menu_item['name']+" #"+str(i))
            listitem.setArt({"icon" : menu_item['icon']})
            listitem.addContextMenuItems([("Remove from menu", f'RunPlugin("plugin://plugin.fxml.helper/menu/remove?id={str(i)}")')])
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url=menu_item['url'], search=False), listitem=listitem, isFolder=True)
        else:
            print(menu_item_json+"is equal 0")


    # listitem = ListItem("SpiderXML")
    # listitem.setArt({"icon" : "http://spiderxml.com/spidericon.png"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://spiderxml.com/", search=False), listitem=listitem, isFolder=True)

    # listitem = ListItem("nserv")
    # listitem.setArt({"icon" : "http://cdn.nserv.host/logo/nserv.png"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://nserv.host:5300/", search=False), listitem=listitem, isFolder=True)

    # listitem = ListItem("CoolTV")
    # listitem.setArt({"icon" : "http://cltv.club/img/tvcool23.jpg"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://cltv.club/start/", search=False), listitem=listitem, isFolder=True)

    # listitem = ListItem("Lnka")
    # #listitem.setArt({"icon" : "https://images.vfl.ru/ii/1596805732/19e65e77/31279532.png"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://p.lnka.ru/", search=False), listitem=listitem, isFolder=True)

    # listitem = ListItem("KB team")
    # listitem.setArt({"icon" : "http://kb-team.club/no_save/logotip/kb_logo.png"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://kb-team.club/", search=False), listitem=listitem, isFolder=True)

    # listitem = ListItem("Vplay")
    # listitem.setArt({"icon" : "http://cdn.vplay.one/fork/logo.png"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://fork.vplay.one/", search=False), listitem=listitem, isFolder=True)

    # listitem = ListItem("test playlist")
    # #listitem.setArt({"icon" : "http://kb-team.club/no_save/logotip/kb_logo.png"})
    # addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="https://iptvm3u.ru/list.m3u", search=False), listitem=listitem, isFolder=True)
    
    endOfDirectory(plugin.handle)


@plugin.route('/play')
def play():
    if 'url_type' in plugin.args and int(plugin.args['url_type'][0]) == 2:
        files = json.loads(get_page(plugin.args['url'][0]))
        files_list = []
        for i in files['FileStats']:
            files_list.append(i['Path'])
        file_id = Dialog().select('Choose a file to play', files_list)
        listitem = ListItem()
        listitem.setPath(plugin.args['url'][0]+"&file="+str(file_id))
        setResolvedUrl(plugin.handle, True, listitem)
    else:
        listitem = ListItem()
        listitem.setPath(plugin.args['url'][0])
        setResolvedUrl(plugin.handle, True, listitem)
        


@plugin.route('/extract_and_play')
def extract_and_play():
    if int(plugin.args['url_type'][0]) == 2:
        files = json.loads(get_page(plugin.args['url'][0]))
        files_list = []
        for i in files['FileStats']:
            files_list.append(i['Path'])
        file_id = Dialog().select('Choose a file to play', files_list)
        listitem = ListItem()
        listitem.setPath(plugin.args['url'][0]+"&file="+str(file_id))
        setResolvedUrl(plugin.handle, True, listitem)
    else:
        listitem = ListItem()
        print(f"extracting stream {plugin.args['order'][0]} from {plugin.args['url'][0]} with page type {plugin.args['page_type'][0]}")
        listitem.setPath(get_stream(plugin.args['url'][0], plugin.args['order'][0], plugin.args['page_type'][0]))
        setResolvedUrl(plugin.handle, True, listitem)



@plugin.route('/open_json')
def open_json(request=''):
    print(plugin.args)
    if 'elements' in plugin.args and len(plugin.args['elements']) > 0:
        page = parse_json(plugin.args['url'][0], elements=plugin.args['elements'])
        plugin.args['url'][0] = "#"
    elif len(request) > 0:
        plugin.args['search'][0] = "False"
        page = parse_json(plugin.args['url'][0], request=request)
    else:
        page = parse_json(plugin.args['url'][0])
    
    if plugin.args['search'][0] == "True":
        return open_json(request=Dialog().input("Enter your data..."))
    for item in page:
        #print(item)
        if item['url_type'] == 'link':
            #print('render started')
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setInfo("video", {"plot" : item['desc']})
            listitem.addContextMenuItems([('Add as playlist', f'RunPlugin("plugin://plugin.fxml.helper/iptv/add?url={item["url"]}&handle={plugin.handle}")'),
                                            ('Add to main menu', f'RunPlugin("plugin://plugin.fxml.helper/menu/add?url={item["url"]}&handle={plugin.handle}&name={item["title"]}&icon={item["icon"]}")')])
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url=item['url'], search=False), listitem, isFolder=True)
        elif item['url_type'] == 'search':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url=item['url'], search=True), listitem, isFolder=True)
        elif item['url_type'] == 'submenu':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url='submenu', search=False, elements=json.dumps(item['submenu'])), listitem, isFolder=True)
        elif item['url_type'] == 'none':
            # listitem = ListItem(item['title'])
            # listitem.setArt({"icon" : item['icon']})
            # listitem.setArt({"poster" : item['poster']})
            # listitem.setInfo("video", {"plot" : item['desc']})
            # addDirectoryItem(plugin.handle, "", listitem=listitem, isFolder=False)
            pass
        elif item['url_type'] == 'stream':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={item["parent_page"]}&order={item["order"]}&page_type={item["page_type"]}&title={item["title"]}&item_type=stream&url_type=0")')])
            if item['page_type'] == "m3u":
                addDirectoryItem(plugin.handle, plugin.url_for(play, url=item['url'], url_type=0), listitem=listitem, isFolder=False)
            else:
                addDirectoryItem(plugin.handle, plugin.url_for(extract_and_play, url=item['parent_page'], order=item['order'] ,page_type=item['page_type'], url_type=0), listitem=listitem, isFolder=False)
        elif item['url_type'] == 'magnet':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            if Addon().getSettingInt('p2p_engine') == 0:
                listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={item["url"]}&order={item["stream_id"]}&title={quote_plus(item["title"])}&item_type=magnet&url_type=3")')])
                addDirectoryItem(plugin.handle, plugin.url_for(play, url="plugin://plugin.video.elementum/play?uri="+item['url'], url_type=3), listitem=listitem, isFolder=False)
            elif Addon().getSettingInt('p2p_engine') == 1:
                print(item)
                if 'stream_id' in item:
                    listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={item["url"]}&order={item["stream_id"]}&title={quote_plus(item["title"])}&item_type=magnet&url_type=1")')])
                    addDirectoryItem(plugin.handle, plugin.url_for(play_torr, hash=item['url'], url_type=1, stream_id=item['stream_id']), listitem=listitem, isFolder=False)
                else:
                    listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={item["url"]}&title={quote_plus(item["title"])}&item_type=magnet&url_type=2")')])
                    addDirectoryItem(plugin.handle, plugin.url_for(play_torr, hash=item['url'], url_type=2), listitem=listitem, isFolder=False)
            elif Addon().getSettingInt('p2p_engine') == 2:
                if 'stream_id' in item:
                    listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={item["url"]}&order={item["stream_id"]}&title={quote_plus(item["title"])}&item_type=magnet&url_type=1")')])
                    addDirectoryItem(plugin.handle, plugin.url_for(play_torr, hash=item['url'], url_type=1, stream_id=item['stream_id']), listitem=listitem, isFolder=False)
                else:
                    listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={item["url"]}&title={quote_plus(item["title"])}&item_type=magnet&url_type=2")')])
                    addDirectoryItem(plugin.handle, plugin.url_for(play_torr, hash=item['url'], url_type=2), listitem=listitem, isFolder=False)
        elif item['url_type'] == 'ace':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            #listitem.addContextMenuItems([('Add to kodi library', f'RunPlugin("plugin://plugin.fxml.helper/library/add?url={Addon().getSettingString("acestream_url")+"/ace/getstream?infohash="+item["url"]}&title={item["title"]}&item_type=ace")')])
            addDirectoryItem(plugin.handle, plugin.url_for(play, url=Addon().getSettingString('acestream_url')+"/ace/getstream?infohash="+item['url']), listitem=listitem, isFolder=False)
        elif item['url_type'] == 'alert':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"fanart" : item['background']})
            listitem.setArt({"poster" : item['poster']})
            #listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(alert, title=item['title'], msg=item['msg']), listitem=listitem, isFolder=False)

    endOfDirectory(plugin.handle)

@plugin.route('/play_t')
def play_torr():
    torr_ver = Addon().getSettingInt('p2p_engine')
    print("hash is: " + plugin.args['hash'][0])
    print("torr ver is: "+str(torr_ver))
    if '&title=' in plugin.args['hash'][0]:
        print("truncated \"title\" form hash")
        plugin.args['hash'][0] = re.sub(r'(\&title\=.+)', '', plugin.args['hash'][0])
    if 'url_type' in plugin.args and int(plugin.args['url_type'][0]) == 2:
        if torr_ver == 0:
            listitem = ListItem()
            listitem.setPath("plugin://plugin.video.elementum/play?uri="+plugin.args['hash'][0])
            
        elif torr_ver == 1:
            files = json.loads(get_page(Addon().getSettingString('torrserver_url')+'/torrent/play/?link='+plugin.args['hash'][0])[0])
            files_list = []
            for i in files['FileStats']:
                files_list.append(i['Path'])
            file_id = Dialog().select('Choose a file to play', files_list)
            listitem = ListItem()
            listitem.setPath(Addon().getSettingString("torrserver_url")+"/torrent/play/?link="+plugin.args["hash"][0]+"&file="+str(file_id))
            
        elif torr_ver == 2:
            files = json.loads(get_page(Addon().getSettingString('torrserver_url')+'/stream/fname?link='+plugin.args['hash'][0]+"&stat")[0])
            files_list = []
            for i in files['file_stats']:
                files_list.append(i['path'])
            file_id = Dialog().select('Choose a file to play', files_list)
            listitem = ListItem()
            listitem.setPath(Addon().getSettingString('torrserver_url')+"/stream/fname?link="+plugin.args['hash'][0]+"&index="+str(file_id + 1)+"&play")
        setResolvedUrl(plugin.handle, True, listitem)
    else:
        listitem = ListItem()
        if torr_ver == 0:
            listitem.setPath("plugin://plugin.video.elementum/play?uri="+plugin.args['hash'][0])
            
        elif torr_ver == 1:
            listitem.setPath(Addon().getSettingString('torrserver_url')+"/torrent/play/?link="+plugin.args['hash'][0]+"&file="+str(int(plugin.args['stream_id'][0])))
            
        elif torr_ver == 2:
            listitem.setPath(Addon().getSettingString('torrserver_url')+"/stream/fname?link="+plugin.args['hash'][0]+"&index="+str(int(plugin.args['stream_id'][0])+1)+"&play")
        setResolvedUrl(plugin.handle, True, listitem)


@plugin.route('/iptv/channels')
def iptv_channels():
    """Return JSON-STREAMS formatted data for all live channels"""
    from resources.lib.iptv import IPTVManager
    port = int(plugin.args.get('port')[0])
    IPTVManager(port).send_channels()



@plugin.route('/iptv/add')
def add_playlist():
    print(plugin.args)
    url = plugin.args['url'][0]
    menu_slots = []
    for slot in range(1, 8):
        current_slot = Addon().getSettingString('iptv'+str(slot))
        if len(current_slot) > 0:
            menu_slots.append(current_slot)
        else:
            menu_slots.append(f"Playlist {str(slot)}")
    order = str(Dialog().select("Select playlist slot", menu_slots) + 1)
    if Dialog().yesno("Are you sure?", f"Playlist will be added on slot {order}") == False:
        return False
    Addon().setSetting(id=str('iptv'+order), value=url)
    Dialog().notification("Success", "playlist added to slot " + order, NOTIFICATION_INFO)


@plugin.route('/menu/add')
def add_menu_portal():
    url = plugin.args['url'][0]
    name = plugin.args['name'][0]
    icon = plugin.args['icon'][0]
    menu_slots = []
    for slot in range(1, 8):
        current_slot = Addon().getSettingString('menu'+str(slot))
        if len(current_slot) > 0:
            current_slot = json.loads(current_slot)
            menu_slots.append(current_slot['name'])
        else:
            menu_slots.append(f"Menu slot {str(slot)}")
    order = str(Dialog().select("Select menu slot", menu_slots) + 1)
    if Dialog().yesno("Are you sure?", f"Portal will be added on slot {order}") == False:
        return False
    Addon().setSetting(id=str('menu'+order), value=json.dumps({"url" : url, "name" : name, "icon" : icon}))
    Dialog().notification("Success", "\""+name + "\" added to menu slot " + order, NOTIFICATION_INFO)


@plugin.route('/menu/remove')
def rem_menu_portal():
    order = plugin.args['id'][0]
    Addon().setSetting(id=str('menu'+order), value="")
    Dialog().notification("Success", "\""+order + "\" slot was removed", NOTIFICATION_INFO)

@plugin.route('/alert')
def alert():
    print(plugin.args)
    Dialog().ok(plugin.args['title'][0], str(plugin.args['msg'][0]))

@plugin.route('/do_auth')
def auth():
    login = Addon().getSettingString('email')
    password = Addon().getSettingString('password')
    if len(login) == 0 or len(password) == 0:
        return  Dialog().notification("Save settings!", "Enter your login and pass and save settings before trying to auth!", icon=NOTIFICATION_ERROR)
    response = json.loads(get_page(f"http://forkplayer.tv/xml/account.php?act=submit&login={login}&password={password}")[0])
    if 'error' in response:
        Dialog().notification("Error!", response['error'], icon=NOTIFICATION_ERROR)
    else:
        Addon().setSetting('fork_cookie', response['setcookie']['sid'])
        Dialog().notification("Success", "Authorised!", icon=NOTIFICATION_INFO)

@plugin.route('/library/add')
def add_to_lib():
    item_type = plugin.args['item_type'][0]
    if Dialog().yesno("Change default title?", f"Current title is \"{unquote_plus(plugin.args['title'][0])}\"") == True:
        title = Dialog().input("Enter new title...")
    else:
        title = unquote_plus(plugin.args['title'][0])
    if item_type == "stream":
        url = f"plugin://plugin.fxml.helper/extract_and_play?order={plugin.args['order'][0]}&url={plugin.args['url'][0]}&page_type={plugin.args['page_type'][0]}&url_type=0"
    elif item_type == "magnet":
        url = f"plugin://plugin.fxml.helper/play_t?url_type={plugin.args['url_type'][0]}&hash={plugin.args['url'][0]}&url_type={plugin.args['url_type'][0]}"
    elif item_type == 'ace':
        url = f"plugin://plugin.fxml.helper/play?url={plugin.args['url_type'][0]}"
    folder = Addon().getSettingString('library_folder')
    f = open(translatePath(os.path.join(folder, correct_spaces(title+".strm"))), "w")
    f.write(url)
    f.close()
    executebuiltin('UpdateLibrary("video")')
    Dialog().notification("Success", "Film added to kodi library", NOTIFICATION_INFO)


def run():
    plugin.run()
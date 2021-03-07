import routing
from xbmcgui import ListItem, Dialog, NOTIFICATION_INFO, NOTIFICATION_ERROR, NOTIFICATION_WARNING
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl
from xbmcaddon import Addon
from resources.lib.parsers import parse_json
from resources.lib.utils import get_page
import json
import sys

plugin = routing.Plugin() 

@plugin.route('/')
def index():

    listitem = ListItem("SpiderXML (search engine)")
    listitem.setArt({"icon" : "http://spiderxml.com/spidericon.png"})
    addDirectoryItem(plugin.handle, plugin.url_for(open_json, url="http://spiderxml.com/", search=False), listitem=listitem, isFolder=True)

    for i in range(1, 8):
        #print(Addon().getSettingString('menu'+str(i)))
        menu_item_json = Addon().getSettingString('menu'+str(i))
        if len(menu_item_json) > 0:
            menu_item = json.loads(menu_item_json)
            listitem = ListItem(menu_item['name']+" #"+str(i))
            listitem.setArt({"icon" : menu_item['icon']})
            listitem.addContextMenuItems([("Remove from menu", f'RunPlugin("plugin://plugin.fxml.helper/menu/remove?id={str(i)}")')])
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url=menu_item['url'], search=False), listitem=listitem, isFolder=True)

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
        listitem.setPath(plugin.args['url'][0])
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
        if item['url_type'] == 'link':
            #print('render started')
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setInfo("video", {"plot" : item['desc']})
            listitem.addContextMenuItems([('Add as playlist', f'RunPlugin("plugin://plugin.fxml.helper/iptv/add?url={item["url"]}&handle={plugin.handle}")'),
                                            ('Add to main menu', f'RunPlugin("plugin://plugin.fxml.helper/menu/add?url={item["url"]}&handle={plugin.handle}&name={item["title"]}&icon={item["icon"]}")')])
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url=item['url'], search=False), listitem, isFolder=True)
        elif item['url_type'] == 'search':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url=item['url'], search=True), listitem, isFolder=True)
        elif item['url_type'] == 'submenu':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(open_json, url='submenu', search=False, elements=json.dumps(item['submenu'])), listitem, isFolder=True)
        elif item['url_type'] == 'none':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, "", listitem=listitem, isFolder=False)
        elif item['url_type'] == 'stream':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(play, url=item['url'], url_type=0), listitem=listitem, isFolder=False)
        elif item['url_type'] == 'magnet':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            if Addon().getSettingInt('p2p_engine') == 0:
                addDirectoryItem(plugin.handle, plugin.url_for(play, url="plugin://plugin.video.elementum/play?uri="+item['url']), listitem=listitem, isFolder=False)
            elif Addon().getSettingInt('p2p_engine') == 1:
                if 'stream_id' in item:
                    addDirectoryItem(plugin.handle, plugin.url_for(play, url=Addon().getSettingString('torrserver_url')+"/torrent/play/?link="+item['url']+"&file="+item['stream_id'], url_type=1), listitem=listitem, isFolder=False)
                else:
                    addDirectoryItem(plugin.handle, plugin.url_for(play, url=Addon().getSettingString('torrserver_url')+"/torrent/play/?link="+item['url'], url_type=2), listitem=listitem, isFolder=False)
            elif Addon().getSettingInt('p2p_engine') == 2:
                pass
        elif item['url_type'] == 'ace':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(play, url=Addon().getSettingString('acestream_url')+"/ace/getstream?infohash="+item['url']), listitem=listitem, isFolder=False)
        elif item['url_type'] == 'alert':
            listitem = ListItem(item['title'])
            listitem.setArt({"icon" : item['icon']})
            listitem.setArt({"poster" : item['poster']})
            #listitem.setProperty("IsPlayable", "true")
            listitem.setInfo("video", {"plot" : item['desc']})
            addDirectoryItem(plugin.handle, plugin.url_for(alert, title=item['title'], msg=item['msg']), listitem=listitem, isFolder=False)

    endOfDirectory(plugin.handle)


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

def run():
    plugin.run()
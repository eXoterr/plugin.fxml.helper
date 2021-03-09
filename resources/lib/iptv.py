# -*- coding: utf-8 -*-
"""IPTV Manager Integration module"""

import json
import socket
from resources.lib.utils import get_page
from resources.lib.parsers import parse_json
from xbmcplugin import getSetting
from xbmcaddon import Addon


class IPTVManager:
    """Interface to IPTV Manager"""

    def __init__(self, port):
        """Initialize IPTV Manager object"""
        self.port = port

    def via_socket(func):
        """Send the output of the wrapped function to socket"""

        def send(self):
            """Decorator to send over a socket"""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', self.port))
            try:
                sock.sendall(json.dumps(func(self)).encode())
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self):
        """Return JSON-STREAMS formatted python datastructure to IPTV Manager"""
        #CHANNELS = get_page()
        if Addon().getSettingBool('merge') == True:
            pl_channels = []
            for pl in range(7):
                url = Addon().getSettingString('iptv'+str(pl+1))
                if len(url) == 0:
                    continue 
                channels = parse_json(url)
                for channel in channels:
                    pl_channels.append({"name" : channel['title'], "stream" : channel['url']})
        else:
            pl_channels = []
            url = Addon().getSettingString('iptv'+str(Addon().getSettingInt('active_playlist') + 1)) #will be changed in new settings format
            channels = parse_json(url)
            for channel in channels:
                #print(channel)
                pl_channels.append({"name" : channel['title'], "stream" : channel['url']})
        return dict(version=1, streams=pl_channels)
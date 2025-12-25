#twentytw93-KronosTeam
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import os
import urllib.parse as urlparse

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
HANDLE = int(sys.argv[1])
FANART = os.path.join(ADDON_PATH, "resources", "media", "kronos_shield.jpg")
MEDIA = os.path.join(ADDON_PATH, "resources", "media")

sys.path.append(ADDON_PATH)
from service import check_vpn_status, show_external_ip


def router(params):
    if "action" in params:
        if params["action"] == "check_vpn":
            check_vpn_status()
        elif params["action"] == "show_ip":
            show_external_ip()
    else:
        build_main_menu()


def build_main_menu():
    items = []

    li1 = xbmcgui.ListItem("[B]Check VPN Status[/B]")
    li1.setArt({"thumb": os.path.join(MEDIA, "check.png"), "fanart": FANART})
    url1 = sys.argv[0] + "?action=check_vpn"
    items.append((url1, li1, False))

    li2 = xbmcgui.ListItem("[B]Check External IP[/B]")
    li2.setArt({"thumb": os.path.join(MEDIA, "ip.png"), "fanart": FANART})
    url2 = sys.argv[0] + "?action=show_ip"
    items.append((url2, li2, False))

    for url, list_item, is_folder in items:
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

    xbmcplugin.endOfDirectory(HANDLE)


def parse_query():
    return dict(urlparse.parse_qsl(sys.argv[2][1:]))


params = parse_query()
router(params)
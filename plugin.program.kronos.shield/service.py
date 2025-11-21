#twentytw93-KronosTeam
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import time
import sys
import os
import threading
import urllib.request
import socket

ADDON_ID = 'plugin.program.kronos.shield'
PROTECTED_ADDONS = [
    'plugin.video.retrospect',
    'plugin.video.cumination',
    'plugin.video.watchnixtoons2',
    'plugin.video.elementum',
    'plugin.video.youtube',
    'plugin.audio.soundcloud',
    'plugin.audio.mp3streams',
    'pvr.iptvsimple'
]


def notify(title, message, icon_file, cooldown=8):
    if not hasattr(notify, "_last_shown"):
        notify._last_shown = {}
    now = time.time()
    key = (title, message)
    if key in notify._last_shown and now - notify._last_shown[key] < cooldown:
        return
    notify._last_shown[key] = now

    addon_path = xbmcvfs.translatePath('special://home/addons/plugin.program.kronos.shield')
    icon_path = os.path.join(addon_path, 'resources', 'media', icon_file)
    xbmc.executebuiltin(f'Notification({title},{message},4000,{icon_path})')

addon_path = xbmcaddon.Addon(ADDON_ID).getAddonInfo('path')
sys.path.append(os.path.join(addon_path, 'lib'))
from vpn_utils import is_vpn_active


def check_vpn_status():
    if is_vpn_active():
        xbmcgui.Dialog().ok("[B]Kronos Shield[/B]", "VPN is active. You’re protected.")
    else:
        xbmcgui.Dialog().ok("[B]Kronos Shield[/B]", "Warning: VPN not detected. Your real IP is exposed!")


def show_external_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=2) as response:
            ip = response.read().decode().strip()
        xbmcgui.Dialog().ok("[B]Kronos Shield[/B]", f"Your current external IP is:\n\n{ip}")
    except (Exception, socket.timeout):
        xbmcgui.Dialog().ok("[B]Kronos Shield[/B]", "Unable to fetch external IP.")


class VPNStartupCheck(threading.Thread):
    def run(self):
        mon = xbmc.Monitor()
        xbmc.log("[Kronos Shield] Delaying startup for 2 seconds...", xbmc.LOGINFO)
        if mon.waitForAbort(2):
            return

        dialog = xbmcgui.DialogProgress()
        dialog.create("[B]Kronos Shield[/B]", "Checking [B]VPN Tunnel[/B]...")

        retries = 3
        delay = 3

        for attempt in range(1, retries + 1):
            if is_vpn_active():
                dialog.update(100, "VPN Tunnel Detected!")
                dialog.close()
                notify('[B]Kronos Shield[/B]', 'VPN Tunnel is Active.', 'checkmark.png')
                return

            percent = int((attempt / retries) * 100)
            dialog.update(percent, f"Retrying... ({attempt}/{retries})")
            if mon.waitForAbort(delay):
                dialog.close()
                return

        dialog.close()
        notify('[B]Kronos Shield[/B]', 'VPN Tunnel is NOT Detected.', 'error.png')


class KronosShieldService(xbmc.Monitor):
    def __init__(self):
        super().__init__()
        self.player = xbmc.Player()

    def run(self):
        while not self.abortRequested():
            try:
                if self.player.isPlaying() and not is_vpn_active():
                    self.player.stop()
                    notify('[B]Kronos Shield[/B]', 'VPN Disconnected! Playback Stopped', 'error.png')

                current_plugin = xbmc.getInfoLabel('Container.PluginName')
                if current_plugin and current_plugin in PROTECTED_ADDONS:
                    if not is_vpn_active():
                        xbmc.executebuiltin('Dialog.Close(all,true)')
                        xbmcgui.Dialog().ok(
                            '[B]Kronos Shield[/B]',
                            'VPN Tunnel is NOT Detected!\nReturning To Home Screen.'
                        )
                        xbmc.executebuiltin('ActivateWindow(home)')
                        # replace hard sleep with abort-aware wait
                        self.waitForAbort(5)

            except Exception as e:
                xbmc.log(f"[Kronos Shield] Error: {str(e)}", xbmc.LOGERROR)

            self.waitForAbort(3)


def delayed_startup_check():
    mon = xbmc.Monitor()
    while not mon.abortRequested() and not xbmc.getCondVisibility("Window.IsVisible(home)"):
        if mon.waitForAbort(0.1):
            return
    if mon.waitForAbort(3.0):
        return
    while not mon.abortRequested() and (
        xbmc.getCondVisibility("Window.IsVisible(DialogBusy.xml)") or
        xbmc.getCondVisibility("System.HasActiveModalDialog")
    ):
        if mon.waitForAbort(0.1):
            return
    if mon.waitForAbort(1):
        return

    xbmc.log("[Kronos Shield] Claimdown engaged (1s)", xbmc.LOGINFO)
    if not mon.waitForAbort(1):
        VPNStartupCheck().start()


if __name__ == '__main__':
    t = threading.Thread(target=delayed_startup_check)
    t.daemon = True
    t.start()

    service = KronosShieldService()
    service.run()
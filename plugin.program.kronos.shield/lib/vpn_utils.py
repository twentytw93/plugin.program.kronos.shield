import os
import subprocess

def is_vpn_active():
    try:
        result = subprocess.check_output(['ip', 'addr'], text=True)
        return 'tun0' in result
    except Exception:
        return False
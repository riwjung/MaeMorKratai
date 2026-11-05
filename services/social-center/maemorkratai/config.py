import json
import os
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(os.environ.get('MAEMOR_DATA_DIR', Path.home() / 'AIVideoLocal/maemorkratai')).resolve()
VAULT = Path(os.environ.get('MAEMOR_VAULT_DIR', Path.home() / 'Desktop/AI_Video/MaeMorKratai')).resolve()
TZ = ZoneInfo('Asia/Bangkok')

def now():
    return datetime.now(TZ).isoformat(timespec='seconds')

def setup():
    for folder in ('data', 'data/snapshots', 'logs'):
        p = ROOT / folder
        p.mkdir(parents=True, exist_ok=True)
        p.chmod(0o700)

def settings():
    setup()
    p = ROOT / 'data/settings.json'
    return json.loads(p.read_text()) if p.exists() else {
        'api_version': '', 'page_id': '', 'ig_id': '', 'page_name': '',
        'expected_ig': 'maemorkratai', 'ig_username': '', 'permissions': [],
        'facebook_account_metrics': ['page_media_view'],
        'facebook_post_metrics': ['post_media_view'],
        'instagram_account_metrics': ['views', 'total_interactions'],
        'instagram_post_metrics': ['views', 'shares', 'saved', 'total_interactions', 'ig_reels_avg_watch_time'],
        'request_budget': 500,
    }

def save_settings(value):
    setup()
    if value.get('api_version') and not re.fullmatch(r'v\d{2}\.\d+', value['api_version']):
        raise ValueError('API version ต้องเป็นรูปแบบ vXX.X ตาม Meta App Dashboard')
    p = ROOT / 'data/settings.json'
    tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    tmp.chmod(0o600)
    tmp.replace(p)

class Secrets:
    """No plaintext fallback: macOS Keychain is mandatory."""
    service = 'maemorkratai.meta'

    @staticmethod
    def backend():
        import sys
        if sys.platform != 'darwin':
            raise RuntimeError('ระบบนี้ใช้ macOS Keychain สำหรับ token เท่านั้น')
        from keyring.backends.macOS import Keyring
        return Keyring()

    def get(self, name):
        return self.backend().get_password(self.service, name)

    def set(self, name, value):
        self.backend().set_password(self.service, name, value)

    def delete(self, name):
        from keyring.errors import PasswordDeleteError
        try:
            self.backend().delete_password(self.service, name)
        except PasswordDeleteError:
            pass

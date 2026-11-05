import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from .config import ROOT, now, setup

SECRET_KEYS = {'access_token', 'token', 'authorization', 'client_secret', 'app_secret', 'appsecret_proof'}

def redact(value, secrets=()):
    if isinstance(value, dict):
        return {k: redact(v, secrets) for k, v in value.items() if k.lower() not in SECRET_KEYS}
    if isinstance(value, list):
        return [redact(v, secrets) for v in value]
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(secret, '[REDACTED]')
        value = re.sub(r'(?i)((?:access_token|appsecret_proof|client_secret)=)[^&\s]+', r'\1[REDACTED]', value)
        return value
    return value

@contextmanager
def db():
    setup()
    conn = sqlite3.connect(ROOT / 'data/analytics.sqlite3', timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

def init():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS sources(
            id TEXT PRIMARY KEY, path TEXT NOT NULL, fetched_at TEXT NOT NULL,
            platform TEXT NOT NULL, endpoint TEXT NOT NULL, api_version TEXT, parameters TEXT,
            sha256 TEXT NOT NULL, kind TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS accounts(
            platform TEXT PRIMARY KEY, account_id TEXT NOT NULL, name TEXT,
            username TEXT, followers REAL, updated_at TEXT, source_id TEXT);
        CREATE TABLE IF NOT EXISTS posts(
            platform TEXT NOT NULL, account_id TEXT NOT NULL, post_id TEXT NOT NULL,
            published_at TEXT, text TEXT, media_type TEXT, permalink TEXT, source_id TEXT,
            updated_at TEXT, PRIMARY KEY(platform, account_id, post_id));
        CREATE TABLE IF NOT EXISTS comments(
            platform TEXT NOT NULL, account_id TEXT NOT NULL, comment_id TEXT NOT NULL,
            post_id TEXT NOT NULL, parent_id TEXT, text TEXT, created_at TEXT,
            source_id TEXT, PRIMARY KEY(platform, account_id, comment_id));
        CREATE TABLE IF NOT EXISTS metrics(
            platform TEXT NOT NULL, account_id TEXT NOT NULL, object_id TEXT NOT NULL,
            metric TEXT NOT NULL, native_metric TEXT NOT NULL, period TEXT NOT NULL,
            start_at TEXT NOT NULL DEFAULT '', end_at TEXT NOT NULL DEFAULT '',
            value REAL, unit TEXT NOT NULL DEFAULT 'count', status TEXT NOT NULL,
            source_id TEXT, observed_at TEXT NOT NULL,
            PRIMARY KEY(platform,account_id,object_id,metric,native_metric,period,start_at,end_at));
        CREATE TABLE IF NOT EXISTS coverage(
            platform TEXT NOT NULL, account_id TEXT NOT NULL, endpoint TEXT NOT NULL,
            metric TEXT NOT NULL DEFAULT '', status TEXT NOT NULL, detail TEXT,
            updated_at TEXT, PRIMARY KEY(platform,account_id,endpoint,metric));
        CREATE TABLE IF NOT EXISTS checkpoints(
            key TEXT PRIMARY KEY, cursor TEXT, complete INTEGER NOT NULL DEFAULT 0, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY, started_at TEXT, ended_at TEXT, status TEXT, message TEXT);
        CREATE TABLE IF NOT EXISTS imports(sha256 TEXT PRIMARY KEY, source_id TEXT, imported_at TEXT);
        ''')
        # Additive migration: keep existing posts/sources when upgrading the local app.
        columns = {r['name'] for r in c.execute('PRAGMA table_info(posts)')}
        for name in ('media_url', 'thumbnail_url'):
            if name not in columns:
                c.execute(f"ALTER TABLE posts ADD COLUMN {name} TEXT NOT NULL DEFAULT ''")

def media_url(value):
    """Keep only browser-safe Meta CDN references, never credential-bearing URLs."""
    if not isinstance(value, str):
        return ''
    try:
        parts = urlsplit(value)
        host = (parts.hostname or '').lower()
        trusted = any(host == domain or host.endswith('.' + domain)
                      for domain in ('fbcdn.net', 'cdninstagram.com', 'fbsbx.com'))
        if (parts.scheme != 'https' or not trusted or parts.username or parts.password
                or parts.port not in (None, 443)
                or any(k.lower() in SECRET_KEYS for k, _ in parse_qsl(parts.query))):
            return ''
        return value
    except ValueError:
        return ''

def snapshot(platform, endpoint, parameters, data, version='', kind='meta', secrets=()):
    setup()
    ident = uuid.uuid4().hex
    payload = redact({'platform': platform, 'endpoint': endpoint, 'parameters': parameters,
                      'api_version': version, 'fetched_at': now(), 'kind': kind, 'data': data}, secrets)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    p = ROOT / 'data/snapshots' / (ident + '.json')
    with p.open('xb') as f:
        f.write(encoded)
    p.chmod(0o600)
    with db() as c:
        c.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)',
                  (ident, str(p), payload['fetched_at'], platform, endpoint, version,
                   json.dumps(payload['parameters']), hashlib.sha256(encoded).hexdigest(), kind))
    return ident

def rows(query, params=()):
    with db() as c:
        return [dict(r) for r in c.execute(query, params)]

def account(platform, ident, name, username, followers, source):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO accounts VALUES(?,?,?,?,?,?,?)',
                  (platform, ident, name, username, followers, now(), source))
    if followers is not None:
        metric(platform, ident, ident, 'followers', 'followers_count', 'snapshot', '',
               now()[:10], followers, source)

def post(platform, account_id, item, source):
    ident = str(item['id'])
    with db() as c:
        c.execute('''INSERT INTO posts
                     (platform,account_id,post_id,published_at,text,media_type,permalink,source_id,updated_at,media_url,thumbnail_url)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?)
                     ON CONFLICT(platform,account_id,post_id) DO UPDATE SET
                     published_at=excluded.published_at,text=excluded.text,media_type=excluded.media_type,
                     permalink=excluded.permalink,source_id=excluded.source_id,updated_at=excluded.updated_at,
                     media_url=CASE WHEN excluded.media_url<>'' THEN excluded.media_url ELSE posts.media_url END,
                     thumbnail_url=CASE WHEN excluded.thumbnail_url<>'' THEN excluded.thumbnail_url ELSE posts.thumbnail_url END''',
                  (platform, account_id, ident, item.get('timestamp') or item.get('created_time'),
                   item.get('caption') or item.get('message') or '',
                   item.get('media_product_type') or item.get('media_type') or item.get('type') or 'POST',
                   item.get('permalink') or item.get('permalink_url') or '', source, now(),
                   media_url(item.get('media_url')), media_url(item.get('thumbnail_url') or
                      (item.get('media_url') if item.get('media_type')=='IMAGE' else ''))))

def comment(platform, account_id, post_id, item, source, parent_id=''):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO comments VALUES(?,?,?,?,?,?,?,?)',
                  (platform, account_id, str(item['id']), post_id, parent_id,
                   item.get('text') or item.get('message') or '',
                   item.get('timestamp') or item.get('created_time'), source))

def metric(platform, account_id, object_id, name, native, period, start, end, value, source,
           status='available', unit='count'):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO metrics VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (platform, account_id, object_id, name, native, period, start or '', end or '',
                   value, unit, status, source, now()))

def coverage(platform, account_id, endpoint, status, detail='', name=''):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO coverage VALUES(?,?,?,?,?,?,?)',
                  (platform, account_id, endpoint, name, status, detail, now()))

def checkpoint(key):
    found = rows('SELECT * FROM checkpoints WHERE key=?', (key,))
    return found[0] if found else {'cursor': None, 'complete': 0}

def save_checkpoint(key, cursor, complete):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO checkpoints VALUES(?,?,?,?)', (key, cursor, int(complete), now()))

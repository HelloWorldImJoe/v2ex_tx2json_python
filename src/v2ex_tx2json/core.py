"""Core implementation for v2ex_tx2json

Provides TX2JSON class with a parse(tx) method.
"""
from typing import Optional, Tuple, Dict
import re
import urllib.parse
import urllib.request

FIELD_TR_RE = re.compile(r'<tr>\s*<td[^>]*>\s*([^<]+)\s*</td>\s*<td[^>]*>(.*?)</td>\s*</tr>', re.S)
IMG_TAG_RE = re.compile(r'<img[^>]*>', re.S)
IMG_SRC_RE = re.compile(r'\bsrc="([^"]+)"')
IMG_ALT_RE = re.compile(r'\balt="([^"]+)"')

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.6',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://v2ex.com',
    'priority': 'u=0, i',
    'referer': 'https://v2ex.com/solana/tx',
    'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'python-urllib/3',
}


def build_headers(base_url: str) -> dict:
    h = dict(HEADERS)
    base = base_url.rstrip('/')
    h['origin'] = base
    h['referer'] = f'{base}/solana/tx'
    return h


def http_post(url: str, data: dict, headers: dict) -> Tuple[int, bytes]:
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        return resp.getcode(), resp.read()


def extract_avatar_and_name(td_html: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    img_tag_m = IMG_TAG_RE.search(td_html)
    username = None
    avatar = None
    uid = None
    if img_tag_m:
        tag = img_tag_m.group(0)
        alt = IMG_ALT_RE.search(tag)
        src = IMG_SRC_RE.search(tag)
        if alt:
            username = alt.group(1).strip()
        if src:
            avatar = src.group(1).strip()
        data_uid = re.search(r'data-uid="([^"]+)"', tag)
        if data_uid:
            uid = data_uid.group(1).strip()

    if not username:
        text = re.sub(r'<[^>]+>', ' ', td_html)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            parts = text.split()
            username = parts[-1]

    return username, avatar, uid


def extract_fields_from_html(html: str) -> Optional[Dict]:
    fields = {}
    for m in FIELD_TR_RE.finditer(html):
        key = m.group(1).strip()
        val_html = m.group(2).strip()
        fields[key] = val_html

    if '交易哈希' not in fields and 'Transaction Hash' not in fields:
        return None

    tx_hash_html = fields.get('交易哈希') or fields.get('Transaction Hash')
    tx_hash = re.sub(r'<[^>]+>', '', tx_hash_html).strip()

    sender_html = fields.get('发送方') or fields.get('Sender') or ''
    receiver_html = fields.get('接收方') or fields.get('Receiver') or ''

    sender_name, sender_avatar, sender_uid = extract_avatar_and_name(sender_html)
    receiver_name, receiver_avatar, receiver_uid = extract_avatar_and_name(receiver_html)

    token_type = re.sub(r'<[^>]+>', '', fields.get('代币类型') or fields.get('Token Type') or '').strip() or None
    token_address = re.sub(r'<[^>]+>', '', fields.get('Token Account') or fields.get('Token Account') or '').strip() or None
    amount = re.sub(r'<[^>]+>', '', fields.get('数额') or fields.get('Amount') or '').strip() or None
    send_time = re.sub(r'<[^>]+>', '', fields.get('发送时间') or fields.get('Time') or '').strip() or None
    memo = re.sub(r'<[^>]+>', '', fields.get('附言（只对发送者或者接收者可见）') or fields.get('Memo') or '').strip() or None

    amount_value = None
    if amount:
        m = re.search(r'([-+]?[0-9]*\.?[0-9]+)', amount.replace(',', ''))
        if m:
            try:
                amount_value = float(m.group(1))
            except Exception:
                amount_value = None

    return {
        'tx_hash': tx_hash,
        'sender': {
            'username': sender_name,
            'avatar': sender_avatar,
            'uid': sender_uid,
        },
        'receiver': {
            'username': receiver_name,
            'avatar': receiver_avatar,
            'uid': receiver_uid,
        },
        'token_type': token_type,
        'token_address': token_address,
        'amount': amount,
        'amount_value': amount_value,
        'time': send_time,
        'memo': memo,
    }


class TX2JSON:
    """Client for fetching and parsing tx pages into JSON-like dicts.

    Usage:
        client = TX2JSON(base_url, cookie)
        info = client.parse(tx)
    """

    def __init__(self, base_url: str, cookie: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.cookie = cookie

    def fetch_html_for_tx(self, tx: str) -> Optional[str]:
        headers = build_headers(self.base_url)
        if self.cookie:
            headers['Cookie'] = self.cookie
        post_url = f'{self.base_url}/solana/tx'
        try:
            code, body = http_post(post_url, {'tx': tx}, headers)
            if code == 200 and body:
                html = body.decode('utf-8', errors='ignore')
                if '接收方' in html or 'Receiver' in html:
                    return html
        except Exception:
            return None
        return None

    def parse(self, tx: str) -> Optional[Dict]:
        html = self.fetch_html_for_tx(tx)
        if not html:
            return None
        return extract_fields_from_html(html)
"""Core implementation for v2ex_tx2json

Provides TX2JSON class with a parse(tx) method.
"""
from typing import Optional, Tuple, Dict
import re
import urllib.parse
import urllib.request
import os

FIELD_TR_RE = re.compile(r'<tr>\s*<td[^>]*>\s*([^<]+)\s*</td>\s*<td[^>]*>(.*?)</td>\s*</tr>', re.S)
IMG_TAG_RE = re.compile(r'<img[^>]*>', re.S)
IMG_SRC_RE = re.compile(r'\bsrc="([^"]+)"')
IMG_ALT_RE = re.compile(r'\balt="([^"]+)"')

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.6',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://v2ex.com',
    'priority': 'u=0, i',
    'referer': 'https://v2ex.com/solana/tx',
    'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'python-urllib/3',
}


def build_headers(base_url: str) -> dict:
    h = dict(HEADERS)
    base = base_url.rstrip('/')
    h['origin'] = base
    h['referer'] = f'{base}/solana/tx'
    return h


def http_post(url: str, data: dict, headers: dict) -> Tuple[int, bytes]:
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        return resp.getcode(), resp.read()


def extract_avatar_and_name(td_html: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    img_tag_m = IMG_TAG_RE.search(td_html)
    username = None
    avatar = None
    uid = None
    if img_tag_m:
        tag = img_tag_m.group(0)
        alt = IMG_ALT_RE.search(tag)
        src = IMG_SRC_RE.search(tag)
        if alt:
            username = alt.group(1).strip()
        if src:
            avatar = src.group(1).strip()
        data_uid = re.search(r'data-uid="([^"]+)"', tag)
        if data_uid:
            uid = data_uid.group(1).strip()

    if not username:
        text = re.sub(r'<[^>]+>', ' ', td_html)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            parts = text.split()
            username = parts[-1]

    return username, avatar, uid


def extract_fields_from_html(html: str) -> Optional[Dict]:
    fields = {}
    for m in FIELD_TR_RE.finditer(html):
        key = m.group(1).strip()
        val_html = m.group(2).strip()
        fields[key] = val_html

    if '交易哈希' not in fields and 'Transaction Hash' not in fields:
        return None

    tx_hash_html = fields.get('交易哈希') or fields.get('Transaction Hash')
    tx_hash = re.sub(r'<[^>]+>', '', tx_hash_html).strip()

    sender_html = fields.get('发送方') or fields.get('Sender') or ''
    receiver_html = fields.get('接收方') or fields.get('Receiver') or ''

    sender_name, sender_avatar, sender_uid = extract_avatar_and_name(sender_html)
    receiver_name, receiver_avatar, receiver_uid = extract_avatar_and_name(receiver_html)

    token_type = re.sub(r'<[^>]+>', '', fields.get('代币类型') or fields.get('Token Type') or '').strip() or None
    token_address = re.sub(r'<[^>]+>', '', fields.get('Token Account') or fields.get('Token Account') or '').strip() or None
    amount = re.sub(r'<[^>]+>', '', fields.get('数额') or fields.get('Amount') or '').strip() or None
    send_time = re.sub(r'<[^>]+>', '', fields.get('发送时间') or fields.get('Time') or '').strip() or None
    memo = re.sub(r'<[^>]+>', '', fields.get('附言（只对发送者或者接收者可见）') or fields.get('Memo') or '').strip() or None

    amount_value = None
    if amount:
        m = re.search(r'([-+]?[0-9]*\.?[0-9]+)', amount.replace(',', ''))
        if m:
            try:
                amount_value = float(m.group(1))
            except Exception:
                amount_value = None

    return {
        'tx_hash': tx_hash,
        'sender': {
            'username': sender_name,
            'avatar': sender_avatar,
            'uid': sender_uid,
        },
        'receiver': {
            'username': receiver_name,
            'avatar': receiver_avatar,
            'uid': receiver_uid,
        },
        'token_type': token_type,
        'token_address': token_address,
        'amount': amount,
        'amount_value': amount_value,
        'time': send_time,
        'memo': memo,
    }


class TX2JSON:
    """Client for fetching and parsing tx pages into JSON-like dicts.

    Usage:
        client = TX2JSON(base_url, cookie)
        info = client.parse(tx)
    """

    def __init__(self, base_url: str, cookie: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.cookie = cookie

    def fetch_html_for_tx(self, tx: str) -> Optional[str]:
        headers = build_headers(self.base_url)
        if self.cookie:
            headers['Cookie'] = self.cookie
        post_url = f'{self.base_url}/solana/tx'
        try:
            code, body = http_post(post_url, {'tx': tx}, headers)
            if code == 200 and body:
                html = body.decode('utf-8', errors='ignore')
                if '接收方' in html or 'Receiver' in html:
                    return html
        except Exception:
            return None
        return None

    def parse(self, tx: str) -> Optional[Dict]:
        html = self.fetch_html_for_tx(tx)
        if not html:
            return None
        return extract_fields_from_html(html)

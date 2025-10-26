import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from v2ex_tx2json.core import extract_fields_from_html, TX2JSON


def sample_html():
    # Minimal HTML that matches the FIELD_TR_RE used by the parser
    return '''
    <table>
      <tr><td>交易哈希</td><td><code><a>abcd1234</a></code></td></tr>
      <tr><td>发送方</td><td><img src="https://example.com/avatar.png" alt="alice" data-uid="1001" /> Alice</td></tr>
      <tr><td>接收方</td><td><img src="https://example.com/avatar2.png" alt="bob" data-uid="1002" /> Bob</td></tr>
      <tr><td>代币类型</td><td>SOL</td></tr>
      <tr><td>数额</td><td>1.2345 SOL</td></tr>
      <tr><td>发送时间</td><td>2025-10-26 12:00:00</td></tr>
      <tr><td>附言（只对发送者或者接收者可见）</td><td>test memo</td></tr>
    </table>
    '''


def test_extract_fields_from_html_basic():
    html = sample_html()
    info = extract_fields_from_html(html)
    assert info is not None
    assert info['tx_hash'] == 'abcd1234'
    assert info['sender']['username'] == 'alice'
    assert info['sender']['avatar'] == 'https://example.com/avatar.png'
    assert info['sender']['uid'] == '1001'
    assert info['receiver']['username'] == 'bob'
    assert info['token_type'] == 'SOL'
    assert info['amount_value'] == pytest.approx(1.2345)
    assert info['memo'] == 'test memo'


def test_tx2json_parse_monkeypatch(monkeypatch):
    html = sample_html()

    def fake_fetch(self, tx):
        return html

    monkeypatch.setattr(TX2JSON, 'fetch_html_for_tx', fake_fetch)

    client = TX2JSON('https://v2ex.com')
    info = client.parse('dummy_tx')
    assert info is not None
    assert info['tx_hash'] == 'abcd1234'

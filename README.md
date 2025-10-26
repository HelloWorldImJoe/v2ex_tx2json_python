# v2ex_tx2json
将 solana 的 tx 解析为 JSON 数据.

快速开始:

```python
from v2ex_tx2json import TX2JSON

client = TX2JSON("https://v2ex.com", cookie="your_cookie_here")
info = client.parse("<tx_hash_here>")
print(info)
```
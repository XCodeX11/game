import os
import json
import time
import random
import requests
import base64
from urllib.parse import urlparse
U_A = os.environ.get("URL_A")
U_B = os.environ.get("URL_B")
K_A = os.environ.get("KEY_A")
K_B = os.environ.get("KEY_B")
K_C = os.environ.get("KEY_C")
K_D = os.environ.get("KEY_D")
K_E = os.environ.get("KEY_E")
K_F = os.environ.get("KEY_F")
K_G = os.environ.get("KEY_G")
K_H = os.environ.get("KEY_H")
K_I = os.environ.get("KEY_I")
H_D = os.environ.get("HDR_DEV")
def a(x):
    y = []
    if isinstance(x, dict):
        if K_A in x and isinstance(x[K_A], list):
            for item in x[K_A]:
                u = item.get(K_B, "")
                if "/DETAIL/" in u:
                    p = u.split("/DETAIL/")[1]
                    val = ""
                    for char in p:
                        if char.isdigit():
                            val += char
                        else:
                            break
                    if val:
                        y.append(int(val))
        meta = x.get(K_C, {})
        if isinstance(meta, dict):
            ct = meta.get(K_D, "")
            ot = meta.get(K_E, "")
            cid = meta.get(K_F)
            if (ct == K_G or ot == K_G) and isinstance(cid, int):
                y.append(cid)
        for v in x.values():
            y.extend(a(v))
    elif isinstance(x, list):
        for item in x:
            y.extend(a(item))
    return list(dict.fromkeys(y))

def b():
    urls = [
        os.environ.get("P_URL_1", ""),
        os.environ.get("P_URL_2", ""),
        os.environ.get("P_URL_3", "")
    ]
    p_list = []
    for u in urls:
        if not u:
            continue
        try:
            res = requests.get(u, timeout=12)
            if res.status_code == 200:
                for line in res.text.strip().split("\n"):
                    clean = line.strip().replace("http://", "").replace("https://", "")
                    parts = clean.split(":")
                    if len(parts) == 2 and parts[0].replace(".", "").isdigit() and parts[1].isdigit():
                        p_list.append(clean)
        except:
            continue
    return list(dict.fromkeys(p_list))

def c(tok, i):
    pat = os.environ.get("GH_PAT")
    tr = os.environ.get("TARGET_REPO")
    ep = os.environ.get("GH_API")
    if not pat or not tr or not ep:
        return False
    api = ep.format(repo=tr)
    headers = {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    content_bytes = json.dumps({"timestamp": int(time.time()), "id": i, "token": tok}, indent=2).encode('utf-8')
    enc = base64.b64encode(content_bytes).decode('utf-8')
    sha = None
    res = requests.get(api, headers=headers)
    if res.status_code == 200:
        sha = res.json().get("sha")
    payload = {
        "message": f"update {int(time.time())}",
        "content": enc,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha
    put_res = requests.put(api, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

def d():
    h = {
        "origin": os.environ.get("ORIG_URL", ""),
        "referer": os.environ.get("REF_URL", ""),
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        os.environ.get("HDR_VIA_KEY", ""): H_D
    }
    try:
        res = requests.get(U_A, headers=h, timeout=15)
        if res.status_code != 200:
            return
        data = res.json()
    except:
        return

    ids = a(data)
    if not ids:
        return

    p_pool = b()
    if not p_pool:
        return

    random.shuffle(p_pool)
    idx = 0
    max_r = 10

    for target in ids:
        t_url = U_B.format(id=target)
        retries = 0
        while retries < max_r and idx < len(p_pool):
            node = p_pool[idx]
            idx += 1
            proxies = {
                "http": f"http://{node}",
                "https": f"http://{node}"
            }
            
            ip_attempts = 0
            success = False
            while ip_attempts < 2:
                try:
                    r = requests.get(t_url, headers=h, proxies=proxies, timeout=6)
                    if r.status_code != 200:
                        ip_attempts = 2
                        break
                    r_json = r.json()
                    v_url = r_json.get(K_H, {}).get(K_I, "")
                    if v_url and any(ext in v_url.lower() for ext in os.environ.get("EXT_LIST", "").split(",")):
                        if any(k in v_url for k in os.environ.get("TOK_KEYS", "").split(",")):
                            parsed = urlparse(v_url)
                            tok = parsed.query
                            if c(tok, target):
                                return
                    ip_attempts = 2
                    success = True
                except:
                    ip_attempts += 1 
            
            if not success:
                retries += 1

if __name__ == "__main__":
    d()

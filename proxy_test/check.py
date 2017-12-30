import requests

def check_proxy(proxy, name=None):

    proxies = {
        'http': proxy,
        'https': proxy
    }
    try:
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=15, verify=False)
        if r.status_code == 200:
            return True
    except Exception as e:
        return False

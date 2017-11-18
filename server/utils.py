from urllib.parse import urlparse

def is_url(url):
    if not url:
        return False
    parse_res = urlparse(url)
    return bool(parse_res.scheme and parse_res.netloc)

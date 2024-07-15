from typing import Union
import requests
import httpx

class CookieManager:

    _cookies:dict
    
    def __init__(self, cookie_path:str='./cookie') -> None:
        self._cookie_path = cookie_path
        self._cookies = {}

        try:
            open(cookie_path, 'r')
            self._load_cookies()
        except: pass

    def __del__(self):
        self._save_cookies()
        
    def add_cookies(self, cookies:dict) -> None:
        self._cookies.update(cookies)

    def get_cookie(self, k:str) -> str:
        return self._cookies.get(k, '')

    def _set_cookies(self, r:Union[requests.Response, httpx.Response]) -> None:
        if isinstance(r, requests.Response):
            self._cookies.update(r.cookies.get_dict())
        elif isinstance(r, httpx.Response):
            self._cookies.update(dict(r.cookies))
        ...

    def _reset_cookies(self, keys:list=[]) -> None:
        self._cookies = {k: self._cookies[k] for k in keys}
    
    def _save_cookies(self) -> None:
        try:
            open(self._cookie_path, 'w').write('\n'.join(['{}={}'.format(k, v) for k, v in self._cookies.items()]))
        except:
            ...
        
    def _load_cookies(self) -> dict:
        for l in open(self._cookie_path, 'r').readlines():
            _idx = l.index('=')
            self._cookies.update({l[:_idx]: l[_idx+1:].rstrip()})
import json
import random
import string

from typing import BinaryIO, Union

import requests
from requests_toolbelt import MultipartEncoder

class SessionManager:
    """
    Session Manager
    """

    history:list[requests.Response] = []

    def __init__(self, cookie_path:str='./cookie', history_mode:bool=False) -> None:
        self._headers = { 'User-Agent': 'Mozilla/5.0' }
        self._cookies = {}
        self._cookie_path = cookie_path
        self._mode = history_mode
        
        try:
            open(cookie_path, 'r')
            self._load_cookies()
        except: pass

    def __del__(self):
        self._save_cookies()
    
    # ------------------------------------------------------------------------
    # Request Management
    def get(self, url:str, headers:dict={}, cookies:dict={}, **kwargs) -> requests.Response:
        r = self._request(url, headers=headers, cookies=cookies, method='get', **kwargs)

        if self._mode:
            self.history.append(r)
        return r

    def post(self, url:str, headers:dict={}, cookies:dict={}, 
                data:Union[str, dict]={}, files:dict[str]={}, 
                no_parsing:bool=False, **kwargs) -> requests.Response:
        
        r = self._request(url, headers=headers, cookies=cookies, data=data, files=files, 
                          no_parsing=no_parsing, method='post', **kwargs)

        if self._mode:
            self.history.append(r)
        return r
    
    def put(self, url:str, headers:dict={}, cookies:dict={}, 
                 data:Union[str, dict, list]={}, files:dict[str]={}, **kwargs):
        r = self._request(url, headers=headers, cookies=cookies, data=data, files=files, method='put', **kwargs)

        if self._mode:
            self.history.append(r)
        return r

    def _request(self, url:str, headers:dict={}, cookies:dict={}, 
                 data:Union[str, dict]={}, files:dict[str]={}, 
                 method:str='post', no_parsing:bool=False, **kwargs) -> requests.Response:
        """
        request

        method = get, post, put
        files -> {key: file_path}
        """
        headers = {k.lower(): headers[k] for k in headers}

        type_header = {}
        if data and not no_parsing:
            # charset?
            type_header['content-type'] = 'application/x-www-form-urlencoded'\
                if type(data) == str else 'application/json;charset=UTF-8'

        if method.lower() == 'post':
            if files:
                boundary = '----WebKitFormBoundary' +\
                    ''.join(random.sample(string.ascii_letters + string.digits, 16))
                data = MultipartEncoder(fields={**data, **{k: self.get_file_form(v) for k, v in files.items()}}, boundary=boundary)
                headers = {**headers, 'content-type': data.content_type, "connection": "keep-alive"}

            r = requests.post(url, headers={**self._headers, **type_header, **headers}, 
                              cookies={**self._cookies, **cookies}, 
                              data=data if type(data) in [str, MultipartEncoder] or no_parsing else json.dumps(data), **kwargs)
        elif method.lower() == 'get':
            r = requests.get(url, headers={**self._headers, **type_header, **headers}, 
                             cookies={**self._cookies, **cookies}, **kwargs)
        elif method.lower() == 'put':
            r = requests.put(url, headers={**self._headers, **type_header, **headers}, 
                             cookies={**self._cookies, **cookies}, data=json.dumps(data), **kwargs)
        
        self._set_cookies(r)
        return r
    
    # ------------------------------------------------------------------------
    # Cookie Management
    def add_cookies(self, cookies:dict) -> None:
        self._cookies.update(cookies)

    def get_cookie(self, k:str) -> str:
        return self._cookies.get(k, '')

    def _set_cookies(self, r:requests.Response) -> None:
        self._cookies.update(dict(r.cookies))

    def _reset_cookies(self, keys:list=[]) -> None:
        self._cookies = {k: self._cookies[k] for k in keys}
    
    def _save_cookies(self) -> None:
        open(self._cookie_path, 'w').write('\n'.join(['{}={}'.format(k, v) for k, v in self._cookies.items()]))
        
    def _load_cookies(self) -> dict:
        for l in open(self._cookie_path, 'r').readlines():
            _idx = l.index('=')
            self._cookies.update({l[:_idx]: l[_idx+1:].rstrip()})

    # ------------------------------------------------------------------------
    # Utils
    @staticmethod
    def get_file_form(f:str) -> tuple[str, BinaryIO]:
        """
        change file path to requestable formats
        """
        fn = f.split('/').pop()
        ext = fn.split('.').pop()
        mime_type = ''
        if ext in ['jpg', 'jpeg']:
            mime_type = 'image/jpeg'
        elif ext == 'png':
            mime_type = 'image/png'
        elif ext == 'xlsx':
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif ext == 'xls':
            mime_type = 'application/vnd.ms-excel'
        elif ext == 'zip':
            mime_type = 'application/x-zip-compressed'

        return fn, open(f, 'rb'), mime_type

if __name__ == '__main__':
    s = SessionManager()
    # s.get()
    # s.post()
    # s.put()

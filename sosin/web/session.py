import random
import string

from typing import BinaryIO, Union

import requests
from requests_toolbelt import MultipartEncoder

from .cookie import CookieManager
from sosin.utils.history import HistoryManager

class SessionManager(CookieManager):
    """
    Session Manager
    """

    def __init__(self, 
                 cookie_path:str=None, 
                 history_mode:bool=False
                 ) -> None:
        super().__init__(cookie_path)
        self._headers = { 'User-Agent': 'Mozilla/5.0' }
        self.history_manager = HistoryManager() if history_mode else None
    
    # ------------------------------------------------------------------------
    # Request Management
    def get(self, 
            url:str, 
            headers:dict={}, 
            cookies:dict={},
            params:dict={}, 
            **kwargs
            ) -> requests.Response:
        
        r = self._request(url, 
                          headers=headers, cookies=cookies, params=params, 
                          method='get', **kwargs)
        return r

    def post(self, 
             url:str, 
             headers:dict={}, 
             cookies:dict={}, 
             params:dict={},
             data:Union[str, dict]={}, 
             json:Union[dict, list]=None, 
             files:dict[str]={}, 
             **kwargs
             ) -> requests.Response:
        
        r = self._request(url, 
                          headers=headers, cookies=cookies, params=params, 
                          data=data, json=json, files=files, 
                          method='post', **kwargs)
        return r
    
    def put(self, 
            url:str, 
            headers:dict={}, 
            cookies:dict={}, 
            params:dict={},
            data:Union[str, dict, list]={}, 
            json:Union[dict, list]=None, 
            files:dict[str]={}, 
            **kwargs
            ) -> requests.Response:
        
        r = self._request(url, 
                          headers=headers, cookies=cookies, params=params,
                          data=data, json=json, files=files, 
                          method='put', **kwargs)
        return r

    def patch(self, 
              url:str, 
              headers:dict={}, 
              cookies:dict={}, 
              params:dict={},
              data:Union[str, dict, list]={}, 
              json:Union[dict, list]=None, 
              files:dict[str]={}, 
              **kwargs
              ) -> requests.Response:
        
        r = self._request(url, 
                          headers=headers, cookies=cookies, params=params,
                          data=data, json=json, files=files, 
                          method='patch', **kwargs)
        return r
    
    def delete(self, 
               url:str, 
               headers:dict={}, 
               cookies:dict={}, 
               params:dict={},
               data:Union[str, dict, list]={}, 
               json:Union[dict, list]=None, 
               files:dict[str]={}, 
               **kwargs
               ) -> requests.Response:
        
        r = self._request(url, 
                          headers=headers, cookies=cookies, params=params,
                          data=data, json=json, files=files, 
                          method='delete', **kwargs)
        return r

    def _request(self, 
                 url:str, 
                 headers:dict={}, 
                 cookies:dict={}, 
                 params:dict={},
                 data:Union[str, dict]={}, 
                 json:Union[dict, list]={}, 
                 files:dict[str]={}, 
                 method:str='post', 
                 **kwargs
                 ) -> requests.Response:
        """
        files -> {key: file_path}
        """
        
        headers = {k.lower(): headers[k] for k in headers}

        type_header = {}
        if data:
            type_header['content-type'] = 'application/x-www-form-urlencoded'
        if json:
            type_header['content-type'] = 'application/json;charset=UTF-8'
        if files:
            boundary = '----WebKitFormBoundary' +\
                ''.join(random.sample(string.ascii_letters + string.digits, 16))
            data = MultipartEncoder(fields={**data, **{k: self.get_file_form(v) for k, v in files.items()}}, boundary=boundary)
            type_header['content-type'] = data.content_type
            type_header['connection'] = 'keep-alive'

        if method.lower() == 'get':
            r = requests.get(url, 
                             headers={**self._headers, **type_header, **headers},
                             cookies={**self._cookies, **cookies}, 
                             params=params, **kwargs)
        elif method.lower() == 'post':
            r = requests.post(url, 
                              headers={**self._headers, **type_header, **headers}, 
                              cookies={**self._cookies, **cookies},
                              params=params, data=data, json=json, **kwargs)
        elif method.lower() == 'put':
            r = requests.put(url, 
                             headers={**self._headers, **type_header, **headers}, 
                             cookies={**self._cookies, **cookies},
                             params=params, data=data, json=json, **kwargs)
        elif method.lower() == 'patch':
            r = requests.patch(url, 
                             headers={**self._headers, **type_header, **headers}, 
                             cookies={**self._cookies, **cookies},
                             params=params, data=data, json=json, **kwargs)
        elif method.lower() == 'delete':
            r = requests.delete(url, 
                             headers={**self._headers, **type_header, **headers}, 
                             cookies={**self._cookies, **cookies},
                             params=params, data=data, json=json, **kwargs)

        self._set_cookies(r)
        self._add_history(r)

        return r
    
    # ------------------------------------------------------------------------
    # History Functions
    def _add_history(self, r):
        if self.history_manager:
            self.history_manager.add_history(r)
    
    def get_histories(self) -> list:
        return self.history_manager.get_histories() if self.history_manager else []
    
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

import random
import string

from typing import BinaryIO, Union

import httpx
from requests_toolbelt import MultipartEncoder

from .cookie import CookieManager
from sosin.utils.history import HistoryManager

class AsyncSessionManager(CookieManager):
    """
    Session Manager
    """

    history:list[httpx.Response] = []

    def __init__(self, cookie_path:str=None, history_mode:bool=False, timeout:int=5) -> None:
        self._headers = { 'User-Agent': 'Mozilla/5.0' }
        super().__init__(cookie_path)
        self.history_manager = HistoryManager() if history_mode else None
        self.timeout = httpx.Timeout(timeout)

    # ------------------------------------------------------------------------
    # Request Management
    async def get(self, 
                  url:str, 
                  headers:dict={}, 
                  cookies:dict={}, 
                  params:dict={}, 
                  **kwargs
                  ) -> httpx.Response:
        
        r = await self._request(url, headers=headers, cookies=cookies, params=params,
                                method='get', **kwargs)
        return r

    async def post(self, 
                   url:str, 
                   headers:dict={}, 
                   cookies:dict={}, 
                   params:dict={},
                   data:Union[str, dict]={}, 
                   json:Union[dict, list]=None, 
                   files:dict[str]={}, 
                   **kwargs
                   ) -> httpx.Response:
        
        r = await self._request(url, headers=headers, cookies=cookies, params=params, 
                                data=data, files=files, json=json,
                                method='post', **kwargs)
        return r
    
    async def put(self, 
                  url:str, 
                  headers:dict={}, 
                  cookies:dict={}, 
                  params:dict={},
                  data:Union[str, dict, list]={}, 
                  json:Union[dict, list]=None, 
                  files:dict[str]={}, **kwargs
                  ) -> httpx.Response:
        
        r = await self._request(url, 
                                headers=headers, cookies=cookies, params=params, 
                                data=data, json=json, files=files, 
                                method='put', **kwargs)
        return r

    async def patch(self, 
                    url:str, 
                    headers:dict={}, 
                    cookies:dict={}, 
                    params:dict={},
                    data:Union[str, dict, list]={}, 
                    json:Union[list, dict]=None, 
                    files:dict[str]={}, 
                    **kwargs
                    ) -> httpx.Response:
        
        r = await self._request(url, 
                                headers=headers, cookies=cookies, params=params, 
                                data=data, json=json, files=files, 
                                method='patch', **kwargs)
        return r
    async def delete(self, 
                     url:str, 
                     headers:dict={}, 
                     cookies:dict={}, 
                     params:dict={},
                     data:Union[str, dict, list]={}, 
                     json:Union[list, dict]=None, 
                     files:dict[str]={}, 
                     **kwargs
                     ) -> httpx.Response:
        
        r = await self._request(url, 
                                headers=headers, cookies=cookies, params=params, 
                                data=data, json=json, files=files, 
                                method='delete', **kwargs)
        return r

    async def _request(self, 
                       url:str, 
                       headers:dict={}, 
                       cookies:dict={}, 
                       params:dict={}, 
                       data:Union[str, dict]={}, 
                       json:Union[dict, list]=None, 
                       files:dict[str]={}, 
                       method:str='post', 
                       **kwargs
                       ) -> httpx.Response:
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

        async with httpx.AsyncClient(verify=kwargs.pop('verify', True), timeout=self.timeout) as client:
            if method.lower() == 'get':
                r = await client.get(url, 
                                     headers={**self._headers, **type_header, **headers}, 
                                     cookies={**self._cookies, **cookies}, 
                                     params=params, **kwargs)
            elif method.lower() == 'post':
                r = await client.post(url, 
                                      headers={**self._headers, **type_header, **headers},
                                      cookies={**self._cookies, **cookies},
                                      params=params, data=data, json=json, **kwargs)
            elif method.lower() == 'put':
                r = await client.put(url, 
                                     headers={**self._headers, **type_header, **headers},
                                     cookies={**self._cookies, **cookies}, 
                                     params=params, data=data, json=json, **kwargs)
            elif method.lower() == 'patch':
                r = await client.patch(url, 
                                       headers={**self._headers, **type_header, **headers}, 
                                       cookies={**self._cookies, **cookies}, 
                                       params=params, data=data, json=json, **kwargs)
            elif method.lower() == 'delete':
                r = await client.delete(url, 
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
    s = AsyncSessionManager()
    # s.get()
    # s.post()
    # s.put()

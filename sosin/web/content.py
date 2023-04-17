import requests

headers = {
    'user-agent': 'Mozilla/5.0'
}

class WebContentManager:
    """
    Web Content Manager
    download(path)
    get_content_type() -> image/jpeg, image/png, ...
    get_body() -> binary content
    """
    def __init__(self, url, method:str='get', add_headers:dict={}, add_body:dict={}) -> None:
        if method.lower()=='get':
            r = requests.get(url, headers={**headers, **add_headers})
        else:
            r = requests.post(url, headers={**headers, **add_headers}, body=add_body)
        r.raise_for_status()
        self.r = r

    def download(self, file_path:str):
        with open(file_path, 'wb') as f:
            f.write(self.get_body())
    
    def get_content_type(self):
        return self.r.headers['content-type']
    
    def get_body(self):
        return self.r.content

if __name__ == '__main__':
    wfm = WebContentManager('https://media.classicmanager.com/album/aac/MM014-2/01.m4a')

    wfm.download('./music.m4a')

    wfm.get_content_type()

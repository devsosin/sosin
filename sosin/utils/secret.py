
def read_config(config_path:str, splitter:str='=', encoding=None) -> dict:
    """
    config 파일 읽고 반환
    config_path = 파일 경로
    splitter = 구분 기호
    """
    temp = {}
    with open(config_path, 'r', encoding=encoding) as f:
        for l in f.readlines():
            idx = l.find(splitter)
            k, v = l[:idx], l[idx+1:].rstrip()
            temp[k] = v
    return temp
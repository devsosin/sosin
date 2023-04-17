from datetime import datetime

def logging(t, log_path='./debug.log'):
    """
    log를 생성합니다.
    default path = ./debug.log
    """
    dt_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', encoding='UTF-8') as f:
        f.write(f'{dt_now} : {t}\n')

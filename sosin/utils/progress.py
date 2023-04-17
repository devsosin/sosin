def progressBar(current, total, barLength=100):
    """
    진행상황을 출력합니다.
    current - 현재 값 
    total - 전체 값
    """
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

if __name__ == '__main__':
    import time
    total = 20
    for i in range(total+1):
        progressBar(i, total)
        time.sleep(0.5)
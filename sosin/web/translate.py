import time
try:
    from sosin.web.virtual import VirtualDriver, By, WebDriverWait, EC
except:
    pass

def papago(txts:list[str]) -> list[str]:
    
    """
    파파고 번역기
    """
    webdriver = VirtualDriver()
    webdriver.set_argument()
    driver = webdriver.get_driver()
    driver.execute_script("window.open('https://papago.naver.com/')")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    result = []
    for txt in txts:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, 'txtSource'))).send_keys(txt)
        target_text = ''
        while True:
            # 충분히 번역할때까지 재확인
            time.sleep(2)
            if target_text == driver.find_element(By.ID, 'txtTarget').text:
                result.append(target_text)
                driver.find_element(By.ID, 'txtSource').clear()
                break
            target_text = driver.find_element(By.ID, 'txtTarget').text
        
    driver.quit()
    return result
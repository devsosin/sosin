# python -m pip install selenium
# python -m pip install webdriver-manager

# ---------------------------------------------------------------------------------------------
# Selnium Setting
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except:
    raise ImportError('you need to install selenium, webdriver-manager\n$ : python -m pip install selenium\n$ : python -m pip install webdriver-manager')

class VirtualDriver:
    """
    Selenium VirtualDriver
    """
    def __init__(self, engine='chrome') -> None:
        self.engine = engine.lower().strip()
        if self.engine  == 'chrome':
            self.options = webdriver.ChromeOptions()
        
    def set_argument(self, headless=True, linux=True, maximize=True, 
                        user_agent=False, lang_kr=False, secret_mode=False, download_path=None):
        """
        셀레니움 드라이버 옵션 설정
        headless: GUI 사용 안함
        gui: GUI 사용안할 시 추가
        maximize: 브라우저 최대화
        lang_kr: 한국어 설정
        secret_mode: 시크릿 모드
        download_path: headless 시 파일 다운로드 경로 설정
        """

        # 시스템에 부착된 ... 로그 제거
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

        if headless:
            self.options.add_argument('--headless')

            if linux:
                # Bypass OS security model
                self.options.add_argument('--no-sandbox')
                self.options.add_argument("--disable-gpu")
                # overcome limited resource problems. 메모리가 부족해서 에러가 발생하는 것 막음
                self.options.add_argument('--disable-dev-shm-usage')
                
                # 크롬 드라이버에 setuid를 하지 않음으로써 크롬의 충돌 막음
                self.options.add_argument('--disable-setuid-sandbox')

                # disabling extensions
                self.options.add_argument("--disable-extensions")

                # 일단 좀 더 확인 필요
                self.options.add_argument('--single-process')

            if download_path:
                p = {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
                }
                self.options.add_experimental_option("prefs", p)

        if maximize:
            self.options.add_argument("--start-maximized")
        if user_agent:
            self.options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")
        if lang_kr:
            self.options.add_argument("--lang=ko_KR")
        if secret_mode:
            self.options.add_argument("--incognito")

    def get_driver(self) -> webdriver.Chrome:
        """
        셀레니움 웹드라이버 실행
        """
        if self.engine == 'chrome':
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            driver.maximize_window()
            driver.implicitly_wait(5)
            return driver


# ---------------------------------------------------------------------------------------------
# Selenium Utils
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

MAX_RETRY_COUNT = 5
def click_alert(d):
    """
    알림창 처리
    """
    retry = 0
    while True:
        try:
            Alert(d).accept()
            break
        except:
            time.sleep(1)
            retry+=1

        if retry == MAX_RETRY_COUNT:
            # 에러 발생
            assert False, '알림창 클릭 실패 !!'

# WebDriver 클래스로 webdriver 객체를 생성했다고 가정
if __name__ == '__main__':
    # 1. 예외처리문 활용
    try:
        driver = webdriver.get_driver()

        """
        Code Blocks
        """
    except Exception as e:
        print(e)
    finally:
        driver.quit()

    # 2. 클래스의 생성자, 소멸자 활용
    class MyWeb:
        def __init__(self):
            self.driver = webdriver.get_driver()
            
        def __del__(self):
            self.driver.quit()

    """
    Code Blocks
    """

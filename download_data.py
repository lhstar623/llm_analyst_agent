import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_livebench_leaderboard():
    # 1. 브라우저 설정 (Headless 모드)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 화면 없이 실행 (디버깅 시 주석 처리)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Mac Apple Silicon 사용 시 간혹 필요한 설정
    chrome_options.add_argument("--window-size=1920,1080") 

    print("Step 1: 브라우저를 실행합니다...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 2. 사이트 접속
        url = "https://livebench.ai/#/"
        driver.get(url)
        print(f"Step 2: {url} 에 접속 중...")

        # 3. 데이터 로딩 대기 (SPA이므로 데이터가 렌더링될 때까지 기다려야 함)
        # 테이블의 헤더나 특정 요소가 뜰 때까지 최대 20초 대기
        # 보통 테이블 태그나 특정 클래스를 기다립니다. 
        print("Step 3: 데이터 렌더링을 기다리는 중...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # 데이터가 다 로드되도록 잠시 더 안전하게 대기 (네트워크 상황 고려)
        time.sleep(5) 

        # 4. HTML 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 5. 테이블 찾기
        table = soup.find('table')
        if not table:
            print("Error: 테이블을 찾을 수 없습니다.")
            return

        # 6. 헤더 추출
        headers = []
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                headers.append(th.get_text(strip=True))
        else:
            # thead가 없는 경우 첫 번째 tr을 헤더로 가정
            rows = table.find_all('tr')
            for th in rows[0].find_all(['td', 'th']):
                headers.append(th.get_text(strip=True))

        print(f"헤더 발견: {headers}")

        # 7. 데이터 행 추출
        data = []
        tbody = table.find('tbody')
        rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]

        for row in rows:
            cols = row.find_all('td')
            cols = [ele.get_text(strip=True) for ele in cols]
            if cols:  # 빈 행 제외
                # 헤더 길이와 데이터 길이가 다른 경우(숨김 컬럼 등) 처리
                if len(cols) == len(headers):
                    data.append(cols)
                else:
                    # 길이가 안 맞을 경우 일단 넣거나, 로직에 따라 조정
                    # 보통 리더보드는 모델명 포함 일부 컬럼이 복잡할 수 있음
                    data.append(cols)

        # 8. 데이터프레임 생성 및 저장
        df = pd.DataFrame(data, columns=headers if len(data[0]) == len(headers) else None)
        
        # CSV 저장
        output_file = "livebench_leaderboard.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n성공! 데이터가 '{output_file}'로 저장되었습니다.")
        print(f"수집된 모델 수: {len(df)}")
        print(df.head())

    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_livebench_leaderboard()
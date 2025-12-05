import time
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def scrape_livebench_leaderboard():
    url = "https://livebench.ai/#/"

    print("Step 1: 브라우저 실행 (Playwright / Chromium)")
    with sync_playwright() as p:
        # Chromium 브라우저 실행 (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Step 2: {url} 접속 중...")
        page.goto(url, wait_until="networkidle")

        print("Step 3: 데이터 렌더링 대기...")
        time.sleep(5)  # SPA 렌더링 대기 (LiveBench는 JS 렌더링이 느림)

        html = page.content()
        browser.close()

    print("Step 4: HTML 파싱 중...")
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if not table:
        print("❌ Error: 테이블을 찾을 수 없음")
        print("HTML 일부:")
        print(soup.prettify()[:2000])
        return

    # Step 5: 헤더 추출
    headers = []
    thead = table.find("thead")
    if thead:
        for th in thead.find_all("th"):
            headers.append(th.get_text(strip=True))
    else:
        # thead 없는 경우 첫 tr을 헤더로 사용
        rows = table.find_all("tr")
        for th in rows[0].find_all(["td", "th"]):
            headers.append(th.get_text(strip=True))

    print(f"헤더 발견: {headers}")

    # Step 6: 데이터 추출
    data = []
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]

    for row in rows:
        cols = row.find_all("td")
        cols = [ele.get_text(strip=True) for ele in cols]
        if cols:
            data.append(cols)

    if not data:
        print("❌ Error: 데이터 행 없음")
        return

    # Step 7: DataFrame 생성
    df = pd.DataFrame(data, columns=headers if len(data[0]) == len(headers) else None)

    # Step 8: CSV 저장
    output_file = "livebench_leaderboard.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n🎉 성공! 데이터가 '{output_file}' 로 저장되었습니다.")
    print(f"📌 수집된 모델 수: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    scrape_livebench_leaderboard()

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import requests

def init_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式提升性能
    options.add_argument('--disable-gpu')
    return webdriver.Chrome(service=service, options=options)

def is_valid_response(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def crawl_magnets(avName, start, end, output_file, error_file):
    driver = init_driver()
    wait = WebDriverWait(driver, 15)  # 延长等待时间
    
    with open(output_file, 'a', encoding='utf-8') as f_out, open(error_file, 'a', encoding='utf-8') as f_err:
        for i in range(start, end + 1):
            avURL = f"https://www.javbus.com/{avName}-{i}"
            if not is_valid_response(avURL):
                f_err.write(f"{avName}-{i} error\n")
                print(f"[SKIPPED] {avName}-{i}: Invalid response")
                continue
            
            try:
                driver.get(avURL)
                time.sleep(1)  # 基础防封间隔
                
                magnet = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'a[href^="magnet"]')
                    )
                ).get_attribute('href')
                
                f_out.write(f"{magnet}\n")
                print(f"[SUCCESS] {avName}-{i}")
                
            except WebDriverException as e:
                f_err.write(f"{avName}-{i} {type(e).__name__}\n")
                print(f"[FAILED] {avName}-{i}: {type(e).__name__}")
                continue
                
            except Exception as e:
                f_err.write(f"{avName}-{i} error\n")
                print(f"[ERROR] {avName}-{i}: Unexpected error")
                continue
                
    driver.quit()

if __name__ == "__main__":
    avName = "shkd"
    avStartID = 381      # 起始ID
    avEndID = 500     # 结束ID
    batch_size = 10   # 每批处理量
    
    output_file = os.path.join(os.path.dirname(__file__), f"{avName}.txt")
    error_file = os.path.join(os.path.dirname(__file__), f"{avName}_error.txt")
    
    # 分批处理避免内存溢出
    for batch_start in range(avStartID, avEndID + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, avEndID)
        crawl_magnets(avName, batch_start, batch_end, output_file, error_file)
        print(f"已完成批次 {batch_start}-{batch_end}")




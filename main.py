import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def send_telegram(message, photo_path=None):
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not token or not chat_id:
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})
    
    if photo_path and os.path.exists(photo_path):
        url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(photo_path, "rb") as f:
            requests.post(url_photo, data={"chat_id": chat_id}, files={"photo": f})

def main():
    options = Options()
    if os.getenv("GITHUB_ACTIONS"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    # 增加隐式等待基础配置
    driver.implicitly_wait(10)

    try:
        driver.get("https://www.vortexa.cloud/dashboard")
        wait = WebDriverWait(driver, 20)
        
        # 1. 处理 Cookie 弹窗
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All')]")))
            cookie_btn.click()
        except:
            pass

        # 2. 输入信息
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(os.getenv("USER_EMAIL"))
        driver.find_element(By.ID, "password").send_keys(os.getenv("USER_PASSWORD"))

        # 3. 点击登录
        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Sign In')]")
        submit_btn.click()

        # 4. 关键：等待登录完成
        # 登录成功后，页面通常会跳转，或者原页面的 "Sign In" 按钮消失/转圈停止
        # 我们等待 URL 发生变化，或者等待页面进入登录后的状态
        print("正在等待登录完成...")
        time.sleep(5) # 强制给一点响应时间
        
        # 等待直到登录按钮从 DOM 中消失或不可见，说明请求已提交并跳转
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[contains(., 'Sign In')]")))
        
        # 额外等待跳转，确保 Cookie 已经写入
        wait.until(lambda d: d.current_url != "https://www.vortexa.cloud/dashboard")
        
        driver.save_screenshot("screenshot.png")

        # 5. 登录后获取状态
        driver.get("https://api.vortexa.cloud/api/hosting/free/status")
        content = driver.find_element(By.TAG_NAME, "pre").text
        
        send_telegram(f"登录成功，获取状态:\n{content}", "screenshot.png")
        
    except Exception as e:
        driver.save_screenshot("error.png")
        send_telegram(f"登录出现异常: {str(e)}", "error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

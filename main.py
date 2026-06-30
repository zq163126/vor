import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_telegram(message, photo_path=None):
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})
    if photo_path and os.path.exists(photo_path):
        url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(photo_path, "rb") as f:
            requests.post(url_photo, data={"chat_id": chat_id}, files={"photo": f})

def main():
    options = Options()
    # GitHub Actions 环境参数
    if os.getenv("GITHUB_ACTIONS"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.vortexa.cloud/dashboard")
        wait = WebDriverWait(driver, 20)
        
        # 输入信息
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys(os.getenv("USER_EMAIL"))
        
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(os.getenv("USER_PASSWORD"))

        # 鲁棒性定位按钮：通过包含 "Sign In" 文本的 button 元素定位
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign In')]")))
        submit_btn.click()

        # 等待页面跳转并完成登录
        wait.until(EC.url_contains("dashboard"))
        driver.save_screenshot("screenshot.png")

        # 验证登录状态
        driver.get("https://api.vortexa.cloud/api/hosting/free/status")
        content = driver.find_element(By.TAG_NAME, "pre").text
        
        send_telegram(f"登录检查结果:\n{content}", "screenshot.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

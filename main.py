import os
import requests
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
        print("未配置 Telegram Token 或 Chat ID，跳过发送")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})
    
    if photo_path and os.path.exists(photo_path):
        url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(photo_path, "rb") as f:
            requests.post(url_photo, data={"chat_id": chat_id}, files={"photo": f})

def main():
    options = Options()
    # GitHub Actions 环境配置
    if os.getenv("GITHUB_ACTIONS"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)

    try:
        # 访问首页
        driver.get("https://www.vortexa.cloud/dashboard")
        wait = WebDriverWait(driver, 15)
        
        # 1. 处理 Cookie 弹窗 (如果出现则点击)
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All')]")))
            cookie_btn.click()
            print("已处理 Cookie 弹窗")
        except TimeoutException:
            print("未检测到 Cookie 弹窗，跳过")

        # 2. 输入账号密码
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(os.getenv("USER_EMAIL"))
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(os.getenv("USER_PASSWORD"))

        # 3. 点击登录按钮 (使用鲁棒的 XPath 定位)
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign In')]")))
        submit_btn.click()

        # 4. 等待页面加载完成 (观察 URL 变化)
        wait.until(EC.url_contains("dashboard"))
        driver.save_screenshot("screenshot.png")

        # 5. 访问 API 获取状态
        driver.get("https://api.vortexa.cloud/api/hosting/free/status")
        
        # 获取页面内容
        try:
            content = driver.find_element(By.TAG_NAME, "pre").text
        except:
            content = "无法获取 API 内容，请检查登录是否成功。"
        
        # 6. 发送结果到 Telegram
        send_telegram(f"登录检查结果:\n{content}", "screenshot.png")
        print("操作完成")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

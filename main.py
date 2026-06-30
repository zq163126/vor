import os
import time
import requests  # 补充了这一行导入
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_telegram(message, photo_path=None):
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not token or not chat_id:
        print("未配置 Telegram Token 或 Chat ID")
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
        options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        # 1. 进入登录页
        driver.get("https://www.vortexa.cloud/dashboard")
        
        # 2. 点击 Cookie 弹窗
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All')]")))
            cookie_btn.click()
        except:
            pass

        # 3. 填写登录信息
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(os.getenv("USER_EMAIL"))
        driver.find_element(By.ID, "password").send_keys(os.getenv("USER_PASSWORD"))
        
        # 4. 点击提交
        driver.find_element(By.XPATH, "//button[contains(., 'Sign In')]").click()
        
        # 5. 判定登录成功：检查特定元素
        target_xpath = "//p[contains(text(), 'Manage your servers, invoices and deployments all in one place.')]"
        
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, target_xpath)))
            success_msg = "vortexa登录成功：检测到仪表盘特征元素。"
            print(success_msg)
        except Exception as e:
            success_msg = "vortexa登录失败或超时：未检测到特征元素。"
            print(success_msg)

        # 6. 截图并发送通知
        driver.save_screenshot("result.png")
        send_telegram(success_msg, "result.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

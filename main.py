import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        # 确保窗口大小足够，防止某些按钮因响应式布局而无法点击
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
        
        # 4. 点击提交并等待登录动作响应
        driver.find_element(By.XPATH, "//button[contains(., 'Sign In')]").click()
        
        # 强制等待，因为 API 的鉴权可能依赖于登录请求完成后的 Redirect
        # 如果登录成功，通常页面会跳转，我们给 10 秒缓冲
        time.sleep(10)
        driver.save_screenshot("after_login.png")

        # 5. 读取 STATUS 信息 (判定登录成功的唯一标准)
        driver.get("https://api.vortexa.cloud/api/hosting/free/status")
        
        # 等待页面加载（有时返回的是纯文本或简单的 JSON 文本）
        time.sleep(2)
        
        # 获取页面内容
        try:
            content = driver.find_element(By.TAG_NAME, "pre").text
        except:
            content = driver.page_source
        
        # 6. 发送最终判断结果
        send_telegram(f"API 返回数据:\n{content}", "after_login.png")
        print("API 数据读取完成并已发送")
        
    except Exception as e:
        print(f"执行出错: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

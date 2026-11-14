import os
import time
import requests
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
    
    # 强制启用 SOCKS5 代理
    proxy_server = "socks5://127.0.0.1:10808"
    options.add_argument(f'--proxy-server={proxy_server}')
    
    if os.getenv("GITHUB_ACTIONS"):
        options.add_argument("--headless=new") # 使用较新的无头模式
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled") # 关键：隐藏自动化特征
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. 【新增】先访问 IP 检查网站，验证当前代理是否生效
        driver.get("https://api.ipify.org")
        time.sleep(2)
        ip_address = driver.find_element(By.TAG_NAME, "body").text
        print(f"当前浏览器出口 IP: {ip_address}")
        send_telegram(f"【IP 检测】当前浏览器出口 IP 为: {ip_address}")

        # 2. 进入登录页
        driver.get("https://www.vortexa.cloud/dashboard")
        
        time.sleep(3)
        driver.save_screenshot("init_load.png")
        send_telegram("【排查】访问目标网站初始截图：", "init_load.png")

        # 3. 点击 Cookie 弹窗
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All')]")))
            cookie_btn.click()
        except:
            pass

        # 4. 填写登录信息
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(os.getenv("USER_EMAIL"))
        driver.find_element(By.ID, "password").send_keys(os.getenv("USER_PASSWORD"))
        
        # 5. 点击提交
        driver.find_element(By.XPATH, "//button[contains(., 'Sign In')]").click()
        
        # 6. 判定登录成功：检查特定元素
        target_xpath = "//p[contains(text(), 'Manage your servers, invoices and deployments all in one place.')]"
        
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, target_xpath)))
            success_msg = "登录成功：检测到仪表盘特征元素。"
            print(success_msg)
        except Exception as e:
            success_msg = "登录失败或超时：未检测到特征元素。"
            print(success_msg)

        # 7. 进入面板页
        time.sleep(2)
        driver.get("https://www.vortexa.cloud/server/5878")
        time.sleep(3)

        # 8. 最终截图并发送通知
        driver.save_screenshot("result.png")
        send_telegram(f"{success_msg}\n已跳转至服务器详情页。", "result.png")
        
    except Exception as e:
        driver.save_screenshot("error_screenshot.png")
        print(f"发生异常: {e}")
        send_telegram(f"脚本运行出错: {str(e)}", "error_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

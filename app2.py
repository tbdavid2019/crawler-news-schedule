import os
import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
import openai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# OpenAI 設置
openai.api_key = os.getenv("OPENAI_API_KEY")

# ============ RSS 來源與開關 ============
RSS_SOURCES = {
    "BBC Technology": {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "enabled": 0},
    "Yahoo Market Global": {"url": "https://tw.stock.yahoo.com/rss?category=intl-markets", "enabled": 1},
    "Yahoo Market TW": {"url": "https://tw.stock.yahoo.com/rss?category=tw-market", "enabled": 0},
    "Yahoo Expert TW": {"url": "https://tw.stock.yahoo.com/rss?category=column", "enabled": 0},
    "Yahoo Research TW": {"url": "https://tw.stock.yahoo.com/rss?category=research", "enabled": 0},
    "BBC Business": {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "enabled": 0},
    "Yahoo Global finance News": {"url": "https://news.yahoo.com/rss/finance", "enabled": 1},
    "Yahoo TOPSTORY": {"url": "https://news.yahoo.com/rss/topstories", "enabled": 0},
}


# MongoDB 設置
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "financial_news")  # 提供默認值
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "global_market_news")  # 提供默認值

# 設置 logging
logger = logging.getLogger("FinancialNewsBot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def save_to_mongodb(report_content, source, date):
    """將報告存入 MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        document = {
            "source": source,
            "date": date,
            "report": report_content,
            "created_at": datetime.now()
        }
        collection.insert_one(document)
        logger.info("成功寫入 MongoDB")
    except Exception as e:
        logger.error(f"MongoDB 寫入失敗: {e}")
    finally:
        client.close()

def send_to_discord(webhook_url, message, date):
    """發送訊息到 Discord（以檔案形式）"""
    try:
        # 建立檔案名稱，包含日期以便識別
        file_name = f"888全球股市日報_{date.replace('/', '-')}.txt"
        
        # 將報告內容寫入文字檔案
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(message)
        
        # 準備檔案上傳
        files = {
            "file": (file_name, open(file_name, "rb"), "text/plain")
        }
        
        # 可以添加簡短的訊息說明
        data = {
            "content": f"全球股市日報 - {date}"
        }
        
        # 使用 multipart/form-data 發送請求
        response = requests.post(webhook_url, data=data, files=files)
        
        # 關閉檔案
        files["file"][1].close()
        
        if response.status_code == 204 or response.status_code == 200:
            logger.info("成功發送檔案到 Discord")
        else:
            logger.error(f"Discord 檔案發送失敗: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Discord 發送出錯: {e}")

def clear_file(file_name):
    """清空指定檔案內容"""
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.truncate(0)
        logger.info(f"已清空檔案: {file_name}")
    except Exception as e:
        logger.error(f"清空檔案失敗: {e}")

def scrape_articles(article_urls, content_selector, file_name):
    """爬取文章內容"""
    articles = []
    for index, url in enumerate(article_urls, 1):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                content = "\n".join([p.get_text(strip=True) for p in soup.select(content_selector)])
                if content:
                    articles.append({"URL": url, "Content": content})
                    logger.info(f"成功爬取文章 {index}/{len(article_urls)}")
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.error(f"爬取文章失敗 {url}: {e}")

    if articles:
        with open(file_name, "a", encoding="utf-8") as f:
            for article in articles:
                f.write(f"URL: {article['URL']}\nContent: {article['Content']}\n\n")

def scrape_rss_feed(rss_url, content_selector, file_name):
    """爬取 RSS feed"""
    try:
        response = requests.get(rss_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "xml")
            items = soup.find_all("item")
            urls = [item.link.text for item in items if item.link]
            scrape_articles(urls, content_selector, file_name)
    except Exception as e:
        logger.error(f"RSS 爬取失敗 {rss_url}: {e}")



def generate_report_with_openai(date):
    """使用 OpenAI API 生成報告"""
    try:
        # url = "https://api.openai.com/v1/chat/completions"
        
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"        

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # 讀取新聞文件內容
        with open("allnews.txt", "r", encoding="utf-8") as file:
            news_content = file.read()


        prompt = f"""
        您是一位專業的投資顧問，擅長分析財經新聞並提取對投資者有價值的信息。請您分析以下在 {date} 收集的所有財經新聞：

        {news_content}

        ------

        請您從投資顧問的角度，總結今日最重要的6大投資相關重點。這些重點可以是：
        1. 從多則相關新聞中歸納出的市場趨勢或重大事件
        2. 單一則具有重大投資意義的新聞

        每個重點請按以下結構分析：
        1. 【重點標題】- 簡明扼要的總結
        2. 【事件背景】- 這個事件或趨勢的來龍去脈
        3. 【影響分析】- 對金融市場、經濟環境或特定行業的潛在影響
        4. 【投資啟示】- 對投資者的具體建議或應對策略
        5. 【相關標的】- 受影響的股票、ETF或其他投資工具（請務必包含股票代碼或ETF代碼）
        6. 【重要性評分】- ⭐️⭐️⭐️⭐️⭐️（1-5顆星）
        7. 【消息來源】- 引用的具體新聞來源

        請以專業、客觀的口吻撰寫，並確保每個重點分析都有實質的投資參考價值。如果某些投資機會具有時效性，請特別標注。

        請用繁體中文輸出完整分析。
        """   

        # prompt = f"""
        

        # 日期：{date}

        #      以下是所有新聞內容：
        #     {news_content}

        #     ------
        #         綜合所有新聞，整理10條分析(可以多條新聞合併在同一個分析中) ：背景、影響與後果、重要性⭐️⭐️⭐️(最多5顆星)、對相關股票的潛在影響（含股票代碼）、新聞來源。  

        
        #         用繁體中文輸出
        # """
        
        data = {
            "model": "gemini-1.5-pro-latest",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000000
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            report = response.json()["choices"][0]["message"]["content"]
            return report
        else:
            logger.error(f"報告生成失敗: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"報告生成失敗: {e}")
        return None





def send_email(report_content, date):
    """發送電子郵件"""
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        port = int(os.getenv("SMTP_PORT"))
        sender_email = os.getenv("SENDER_EMAIL")
        password = os.getenv("EMAIL_PASSWORD")
        to_emails = os.getenv("TO_EMAILS").split(',')

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = f"888全球股市日報 - {date}"
        msg.attach(MIMEText(report_content, "plain"))

        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_emails, msg.as_string())
        logger.info("郵件發送成功")
    except Exception as e:
        logger.error(f"郵件發送失敗: {e}")

def send_telegram_message(report_content, date):
    """發送 Telegram 消息"""
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # 由於 Telegram 消息長度限制，可能需要分段發送
        max_length = 4096
        message = f"888全球股市日報 - {date}\n\n{report_content}"
        
        if len(message) <= max_length:
            payload = {
                "chat_id": channel_id,
                "text": message
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
        else:
            # 分段發送
            chunks = [message[i:i+max_length] for i in range(0, len(message), max_length)]
            for chunk in chunks:
                payload = {
                    "chat_id": channel_id,
                    "text": chunk
                }
                response = requests.post(url, json=payload)
                response.raise_for_status()
                time.sleep(1)  # 避免發送過快
        
        logger.info("Telegram 消息發送成功")
    except Exception as e:
        logger.error(f"Telegram 消息發送失敗: {e}")

def main():
    """主程序"""
    try:
        # 清空舊檔案
        clear_file("bot.log")
        clear_file("allnews.txt")

        # 爬取新聞
        logger.info("開始爬取新聞...")
        for name, data in RSS_SOURCES.items():
            if data["enabled"]:
                logger.info(f"正在處理 RSS 源: {name}")
                scrape_rss_feed(data["url"], "p", "allnews.txt")

        # 獲取今天日期
        today_date = datetime.now().strftime("%Y/%m/%d")

        # 生成報告
        logger.info("正在生成報告...")
        report = generate_report_with_openai(today_date)
        if not report:
            raise Exception("報告生成失敗")

        # 保存到 MongoDB
        logger.info("保存報告到 MongoDB...")
        save_to_mongodb(report, "RSS_Feed_Analysis", today_date)

        # 發送到 Discord
        logger.info("發送報告到 Discord...")
        discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        send_to_discord(discord_webhook_url, report, today_date)

        # 發送電子郵件
        logger.info("發送電子郵件...")
        send_email(report, today_date)

        # 發送到 Telegram
        logger.info("發送到 Telegram...")
        send_telegram_message(report, today_date)

    except Exception as e:
        logger.error(f"執行過程發生錯誤: {e}")
        # 可以在這裡添加錯誤通知機制
        send_telegram_message(f"執行過程發生錯誤: {e}", today_date)

if __name__ == "__main__":
    main()

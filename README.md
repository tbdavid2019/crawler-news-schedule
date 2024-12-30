# 全球財經新聞分析機器人 | Global Financial News Analysis Bot

## 專案介紹 | Introduction

這是一個自動化的財經新聞分析機器人，能夠從多個 RSS 來源抓取新聞，使用 OpenAI GPT-4o 進行分析，並通過多個管道（MongoDB、Discord、Telegram 和 Email）發送分析報告。

This is an automated financial news analysis bot that scrapes news from multiple RSS sources, analyzes content using OpenAI's GPT-4, and distributes reports through various channels.

## 功能特點 | Features

- 📰 RSS 新聞爬蟲
- 🤖 AI 新聞分析
- 📊 自動報告生成
- 📫 多管道分發（MongoDB、Discord、Telegram、Email）
- 🔄 每日自動更新

## 使用需求 | Prerequisites

- Python 3.8+
- MongoDB 帳號
- OpenAI API 金鑰
- Discord Webhook (選用)
- Telegram Bot Token (選用)
- Gmail 帳號 (用於發送郵件通知)

## 安裝說明 | Installation

1. 複製專案
```bash
git clone https://github.com/tbdavid2019/crawler-news-schedule.git
cd crawler-news-schedule
```

2. 安裝相依套件
```bash
pip install -r requirements.txt
```

3. 設定環境變數
```bash
cp .env.example .env
# 編輯 .env 填入您的設定
```

---

## English Documentation

### Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Settings
OPENAI_API_KEY=your_openai_api_key

# MongoDB Settings
MONGO_URI=your_mongodb_connection_string
MONGO_DB=financial_news
MONGO_COLLECTION=global_market_news

# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
TO_EMAILS=recipient1@example.com,recipient2@example.com

# Discord Settings
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Telegram Settings
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id

# Scraper Settings
SCRAPE_DELAY_MIN=1
SCRAPE_DELAY_MAX=3
```

### News Sources

Currently supported RSS sources:
```python
RSS_SOURCES = {
    "BBC Business": {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "enabled": 0},
    "BBC Technology": {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "enabled": 0},
    "Yahoo Market Global": {"url": "https://tw.stock.yahoo.com/rss?category=intl-markets", "enabled": 1},
    "Yahoo Market TW": {"url": "https://tw.stock.yahoo.com/rss?category=tw-market", "enabled": 1},
    "Yahoo Expert TW": {"url": "https://tw.stock.yahoo.com/rss?category=column", "enabled": 1},
    "Yahoo Research TW": {"url": "https://tw.stock.yahoo.com/rss?category=research", "enabled": 1},
    "Yahoo Global finance News": {"url": "https://finance.yahoo.com/news/rssindex", "enabled": 0},
}
```

### Output Format

```
全球市場財經日報 (YYYY/MM/DD)

1. 今日重點新聞：
   - [Important News 1]
   - [Important News 2]
   ...

2. 深度分析：
   1. [News Title 1]
      Importance: ⭐️⭐️⭐️⭐️⭐️
      Background: [Description]
      Impact: [Analysis]
      Market Impact: [Related Stock Codes]
   ...
```

### Dependencies

```
python-dotenv
requests
beautifulsoup4
pymongo
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### License

MIT License

### Disclaimer

This bot is for educational purposes only. Please ensure you comply with all relevant terms of service and API usage guidelines.

### Support

For support, please open an issue in the GitHub repository.

---
Created by TBDAVID2019 - Feel free to contact me!
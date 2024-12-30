#!/bin/bash

# 獲取當前小時
current_hour=$(date +"%H")

# 啟用虛擬環境 
source /home/david/crawler/myenv/bin/activate

pip install -r requirements.txt


# 根據時間執行不同的 Python 應用程式
if [ "$current_hour" -lt 12 ]; then
    echo "現在是上午，執行 app.py"
    python /home/david/crawler/app.py
else
    echo "現在是下午，執行 app2.py"
    python /home/david/crawler/app2.py
fi

# 避免影響其他進程，退出虛擬環境
deactivate
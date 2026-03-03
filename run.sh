#!/bin/bash

# 下载 bot.py
curl -L -o bot.py https://gh-proxy.org/https://github.com/adnogpu/open-proxy/raw/refs/heads/main/bot.py

# 安装依赖
pip install cloudscraper requests pysocks scapy icmplib -q

# 后台静默运行
nohup python3 bot.py > /dev/null 2>&1 &

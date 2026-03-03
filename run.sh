#!/bin/bash

curl -L -o bot.py https://gh-proxy.org/https://github.com/adnogpu/open-proxy/raw/refs/heads/main/bot.py

nohup python3 bot.py > /dev/null 2>&1 &

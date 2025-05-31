import aiohttp
import asyncio
import os

PROXY_LIST_URL = "https://openproxylist.xyz/http.txt"
CHECK_URL = "https://rewards.bing.com/Signin?idru=%2F"
TARGET_REDIRECT = "https://login.live.com/oauth20_authorize.srf?"
CONCURRENT = 100  # 并发数量（可根据硬件适当调整）

async def fetch_proxy_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(PROXY_LIST_URL, timeout=15) as resp:
            text = await resp.text()
            return [line.strip() for line in text.splitlines() if line.strip()]

async def check_proxy(proxy, session, sem, good_list):
    proxy_url = f"http://{proxy}"
    try:
        async with sem:
            async with session.get(
                CHECK_URL,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=10),
                allow_redirects=False
            ) as resp:
                loc = resp.headers.get("Location", "")
                # 跟踪一次重定向
                if TARGET_REDIRECT in loc:
                    good_list.append(proxy)
                    print(f"GOOD: {proxy}")
                elif resp.status in (301, 302, 303, 307, 308) and loc:
                    # 再跟一次
                    async with session.get(loc, proxy=proxy_url, timeout=10, allow_redirects=False) as resp2:
                        loc2 = resp2.headers.get("Location", "")
                        if TARGET_REDIRECT in loc2 or TARGET_REDIRECT in str(resp2.url):
                            good_list.append(proxy)
                            print(f"GOOD: {proxy}")
    except Exception:
        pass

async def main():
    proxies = await fetch_proxy_list()
    with open("http.txt", "w") as f:
        f.write('\n'.join(proxies))
    print(f"Loaded {len(proxies)} proxies.")

    sem = asyncio.Semaphore(CONCURRENT)
    good_list = []
    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy(proxy, session, sem, good_list) for proxy in proxies]
        await asyncio.gather(*tasks)

    # 批量写入
    with open("good.txt", "w") as f:
        f.write('\n'.join(good_list))
    print(f"Checked all. {len(good_list)} good proxies saved to good.txt.")

if __name__ == "__main__":
    asyncio.run(main())

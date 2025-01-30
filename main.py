import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, init
from tqdm import tqdm

# 初始化 colorama
init(autoreset=True)

# 下载代理列表并保存到指定文件
def download_proxy_list(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        with open(file_path, 'w') as file:
            file.write(response.text)
        print("代理列表下载成功！")
    except requests.RequestException as e:
        print(f"下载代理列表失败：{e}")

# 检测代理有效性（通过状态码）
def check_proxy(proxy):
    test_url = "https://lanzoui.com/"
    proxies = {
        "http": proxy,
        "https": proxy
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=3)
        # 检查返回状态码是否为200
        if response.status_code == 200:
            return True  # 返回True表示代理有效
    except requests.RequestException:
        pass
    return False

# 多线程测试代理有效性并显示进度条
def test_proxies(proxies, max_workers=100):
    valid_proxies = []
    total_proxies = len(proxies)
    
    # 创建进度条
    with tqdm(total=total_proxies, desc="检测代理", ncols=100) as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}

            for future in as_completed(futures):
                pbar.update(1)  # 更新进度条
                if future.result():
                    valid_proxies.append(futures[future])  # 记录有效代理
                    pbar.set_postfix(有效代理数=len(valid_proxies))  # 动态更新有效代理数量

    print(f"总代理数量：{total_proxies}, 有效代理数量：{len(valid_proxies)}")
    return valid_proxies

# 下载代理并检测有效性
def download_and_check_proxies(proxy_url, output_file='good.txt', max_workers=250):
    # 下载代理列表
    download_proxy_list(proxy_url, 'proxy.txt')

    # 读取下载的代理列表
    with open('proxy.txt', 'r') as file:
        proxies = [line.strip() for line in file.readlines()]

    # 检测有效代理
    valid_proxies = test_proxies(proxies, max_workers=max_workers)

    # 将有效代理保存到文件
    with open(output_file, "w") as file:
        for proxy in valid_proxies:
            file.write(proxy + "\n")
    print(f"有效代理已保存到 {output_file} 文件中。")

if __name__ == "__main__":
    # 设置代理列表的下载链接
    proxy_url = "https://openproxylist.xyz/http.txt"
    

    # 下载代理列表并检测有效性
    download_and_check_proxies(proxy_url, 'good.txt', max_workers=250)

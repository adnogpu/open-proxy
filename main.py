import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, init
from tqdm import tqdm
import re

# 初始化 colorama
init(autoreset=True)

def get_proxy(file_path='proxy.txt'):
    """
    下载代理列表并保存到指定的文件中。

    参数:
    - file_path: 保存代理列表的文件路径，默认为根目录下的 'proxy.txt'。
    """
    # 第一步：获取页面内容并解析nonce值
    url = "https://proxycompass.com/cn/free-proxy/"
    response = requests.get(url)
    content = response.text

    # 使用正则表达式查找 nonce 值
    nonce_pattern = r'var proxylister_ajax = \{"ajax_url":"https:\\/\\/proxycompass.com\\/wp-admin\\/admin-ajax.php","nonce":"(.*?)"\}'
    nonce_match = re.search(nonce_pattern, content)

    if nonce_match:
        nonce = nonce_match.group(1)
        print(f"Nonce值为: {nonce}")
    else:
        print("未找到nonce值")
        return

    # 第二步：使用解析到的 nonce 值请求代理下载地址
    download_url = f"https://proxycompass.com/wp-admin/admin-ajax.php?action=proxylister_download&nonce={nonce}&format=txt&filter={{}}"
    proxy_response = requests.get(download_url)
    # 保存代理到指定路径的文件中
    with open("/proxy/proxy/123_1.txt", 'w', encoding='utf-8') as file:
        file.write(proxy_response.text)

    print(f"代理已成功保存到 {file_path}")

# 下载代理列表并保存到指定文件
def download_proxy_list(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        with open("/proxy/proxy/123_2.txt", 'w') as file:
            file.write(response.text)
        print("代理列表下载成功！")
    except requests.RequestException as e:
        print(f"下载代理列表失败：{e}")

# 检测代理有效性（通过状态码）
def check_proxy(proxy):
    test_url = "https://ddns.oray.com/checkip"
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

# 合并代理列表并进行检测
def combine_and_check_proxies(file1, file2, output_file='good.txt', max_workers=100):
    # 读取第一个文件的代理列表
    with open("/proxy/proxy/123_1.txt", 'r') as file:
        proxies1 = [line.strip() for line in file.readlines()]
    
    # 读取第二个文件的代理列表
    with open("/proxy/proxy/123_2.txt", 'r') as file:
        proxies2 = [line.strip() for line in file.readlines()]
    
    # 合并代理列表
    combined_proxies = list(set(proxies1 + proxies2))  # 去重

    # 检测有效代理
    valid_proxies = test_proxies(combined_proxies, max_workers=max_workers)

    # 将有效代理保存到文件
    with open("/proxy/proxy/http.txt", "w") as file:
        for proxy in valid_proxies:
            file.write(proxy + "\n")
    print(f"有效代理已保存到 {output_file} 文件中。")

if __name__ == "__main__":
    # 下载第一个代理列表
    #get_proxy('proxy1.txt')

    # 下载第二个代理列表
    proxy_url = "http://165.154.13.41/http.txt"
    download_proxy_list(proxy_url, 'proxy2.txt')

    # 合并两个代理列表并检测有效性
    combine_and_check_proxies('proxy1.txt', 'proxy2.txt', 'good.txt', max_workers=100)

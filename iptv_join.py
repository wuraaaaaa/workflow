import re
import requests
import signal
import time

# 开启 连通性测试 有bug 会导致变成下载- -
test_connect = False


class IPTV:
    def __init__(self, group_title, tvg_id, tvg_logo, name, url):
        # 分组
        self.group_title = group_title
        # 频道id
        self.tvg_id = tvg_id
        # 频道logo
        self.tvg_logo = tvg_logo
        # 频道名称
        self.name = name
        # 播放url
        self.url = url

    def __str__(self):
        return f"#EXTINF:-1 group-title=\"{self.group_title}\" tvg-id=\"{self.tvg_id}\" tvg-logo=\"{self.tvg_logo}\",{self.name}\n{self.url}"


live_infos = []

# 去重
add_url = []


def timeout_handler(signal, frame):
    # 引发异常
    raise TimeoutError("超时!")

def request(url, timeout=2, use_signal = False, only_test = False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537',
        'Range': 'bytes=0-1023'  # 如果需要的话，可以限制请求的范围，但这不是必要的
    }
    if not use_signal:
        try:
            if only_test:
                result = requests.get(url, verify=False, stream=True, timeout=(timeout,timeout))
                return result
            result = requests.get(url, verify=False, timeout=(timeout,timeout))
            return result
        except Exception as e:
            print(f"request error {e}")
            return None

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        result = requests.get(url, verify=False, timeout=timeout)
        return result
    except Exception as e:
        print(f"request error {e}")
        return None
    finally:
        signal.alarm(0)

def is_add(url):
    if add_url.__contains__(url):
        return True
    add_url.append(url)
    return False


# 转换每个源的不同group 为同一个
def get_group_name(current_name):
    cctv = ["央视高清", "央视", "央视台", "CCTV"]
    if contains(cctv,current_name): return "央视台"
    city = ["卫视台", "卫视高清", "卫视"]
    if contains(city,current_name): return "卫视台"
    digital = ["数字电视", "数字高清", "数字", "电影" ,"卡通", "4K"]
    if contains(digital, current_name): return "数字高清"
    golab = ["国际时事", "国际"]
    if contains(golab ,current_name): return "国际"
    local = ["地方特色", "河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
             "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆", "北京",
             "天津", "上海", "重庆", "香港", "澳门"]
    if contains(local, current_name): return "地方特色"
    return "其他"

def contains(list, str):
    for item in list:
        if item.lower() in str.lower():
            return True
    return False

def get_tv_id(tv_id):
    return tv_id.replace("-", "")

def test_play_url(url):
    # 不需要测试连通性 直接返回
    if not test_connect:
        return True
    print(f"test : {url}")
    try:
        context = request(url, timeout=2, only_test= True)
        if context.status_code == 200:
            print("result: True")
            return True
        else:
            print("result: False")
            return False
    except Exception as e:
        print("result: False")
        return False

def download_m3u8(url, use_proxy = False):
    link = url
    if use_proxy:
        link = "https://mirror.ghproxy.com/"+url
    try:
        print(f"start -> download from : {link}")
        context = request(link, timeout=5)
        if context is not None and context.status_code == 200:
            lines = context.text.split('\n')
            # print(lines)
            return lines
        else:
            return None
    except Exception as e:
        print(f"error : {e}")
        return None


# https://github.com/Meroser/IPTV
def get_meroser_source():
    pattern = re.compile(
        r'#EXTINF:-1 tvg-id="([^"]+)" tvg-name="([^"]+)" tvg-logo="([^"]+)" group-title="([^"]+)",([^"]+)')
    url = "https://raw.githubusercontent.com/Meroser/IPTV/main/IPTV.m3u"

    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    tvg_id, tvg_name, tvg_logo, group_title, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    if is_add(url) or not test_play_url(url):
                        continue
                    live_info = IPTV(get_group_name(group_title), get_tv_id(tvg_name), tvg_logo, name, url)
                    live_infos.append(live_info)

# https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u
def get_YueChan_source():
    pattern = re.compile(
        r'#EXTINF:-1 tvg-id="([^"]+)" tvg-name="([^"]+)" tvg-logo="([^"]+)" group-title="([^"]+)",([^"]+)')
    url = "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"

    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    tvg_id, tvg_name, tvg_logo, group_title, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    if is_add(url) or not test_play_url(url):
                        continue
                    live_info = IPTV(get_group_name(group_title), get_tv_id(tvg_name), tvg_logo, name, url)
                    live_infos.append(live_info)

# https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/IPV6.m3u
def get_Ftindy_IPV6_source():
    pattern = re.compile(
        r'#EXTINF:-1 tvg-logo="([^"]+)" tvg-id="([^"]+)" tvg-name="([^"]+)",([^"]+)')
    url = "https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/IPV6.m3u"

    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    tvg_logo,tvg_id,tvg_name, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    if is_add(url) or not test_play_url(url):
                        continue
                    live_info = IPTV(get_group_name(tvg_name), get_tv_id(tvg_name), tvg_logo, name, url)
                    live_infos.append(live_info)

# https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/IPV6.m3u
def get_Ftindy_bestv_source():
    pattern = re.compile(
        r'#EXTINF:-1,tvg-id="([^"]+)" tvg-name="([^"]+)" tvg-logo="([^"]+)" group-title="([^"]+)",([^"]+)')
    url = "https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/bestv.m3u"

    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    tvg_id,tvg_name,tvg_logo,group_title, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    if is_add(url) or not test_play_url(url):
                        continue
                    live_info = IPTV(get_group_name(tvg_name), get_tv_id(tvg_name), tvg_logo, name, url)
                    live_infos.append(live_info)

# https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/IPV6.m3u
def get_Ftindy_sxg_source():
    pattern = re.compile(
        r'#EXTINF:-1,tvg-id="([^"]+)" tvg-name="([^"]+)" tvg-logo="([^"]+)" group-title="([^"]+)",([^"]+)')
    url = "https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/sxg.m3u"

    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    tvg_id,tvg_name,tvg_logo,group_title, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    if is_add(url) or not test_play_url(url):
                        continue
                    live_info = IPTV(get_group_name(tvg_name), get_tv_id(tvg_name), tvg_logo, name, url)
                    live_infos.append(live_info)

# https://github.com/joevess/IPTV
def get_joevess_source():
    pattern = re.compile(
        r'#EXTINF:-1 group-title="([^"]+)" tvg-id="([^"]+)" tvg-logo="([^"]+)",([^"]+)')
    url = "https://raw.githubusercontent.com/joevess/IPTV/main/sources/iptv_sources.m3u8"
    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    group_title, tvg_id, tvg_logo, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    if is_add(url) or not test_play_url(url):
                        continue
                    live_info = IPTV(get_group_name(group_title), get_tv_id(tvg_id), tvg_logo, name, url)
                    live_infos.append(live_info)


if __name__ == '__main__':


    #get_meroser_source()
    get_joevess_source()
    get_YueChan_source()
    get_Ftindy_IPV6_source()
    get_Ftindy_bestv_source()
    get_Ftindy_sxg_source()
    with open('output.m3u8', 'w', encoding='utf-8') as f:
        print("#EXTM3U", file=f)
        # 使用 sorted 函数和 lambda 表达式按照 group_title 排序
        sorted_live_infos = sorted(live_infos, key=lambda IPTV: IPTV.group_title + IPTV.tvg_id, reverse=True)
        for i in sorted_live_infos:
            print(i, file=f)

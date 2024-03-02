import re
import requests


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


# 转换每个源的不同group 为同一个
def get_group_name(current_name):
    cctv = ["央视高清", "央视", "央视台"]
    if cctv.__contains__(current_name): return "央视台"
    city = ["卫视台", "卫视高清", "卫视"]
    if city.__contains__(current_name): return "卫视台"
    digital = ["数字电视", "数字高清", "数字", "电影"]
    if digital.__contains__(current_name): return "数字高清"
    golab = ["国际时事", "国际"]
    if golab.__contains__(current_name): return "国际"
    local = ["地方特色", "河北台", "山西台", "辽宁台", "吉林台", "黑龙江台", "江苏台", "浙江台", "安徽台", "福建台", "江西台", "山东台", "河南台", "湖北台", "湖南台",
             "广东台", "海南台", "四川台", "贵州台", "云南台", "陕西台", "甘肃台", "青海台", "台湾台", "内蒙古台", "广西台", "西藏台", "宁夏台", "新疆台", "北京市台",
             "天津市台", "上海市台", "重庆市台", "香港台", "澳门台"]
    if local.__contains__(current_name): return "地方特色"


def get_tv_id(tv_id):
    return tv_id.replace("-", "")


def download_m3u8(url):
    context = requests.get(url, verify=False, timeout=30)
    if context is not None and context.status_code == 200:
        lines = context.text.split('\n')
        # print(lines)
        return lines
    else:
        return None

    # https://github.com/Meroser/IPTV


def get_meroser_source():
    pattern = re.compile(
        r'#EXTINF:-1 tvg-id="([^"]+)" tvg-name="([^"]+)" tvg-logo="([^"]+)" group-title="([^"]+)",([^"]+)')
    url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/Meroser/IPTV/main/IPTV.m3u"

    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    tvg_id, tvg_name, tvg_logo, group_title, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    live_info = IPTV(get_group_name(group_title), get_tv_id(tvg_name), tvg_logo, name, url)
                    live_infos.append(live_info)


# https://github.com/joevess/IPTV
def get_joevess_source():
    pattern = re.compile(
        r'#EXTINF:-1 group-title="([^"]+)" tvg-id="([^"]+)" tvg-logo="([^"]+)",([^"]+)')
    url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/joevess/IPTV/main/sources/iptv_sources.m3u8"
    lines = download_m3u8(url)
    if lines is not None:
        for line in lines:
            if line.startswith('#EXTINF:-1'):
                match = pattern.match(line)
                if match:
                    group_title, tvg_id, tvg_logo, name = match.groups()
                    # 下一行就是url
                    url = lines[lines.index(line) + 1].strip()
                    live_info = IPTV(get_group_name(group_title), get_tv_id(tvg_id), tvg_logo, name, url)
                    live_infos.append(live_info)


if __name__ == '__main__':
    get_meroser_source()
    get_joevess_source()
    with open('output.m3u8', 'w', encoding='utf-8') as f:
        print("#EXTM3U", file=f)
        for i in live_infos:
            print(i, file=f)

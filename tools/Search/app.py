# 多功能融合的工具，可以查询天气，可以查询ip地址，可以查询电话所属地，身份证所属地

import requests as req
from lxml import etree
from bs4 import BeautifulSoup

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': "1",
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document'
}

#网站url
url = "https://www.ks121.com"

# 搜索ip地址所在地
def ip_search(ip,headers=headers):
    """
    ip:str
    headers:dic
    """
    url_ip = f"https://www.ip138.com/iplookup.php?ip={ip}&action=2"
    response_ip = req.get(url_ip,headers=headers)
    response_ip.encoding = response_ip.apparent_encoding # 自动匹配编码

    e = etree.HTML(response_ip.text)
    if e.xpath('//td/span/text()'):
        print(e.xpath('//td/span/text()')[0])
    else:
        print("ip地址格式错误或者不存在该ip")

# ip_search(ip='123.9.8.7')

# 查询天气
def weather_search(loc,headers=headers,url=url):
    """
    loc:str
    headers:dic
    url:str
    """
    url_w = f"https://www.ks121.com/search/?location={loc}"
    response_w = req.get(url_w,headers=headers)
    response_w.encoding = response_w.apparent_encoding

    soup = BeautifulSoup(response_w.text,"html.parser")
    table = soup.find("table")
    all_tr = table.find_all("tr")

    loc = all_tr[0].find("a").text if all_tr[0].find("a") else "地点未知"
    week = all_tr[1].select_one("p.week").text if all_tr[1].select_one("p.week") else "未知"
    img_url = []
    for v in all_tr[1].select("img"):
        if v:
            img_url.append(url+v['src'])

    w = all_tr[1].select_one('span').text if all_tr[1].select_one('span') else "天气未知"
    temp = all_tr[1].find_all('p')[-2].text if '℃ ' in all_tr[1].find_all('p')[-2].text  else "温度未知"
    wind = all_tr[1].find_all('p')[-1].text if all_tr[1].find_all('p')[-1].text else '风速不明'
    res = {
        'location':loc,
        "week":week,
        "weather":w,
        "weather_icons":img_url,
        'temperature':temp,
        'wind_speed':wind,
    }
    return res

# print(weather_search("柴桑区"))

# 电话归属
def phone(p,headers=headers):
    """
    p:电话号码
    return:->{location:电话归属地址
    server:服务厂商
    server_img:服务厂商图片
    }
    """
    if p[0] == '1' and len(p) == 11:
        url_p = f"https://www.haoshudi.com/{p}.htm"

        response_p = req.get(url_p,headers=headers)
        response_p.encoding = response_p.apparent_encoding

        e = etree.HTML(response_p.text)
        try:
            loc = e.xpath('//span/text()')
            loc_ser = e.xpath("//a[@class='link']/text()")[:2]
            loc = loc_ser[0] + loc[-13] #地点信息
            server = loc_ser[1] #服务商信息
            server_img = 'https://www.haoshudi.com' + e.xpath("//span/img/@src")[0]
            return {'location':loc,'server':server,'server_img':server_img}
        except:
            return {'location':'位置没找到','server':'未找到','server_img':'未找到'}
    else:
        return "该号码不存在"
# print(phone('15180698310'))

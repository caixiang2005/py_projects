# 这里获取hero的数据内容
import requests as req
from lxml import etree

def get_hero_list():
    url = "https://pvp.qq.com/web201605/herolist.shtml"
    headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'}

    response = req.get(url,headers=headers)
    response.encoding = response.apparent_encoding 

    e = etree.HTML(response.text)
    hero = e.xpath("//li/a/text()")[3:]
    hero_img_url = e.xpath("//li/a/img/@src")
    d_hero = [[],[]]
    for i in range(len(hero)):
        d_hero[0].append(hero[i])
        d_hero[1].append(hero_img_url[i])
    return d_hero

if __name__ == "__main__":
    hero_list = get_hero_list()
    print(hero_list)

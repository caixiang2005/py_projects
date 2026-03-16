import requests as req
from lxml import etree
import os

# 伪装请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}
web_url = 'https://www.wanbenxs.cc'

# 输入小说名字的函数-》返回小说名字和链接的字典
def input_novel_name(novel,headers):
    #网站url
    web_url = 'https://www.wanbenxs.cc'

    url = f"https://www.wanbenxs.cc/search/?searchkey={novel}"
    print(url)
    response = req.get(url,headers=headers)
    response.encoding = 'utf-8'

    e = etree.HTML(response.text)
    novel_names = e.xpath("//dl/dt/a/text()")
    novel_urls = e.xpath("//dl/dt/a/@href")
    novel_infs = e.xpath("//dl/dd/text()")


    d_novel = {
    }
    for name, url, info in zip(novel_names, novel_urls, novel_infs):
        d_novel[name] = {'url': web_url + url, 'info': info}   #名字对应链接和对应小说信息
    

    return d_novel

# 进入到对应的书内显示
def in_book(url,headers):
    """
    通过书的url进入到对应的书本内
    """
    response = req.get(url,headers=headers)
    response.encoding = 'utf-8'
    e = etree.HTML(response.text)

    # 找到书的总章节数
    num = e.xpath("//dl/a/dt/text()")[0]
    
    #左右指针找到括号内的内容进行计算实际的章节数
    for l in range(len(num)):
        if num[l] == '（':
            num = int(num[l+2:-2])
            break

    #进入到下载的url
    dwn_load_url = web_url + e.xpath("//div[@class='readbtn']/a[1]/@href")[0]

    
    return [dwn_load_url,num]   #返回[下载小说开始地址，小说总的章节数]


# 下载小说的函数
def get_book(url,book_name,headers):
    """
    传书的第一章第一页的url
    book_name = 小说名字
    请求头
    """
    # 记得创建对应的书籍文件夹
    # 获取脚本自身所在目录
    target_dir = os.path.dirname(os.path.abspath(__file__))+f'\\books\\{book_name}'
    os.makedirs(target_dir, exist_ok=True)
    # 书本url
    # url = 'https://www.wanbenxs.cc/zj/149888/46009344.html'
    pre_title = ''

    while(True):

        # 发送请求
        response = req.get(url,headers=headers)
        response.encoding = 'utf-8'

        e = etree.HTML(response.text)
        # 标题
        title = e.xpath("string(//h1)")[:-5]
        if title != pre_title:          
            # 如果前一个后后一个章节名字不一样输出名字
            print(f'{pre_title}写入完成')
        elif pre_title == '':
            print('开始下载了')

        pre_title = title   # 记录前一个章节的标题

        txt_li = e.xpath("//div[@id='booktxt']/p/text()")
        # 文章内容
        txt = '\n'.join(txt_li)


        # 用来判断是下一章还是下一页
        next_jud= e.xpath("//div[@class='bottem1']/a[3]/text()")
        next_jud = ''.join(next_jud)
        # 下一个位置url
        next_url = web_url + ''.join(e.xpath("//div[@class='bottem1']/a[3]/@href"))
        # print(next_url)

        # 通过章节名就可以判断要不要进行新建文件
        if next_jud == '下一页' or next_jud == '下一章':
            # 记得修改书名
            with open(f'{target_dir}/{title}.txt','a',encoding='utf-8') as f:
                # 将内容写入txt
                f.write(txt)
        else:
            print('整本书结束了')
            break

        # 更新url
        url = next_url


def get_book_with_callback(url, book_name, headers, progress_callback=None):
    """
    带回调的下载函数
    progress_callback: 回调函数，接收进度消息
    """
    target_dir = os.path.dirname(os.path.abspath(__file__)) + f'\\books\\{book_name}'
    os.makedirs(target_dir, exist_ok=True)
    pre_title = ''

    while True:
        response = req.get(url, headers=headers)
        response.encoding = 'utf-8'
        e = etree.HTML(response.text)

        title = e.xpath("string(//h1)")[:-5]
        if title != pre_title:
            if progress_callback:
                progress_callback(f'{pre_title}写入完成')
            else:
                print(f'{pre_title}写入完成')
        elif pre_title == '':
            if progress_callback:
                progress_callback('开始下载了')
            else:
                print('开始下载了')

        pre_title = title

        txt_li = e.xpath("//div[@id='booktxt']/p/text()")
        txt = '\n'.join(txt_li)

        next_jud = e.xpath("//div[@class='bottem1']/a[3]/text()")
        next_jud = ''.join(next_jud)
        next_url = web_url + ''.join(e.xpath("//div[@class='bottem1']/a[3]/@href"))

        if next_jud == '下一页' or next_jud == '下一章':
            with open(f'{target_dir}/{title}.txt', 'a', encoding='utf-8') as f:
                f.write(txt)
        else:
            if progress_callback:
                progress_callback('整本书结束了')
            else:
                print('整本书结束了')
            break

        url = next_url
# get_book('https://www.wanbenxs.cc/zj/149888/46009344.html','天人图谱',headers)

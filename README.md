# python项目
- 内部会涉及多个内容的项目
  爬虫自动化工具
web等内容进行学习
```
本内容仅用作学习无其他作用
```
---
## tools
### Auto_Novel_Fetcher.py
```
简介：基于python爬虫制作的自动下载小说工具，搜索下载到本地
```
- 项目展示
![加载失败](./README_pic/search_novel.png "搜索页面")
![加载失败](./README_pic/novel_dwn_load.png "搜索页面")
- 依赖库下载
```python
pip install requests
pip install lxml
pip install PyQt6
pip install pyinstaller
```
#### 项目内容详情
项目主要是基于request，lxml这些技术栈进行，对数据进行学习下载浏览
- 📄 Auto_Novel_Fetcher.py  
- 📄 app.py                 
- 📁 books/                 
  - 📁 书本名1/             
    - 📝 具体章节内容.txt       
  - 📁 书本名2/             
    - 📝 具体章节内容.txt      
```python
app.py内为主要的文件启动页面
Auto_Novel_Fetcher.py 内为细节的逻辑处理部分
books内存储的是书本下载的位置
```
项目完成后进行exe可执行程序的打包pyinstaller
```bash
pyinstaller -F -w tools/Auto-Novel-Fetcher/app.py
```
---
## Web
### Lotery
```
简介：基于flask的简单抽奖web
```
- 项目展示
![加载失败](./README_pic/lottery_pic.png "搜索页面")
- 
- 依赖库下载
```python
pip install requests
pip install lxml
pip install flask
```
#### 项目内容详情
本项目主页是就flask的web框架制作的一个简易路由抽奖画面
，内部动态数据由王者荣耀官网的动态获取
- 📄 app.py  
- 📄 hero.py                 
- 📁 templates/                 
  - 📄 index.html              
```python
本项目主要路由启动在app.py内进行
hero.py为网页数据的读取
templates内为超文本内容存放的位置
启动项目后浏览器访问http://127.0.0.1:5000/index进入页面内容便可体验此抽奖系统内容
```
---
### Like
```
简介：基于flask的简单点赞web
```
- 项目展示
![加载失败](./README_pic/like_pic.png "搜索页面")
- 依赖库下载
```python
pip install flask
```
#### 项目内容详情
内部的数据根据王者荣耀官网的动态获取，我直接写入数据了建议对内容进行爬取
数据内容动态存储在data.json文件内
- 📄 app.py                 
- 📁 templates/                 
  - 📄 index.html    
- 📄 data.json           
```python
本项目主要路由启动在app.py内进行
templates内为超文本内容存放的位置
data.json内存储的是角色的数据
启动项目后浏览器访问http://127.0.0.1:5000/index进入页面内容便可体验此点赞系统内容
```
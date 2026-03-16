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
简介：基于python爬虫制作的自动化小工具，搜索下载到本地
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
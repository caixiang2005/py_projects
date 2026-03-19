from flask import Flask,render_template,request
from app import idCard, phone,weather_search,ip_search

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

app = Flask(__name__)

@app.route('/index')
def index():
    ip = request.args.get('ip')
    ip = ip_search(ip)

    w = request.args.get('w')
    w = weather_search(w)

    tp = request.args.get('tp')
    tp = phone(tp)

    id = request.args.get('id')
    id = idCard(id)
    return render_template('index.html',ip=ip,w=w,tp=tp,id=id)

if __name__ == "__main__":
    app.run(debug=True)
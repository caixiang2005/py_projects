# 抽奖系统
from flask import Flask,render_template
from random import randint
import hero
# 创建一个应用
app = Flask(__name__)

hero = hero.get_hero_list()

# 主页路由
@app.route("/index")
def index():
    return render_template("index.html", hero=hero[0], hero_img_url=hero[1])

# 抽奖路由
@app.route("/choujiang")
def choujiang():
    num = randint(0,len(hero[0])-1)
    return render_template('index.html', hero=hero[0], hero_img_url=hero[1], h=hero[0][num], img_url=hero[1][num])

if __name__ == "__main__":
    app.run(debug=True)
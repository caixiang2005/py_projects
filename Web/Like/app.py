from flask import Flask,render_template,request,redirect,url_for
import json
import os

app = Flask(__name__)

cur_dir = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(cur_dir,"data.json")

# 加载数据
def load_hero():
    if not os.path.exists(json_file):
        return {}
    with open(json_file,'r',encoding='utf-8') as f:
        return json.load(f)
    
# 保存数据
def save_hero(data):
    with open(json_file,"w",encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

# 第一次创建初始化数据
def init_hero():
    if os.path.exists(json_file):
        return
    
    # 英雄数据
    hero = {'巫真 灵弓镇厄':[0,'https://yjwujian.res.netease.com/pc/zt/20220802191715/img/wz-1_3b2c7dba.jpg'],'万钧 惊世先生':[0,'https://yjwujian.res.netease.com/pc/zt/20220802191715/img/wj-1_35730448.jpg'],
        '宁红夜 无明赤练':[0,'https://yjwujian.res.netease.com/pc/zt/20220802191715/img/nhy-1_caa316bf.jpg'],'天海 云游者':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/tianhai-1_b49c6c40.jpg"],
        '崔三娘 雾海龙王':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/csn-1_f7fd073e.jpg"],'武田信忠 末路之鬼':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/wtxz-1_98ec4a06.jpg"],
        '顾清寒 冰雁':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/gqh-1_836d4630.jpg"],'胡桃 阴阳师':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/hutao-1_bfaef088.jpg"],
        '季沧海 烈豪':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/jch-1_8726e502.jpg"],'迦南 魅灵孤鹰':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/jianan-1_7ffd35a9.jpg"],
        '特木尔 苍狼':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/tme-1_a0c6542d.jpg"],'无尘 妙法通玄':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/wuchen-1_864d6ded.jpg"],
        '岳山 武威侯':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/yueshan-1_4f6bc484.jpg"],'沈妙 神机':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/sm-1_87a0af66.jpg"],
        '胡为 狂虎':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/huwei-1_cd9281a8.jpg"],'季莹莹 白无常':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/jyy-1_66ef6185.jpg"],
        '玉玲珑 天通元君':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/yll-1_de21858d.jpg"],'哈迪 千机手':[0,],
        '魏轻 玉面判官':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/weiqing-1_28e29a0c.jpg"],'刘炼 司南星':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/liulian-1_e25b5f94.jpg"],
        '席拉 启明之辉':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/xl-1_fecece78.jpg"],'蓝梦 彩云仙':[0,"https://yjwujian.res.netease.com/pc/zt/20220802191715/img/lm-1_2b7fb7d8.jpg"]
}

    save_hero(hero)

#将数据进行排序返回
def get_sorted_hero():
    hero = load_hero()
    return sorted(hero.items(), key=lambda x: x[1][0], reverse=True)

# 主界面路由
@app.route("/index")
def index():
    # 如果第一次运行直接创建josn文件
    init_hero()
    hero = load_hero()

    sorted_hero = get_sorted_hero()
    top3 = sorted_hero[:3]
    if len(top3) >= 3:
        top3_display = [top3[1], top3[0], top3[2]]
    else:
        top3_display = top3
    return render_template("index.html", hero=hero, sorted_hero=sorted_hero, top3=top3_display)

# 点赞路由
@app.route('/like', methods=['POST'])
def like():
    name = request.form.get("name")

    hero = load_hero()
    hero[name][0] += 1

    # 写回json
    save_hero(hero)
    return redirect(url_for('index'))

#搜索框路由
@app.route('/search',methods=['GET'])
def search():
    keyword = request.args.get('keyword','').strip()
    hero = load_hero()
    res = {}
    if keyword:
        for hero_name, hero_info in hero.items():
            if keyword.lower() in hero_name.lower():
                res[hero_name] = {
                    'likes':hero_info[0],
                    'img':hero_info[1] if len(hero_info) > 1 else ''
                }
 
    sorted_hero = get_sorted_hero()
    top3 = sorted_hero[:3]
    # 调整TOP3展示顺序（第二名放中间，第一名放中间最上面）
    if len(top3) >= 3:
        top3_display = [top3[1], top3[0], top3[2]]
    else:
        top3_display = top3
    return render_template("index.html",hero=hero,sorted_hero=sorted_hero,top3=top3_display,search_res=res,search_key=keyword)

if __name__ == "__main__":
    init_hero()
    app.run(debug=True)
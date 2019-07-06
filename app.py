#!/usr/bin/env python3
import sqlite3
# flaskをimportしてflaskを使えるようにする
from flask import Flask, render_template, request, redirect, session
# appにFlaskを定義して使えるようにしています。Flask クラスのインスタンスを作って、 app という変数に代入しています。
app = Flask(__name__)

# Flask では標準で Flask.secret_key を設定すると、sessionを使うことができます。この時、Flask では session の内容を署名付きで Cookie に保存します。
app.secret_key = 'sunabakoza'

# app に対して / というURLに対応するアクションを登録しています。


@app.route("/")
def index():
    title_name = "KOZADOのホームページ"
    css = "../static/css/home.css"
    return render_template('index.html', title_name=title_name, css=css)


@app.route('/regist', methods=["GET", "POST"])
def regist():
    title_name = "KOZADOの登録ページ"
    css = "../static/css/regist.css"
    # 登録ページを表示させる
    if request.method == "GET":
        if 'id' in session:
            return redirect('/genre')
        else:
            return render_template("regist.html", title_name=title_name, css=css)
    # ここからPOSTの処理
    else:
        name = request.form.get("name")
        password = request.form.get("password")

        conn = sqlite3.connect('groupwork.db')
        c = conn.cursor()
        c.execute("insert into users values(null,?,?)", (name, password))
        conn.commit()
        conn.close()
        return redirect('/login')

# GET  /login => ログイン画面を表示
# POST /login => ログイン処理をする


@app.route("/login", methods=["GET", "POST"])
def login():
    title_name = "KOZADOのログインページ"
    css = "../static/css/login.css"
    if request.method == "GET":
        if 'id' in session:
            return redirect("/genre")
        else:
            return render_template("login.html", title_name=title_name, css=css)
    else:
        # ブラウザから送られてきたデータを受け取る
        name = request.form.get("name")
        password = request.form.get("password")
        # ブラウザから送られてきた name, password を usersテーブルに一致するレコードが存在するかを判定する。レコードが存在するとuser_idに整数が代入、存在しなければ nullが入る
        conn = sqlite3.connect('groupwork.db')
        c = conn.cursor()
        c.execute(
            "select id from users where name = ? and password = ?", (name, password))
        user_id = c.fetchone()
        conn.close()
        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if user_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html", title_name=title_name, css=css)
        else:
            session['user_id'] = user_id
            return redirect("/genre")


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect("/login")


@app.route("/genre")
def img_list():
    conn = sqlite3.connect('groupwork.db')
    c = conn.cursor()
    c.execute("SELECT store_id,max(c) FROM(SELECT store_id,count(store_id) as c FROM favorite GROUP BY store_id)")
    rec=c.fetchall()[0]
    print(rec[0])
    c.execute("select stores.store_img,stores.name,stores.id from stores where stores.id=?", (rec[0],))
    rec_list=[{"rec_img":r[0],"rec_name":r[1],"rec_id":r[2]} for r in c.fetchall()]
    
    c.execute("select genre.id from genre")
    genre_num=c.fetchall()
    print(genre_num)

    all_stores = []
    for i in genre_num:
        img_list = []
        c.execute("select stores.store_img,stores.name,stores.id from stores join genre on stores.genre_id=genre.id where genre.id=?", (i))
        for row in c.fetchall():
            img_list.append({"img": row[0], "name": row[1], "id": row[2]})
        all_stores.append(img_list)
    conn.close
    title_name = "KOZADO ジャンル選択ページ"
    css = "../static/css/genre.css"
    return render_template("genre.html", img_list=img_list, all_stores=all_stores,rec_list=rec_list, title_name=title_name, css=css)


@app.route('/scene')
def scene_list():
    conn = sqlite3.connect('groupwork.db')
    c = conn.cursor()
    c.execute("SELECT store_id,max(c) FROM(SELECT store_id,count(store_id) as c FROM favorite GROUP BY store_id)")
    rec=c.fetchall()[0]
    print(rec[0])
    c.execute("select stores.store_img,stores.name,stores.id from stores where stores.id=?", (rec[0],))
    rec_list=[]
    for r in c.fetchall():
        rec_list.append({"rec_img":r[0],"rec_name":r[1],"rec_id":r[2]})
    
    c.execute("select scene.id from scene")
    scene_num=c.fetchall()
    print(scene_num)

    all_stores = []
    for i in scene_num:
        img_list = []
        c.execute("select stores.store_img,stores.name,stores.id from stores join scene on stores.scene_id=scene.id where scene.id=?", (i))
        for row in c.fetchall():
            img_list.append({"img": row[0], "name": row[1], "id": row[2]})
        all_stores.append(img_list)
    conn.close
    title_name = "KOZADO シーン選択ページ"
    css = "../static/css/scene.css"
    return render_template('scene.html', img_list=img_list, all_stores=all_stores,rec_list=rec_list, title_name=title_name, css=css)


# 店舗詳細ページ


@app.route('/shopinfo/<int:id>')
def shopinfo(id):

    conn = sqlite3.connect('groupwork.db')
    c = conn.cursor()
    c.execute("select map,store_tel,name,store_img,id,store_time,holiday from stores where stores.id=?",(id,))
    shopinfo=[]
    for row in c.fetchall():
        shopinfo.append({"map":row[0],"tel":row[1],"name":row[2],"store_img":row[3],"store_id":row[4],"time":row[5],"day":row[6]})
    conn.close
    title_name = "KOZADO 店舗詳細ページ"
    css = "../static/css/shopinfo.css"
    return render_template('shopinfo.html',shopinfo=shopinfo,title_name=title_name, css=css)

# お気に入り押した時の処理


@app.route('/add_fav',methods=["POST"])
def add_fav():
    if 'user_id' in session:
        user_id = session['user_id'][0]
        store_id=request.form.get("store_id")
        print('store_id ', store_id)
        print("テストだよ")
        conn = sqlite3.connect('groupwork.db')
        c = conn.cursor()
        c.execute("replace into favorite values(null,?,?,0)",(user_id, store_id,))
        conn.commit()
        conn.close()
           
        return redirect('/favorite')
    else:
        return redirect("/login")

# お気に入り削除


@app.route('/del_fav',methods=["POST"])
def del_fav():
    if 'user_id' in session:
        stores_id=request.form.get("delete")
        print("---------------------")
        print(stores_id)
        conn = sqlite3.connect("groupwork.db")
        c = conn.cursor()
        # c.execute("update favorite set fav = 1 where favorite.store_id=?", (stores_id,))
        c.execute("delete from favorite where favorite.store_id=?",(stores_id,))
        print("oi")
        conn.commit()
        c.close()
        return redirect("/favorite")
    else:
        return redirect("/login")

# お気に入りリスト


@app.route('/favorite')
def favorite():
    if 'user_id' in session:
        user_id = session['user_id'][0]
        conn = sqlite3.connect('groupwork.db')
        c = conn.cursor()
        c.execute("select stores.name,stores.store_img,stores.id from stores join favorite on stores.id=store_id and users_id=? where fav=0",(user_id,))
        fav_list = []
        for row in c.fetchall():
            fav_list.append({"name": row[0], "img": row[1],"id":row[2]})
        title_name = "KOZADO お気に入りリスト"
        css = "../static/css/favorite.css"
        return render_template('favorite.html', title_name=title_name, fav_list=fav_list, css=css)
    else:
        return redirect("/login")    


@app.errorhandler(404)
def notfound(code):
    return "404だよ！！見つからないよ！！！"


# __name__ というのは、自動的に定義される変数で、現在のファイル(モジュール)名が入ります。 ファイルをスクリプトとして直接実行した場合、 __name__ は __main__ になります。
if __name__ == "__main__":
    # Flask が持っている開発用サーバーを、実行します。
    app.run(debug=True)

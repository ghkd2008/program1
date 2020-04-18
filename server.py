from time import strftime

from flask import Flask, render_template, request, jsonify
import requests
import datetime
app = Flask(__name__)

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.program1                    # 'program1'라는 이름의 db를 만듭니다.

@app.route('/')
def home():
    return render_template('index.html')

## API 역할을 하는 부분
@app.route('/ingredients', methods=['POST'])
def write_ingredient():
    ingredient_receive = request.form['ingredient_give']
    quantity_receive = request.form['quantity_give']
    expiration_date_receive = request.form['expiration_date_give']
    production_cost_receive = request.form['production_cost_give']

    ingredient = {
        'ingredient':ingredient_receive,
        'quantity':int(quantity_receive),
        'expiration_date':expiration_date_receive,
        'production_cost':int(production_cost_receive)
    }

    db.ingredients_list.insert_one(ingredient)
    return jsonify({'result':'success', 'msg': '재료가 성공적으로 저장되었습니다!'})

@app.route('/ingredients', methods=['GET'])
def read_ingredients():
    ingredients = list(db.ingredients_list.find({},{'_id':0}))
    return jsonify({'result':'success', 'ingredients': ingredients})

#데이터 수정하기 코드 짜보기! 이어서 할 부분
#db.users.update_one({'name':'bobby'},{'$set':{'name':'bob'}})
#1.페이지에서 값을 입력받고
#2.그것이 db에 있는지 확인하고
#3. 있으면 바꿔주기
#4. 없으면 '이러한 재료가 존재하지 않습니다' 오류 띄우기
#db.ingredients_list.update_one({'ingredient':'...','quantity':'...','expiration_date'},{'$set':{'age':'10'}})


@app.route('/change_ingredients', methods = ['POST'] )
def check_ingredient():
    now_ingredient_name = request.form['now_ingredient_name_give']
    now_ingredient_quantity = request.form['now_ingredient_quantity_give']
    now_ingredient_production_cost = request.form['now_ingredient_production_cost_give']
    now_ingredient_expiration_date = request.form['now_ingredient_expiration_date_give']
    change_ingredient_name = request.form['change_ingredient_name_give']
    change_ingredient_quantity = request.form['change_ingredient_quantity_give']
    change_ingredient_production_cost = request.form['change_ingredient_production_cost_give']
    change_ingredient_expiration_date = request.form['change_ingredient_expiration_date_give']

    now_ingredient = {
        'ingredient':now_ingredient_name,
        'quantity':int(now_ingredient_quantity),
        'expiration_date':now_ingredient_expiration_date,
        'production_cost':int(now_ingredient_production_cost)
    }

    change_ingredient = {
        'ingredient': change_ingredient_name,
        'quantity':int(change_ingredient_quantity),
        'expiration_date':change_ingredient_expiration_date,
        'production_cost':int(change_ingredient_production_cost)

    }

    for i in list(db.ingredients_list.find({},{'_id':0})):
        if now_ingredient == i:
            db.ingredients_list.update_one(i,{'$set': change_ingredient})
        return jsonify({'result':'success', 'msg': '재료가 성공적으로 수정되었습니다!'})


@app.route('/menus',methods = ['POST'])
def write_menus():
    menus_receive = request.form['menus_give']
    menu_date_receive = request.form['menu_date_give']

    order = {
        'menus': menus_receive,
        'menu_date': menu_date_receive,
    }

    db.orders_list.insert_one(order)
    return jsonify({'result':'success', 'msg': '주문이 성공적으로 저장되었습니다!'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)





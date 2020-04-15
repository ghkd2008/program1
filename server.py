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
        'expiration_date':datetime.datetime.strptime(expiration_date_receive,'%Y-%m-%d'),
        'production_cost':int(production_cost_receive)
    }

    db.ingredients_list.insert_one(ingredient)
    return jsonify({'result':'success', 'msg': '재료가 성공적으로 저장되었습니다!'})

@app.route('/ingredients', methods=['GET'])
def read_ingredients():
    ingredients = list(db.ingredients_list.find({},{'_id':0}))
    return jsonify({'result':'success', 'ingredients': ingredients})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)





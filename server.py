import json
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
    ingredients = list(db.ingredients_list.find({}, {'_id': 0}))

    for i in ingredients:
        if ingredient_receive == i['ingredient'] and expiration_date_receive == i['expiration_date'] and int(production_cost_receive) == i['production_cost']:
            db.ingredients_list.update_one({'ingredient':i['ingredient']},{'$set':{'quantity':i['quantity']+int(quantity_receive)}})
        else:
            db.ingredients_list.insert_one(ingredient)
    return jsonify({'result':'success', 'msg': '재료가 성공적으로 저장되었습니다!'})

@app.route('/ingredients', methods=['GET'])
def read_ingredients():
    ingredients = list(db.ingredients_list.find({},{'_id':0}).sort('expiration_date', 1))
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
    ingredient_list = list(db.ingredients_list.find({}, {'_id': 0}))
    for i in ingredient_list:
        if i == now_ingredient:
            db.ingredients_list.update_one(i,{'$set': change_ingredient})
            return jsonify({'result':'success', 'msg': '재료가 성공적으로 수정되었습니다!'})



#메뉴명을 입력하면 그에 맞는 레시피를 레시피 리스트에서 찾아주는 함수 만들기
def find_menu_recipe(name, list):
    for i in list:
        if i['menu_name'] == name:
            return i['recipe_list']





@app.route('/menus',methods = ['POST'])
def write_menus():
    ingredient_list = list(db.ingredients_list.find({}, {'_id': 0}))
    orders = list(db.orders_list.find({}, {'_id': 0}))
    recipes = list(db.recipes_list.find({}, {'_id': 0}))

    menus_receive = request.form['menus_give']
    menu_date_receive = request.form['menu_date_give']

    order = {
        'menus': menus_receive,
        'menu_date': menu_date_receive,
    }

        #menus_receive = [{name, quantity}]
        # 디비 저장

        # 메뉴 레시피 얻어오기
        #recipes = [{menu_name, recipe_list}]
        #recipe_list = "[{ingredient, ingredient_need_quantity}]"

        # 필요 재료들
        # ingredient_needs = [{name, quantity}]
    ingredient_needs = {}

    for m in json.loads(menus_receive):
        menu_count = int(m['quantity'])
        recipe_list = find_menu_recipe(m['name'], recipes)
        for r in json.loads(recipe_list):
            ing_name = r['ingredients']
            use_quantity = r['ingredients_need_quantity']
            if ing_name not in ingredient_needs:
                ingredient_needs[ing_name] = 0
            ingredient_needs[ing_name] += int(use_quantity) * menu_count

    exsist_ingre = {}
    for i in ingredient_list:
        name = i['ingredient']
        if name not in exsist_ingre:
            exsist_ingre[name] = 0
        exsist_ingre[name] += i['quantity']

    for need_ing_name in ingredient_needs:
        need_ing_count = ingredient_needs[need_ing_name]

        if need_ing_name not in exsist_ingre:
            result = {
                'result': 'fail',
                'msg': need_ing_name + '이 없습니다.'
            }
            return jsonify(result)

        exsist_ingre_count = exsist_ingre[need_ing_name]

        if need_ing_count > exsist_ingre_count:
            gap = need_ing_count - exsist_ingre_count
            return jsonify({'result': 'success', 'msg': need_ing_name + '이' + str(gap) + '만큼 부족합니다.'})

    # 이제 만들 수 있다.
    for need_ing_name in ingredient_needs:
        use_count = ingredient_needs[need_ing_name]

        ing_info = list(db.ingredients_list.find({'ingredient': need_ing_name}).sort('expiration_date', 1))

        for info in ing_info:
            if use_count == 0:
                break

            if info['quantity'] >= use_count:
                info['quantity'] -= use_count
            else:
                use_count -= info['quantity']
                info['quantity'] = 0

            db.ingredients_list.update_one({'_id': info['_id']}, {'$set':info})
            #db.users.update_one({'name': 'bobby'}, {'$set': {'age': 19}})


    db.orders_list.insert_one(order)
    return jsonify({'result':'success', 'msg': '주문이 성공적으로 저장되었습니다!'})


@app.route('/menus',methods = ['GET'])
def read_orders():
    orders = list(db.orders_list.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'orders': orders})

@app.route('/recipes', methods = ['POST'])
def write_recipe():
    recipe_name_receive = request.form['menu_name_give']
    recipe_price_receive = request.form['menu_price_give']
    recipe_ingredients_receive = request.form['recipe_list_give']

    recipes = {
        'menu_name': recipe_name_receive,
        'menu_price' : recipe_price_receive,
        'recipe_list' :recipe_ingredients_receive
    }

    db.recipes_list.insert_one(recipes)
    return jsonify({'result': 'success', 'msg': '레시피가 성공적으로 저장되었습니다!'})

@app.route('/recipes',methods = ['GET'])
def read_recipes():
    recipes = list(db.recipes_list.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'recipes': recipes})

#현재 재료 리스트에서 재료명으로 그 재료의 수량을 찾는 함수
def get_ingre_quantity(name, list):
    for i in list:
        if i['ingredient'] == name:
            return i['quantity']
    return 0

@app.route('/max_menu',methods = ['GET'])
def write_max_menu():
    #레시피 db에서 리스트로 가져오기
    recipes_list = list(db.recipes_list.find({}, {'_id': 0}))
    #현재 재료 db에서 리스트로 가져오기
    ingredient_list = list(db.ingredients_list.find({}, {'_id': 0}))
    # 레시피 리스트에 있는 메뉴별 최대 생산가능 갯수 리스트
    counted_menus = []
    for i in recipes_list:
        max_menu_list =[]
        alist = json.loads(i['recipe_list'])
        #재료별로 생산가능한 최대 갯수가 들어감. 이거를 이용해서 최솟값을 뽑기 위해 담아두는 리스트
        for j in alist:
            name = j['ingredients']
            quantity = j['ingredients_need_quantity']
            exist_quantity = get_ingre_quantity(name,ingredient_list)
            number = int(exist_quantity/int(quantity))
            max_menu_list.append(number)
        max_count = min(max_menu_list)

        available_menu = {
        'name': i['menu_name'],
        'count' : max_count
        }

        counted_menus.append(available_menu)

    return jsonify({'result': 'success', 'counted_menus': counted_menus})
#counted_menus = [{'name': '메뉴1', 'count': 1}, {'name': '메뉴2', 'count': 1}]

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)





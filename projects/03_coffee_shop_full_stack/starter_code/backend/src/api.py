import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# TEST DATA
# drink = Drink(
#     title='pina collada',
#     recipe='[{"name": "collada", "color": "yellow", "parts": 1}]'
# )
# drink.insert()

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]

    if not drinks:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200

    



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks_long = [drink.long() for drink in Drink.query.all()]
        if not drinks_long:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks_long
        })
    except:
        abort(401)


'''
@DONE @TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def make_drink(jwt):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if not(title and recipe):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Title and recipe required'
        }), 422

    try:
        drink = Drink(title=title, recipe=json.dumps([recipe]))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    
    except:
        abort(404)



'''
@DONE @TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if not title:
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Title required'
        }), 422

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if drink is None:
            abort(404)
        # Not completed
        drink.title = title
        drink.recipe = json.dumps(recipe)    
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    
    except:
        abort(404)



    


'''
@DONE @TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if not drink:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            "success": True, "delete": id
        })

    except:
        abort(422)




## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized access'
    }), 401

# Snippet from: https://github.com/henrylin2008/coffee_shop_full_stack/blob/master/backend/src/api.py
# https://github.com/henrylin2008/coffee_shop_full_stack/blob/master/backend/src/api.py    
@app.errorhandler(AuthError)
def auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
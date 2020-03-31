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


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        available_drinks = Drink.query.all()
        drinks = [drink.short() for drink in available_drinks]
        print(drinks)
        return jsonify({
            'success': True,
            'drinks': drinks
        })

    except:
        return jsonify({
            'success': False,
            'message': "The drink is not formatted correctly and can't be shown"
        })


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
def get_drink_details(payload):
    try:
        available_drinks = Drink.query.all()
        drinks = [drink.long() for drink in available_drinks]
        print(drinks)
        return jsonify({
            'success': True,
            'drinks': drinks
        })


    except:
        return jsonify({
            'success': False,
            'message': "The drink is not formatted correctly and can't be shown"
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_drink(payload):
    try:
        new_recipe = request.json.get('recipe')
        new_title = request.json.get('title')
        # check if drink already exists
        existing_drinks = Drink.query.all()
        for drink in existing_drinks:
            if drink.title == new_title:
                return jsonify({
                    'success': False,
                    'message': "A drink with this title already exists"
                })

        new_drink = Drink(title=new_title,
                          recipe=json.dumps(new_recipe))
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': Drink.long(new_drink)
        })

    except:
        return jsonify({
            'success': False,
            'message': 'An unknown error happened'
        })


'''
@TODO implement endpoint
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
@requires_auth('post:drinks')
def update_drink(payload, drink_id):
    try:
        # Check if drink exists
        drink_exists = False
        existing_drinks = Drink.query.all()
        for drink in existing_drinks:
            if drink.id == drink_id:
                drink_exists = True

        if not drink_exists:
            return jsonify({
                'success': False,
                'message': 'This drink does not exist',
                'drinks': []
            })

        drink = Drink.query.filter_by(id=drink_id).one()
        if request.json.get('title') is not None:
            drink.title = json.dumps(request.json.get('title'))

        if request.json.get('recipe') is not None:
            drink.recipe = json.dumps(request.json.get('recipe'))

        drink.update()
        print(drink.short())

        return jsonify({
            'success': True,
            'drinks': [Drink.long(drink)]
        })
    except:
        return jsonify({
            'success': False,
            'message': 'An unknown error occured.'
        })


'''
@TODO implement endpoint
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
def delete_drink(payload, drink_id):
    try:
        # Check if drink exists
        drink_exists = False
        existing_drinks = Drink.query.all()
        for drink in existing_drinks:
            if drink.id == drink_id:
                drink_exists = True

        if not drink_exists:
            return jsonify({
                'success': False,
                'message': 'This drink does not exist'
            })

        drink = Drink.query.filter_by(id=drink_id).one()

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        return jsonify({
            'success': False,
            'message': 'An unknown error occured.'
        })


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
        "success": False,
        "error": 404,
        "message": "Ressource could not be found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        'error': error.status_code,
        "message": error.error,
    }), error.status_code

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
@app.route('/drinks')
def get_drinks():
    """
    Return shorter detail of all drinks
    """
    try:
        drinks = Drink.query.all()
        drinks_short_format = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_short_format
        }), 200
    except Exception:
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    """
    provides longer drink details to barista who have permission
    """
    try:
        drinks = Drink.query.all()
        drinks_long_format = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_long_format
        }), 200
    except Exception:
        abort(422)

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
def create_drink(payload):
    """
    Post new drink if manager with post permission
    """
    try:
        body = request.get_json(request)
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title is None or recipe is None:
            abort(400)
        # check if title is already present
        drink = Drink.query.filter(Drink.title == title).one_or_none()
        if drink:
            abort(400)
        # Create new drink
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
        new_drink_result = Drink.query.filter(Drink.id == new_drink.id).first()
        drink_long_format = new_drink_result.long()
        return jsonify({
            'success': True,
            'drinks': drink_long_format
        })
    except Exception:
        abort(422)


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
@app.route('/drinks/<int:drink_id', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(payload, drink_id):
    try:
        body = request.get_json(request)
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title is None or recipe is None:
            abort(400)
        # check if id is already present
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        # edit drink
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()
        drink_long_format = drink.long()
        return jsonify({
            'success': True,
            'drinks': drink_long_format
        })
    except Exception:
        abort(422)



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


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

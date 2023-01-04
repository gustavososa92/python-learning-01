from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient


app = Flask(__name__)

api = Api(app)

client = MongoClient("mongodb://admin:password@mongodb:27017")
db = client["firstdb"]
userNum = db["userNum"]

userNum.insert_one(
    {
        "num_of_users": 0
    }
)


class Visit(Resource):
    def get(self):
        prev_num = userNum.find()[0]["num_of_users"]
        new_num = prev_num + 1
        userNum.update_one(
            {},
            {
                "$set": {"num_of_users": new_num}
            }
        )
        return str("Hello user " + str(new_num))


def checkPostedData(data, functionName):
    if 'x' not in data or 'y' not in data:
        return 400
    if functionName == 'divide':
        if int(data.get('y')) == 0:
            return 418
    return 200


class Add(Resource):
    def post(self):
        # the resource add was requested using POST
        data = request.get_json()

        statusCode = checkPostedData(data, 'add')

        if statusCode != 200:
            retJson = {
                'message': "Error",
                'statusCode': statusCode
            }
            return jsonify(retJson)

        x = data['x']
        y = data['y']

        result = x + y
        retJson = {
            'message': result,
            'statusCode': 200
        }
        return jsonify(retJson)


class Substract(Resource):
    def post(self):
        # the resource substract was requested using POST
        data = request.get_json()

        statusCode = checkPostedData(data, 'substract')

        if statusCode != 200:
            retJson = {
                'message': "Error",
                'statusCode': statusCode
            }
            return jsonify(retJson)

        x = data['x']
        y = data['y']

        result = x - y
        retJson = {
            'message': result,
            'statusCode': 200
        }
        return jsonify(retJson)


class Divide(Resource):
    def post(self):
        # the resource divide was requested using POST
        data = request.get_json()

        statusCode = checkPostedData(data, 'divide')

        if statusCode != 200:
            retJson = {
                'message': "Error",
                'statusCode': statusCode
            }
            return jsonify(retJson)

        x = data['x']
        y = data['y']

        result = (x * 1.0) / y
        retJson = {
            'message': result,
            'statusCode': 200
        }
        return jsonify(retJson)


class Multiply(Resource):
    def post(self):
        # the resource multiply was requested using POST
        data = request.get_json()

        statusCode = checkPostedData(data, 'multiply')

        if statusCode != 200:
            retJson = {
                'message': "Error",
                'statusCode': statusCode
            }
            return jsonify(retJson)

        x = data['x']
        y = data['y']

        result = x * y
        retJson = {
            'message': result,
            'statusCode': 200
        }
        return jsonify(retJson)


api.add_resource(Add, "/add")
api.add_resource(Substract, "/substract")
api.add_resource(Divide, "/divide")
api.add_resource(Multiply, "/multiply")
api.add_resource(Visit, "/hello")


if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=4000, debug=True)

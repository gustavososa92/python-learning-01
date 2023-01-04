"""
Registration of a user 0 tokens
Each user gets 10 tokens
Store a sentencce on our database for 1 token
Retrieve his stored sentence on our database for 1 token
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
import bcrypt


app = Flask(__name__)

api = Api(app)

client = MongoClient("mongodb://admin:password@mongodb:27017")
db = client["sentencesDatabase"]
users = db["users"]

errorMissingParam = "Error: Missing username or password"
errorLogin = "Error: username or password doesnt match"
errorTokens = "Error: Not enough tokens"


class Register(Resource):
    def post(self):
        data = request.get_json()
        statusCode = checkPostedData(data)

        if statusCode != 200:

            retJson = {
                'message': errorMissingParam,
                'statusCode': statusCode
            }
            return jsonify(retJson)

        username = data['username']
        password = data['password']

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one(
            {
                "username": username,
                "password": hashed_pw,
                "sentence": "",
                "tokens": 10
            }
        )

        retJson = {
            'message': "Successfully registered",
            'statusCode': 200
        }
        return jsonify(retJson)


class Store(Resource):
    def post(self):
        data = request.get_json()
        statusCode = checkPostedData(data)

        if statusCode != 200:
            retJson = {
                'message': errorMissingParam,
                'statusCode': statusCode
            }
            return jsonify(retJson)

        username = data['username']
        password = data['password']
        sentence = data['sentence']

        loginOK = login(username, password)
        if not loginOK:
            retJson = {
                'message': errorLogin,
                'statusCode': 401
            }
            return jsonify(retJson)

        tokens = getTokens(username)
        if tokens < 1:
            retJson = {
                'message': errorTokens,
                'statusCode': 400
            }
            return jsonify(retJson)

        users.update_one(
            {"username": username},
            {
                "$set":
                    {
                        "sentence": sentence,
                        "tokens": tokens - 1
                    }
            }
        )

        retJson = {
            'message': "Successfully stored",
            'statusCode': 200
        }
        return jsonify(retJson)


class Retrieve(Resource):
    def post(self):
        data = request.get_json()
        statusCode = checkPostedData(data)

        if statusCode != 200:
            retJson = {
                'message': errorMissingParam,
                'statusCode': statusCode
            }
            return jsonify(retJson)

        username = data['username']
        password = data['password']

        loginOK = login(username, password)
        if not loginOK:
            retJson = {
                'message': errorLogin,
                'statusCode': 401
            }
            return jsonify(retJson)

        tokens = getTokens(username)

        if tokens < 1:
            retJson = {
                'message': errorTokens,
                'statusCode': 400
            }
            return jsonify(retJson)

        sentence = users.find_one(
            {
                "username": username
            }
        )['sentence']
        newTokens = tokens - 1

        users.update_one(
            {"username": username},
            {
                "$set":
                {
                    "tokens": newTokens
                }
            }
        )

        retJson = {
            'message': f'Sentence: {sentence}\nTokens: {newTokens}',
            'statusCode': 200
        }
        return jsonify(retJson)


def checkPostedData(data):
    if 'username' not in data or 'password' not in data:
        return 400
    return 200


def login(username, password):
    hashed_pw = users.find_one({"username": username})['password']
    return bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw


def getTokens(username):
    return users.find_one({"username": username})['tokens']


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Retrieve, "/retrieve")


if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=4000, debug=True)

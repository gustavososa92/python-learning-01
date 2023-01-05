from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

import bcrypt
import spacy


app = Flask(__name__)

api = Api(app)


client = MongoClient("mongodb://admin:password@mongodb:27017")
db = client["similarity"]
users = db["users"]


errorMissingParam = "Error: Missing username or password"
errorUserExists = "Error: User already exists"
errorUserNotExists = "Error: User not exists"
errorLogin = "Error: username or password doesnt match"
errorAdminLogin = "Error: Admin username or password doesnt match"
errorTokens = "Error: Not enough tokens"


def checkPostedData(data):
    if 'username' not in data or 'password' not in data:
        return 400
    return 200


def userExists(username):
    return users.count_documents(
        {
            "username": username
        }
    ) > 0


def login(username, password):
    hashed_pw = users.find_one({"username": username})['password']
    return bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw


def getTokens(username):
    return users.find_one({"username": username})['tokens']


def loginAdmin(username, password):
    user = users.find_one({"username": username})
    hashed_pw = user['password']
    isAdmin = user['isAdmin']

    return bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw and isAdmin


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

        if userExists(username):
            retJson = {
                'message': errorUserExists,
                'statusCode': 400
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one(
            {
                "username": username,
                "password": hashed_pw,
                "tokens": 10
            }
        )

        retJson = {
            'message': "Successfully registered",
            'statusCode': 200
        }
        return jsonify(retJson)


class Detect(Resource):
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
        text1 = data['text1']
        text2 = data['text2']

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

        # Natural language processor
        nlp = spacy.load("en_core_web_sm")
        # Convert each text
        text1 = nlp(text1)
        text2 = nlp(text2)
        # Calculate de similiraty ratio, diff= 0 equals=1
        ratio = text1.similarity(text2)

        users.update_one(
            {"username": username},
            {
                "$set":
                    {
                        "tokens": tokens - 1
                    }
            }
        )

        retJson = {
            'similarity': ratio,
            'message': "Successfully Calculated",
            'statusCode': 200
        }
        return jsonify(retJson)


class Refill(Resource):
    def post(self):
        data = request.get_json()
        statusCode = checkPostedData(data)

        if statusCode != 200:
            retJson = {
                'message': errorMissingParam,
                'statusCode': statusCode
            }
            return jsonify(retJson)

        adminUsername = data['admin_username']
        adminPass = data['admin_pw']
        refillAmount = data['refill']
        userToRefill = data['user']

        loginOK = loginAdmin(adminUsername, adminPass)
        if not loginOK:
            retJson = {
                'message': errorAdminLogin,
                'statusCode': 401
            }
            return jsonify(retJson)

        if not userExists(userToRefill):
            retJson = {
                'message': errorUserNotExists,
                'statusCode': 404
            }
            return jsonify(retJson)

        tokens = getTokens(userToRefill)

        users.update_one(
            {"username": userToRefill},
            {
                "$set":
                {
                    "tokens": tokens + refillAmount
                }
            }
        )

        retJson = {
            'message': "Successfully refilled",
            'statusCode': 200
        }
        return jsonify(retJson)


api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refill, "/refill")


if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=4000, debug=True)

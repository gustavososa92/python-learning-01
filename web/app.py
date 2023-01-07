from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

import bcrypt
import requests
import subprocess
import json


app = Flask(__name__)

api = Api(app)


client = MongoClient("mongodb://admin:password@mongodb:27017")
# client = MongoClient("mongodb://admin:password@localhost:27017")
db = client["classify"]
users = db["users"]


errorMissingParam = "Error: Missing username or password"
errorUserExists = "Error: User already exists"
errorUserNotExists = "Error: User not exists"
errorLogin = "Error: username or password doesnt match"
errorAdminLogin = "Error: Admin username or password doesnt match"
errorTokens = "Error: Not enough tokens"


def checkAdmin():
    adminPassword = bcrypt.hashpw("admin".encode('utf8'), bcrypt.gensalt())
    admin = users.find_one({"username": "admin"})

    if admin is None:
        print("No admin, creating...")
        users.insert_one(
            {
                "username": "admin",
                "password": adminPassword,
                "isAdmin": True
            }
        )
    elif 'password' not in admin:
        print("No admin password, creating...")
        users.update_one(
            {"username": "admin"},
            {"$set":
                {
                    "password": adminPassword
                }
             }
        )


def checkPostedData(data):
    error = 'username' not in data or 'password' not in data
    return generateRetJson(400, errorMissingParam), error


def checkPostedDataAdmin(data):
    error = 'admin_username' not in data or 'admin_pw' not in data
    return generateRetJson(400, errorMissingParam), error


def userExists(username):
    return users.count_documents(
        {
            "username": username
        }
    ) > 0


def login(username, password):
    hashed_pw = users.find_one({"username": username})['password']
    loginOk = bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw
    return generateRetJson(401, errorLogin), not loginOk


def getTokens(username):
    return users.find_one({"username": username})['tokens']


def loginAdmin(username, password):
    user = users.find_one({"username": username})
    hashed_pw = user['password']
    isAdmin = user['isAdmin']

    loginAdminOk = bcrypt.hashpw(password.encode(
        'utf8'), hashed_pw) == hashed_pw and isAdmin

    return generateRetJson(401, errorAdminLogin), not loginAdminOk


def generateRetJson(code, message):
    return {
        'message': message,
        'statusCode': code
    }


def validateEnoughTokens(username):
    tokens = getTokens(username)
    error = tokens < 1
    return tokens, generateRetJson(400, errorTokens), error


class Register(Resource):
    def post(self):
        checkAdmin()
        data = request.get_json()

        retJson, error = checkPostedData(data)
        if error:
            return jsonify(retJson)

        username = data['username']
        password = data['password']

        if userExists(username):
            return jsonify(generateRetJson(400, errorUserExists))

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one(
            {
                "username": username,
                "password": hashed_pw,
                "tokens": 10,
                "isAdmin": False
            }
        )

        return jsonify(generateRetJson(200, "Successfully registered"))


class Classify(Resource):
    def post(self):
        data = request.get_json()

        retJson, error = checkPostedData(data)
        if error:
            return jsonify(retJson)

        username = data['username']
        password = data['password']
        url = data['url']

        retJson, error = login(username, password)
        if error:
            return jsonify(retJson)

        tokens, retJson, error = validateEnoughTokens(username)
        if error:
            return jsonify(retJson)

        r = requests.get(url)
        retJson = {}

        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg',
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            proc.communicate()[0]
            proc.wait()
            with open("text.text") as g:
                retJson = json.load(g)

        users.update_one(
            {"username": username},
            {
                "$set":
                    {
                        "tokens": tokens - 1
                    }
            }
        )

        return jsonify(retJson)


class Refill(Resource):
    def post(self):
        data = request.get_json()

        retJson, error = checkPostedDataAdmin(data)
        if error:
            return jsonify(retJson)

        adminUsername = data['admin_username']
        adminPass = data['admin_pw']
        refillAmount = data['refill']
        userToRefill = data['user']

        retJson, error = loginAdmin(adminUsername, adminPass)
        if error:
            return jsonify(retJson)

        if not userExists(userToRefill):
            return jsonify(generateRetJson(404, errorUserNotExists))

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

        return jsonify(generateRetJson(200, "Successfully refilled"))


api.add_resource(Register, "/register")
api.add_resource(Classify, "/classify")
api.add_resource(Refill, "/refill")


if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=4000, debug=True)

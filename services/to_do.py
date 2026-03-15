from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route('/')
@app.route('/home')
@app.route('/home1', methods=['GET'])
@app.route('/<int:name>')
def func1(name):
    optional = request.args.get("done")

    return f"Fetching todos: {name}+{name}+{optional}" #http://127.0.0.1:5000/15

@app.route('/about/<int:name>')
def func2(name):
    optional = request.args.get("done")
    page= request.args.get('page')
    return f"Fetching todos: {name}+{name}+{optional}+{page}"     #http://127.0.0.1:5000/about/15  http://127.0.0.1:5000/about/15?done=True http://127.0.0.1:5000/about/15?done=True&page=29 http://127.0.0.1:5000/about/15?done=True&page=Okay

@app.route("/users/<string:username>")
def get_user(username):
    return f"Looking up user: {username}"

app.run()



# import requests
# from flask import Flask, jsonify
# #
# # app = Flask(__name__)
# #
# # @app.route("/status")
# # def status():
# #     return jsonify({"status": "API is running"})
#
#
# # from flask import Flask
# #
# # app = Flask(__name__)
# #
# # @app.route("/status")
# # def status():
# #     return jsonify({"status": "API is running"})
# #
# # if __name__ == "__main__":
# #     app.run(debug=True)
#
#
#
#
#
#
# # from flask import Flask
# #
# # app = Flask(__name__)
# #
# # @app.route("/")
# # def home():
# #     return "Welcome to Todo API"
# #
# # if __name__ == "__main__":
# #     app.run(debug=True)
# #
# # ---------------------------------------
# # from flask import Flask, jsonify
# #
# # app = Flask(__name__)
# #
# # @app.route("/status")
# # def status():
# #     return jsonify({"status": "API is running"})
# # ---------------------------------------
# #
# # from flask import Flask, request, jsonify
# #
# # app = Flask(__name__)
# #
# # todos = []
# #
# # @app.route("/todo", methods=["POST"])
# # def create_todo():
# #     data = request.json
# #     task = data["task"]
# #
# #     todos.append(task)
# #
# #     return jsonify({"message": "Task added", "todos": todos})
#
#
# from flask import Flask,jsonify, request
#
#
# app = Flask(__name__)
#
# @app.route("/")
# def func():
#     return request.json
#
# if __name__ == '__main__':
#     app.run(debug=True)
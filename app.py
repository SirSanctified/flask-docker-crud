from os import environ
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DB_URL")
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def json(self):
        return {"id": self.id, "title": self.title, "content": self.content}


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    return make_response(jsonify({"message": "Hello, World!"}), 200)


@app.route("/posts", methods=["POST"])
def create():
    try:
        data = request.get_json()
        post = Post(title=data["title"], content=data["content"])
        db.session.add(post)
        db.session.commit()
        return make_response(jsonify(post.json()), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/posts", methods=["GET"])
def read():
    try:
        posts = Post.query.all()
        return make_response(jsonify([post.json() for post in posts]), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/posts/<int:id>", methods=["GET"])
def read_by_id(id):
    try:
        post = Post.query.filter_by(id=id).first()
        if not post:
            return make_response(jsonify({"error": "Post not found"}), 404)
        return make_response(jsonify(post.json()), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/posts/<int:id>", methods=["PUT"])
def update(id):
    try:
        data = request.get_json()
        post = Post.query.filter_by(id=id).first()
        if not post:
            return make_response(jsonify({"error": "Post not found"}), 404)
        post.title = data["title"]
        post.content = data["content"]
        db.session.commit()
        return make_response(jsonify(post.json()), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/posts/<int:id>", methods=["DELETE"])
def delete(id):
    try:
        post = Post.query.filter_by(id=id).first()
        if not post:
            return make_response(jsonify({"error": "Post not found"}), 404)
        db.session.delete(post)
        db.session.commit()
        return make_response("", 204)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"error": "Bad request"}), 400)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

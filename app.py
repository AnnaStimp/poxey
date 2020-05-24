from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from poke import get_pokemon_data

app = Flask(__name__)
app.secret_key = '*PInefdlyv5@'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(hours=4)

db = SQLAlchemy(app)

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __str__(self):
        return f"Username - {self.name} Email - {self.email}"


@app.route('/')
def index():
    if session.get('username'):
        return redirect(url_for("search"))
    return render_template("index.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if session.get('username'):
        return redirect(url_for("search"))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password = generate_password_hash(password)
        found_user = User.query.filter_by(name=username).first()

        if found_user:
            return redirect(url_for("index"))
        else:
            user = User(username, email, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
        return redirect(url_for("search"))

    return render_template("signup.html")


@app.route('/signin', methods=['GET', 'POST'])
def signin():

    if session.get('username'):
        return redirect(url_for("search"))

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('search', name=user.name))

    return render_template("signin.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('pokemon_username', None)
    session.pop('pokemon_img', None)
    return redirect(url_for("index"))

@app.route('/profile/<name>', methods=['GET', 'POST'])
def profile(name):
    return render_template("profile.html")


@app.route('/adventure', methods=['GET', 'POST'])
def adventure():
    return render_template("adventure.html")


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        user_input = request.form["user_input"].lower()
        pokemon_data = get_pokemon_data(user_input)
        
        if(pokemon_data != "Error"):
            session['pokemon_id'] = pokemon_data["_id"]
            session['pokemon_name'] = pokemon_data["name"]
            session['pokemon_height'] = pokemon_data["height"]
            session['pokemon_weight'] = pokemon_data["weight"]
            session['pokemon_types'] = pokemon_data["pokemonType"]
            session['pokemon_img'] = pokemon_data["sprites"]
        
    return render_template("search.html")
    
@app.route('/history')
def pokemon():
    return render_template("history.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)


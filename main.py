import json
import requests
from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = Users.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None
    return None

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    class Users(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))


    class Cities(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        temp = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        desc = db.Column(db.String(100))
        time = db.Column(db.DateTime, default=datetime.utcnow)
    db.create_all()


class MyModelView(ModelView):
        def is_accessible(self):
            return True

admin = Admin(app)
admin.add_view(MyModelView(Users, db.session))
admin.add_view(MyModelView(Cities, db.session))


@app.route("/")
def start ():











    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name")
        phone=request.form.get("phone")
        password=generate_password_hash(
                request.form.get("password"),
                method='pbkdf2:sha256',
                salt_length=8
            )
        new_user=Users(
            name=name,
            phone=phone,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":


        password = request.form.get('password')

        phone = request.form.get("phone")
        user = Users.query.filter_by(phone=phone).first()
        if not user:
            flash("That user does not exist, please try again.")

            # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')

        # Email exists and password correct
        else:
            login_user(user)

            return redirect("/check")


    return render_template("login.html")
@app.route("/check",methods=["GET","POST"])
def check():
    name=current_user.name
    if request.method=="POST":
        city=request.form.get("city")
        API_KEY = "27bd1c926addeb97bac122010efa9bbc"
        Url = "https://api.openweathermap.org/data/2.5/weather"



        parameters = {
                "q": city,
                "appid": API_KEY
            }
        response = requests.get(url=Url, params=parameters)
        data = response.json()
        description = data["weather"][0]["description"]
        temp_kelvin = data["main"]["temp"]
        temp_in_celsius = int(temp_kelvin) - 273
        return f"{temp_in_celsius}"

    return render_template("check.html",name=name)
@app.route("/logout")
def logout():
    logout_user()
    return "logged out"

if __name__=="__main__":
    app.run(debug=True)
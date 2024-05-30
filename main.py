from random import choice
from os import listdir
from config import *
from database import Database
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from uuid import uuid4
from json import dumps
from models import Feed

app = Flask(__name__)
app.secret_key = "hello"


def logged_in_to(session):
    current_user = session.get("current_user")
    if current_user is None:
        return False
    return True

####################################################

@app.route('/get_feed')
def get_feed() -> list[Response, int]:
    current_user = session.get("current_user")
    if current_user is None:
        return {}, 511

    with Database() as db:        
        data = db.execute("""SELECT username, post_id, user.user_id, parent_post_id, image, caption
FROM post
INNER JOIN user
ON post.user_id = user.user_id""")

    response = Feed(data).serialise()
    return jsonify(response), 200

####################################################

@app.route('/new_post/<parent_post_id>', methods=["GET", "POST"])
def new_post(parent_post_id = None):
    if not logged_in_to(session):
        flash("Must be logged in to do that.")
        return redirect(url_for("login"))

    
    # render upload image form

    # if image has been uploaded, save it to the images directory

    # write the image filename and the caption (if applicable) to the database.

####################################################

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["uname"]
        form_password = request.form["psw"]

        with Database() as db:
            db_password = db.execute("SELECT password FROM user WHERE username = ?", [username], one_row=True)[0]
        
        if db_password and form_password == db_password:     
            session["current_user"] = username
            return redirect(url_for("index"))
        else:
            flash("Invalid username and/or password")
    
    return render_template("login.html")
            
    

####################################################

@app.route('/user/<user>')
def get_stats(user):

    if not logged_in_to(session):
        flash("Must be logged in to do that.")
        return redirect(url_for("login"))
    
    with Database() as db:
        username, profile_pic, post_count = db.execute(f'''SELECT username, profile_picture, COUNT(post_id)
                            FROM user
                            LEFT JOIN post ON user.user_id = post.user_id
                            WHERE username = ?
                            GROUP BY user.user_id;''',
        [user],
        one_row=True)
        
    return render_template("user.html", username=user, post_count=post_count, image=profile_pic)

####################################################

@app.route('/')
def index():
    if not logged_in_to(session):
        flash("Must be logged in to do that.")
        return redirect(url_for("login"))

    return render_template("feed.html")

####################################################

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)

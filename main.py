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
app.config["UPLOAD_FOLDER"] = "static/images/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

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

    query = """SELECT username, post.post_id, user.user_id, post.parent_post_id, image, caption, SUM(prize)
FROM post
INNER JOIN user
ON post.user_id = user.user_id
INNER JOIN vote
ON post.post_id = vote.post_id
GROUP BY post.post_id"""
    with Database() as db:        
        data = db.execute(query)
        print(query)

    response = Feed(data).serialise()
    return jsonify(response), 200

####################################################

@app.route('/new_post/<parent_post_id>', methods=["GET", "POST"])
@app.route('/new_post', methods=["GET", "POST"])
def new_post(parent_post_id = None):

    print("Writing image to disk.....")
    
    caption = request.form.get("caption")
    print(caption)
    image = request.files["uploaded_image"]
    print(caption, image.filename)
    result = image.save(app.config["UPLOAD_FOLDER"] + image.filename)
    print(result)

    ## store the stuff in the database

    with Database() as db:
        db.execute("""INSERT INTO Post(image, user_id, parent_post_id, caption)
                        VALUES (?, ?, ?, ?)""",
                        [image.filename, session['current_user'][0],
                        parent_post_id, caption])

    response = True
    return jsonify(response), 200

####################################################

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["uname"]
        form_password = request.form["psw"]

        with Database() as db:
            result = db.execute("SELECT user_id, password FROM user WHERE username = ?", [username], one_row=True)
        
        if result is not None:
            user_id, db_password = result
            if db_password and form_password == db_password:     
                session["current_user"] = (user_id, username)
                return redirect(url_for("index"))
        
        flash("Invalid username and/or password")
    
    return render_template("login.html")
            
####################################################

@app.route('/submit_vote/<post_id>/<prize>')
def submit_vote(post_id, prize):

    print(f"Submitted votoe {prize} for post {post_id}")
    user_id, username = session["current_user"]

    prize = {"1":"3", "2":"2", "3":"1"}[prize]

    with Database() as db:
            # does not return 
            post_changed_id = db.execute("""INSERT INTO vote(user_id, post_id, prize, parent_post_id)
    VALUES (?, ?, ?, (SELECT parent_post_id
                     FROM post
                     WHERE post_id=?))
    ON CONFLICT(user_id, prize, parent_post_id) 
    DO UPDATE SET post_id = ?""",
    [user_id, post_id, prize, post_id, post_id])
    

                
    feedback = f"Vote #{prize} given to post {post_id} by {username}!"      
    if post_changed_id:
        feedback += f" (Reassigned from {post_changed_id})"

    print(feedback)

    return jsonify(feedback), 200

####################################################

@app.route('/user/<user>')
def get_stats(user):

    if not logged_in_to(session):
        flash("Must be logged in to do that.")
        return redirect(url_for("login"))
    
    with Database() as db:
        username, profile_pic, post_count, popularity = db.execute(f'''SELECT username, profile_picture, COUNT(post_id), SUM()
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

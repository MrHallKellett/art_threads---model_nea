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

@app.route('/get_feed/<mode>')
def get_feed(mode) -> list[Response, int]:
    current_user = session.get("current_user")
    if current_user is None:
        return {}, STATUS_NOT_AUTHORISED


    query = GET_POSTS_AND_VOTES_QUERY
    with Database() as db:        
        data = db.execute(query)
        print(query)

    response = Feed(data, sort_popularity=mode=='2').serialise()
    return jsonify(response), STATUS_OK

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
        db.execute(INSERT_NEW_POST_QUERY,
                        [image.filename, session['current_user'][0],
                        parent_post_id, caption])

    response = True
    return jsonify(response), STATUS_OK

####################################################

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["uname"]
        form_password = request.form["psw"]

        with Database() as db:
            result = db.execute(GET_USERNAME_AND_PASSWORD_QUERY, [username], one_row=True)
        
        if result is not None:
            user_id, db_password = result
            if db_password and form_password == db_password:     
                session["current_user"] = (user_id, username)
                return redirect(url_for("index"))
        
        flash("Invalid username and/or password")
    
    return render_template("login.html")
            
####################################################

@app.route('/submit_vote/<post_id>/<rank>')
def submit_vote(post_id, rank):

    print(f"Submitted votoe {rank} for post {post_id}")
    user_id, username = session["current_user"]

    prize = {"1":"3", "2":"2", "3":"1"}[rank]

    with Database() as db:
            # does not return 
            post_changed_id = db.execute(SUBMIT_VOTE_QUERY,
    [user_id, post_id, prize, post_id, post_id])
    

                
    feedback = f"Vote #{rank} given to post {post_id} by {username}!"      
    if post_changed_id:
        feedback += f" (Reassigned from {post_changed_id})"

    print(feedback)

    return jsonify(feedback), STATUS_OK

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

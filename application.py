import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from jinja2 import Template
from decimal import *
import requests
import flask

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSON_SORT_KEYS'] = False
Session(app)

# Set up database
engine = create_engine(
    "postgres://qqbtleieqckxbs:63fffb4d3b0d624770287c35646381d2e56dc3e2aae838320cf8d001c25187d3@ec2-34-198-243-120.compute-1.amazonaws.com:5432/dp6aa4vgb1f8i")

db = scoped_session(sessionmaker(bind=engine))

globaluser = []


@app.route("/")
def index():
    return render_template("layout.html")


@app.route("/logout")
def logout():
    global globaluser
    globaluser = []
    return render_template("layout.html")


@app.route("/login", methods=["POST", "GET"])
def logIn():
    global globaluser
    if flask.request.method == 'GET':
        return render_template("inside.html", username=globaluser[1].capitalize())
    username = request.form.get("username")
    password = request.form.get("password")
    user = db.execute("SELECT password FROM users WHERE username = :username", {
                      "username": username}).fetchone()

    # check if user exists
    if user is None:
        return render_template("logInReturn.html", popup="Wrong username!")

    user = user[0]
    # check if password is correct
    if (user == password):
        globaluser = db.execute("SELECT * FROM users WHERE username = :username", {
            "username": username}).fetchone()
        return render_template("inside.html", username=globaluser[1].capitalize())
    else:
        return render_template("logInReturn.html", popup="Wrong password!")
    return render_template("logInReturn.html", popup="Something went wrong!")


@app.route("/search", methods=["POST"])
def search():
    global globaluser
    keyword = "%"+request.form.get("search")+"%"
    list = ["isbn", "title", "author"]
    for i in list:
        searchby = request.form.get(i)
        if searchby is not None:
            break
    if searchby == "isbn":
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :keyword", {
            "keyword": keyword})
    elif searchby == "title":
        books = db.execute("SELECT * FROM books WHERE title LIKE :keyword", {
            "keyword": keyword})
    elif searchby == "author":
        books = db.execute("SELECT * FROM books WHERE author LIKE :keyword", {
            "keyword": keyword})
    else:
        return render_template("error.html", type="404")
    return render_template("search.html", username=globaluser[1].capitalize(), books=enumerate(books, 1))


@app.route("/book", methods=['POST'])
def book():
    global globaluser
    bookId = request.form.get('bookId')
    book = db.execute("SELECT * FROM books WHERE id=:bookId",
                      {"bookId": bookId}).fetchone()
    review = db.execute("SELECT * FROM reviews WHERE bookid=:bookId",
                        {"bookId": bookId})
    # From goodread
    goodRead = requests.get("https://www.goodreads.com/book/review_counts.json",
                            params={"key": "B0cG0AVb0hO84rdwYDxuQ", "isbns": book[1]})
    goodRead = goodRead.json()
    grRatingCount = goodRead['books'][0]['work_ratings_count']
    grAverageRating = goodRead['books'][0]['average_rating']
    return render_template("book.html", book=book, review=review, username=globaluser[1].capitalize(), grRatingCount=grRatingCount, grAverageRating=grAverageRating)


@app.route("/reviewd", methods=['POST'])
def reviewed():
    global globaluser
    rating = int(request.form.get('rating'))
    review = request.form.get('review')
    bookid = request.form.get('bookid')
    # Get rating count
    totalcount = db.execute("SELECT count FROM books WHERE id=:bookId",
                            {"bookId": bookid}).fetchone()
    totalcount = totalcount[0]
    # Get rating
    totalrating = db.execute("SELECT rating FROM books WHERE id=:bookId",
                             {"bookId": bookid}).fetchone()
    totalrating = totalrating[0]

    # Check if the user has made a review before
    checkreview = db.execute("SELECT * FROM reviews WHERE username=:username AND bookid=:bookid", {
                             "username": globaluser[1],"bookid":bookid}).fetchone()
    
    # Made review before
    if checkreview is not None:
        #Update in review
        db.execute("UPDATE reviews SET rating=:rating,review=:review WHERE username=:username", {
                   "username": globaluser[1], "rating": rating, "review": review})

        #Update in book
        past_rating = checkreview[2]
        # Get new average rating
        totalrating = totalrating*totalcount-past_rating
        totalrating = (totalrating+rating)/(totalcount)
        db.execute("UPDATE books SET rating=:rating WHERE id=:bookId", {
                   "rating": totalrating, "bookId": bookid})
        # To return to page
        book = db.execute("SELECT * FROM books WHERE id=:bookId",
                          {"bookId": bookid}).fetchone()
        review = db.execute("SELECT * FROM reviews WHERE bookid=:bookId",
                            {"bookId": bookid})
        # From goodread
        goodRead = requests.get("https://www.goodreads.com/book/review_counts.json",
                                params={"key": "B0cG0AVb0hO84rdwYDxuQ", "isbns": book[1]})
        goodRead = goodRead.json()
        grRatingCount = goodRead['books'][0]['work_ratings_count']
        grAverageRating = goodRead['books'][0]['average_rating']
        return render_template("book.html", book=book, review=review, username=globaluser[1].capitalize(), grRatingCount=grRatingCount, grAverageRating=grAverageRating)

    else:
        db.execute("INSERT INTO reviews VALUES (:username,:bookid,:rating,:review)", {
            "username": globaluser[1], "bookid": bookid, "rating": rating, "review": review})
        # Update rating count
        db.execute("UPDATE books SET count=:count WHERE id=:bookId",
                   {"count": totalcount+1, "bookId": bookid})
        # Get new average rating
        totalrating = ((totalrating*totalcount)+rating)/(totalcount+1)
        db.execute("UPDATE books SET rating=:rating WHERE id=:bookId", {
                   "rating": totalrating, "bookId": bookid})

        db.commit()

        book = db.execute("SELECT * FROM books WHERE id=:bookId",
                          {"bookId": bookid}).fetchone()
        review = db.execute("SELECT * FROM reviews WHERE bookid=:bookId",
                            {"bookId": bookid})
        # From goodread
        goodRead = requests.get("https://www.goodreads.com/book/review_counts.json",
                                params={"key": "B0cG0AVb0hO84rdwYDxuQ", "isbns": book[1]})
        goodRead = goodRead.json()
        grRatingCount = goodRead['books'][0]['work_ratings_count']
        grAverageRating = goodRead['books'][0]['average_rating']
        return render_template("book.html", book=book, review=review, username=globaluser[1].capitalize(), grRatingCount=grRatingCount, grAverageRating=grAverageRating)


@app.route("/register", methods=["POST"])
def register():
    global globaluser
    username = request.form.get("rusername")
    password = request.form.get("rpassword")
    rpassword = request.form.get("rrpassword")
    # Check if username exists
    check = db.execute("SELECT username FROM users WHERE username=:username", {
                       "username": username}).fetchone()
    if check is not None:
        return render_template("logInReturn.html", popup="The username has been used! Change a username")
    # Check password
    if password == rpassword:
        db.execute("INSERT INTO users (username,password)VALUES (:username,:password)", {
                   "username": username, "password": password})
        db.commit()
        return render_template("logInReturn.html", popup="Register Succeeded!")
    return render_template("logInReturn.html", popup="Register Fail! Try Again!")


@app.route("/api/<string:isbn>")
def api(isbn):
    global globaluser
    check = db.execute("SELECT * FROM books WHERE isbn=:isbn",
                       {"isbn": isbn}).fetchone()
    if check is None:
        return render_template("error.html", type="404")
    return jsonify({
        "title": check[2],
        "author": check[3],
        "year": check[4],
        "isbn": check[1],
        "review_count": check[5],  # TBC
        "average_score": str(check[6])  # TBC
    })

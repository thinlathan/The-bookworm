import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(
    "postgres://qqbtleieqckxbs:63fffb4d3b0d624770287c35646381d2e56dc3e2aae838320cf8d001c25187d3@ec2-34-198-243-120.compute-1.amazonaws.com:5432/dp6aa4vgb1f8i")
db = scoped_session(sessionmaker(bind=engine))

def main():
    #db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY,username VARCHAR NOT NULL,password VARCHAR NOT NULL);")
    #db.commit()

#def side():
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY,isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year INTEGER NOT NULL);")
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn": isbn, "title": title, "author": author, "year": year})
    
    db.commit()
if __name__=="__main__":
    main()

import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(
    "postgres://qqbtleieqckxbs:63fffb4d3b0d624770287c35646381d2e56dc3e2aae838320cf8d001c25187d3@ec2-34-198-243-120.compute-1.amazonaws.com:5432/dp6aa4vgb1f8i")
db = scoped_session(sessionmaker(bind=engine))


def main():
    #db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY,username VARCHAR NOT NULL,password VARCHAR NOT NULL);")
    # db.commit()
    db.execute("CREATE TABLE reviews (username VARCHAR NOT NULL, bookid INTEGER NOT NULL,rating INTEGER NOT NULL,review VARCHAR NOT NULL);")
    # def side():
    #db.execute(
        #"ALTER TABLE books ADD rating DECIMAL(2,1) DEFAULT 0.0;")
    db.commit()


if __name__ == "__main__":
    main()

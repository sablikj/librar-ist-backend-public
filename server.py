from flask import Flask, request, url_for, flash, redirect
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_sqlalchemy import SQLAlchemy
from flask_jsonpify import jsonify
import sqlalchemy
from sqlalchemy import Text
from sqlalchemy import insert
import uuid
from datetime import datetime


db_connect = create_engine('sqlite:///libraist.db', echo=True, pool_size=10, max_overflow=20)
app = Flask(__name__)


def query_db(query, args=(), one=False):
    cur = db_connect().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/libs", methods = ['GET',"POST"])
def get_libs():
    conn = db_connect.connect() # connect to database
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            print(data)
            id = data['id']
            name = data['name']
            location = data['location']
            photo = data['photo']
            statement = sqlalchemy.text("INSERT INTO Library (id,name,location,photo) VALUES (:id,:name,:location,:photo)")
            conn.execute(statement,{"id":id,"name":name,"location":location,"photo":photo})
            conn.commit()
            return "successfully added"
        else:
            return "Unsupported content type", 400
    else:
        sqlText = sqlalchemy.sql.text("SELECT * FROM Library")
        query = conn.execute(sqlText) # This line performs query and returns json result
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]} # Fetches first column that is Library name
        return jsonify(result)
    
@app.route("/libs/metered", methods = ['GET'])
def get_libs_metered():
    conn = db_connect.connect() # connect to database
    if request.method == 'GET':
        sqlText = sqlalchemy.sql.text("SELECT Library.id, Library.name, Library.location FROM Library")
        query = conn.execute(sqlText) # This line performs query and returns json result
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]} # Fetches first column that is Library name
        return jsonify(result)
    
@app.route("/libs/edit", methods = ["PUT","PATCH"])
def edit_lib():
    conn = db_connect.connect() # connect to database
    args = request.args
    print(args)
    id = args.get("id", default="", type=str)
    if request.method == 'PUT':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            print(data)
            if(data['name'] is not None):
                name = data['name']
            else:
                name=""
            if(data['location'] is not None):
                location = data['location']
            else:
                location = ""
            if(data['photo'] is not None):
                photo = data['photo']
            else:
                location=""
            statement = sqlalchemy.text("UPDATE Library  SET name=:name,location=:location,photo=:photo WHERE id=%s" %str(id))
            conn.execute(statement,{"name":name,"location":location,"photo":photo})
            conn.commit()
            return "successfully updated"
        else:
            return "error"
    elif request.method == 'PATCH':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            print(data)
            if(data['name'] is not None):
                name = data['name']
            else:
                name=""
            if(data['location'] is not None):
                location = data['location']
            else:
                location = ""
            if(data['photo'] is not None):
                photo = data['photo']
            else:
                location=""
            statement = sqlalchemy.text("UPDATE Library  SET name=:name,location=:location,photo=:photo WHERE id=%s" %str(id))
            conn.execute(statement,{"name":name,"location":location,"photo":photo})
            conn.commit()
            return "successfully updated"
        else:
            return "error"
    else:
        return request.method

@app.route("/books", methods = ['GET','POST'])
def get_books():
    conn = db_connect.connect()
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            barcode=data['barcode']
            title = data['title']
            author = data['author']
            photo = data['photo']
            statement = sqlalchemy.text("INSERT INTO Book (barcode,title,author,photo) VALUES (:barcode,:title,:author,:photo)")
            conn.execute(statement,{"barcode":barcode,"title":title,"author":author,"photo":photo})
            conn.commit()
            return "successfully added"
        else:
            print("fail")
            return "fail"
    if request.method == 'GET':
        sqlText = sqlalchemy.sql.text("SELECT * FROM Book")
        query = conn.execute(sqlText)
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)
    

@app.route("/books/edit", methods = ["PUT"])
def edit_book():
    conn = db_connect.connect() # connect to database
    args = request.args
    barcode = args.get("barcode", default="", type=str)
    if request.method == 'PUT':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            title = data['title']
            author = data['author']
            photo = data['photo']
            statement = sqlalchemy.text("UPDATE Book  SET title=:title,author=:author,photo=:photo WHERE barcode=\"%s\"" %str(barcode))
            conn.execute(statement,{"title":title,"author":author,"photo":photo})
            conn.commit()
            return "successfully updated"
        else:
            return "error"

@app.route("/books_in_library/<library_id>", methods = ['GET'])
def get_books_in_libs(library_id):
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT Book.barcode, Book.title, Book.author, Book.photo, Book_lib.id  FROM Book_lib INNER JOIN Book ON Book.barcode=Book_lib.bookCode WHERE libraryId =\"%s\" "  %str(library_id))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/available_books_in_library/<library_id>", methods = ['GET'])
def get_available_books_in_libs(library_id):
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT Book.barcode, Book.title, Book.author, Book.photo, Book_lib.id FROM Book_lib INNER JOIN Book ON Book.barcode=Book_lib.bookCode LEFT JOIN Ratings ON Book.barcode=Ratings.barcode WHERE available=1 AND libraryId =\"%s\" GROUP BY Book.barcode ORDER BY AVG(Ratings.rating) DESC NULLS LAST "  %str(library_id))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/available_books_in_library_metered/<library_id>", methods = ['GET'])
def get_available_books_in_libs_metered(library_id):
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT Book.barcode, Book.title, Book.author, Book_lib.id FROM Book_lib INNER JOIN Book ON Book.barcode=Book_lib.bookCode LEFT JOIN Ratings ON Book.barcode=Ratings.barcode WHERE available=1 AND libraryId =\"%s\" GROUP BY Book.barcode ORDER BY AVG(Ratings.rating) DESC NULLS LAST"  %str(library_id))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_book_by_title", methods = ['GET'])
def get_book_by_title():
    args = request.args
    title = args.get("title", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT * FROM Book WHERE title =%s "  %str(title))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_book_by_barcode", methods = ['GET'])
def get_book_by_id():
    args = request.args
    barcode = args.get("barcode", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT * FROM Book WHERE barcode =%s "  %str(barcode))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_book_by_barcode_metered", methods = ['GET'])
def get_book_by_id_metered():
    args = request.args
    barcode = args.get("barcode", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT Book.barcode, Book.title, Book.author FROM Book WHERE barcode =%s "  %str(barcode))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_booklib_by_barcode", methods = ['GET'])
def get_booklib_by_barcode():
    args = request.args
    bookCode = args.get("barcode", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT * FROM Book_lib WHERE bookCode=%s "  %str(bookCode))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_library_by_name", methods = ['GET'])
def get_library_by_name():
    args = request.args
    name = args.get("name", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT * FROM Library WHERE name =%s "  %str(name))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_library_by_id", methods = ['GET'])
def get_library_by_id():
    args = request.args
    id = args.get("id", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT * FROM Library WHERE id =\"%s\" "  %str(id))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_libraries_by_book_title/", methods = ['GET'])
def get_libraries_by_book_title():
    args = request.args
    title = args.get("title", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT Book_lib.libraryId,Book_lib.bookCode, Book.title, Book_lib.available FROM Book_lib INNER JOIN Book ON Book.barcode=Book_lib.bookCode WHERE Book_lib.available=1 AND Book.title =%s "  %str(title))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_libraries_by_book_barcode/", methods = ['GET'])
def get_libraries_by_book_barcode():
    args = request.args
    barcode = args.get("barcode", default="", type=str)
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT Book_lib.libraryId,Book_lib.bookCode, Book_lib.available FROM Book_lib  WHERE bookCode =%s "  %str(barcode))
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)

@app.route("/get_book_lib/", methods = ['GET'])
def get_book_lib():
    conn = db_connect.connect()
    sqlText = sqlalchemy.sql.text("SELECT * FROM Book_lib")
    query = conn.execute(sqlText)
    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    return jsonify(result)
 
        
@app.route("/checkin/", methods = ['POST'])
def checkin():
    if request.method == 'POST':
        conn = db_connect.connect()
        available = 1
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            id=datetime.utcnow().strftime('%Y.%m.%d.%H.%M.%S.%f')
            libraryId=data['libraryId']
            bookCode = data['bookCode']
            statement = sqlalchemy.text("INSERT INTO Book_lib (id,libraryId,bookCode,available) VALUES (:id,:libraryId,:bookCode,:available)")
            conn.execute(statement,{"id":id,"libraryId":libraryId,"bookCode":bookCode,"available":available})
            conn.commit()
            return "successfully added"
        else: 
            return "error"
        
@app.route("/checkout", methods = ['PUT'])
def checkout():
    if request.method == 'PUT':
        args = request.args
        bookCode = args.get("barcode", default="", type=str)
        libraryId = args.get("libraryId", default="", type=str)
        id=args.get("id", default="", type=str)
        print(bookCode + " "+ libraryId+" "+id)
        conn = db_connect.connect()
        statement = sqlalchemy.text("UPDATE Book_lib  SET available=0  WHERE bookCode=\"%s\" and libraryId=\"%s\" and id =\"%s\"" %(bookCode,libraryId,id))
        conn.execute(statement)
        conn.commit()
        return "successfully updated"
    else:
            return "error"

@app.route("/search", methods = ['GET'])
def search():
    if request.method == 'GET':
        args = request.args
        print(args)
        search = args.get("search")
        search = search.replace('"','')
        search= str(search + "%")
        limit = args.get("limit", default=0, type=int)
        offset = args.get("offset", default=0, type=int)
        conn = db_connect.connect()
        sqlText = sqlalchemy.sql.text("SELECT * FROM Book LEFT JOIN Ratings ON  Book.barcode=Ratings.barcode WHERE Book.title LIKE :search GROUP BY Book.barcode ORDER BY AVG(Ratings.rating) DESC NULLS LAST LIMIT :limit OFFSET :offset")
        query = conn.execute(sqlText, {"search": search, "limit": limit, "offset": offset})
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)
    else:
        return "request is not a GET method"   

@app.route("/search_metered", methods = ['GET'])
def search_metered():
    if request.method == 'GET':
        args = request.args
        print(args)
        search = args.get("search")
        search = search.replace('"','')
        search= str(search + "%")
        limit = args.get("limit", default=0, type=int)
        offset = args.get("offset", default=0, type=int)
        conn = db_connect.connect()
        sqlText = sqlalchemy.sql.text("SELECT Book.barcode, Book.title, Book.author FROM Book LEFT JOIN Ratings ON  Book.barcode=Ratings.barcode WHERE Book.title LIKE :search GROUP BY Book.barcode ORDER BY AVG(Ratings.rating) DESC NULLS LAST LIMIT :limit OFFSET :offset")
        query = conn.execute(sqlText, {"search": search, "limit": limit, "offset": offset})
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)
    else:
        return "request is not a GET method"   


@app.route("/ratings", methods = ['GET','POST'])
def get_ratings():
    conn = db_connect.connect()
    if request.method == 'GET':
        sqlText = sqlalchemy.sql.text("SELECT * FROM Ratings")
        query = conn.execute(sqlText) 
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]} 
        return jsonify(result)
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            id=data['id']
            rating=data['rating']
            barcode = data['barcode']
            statement = sqlalchemy.text("INSERT INTO Ratings (id,barcode,rating) VALUES (:id,:barcode,:rating)")
            conn.execute(statement,{"id":id,"barcode":barcode,"rating":rating})
            conn.commit()
            return "successfully added"
        else: 
            return "error"
        
@app.route("/update_ratings", methods = ['POST'])
def update_ratings():
    conn = db_connect.connect()
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        print(content_type)
        if ('application/json' in content_type):
            data = request.get_json()
            id=data['id']
            rating=data['rating']
            barcode = data['barcode']
            statement = sqlalchemy.text("UPDATE Ratings SET rating=:rating WHERE id=:id AND barcode=:barcode")
            conn.execute(statement,{"id":id,"barcode":barcode,"rating":rating})
            conn.commit()
            return "successfully added"
    
@app.route("/ratings_by_barcode", methods = ['GET'])
def get_ratings_by_barcode():
    conn = db_connect.connect()
    if request.method == 'GET':
        args = request.args
        print(args)
        barcode = args.get("barcode")
        sqlText = sqlalchemy.sql.text("SELECT * FROM Ratings WHERE barcode=:barcode")
        query = conn.execute(sqlText,{"barcode":barcode}) 
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]} 
        return jsonify(result)
    
@app.route("/ratings_by_barcode_sum", methods = ['GET'])
def get_ratings_by_barcode_sum():
    conn = db_connect.connect()
    if request.method == 'GET':
        args = request.args
        print(args)
        barcode = args.get("barcode")
        sqlText = sqlalchemy.sql.text("SELECT AVG(Ratings.rating) FROM Ratings WHERE barcode=:barcode")
        query = conn.execute(sqlText,{"barcode":barcode}) 
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]} 
        return jsonify(result)
# API for LibrarIST android app
## Prerequisite to run the api locally
### Install libraries

`pip install flask-restful`

`pip install SQLAlchemy Flask-SQLAlchemy`

`pip install virtualenv`

`pip install flask flask-jsonpify flask-sqlalchemy`

### Create virtual environment

`virtualenv venv`

`source venv/bin/activate`

`pip freeze`

### Connect to db
#I am using SQLlite, you can download easy db editor/viewer from https://sqlitebrowser.org/

`sqlite3 libraist.db`

###  Run
`flask --app server run`

#### to start the server on the background

`FLASK_APP=server.py nohup flask run --host=0.0.0.0 > log.txt 2>&1`

## End points

### GET requests
#### Get all books
http://100.68.28.175:5000 **/books** -- to get all books

http://100.68.28.175:5000 **/books/metered** - to get all books for metered connection

#### Get all libraries
http://100.68.28.175:5000 **/libs**  - to get all libraries

http://100.68.28.175:5000 **/libs/metered**  - get libraries for metered connection

#### Get all books in library
http://100.68.28.175:5000 **/books_in_library/<library_id>** - get all books in library

#### Get available books in library
http://100.68.28.175:5000 **/available_books_in_library/<library_id>** - get available books in library

#### Get libraries by book title / barcode
http://100.68.28.175:5000 **/get_libraries_by_book_title** ? title = %22 name %20 name %22

http://100.68.28.175:5000 **/get_libraries_by_book_barcode** ? barcode = %22 barcode %22

#### Get library's attributes by name
http://100.68.28.175:5000 **/get_library_by_name** ? name = %22 name %20 name %22.  // %20 - space;  %22 - quotes symbol

#### Get book's attributes by barcode 
http://100.68.28.175:5000 **/get_book_by_barcode** ? barcode = %22 barcode %22

http://100.68.28.175:5000 **/get_book_by_title** ? title = %22 name %20 name %22

#### Get search result for Book title

http://100.68.28.175:5000 **/search** ? search = "what" & offset = 2 & limit = 2



Examples:

      http://127.0.0.1:5000/get_library_by_name?name=%22Sao%20Sebastao%22

      http://127.0.0.1:5000/get_book_by_title?title=%22Flask101%22

      http://100.68.28.175:5000/get_libraries_by_book_barcode/?barcode=%221000%22   

      http://100.68.28.175:5000/get_libraries_by_book_barcode/?barcode=%221000%22

### POST requests

can be made to localhost on https://reqbin.com/

#### Add New Book
Example: for 
http://127.0.0.1:5000 **/books**

      {
        "barcode":" id "
        "title": "Narnia- the Lion the witch and the wardrobe",
        "author": "C.S.Lewis",
        "photo": "string",
        }
        //Note: barcode is a uuid generated string, so there is no need to include it

#### Add New Library
 http://100.68.28.175:5000 **/libs**
 
    {
     "id":"id"
     "name": "string",
     "location":"string",
     "photo":"string",
     }
     //Note: id is a uuid generated string, so there is no need to include it

#### Edit Library
http://100.68.28.175:5000. **/libs/edit** ? id= %22 <library_id> %22

Example:

      http://127.0.0.1:5000/libs/edit?id="1"
      {
      "name":"Alameda",
      "location":"37.765206;-122.241636",
      "photo":""
      }
#### Check in a book - donate a book to a library 
POST request

http://100.68.28.175:5000 **/checkin/**  - update book availability to 1

Example for check out:

    {
    "id":"id",
    "bookCode": "1000",
    "libraryId":""
    }
    
#### Check out a book - take a book from library
PUT request
http://100.68.28.175:5000 **/checkout? barcode= & libraryId= & id= **  - update book availability to 0   

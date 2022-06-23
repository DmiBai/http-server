from server import Server
from urllib.parse import parse_qs
import hashlib
import sys
import time
import sqlalchemy
import os
import bcrypt
import requests
#я пробую написать на русском
engine = sqlalchemy.create_engine("mysql+pymysql://root:@localhost/node_db")
engine.connect()
session = requests.Session()

auth = False
authname = 'anonimous'

if  sys.version_info<(3, 6):
  import sha3

app = Server()

# selecttest=engine.execute('SELECT password FROM course_work WHERE nickname="123"')
# passfromsql = (selecttest.first()[0])
# valid = bcrypt.checkpw('123'.encode(), passfromsql)
# print(valid)

@app.route("/reg", methods =["GET","POST"])
def reg(request, response):
  if request.method == "GET":
    response.body = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>registration</title>
    </head>
    <body>
      <form method="POST">
          Имя
          <input type="text" name="first_name"><br>
          Фамилия:
          <input type="text" name="last_name"><br>
          Логин
          <input type="text" name="nickname"><br>
          Пароль
          <input type="password" name="password"><br>
          <input type="submit">
      </form>
    </body>
    </html>"""
  elif request.method == "POST":
    first_name = parse_qs(request.body)["first_name"][0]
    last_name = parse_qs(request.body)["last_name"][0]
    nickname = parse_qs(request.body)["nickname"][0]
    sqlselect = engine.execute('SELECT password FROM course_work WHERE nickname="'+nickname+'"')
    passfromsql = (sqlselect.first())
    if passfromsql != None:
      response.body = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Регистрация</title>
    </head>
    <body>
      <form method="POST">
          Имя:
          <input type="text" name="first_name"><br>
          Фамилия:
          <input type="text" name="last_name"><br>
          Логин:
          <input type="text" name="nickname"><br>
          Пароль:
          <input type="password" name="password"><br>
          <input type="submit">
      </form>
      ПОЛЬЗОВАТЕЛЬ С ТАКИМ ИМЕНЕМ УЖЕ СУЩЕСТВУЕТ
    </body>
    </html>"""
    else:
      password = parse_qs(request.body)["password"][0]
      hashAndSalt = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
      hshpass = str(hashAndSalt)
      hshpass = hshpass.rpartition("'")[0]
      hshpass = hshpass.partition("'")[2]
      sqlreq = "INSERT INTO course_work (first_name, last_name, nickname, password) VALUES ('" 
      sqlreq += first_name 
      sqlreq += "', '"  
      sqlreq += last_name  
      sqlreq += "', '"  
      sqlreq += nickname  
      sqlreq += "', '" 
      sqlreq += hshpass  
      sqlreq += "')"
      print(sqlreq)
      engine.execute(sqlreq)
      response.body = f"""<!DOCTYPE html>
      <html lang="ru">
      <head>
        <meta charset="UTF-8">
        <title>nice</title>
      <head>
      <body>
        <p>Регистрация прошла успешно!</p>
        <a href="/reg">Регистрация</a><br> 
        <a href="/auth">Авторизация</a><br> 
        <a href="/wall">Стена</a><br> 
        <a href="/sha">Хеширование</a> <br> 
        <a href="/">На главную</a> <br> 
      </body>
      </html>"""
    

@app.route("/auth", methods=["GET", "POST"])
def auth(request, response):
    if request.method == 'GET':
        response.body = f"""<!DOCTYPE html>
  <html lang="ru">
  <head>
    <meta charset="UTF-8">
    <title>Вход</title>
  </head>
  <body>
  <form method="post">
      Логин:
      <input type="text" name="nickname"><br>
      Пароль:
      <input type="password" name="password"><br>
      <input type="submit">
  </form>
  </body>
  </html>"""
    elif request.method == 'POST':
      nickname = parse_qs(request.body)["nickname"][0]
      password = parse_qs(request.body)["password"][0]
      sqlselect = engine.execute('SELECT password FROM course_work WHERE nickname="' + nickname + '"')
      passfromsql = (sqlselect.first()[0])
      print(passfromsql)
      valid = bcrypt.checkpw(password.encode(), passfromsql)
      print(valid)
      if valid == True:
        auth = True
        usern = "'username="+nickname+"'"
        response.body = f"""<!DOCTYPE HTML>
        <html lang="ru">
        <head>
          <meta charset="UTF-8">
          <title>Вход</title>
          
        </head>
        <body>
            Добро пожаловать, {nickname}!
            <a href="/reg">Регистрация</a><br> 
            <a href="/auth">Авторизация</a><br> 
            <a href="/wall">Стена</a><br> 
            <a href="/sha">Хеширование</a> <br> 
            <a href="/">На главную</a> <br> 
            <script> alert("HI");</script>
        </body>
        </html>"""
      else:
        response.body = f"""<!DOCTYPE html>
        <html lang="ru">
        <head>
          <meta charset="UTF-8">
          <title>Вход</title>
        </head>
        <body>
        <form method="post">
            Имя пользователя:
            <input type="text" name="nickname"><br>
            Пароль:
            <input type="password" name="password"><br>
            <input type="submit">
        </form>
        НЕВЕРНЫЕ ЛОГИН ИЛИ ПАРОЛЬ. ПОПРОБУЙТЕ СНОВА
        </body>
        </html>"""
      

@app.route("/wall", methods =["GET","POST"])
def wall(request, response):
  str_data = ''
  if request.method == "GET":
    posts = engine.execute('SELECT * FROM cw_posts')
    for row in posts:
      str_data += row[1] + '<br><hr><br>'
    response.body = f"""<!DOCTYPE html>
            <html lang="ru">
        <head>
          <meta charset="UTF-8">
            <title>Стена</title>
          </head>
          <body>
          <br>
            <form method="POST">
              <input type="text" name="upost">
              <input type="submit">
            </form><br><hr><br>
            {str_data}
          </body>
          </html>
          """
  elif request.method == "POST":
    reqpost = parse_qs(request.body)["upost"][0]
    trig = 0
    engine.execute('INSERT INTO cw_posts (post) VALUE ("' +reqpost+ '")')
    posts = engine.execute('SELECT * FROM cw_posts')
    for row in posts:
      str_data += row[1] + '<br><hr><br>'
    response.body = f"""<!DOCTYPE html>
            <html lang="ru">
        <head>
          <meta charset="UTF-8">
            <title>Стена</title>
          </head>
          <body><br>
            <form method="POST">
              <input type="text" name="upost">
              <input type="submit">
            </form><br>
            {str_data}
          </body>
          </html>
          """


@app.route("/", methods = ["GET", "POST"])
def index(request, response):
    response.body = f"""<!DOCTYPE html>
  <html lang="ru">
        <head>
          <meta charset="UTF-8">
    <title>greeter</title>
  </head>
  <body>
    ДОБРО ПОЖАЛОВАТЬ!<br>
    <a href="/reg">Регистрация</a><br> 
    <a href="/auth">Авторизация</a><br> 
    <a href="/wall">Стена</a><br> 
    <a href="/sha">Хеширование</a> <br> 
    <a href="/">На главную</a> <br>  
  </body>
  </html>
  """

@app.route("/sha", methods=["GET", "POST"])
def sha(request, response):
    if request.method == 'GET':
        response.body = f"""<!DOCTYPE html>
  <html lang="ru">
        <head>
          <meta charset="UTF-8">
    <title>send</title>
  </head>
  <body>
  <form method="post" >
      <input type="text" size="40" name="data">
      <input type="submit">
  </form>
  </form>
  </body>
  </html>"""
    elif request.method == 'POST':
        data = parse_qs(request.body)["data"][0]
        encoded_data = data.encode()
        obj_sha3_224 = hashlib.sha3_224(encoded_data)
        obj_sha3_256 = hashlib.sha3_256(encoded_data)
        obj_sha3_384 = hashlib.sha3_384(encoded_data)
        obj_sha3_512 = hashlib.sha3_512(encoded_data)
        obj_sha1 = hashlib.sha1(encoded_data)
        obj_sha224 = hashlib.sha224(encoded_data)
        obj_sha256 = hashlib.sha256(encoded_data)
        obj_sha384 = hashlib.sha384(encoded_data)
        obj_sha512 = hashlib.sha512(encoded_data)
        sha3_256_data = obj_sha3_256.hexdigest()
        sha3_224_data = obj_sha3_224.hexdigest()
        sha3_384_data = obj_sha3_384.hexdigest()
        sha3_512_data = obj_sha3_512.hexdigest()
        sha256_data = obj_sha256.hexdigest()
        sha224_data = obj_sha224.hexdigest()
        sha384_data = obj_sha384.hexdigest()
        sha512_data = obj_sha512.hexdigest()
        sha1_data = obj_sha1.hexdigest()
        time.sleep(10)
        response.body = f"""<!DOCTYPE html>
  <html lang="ru">
        <head>
          <meta charset="UTF-8">
    <title>Хеширование</title>
  </head>
  <body>
  <p style="background-color: rgba(255, 255, 128, .5);"> Введенная строка<br>
  {data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA3-224<br>
  {sha3_224_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA3-256<br>
  {sha3_256_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA3-384<br>
  {sha3_384_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA3-512<br>
  {sha3_512_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA1<br>
  {sha1_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA224<br>
  {sha224_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA256<br>
  {sha256_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA384<br>
  {sha384_data} </p>
  <p style="background-color: hsla(100, 1%, 65%, .75);"> SHA512<br>
  {sha512_data} </p>
  <a href="/reg">Регистрация</a><br> 
  <a href="/auth">Авторизация</a><br> 
  <a href="/wall">Стена</a><br> 
  <a href="/sha">Хеширование</a> <br> 
  <a href="/">На главную</a> <br> 
  </body>
  </html>
  """


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=3000)

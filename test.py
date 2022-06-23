import os
import bcrypt

password = 'lookhere123'
hashAndSalt = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashAndSalt)
pas = str(hashAndSalt).rpartition("'")[0]
pas = pas.partition("'")[2]
print(pas)
secpas = "b'" + pas + "'"
pas = secpas
print(pas)
valid = bcrypt.checkpw(pas.encode(), hashAndSalt)
print(valid)
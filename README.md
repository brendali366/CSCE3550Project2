CSCE 3550 Sect 002
Brenda Li
JWKS Server Project 2

Project 2 runs the same as project 1. With the addition to SQLite.

Libraries used to run:
-flask
-jwt
-datetime
-cryptography
-base64
-json
-SQLite3


How I installed it:
'pip3 install _____ '

** Note: In case getting error for base64, uninstall and install PyJwt. (This worked for me after getting the error, I was able to get ride of the error by uninstalling and reinstalling it).

-> Created a fileName for short for databases 'totally_not_my_privateKeys.db'.  While the tutorials mainly put the database name right into connect (as in -> "sqlite3.connect('totally_not_my_privateKeys.db')" ) I wanted to make it easy in the case I need to connect to the Database in my functions.

-> Created a creating table for the database and define table schema in global. I tried calling to a function that creates the table, but it did not work for me and putting it in global was the only way I could get the table created.

-> Created a function of add_key that adds private keys and their expiry as parameters.  I tried numerous spots to add the private keys but mainly get errors, for example, globally. 

-> Created a function that retrieves a single non-expired key when there is an expired key.

-> Created a function that retrieves all non-expired keys.

-> In my test.py, I added a check to see if the database exists. 

-> Ran Gradebot and shows 55/65 for grade. 

-> Coverage unknowingly shows 0 even though it is running successfully as shown on Gradebot.  


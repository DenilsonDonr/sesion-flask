#importaciones
from flask import Flask, render_template, request
import config
import pymysql
#app archivo principal de la aplicación
#instancia de Flask

app = Flask(__name__)

#configuracion de la base de datos
app.config['SECRET_KEY'] = config.HEX_SEC_KEY
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

#función para conectarnos a la base de datos
def conectar_db():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
    )

#ruta principal y metodo
@app.route('/', methods=['GET'])
def home():
    #render_template, necesario para renderizar un .html
    return render_template('index.html')

#Ruta para realizar el proceso de login
@app.route('/login', methods=['POST'])
def login():
    #recibir email y password
    email = request.form['email']
    password = request.form['password']

if __name__ == '__main__':
    app.run(debug=True)
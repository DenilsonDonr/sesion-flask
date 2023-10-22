#importaciones
from flask import Flask, render_template, request, session, redirect, url_for
from validate_email_address import validate_email
from datetime import datetime
import config
import pymysql
import bcrypt
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
    # Recibir email y password
    email = request.form['email']
    password = request.form['password']

    # Conectar a la DB
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email))
    user = cursor.fetchone()
    db.close()

    if user is not None:
        stored_password = user[4]  
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            session['email'] = email
            session['name'] = user[1]
            session['surnames'] = user[2]
            return redirect(url_for('tasks'))
    
    return render_template('index.html', message="Las credenciales no son correctas")

@app.route('/registroAction', methods=['POST'])
def registro_post():
    # Recibir nombre, apellido, email y password
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    password = request.form['password']

    # Conectar a la DB
    db = conectar_db()
    cursor = db.cursor()

    # Iniciar mensajes de errores
    errores = []

    # Verificar campos obligatorios
    if not nombre or not apellido or not email or not password:
        errores.append("Todos los campos son obligatorios")

    # Verificar si el nombre contiene números
    if any(char.isdigit() for char in nombre):
        errores.append("El campo 'Nombre' no debe contener números")
    #Verificar si el apellido contiene números
    if any(char.isdigit() for char in apellido):
        errores.append("El campo 'Apellido' no debe contener números")
    # Verificar el email
    if not validate_email(email):
        errores.append("El email no es válido")
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email))
        email_cursor = cursor.fetchone()
        if email_cursor is not None:
            errores.append("El email ya está en uso")
    except Exception as e:
        return render_template('registro.html', message="Error al registrar el email")
    # Unir los elementos de la lista de errores en una sola cadena
    errores_str = ", ".join(errores)

    if errores:
        return render_template('registro.html', message=errores_str)
    
    #Uso de bcrypt para las contraseñas y guardarlas incriptadas
    pwd = password.encode('utf-8')
    #generacion de la "sal"
    sal = bcrypt.gensalt()
    #Incriptamos la contraseña
    encript = bcrypt.hashpw(pwd, sal)
    try:
        # Ejecutar una sentencia insertando los datos
        cursor.execute("INSERT INTO users (name, surnames, email, password) VALUES (%s, %s, %s, %s)",
                       (nombre, apellido, email, encript))
        # Commit para confirmar que el envío de datos se realice y se guarde permanentemente
        db.commit()
        db.close()
        return render_template('index.html', razon=f"Se registró correctamente al usuario {nombre}")
    except Exception as e:
        # En caso de error, se realizará un rollback
        db.rollback()
        db.close()
        return render_template('registro.html', message=e)

#Ruta de creación de tarea
@app.route('/nueva-task', methods=['POST'])
def nuevaTarea():
    #Tomar los valores del formulario para una nueva tarea, también el email
    title = request.form['title']
    descripcion = request.form['description']
    email = session['email']
    #Creamos una variable para verificar la hora en que se agregó la tarea
    d = datetime.now()
    dateTasks = d.strftime("%Y-%m-%d $H:%M:%S")

    #verificamos si hay datos 
    if title and descripcion and email:
        #Conetamos a la DB
        db = conectar_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO tasks (email, title, description, date_task) VALUES(%s, %s, %s, %s)",
                           (email, title, descripcion, dateTasks))
            db.commit()
            db.close()
            return redirect(url_for('tasks'))
        except Exception as e:
            db.rollback()
            db.close()
            return redirect(url_for('tasks'))
#Ruta de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/registro', methods=['GET'])
def registro():
    return render_template('registro.html')

#Ruta de taks
@app.route('/tasks', methods=['GET'])
def tasks():
    #obtemos los datos , para recargar la pagina y mostrar las tareas agregar por el usuario
    email = session['email']
    
    #Conexion a DB
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE email = %s", (email))
    #Recibimos todas las task en la varaiable tasks
    tasks = cursor.fetchall()
    #creamos un diccionario
    objeto = []
    columnaNames = [column[0] for column in cursor.description]

    for record in tasks:
        objeto.append(dict(zip(columnaNames, record)))
    cursor.close()

    return render_template('tasks.html', tasks = objeto)

if __name__ == '__main__':
    app.run(debug=True)
#importaciones
from flask import Flask, render_template

#app archivo principal de la aplicación
#instancia de Flask

app = Flask(__name__)

#ruta principal y metodo
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
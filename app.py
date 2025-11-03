from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/apps')
def apps():
    return render_template('apps.html')

@app.route('/encuesta')
def encuesta():
    return render_template('encuesta.html')

@app.route('/conclusiones')
def conclusiones():
    return render_template('conclusiones.html')

if __name__ == '__main__':
    app.run(debug=True)
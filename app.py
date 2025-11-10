from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

app.config["SECRET_KEY"] = "una_clave_secreta_muy_larga_y_dificil_de_adivinar"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/sesion')
def sesion():
    return render_template('sesion.html')

@app.route('/apps')
def apps():
    return render_template('apps.html')

@app.route('/informacion')
def informacion():
    return render_template('informacion.html')

@app.route('/conclusiones')
def conclusiones():
    return render_template('conclusiones.html')

@app.route('/abo')
def nosotros():
    return render_template('acercaDe.html')

@app.route('/dat')
def datos():
    return render_template('usoDatos.html')


@app.route("/registrame", methods=["GET", "POST"])
def registrame():
    error = None
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        dia = request.form["dia"]
        mes = request.form["mes"]
        anio = request.form["anio"]
        actividad = request.form["actividad"]
        genero = request.form["genero"]
        email = request.form["email"]
        contrasena = request.form["contrasena"]
        confirmar_contrasena = request.form["confirmar_contrasena"]
        
        if len(nombre) < 3:
            flash("El nombre debe tener al menos 3 caracteres.")
            return render_template("registro.html", nombre=nombre)
        
        if len(apellidos) < 3:
            flash("No puede haber menos de 3 caracteres en los apellidos.")
            return render_template("registro.html", apellidos=apellidos) 
        
        if contrasena != confirmar_contrasena:
            error = "La contraseña no coincide."
            
        if error != None:
            flash(error)
            return render_template("registro.html")
        else:
            flash(f"¡Registro exitoso para el usuario: ¡{nombre}!")
            return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        contrasena = request.form["contrasena"]
        confirmar_contrasena = request.form["confirmar_contrasena"]
        
        if contrasena != confirmar_contrasena:
            error = "La contraseña no coincide."
            
        if error != None:
            flash(error)
            return render_template("sesion.html")
        else:
            session["email"] = email
            flash(f"¡Registro exitoso para el usuario: ¡{email}!")
            return redirect(url_for("index"))
    return render_template("sesion.html")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear()  
    return redirect(url_for("login"))

@app.route("/cue", methods=["GET"])
def cuenta():
    return render_template("cuentaUsuario.html")

if __name__ == '__main__':
    app.run(debug=True)
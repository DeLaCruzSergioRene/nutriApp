from flask import Flask, render_template, request, redirect, url_for, session, flash 
import requests

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
#  app.config['MYSQL_DB'] = 'prueba'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# mysql = MySQL(app)


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

@app.route('/informacion')
def informacion():
    return render_template('informacion.html')

@app.route('/basal')
def calculadora_basal():
    return render_template('calculadora_basal.html')

@app.route('/tmb', methods=["GET", "POST"])
def calcular_tmb():
    resultado = None
    if request.method == "POST":
        genero = request.form["genero"]
        peso = float(request.form["peso"])
        altura = float(request.form["altura"])
        edad = int(request.form["edad"])
        if genero == "hombre":
            resultado = 10 * peso + 6.25 * altura - 5 * edad + 5
        else:
            resultado = 10 * peso + 6.25 * altura - 5 * edad - 161
        resultado = round(resultado, 2)
    return render_template("calculadora_basal.html", resultado=resultado)

@app.route('/gasto')
def calculadora_gasto():
    return render_template('calculadora_gasto.html')

@app.route('/gct', methods=["GET", "POST"])
def calculadora_gct():
    resultado = None
    if request.method == "POST":
        tmb = float(request.form["tmb"])
        factor = float(request.form["factor"])
        resultado = round(tmb * factor, 2)
    return render_template("calculadora_gasto.html", resultado=resultado)

@app.route('/ideal')
def calculadora_ideal():
    return render_template('calculadora_ideal.html')

@app.route('/idea', methods=["GET", "POST"])
def calculadora_idea():
    resultado = None
    if request.method == "POST":
        genero = request.form["genero"]
        altura = float(request.form["altura"])
        if genero == "hombre":
            resultado = 50 + 0.91 * (altura - 152)
        else:
            resultado = 45.5 + 0.91 * (altura - 152)
        resultado = round(resultado, 2)
    return render_template("calculadora_ideal.html", resultado=resultado)

@app.route('/masa')
def calculadora_imc():
    return render_template('calculadora_imc.html')

@app.route('/macro', methods=["GET"])
def calculadora_macro():
    return render_template('calculadora_macro.html')

@app.route('/calcular_macro', methods=["POST"])
def calcular_macro():
    alimento = request.form["alimento"]
    grasas = float(request.form["grasas"])
    proteinas = float(request.form["proteinas"])
    carbohidratos = float(request.form["carbohidratos"])

    calorias_totales = (grasas * 9) + (proteinas * 4) + (carbohidratos * 4)
    resultado = {
        "alimento": alimento,
        "grasas": grasas,
        "proteinas": proteinas,
        "carbohidratos": carbohidratos,
        "calorias_totales": round(calorias_totales, 2)
    }
    
    return render_template("calculadora_macro.html", resultado=resultado)

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

@app.route("/imc_calcular", methods=["POST"])
def imc_calcular():
    resultado = None
    peso = float(request.form["peso"])
    estatura = float(request.form["estatura"])
    if request.method == "POST":
        resultado = peso / estatura
        resultado = (resultado)
        return render_template("calculadora_imc.html", resultado=resultado)


if __name__ == '__main__':
    app.run(debug=True)

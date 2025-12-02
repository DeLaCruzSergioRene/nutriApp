from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from werkzeug.security import generate_password_hash
from flaskext.mysql import MySQL
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'prueba'

app.config["SECRET_KEY"] = "una_clave_secreta_muy_larga_y_dificil_de_adivinar"

mysql = MySQL(app)

USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "rfTd35c18oR2TY0uJOMRZpk6kPH9TsHy8Id90E3k" 

def necesita_sesion():
    return "email" not in session 

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

@app.route('/masa')
def calculadora_imc():
    return render_template('calculadora_imc.html')

@app.route('/masa/calcular', methods=["GET", "POST"])
def calcular_imc():
    resultado = None
    if request.method == "POST":
        peso = float(request.form["peso"])
        estatura = float(request.form["estatura"]) 
        # Pasar a metros
        estatura_m = estatura / 100
        # IMC = peso / (estatura_m * estatura_m)
        resultado = round(peso / (estatura_m * estatura_m), 2)
    return render_template("calculadora_imc.html", resultado=resultado)

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

@app.route('/macro')
def calculadora_macro():
    if "email" not in session:
        return redirect(url_for("sesion"))
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

@app.route("/registrame", methods=["POST"])
def registrame():
    nombre = request.form["nombre"]
    apellidos = request.form["apellidos"]
    dia = int(request.form["dia"])
    mes = int(request.form["mes"])
    anio = int(request.form["anio"])
    genero = request.form["genero"]
    email = request.form["email"]
    contrasena = request.form["contrasena"]
    confirmar = request.form["confirmar_contrasena"]

    if contrasena != confirmar:
        flash("La contraseña no coincide")
        return render_template("registro.html")
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nombre, apellidos, dia, mes, anio, genero, correo, contrasenia) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (nombre,apellidos,dia,mes,anio,genero,email,contrasena))
    cursor.connection.commit()
    flash("Registro exitoso!")
    return redirect(url_for("sesion"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    contrasena = request.form["contrasena"]

    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * FROM usuario WHERE correo=%s AND contrasenia=%s",(email,contrasena))
    user = cursor.fetchone()
    if user:
        session["email"] = email
        flash("Sesión iniciada")
        return redirect(url_for("index"))
    else:
        flash("Usuario o contraseña incorrecta")
        return render_template("sesion.html")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear() 
    return redirect(url_for("sesion"))

@app.route("/cue", methods=["GET"])
def cuenta():
    return render_template("cuentaUsuario.html")

@app.route("/search", methods=["GET", "POST"])
def search_food_route():
    if "email" not in session:
        return redirect(url_for("sesion"))
    
    if request.method == "GET":
        return render_template("buscar.html")

    query = request.form.get("food_name", "").strip()
    
    if not query:
        flash("Por favor ingresa un alimento para buscar.")
        return render_template("buscar.html")
    
    try:
        params = {
            "api_key": USDA_API_KEY,
            "query": query,
            "pageSize": 3  
        }

        response = requests.get(USDA_API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            foods = data.get("foods", [])
            
            if not foods:
                flash(f"No se encontraron resultados para '{query}'.", "error")
                return render_template("buscar.html")

            results = []
            for f in foods:
                nutrients = {n["nutrientName"]: n.get("value") for n in f.get("foodNutrients", [])}
                
                results.append({
                    "description": f.get("description", "Sin descripción"),
                    "brand": f.get("brandName", "N/A"),
                    "calories": nutrients.get("Energy", "N/A"),
                    "protein": nutrients.get("Protein", "N/A"),
                    "carbs": nutrients.get("Carbohydrate, by difference", "N/A"),
                    "fat": nutrients.get("Total lipid (fat)", "N/A")
                })
            
            return render_template("buscar_re.html", query=query, foods=results)
        else:
            flash(f"Error en la búsqueda: {response.status_code}", "error")
            return render_template("buscar.html")

    except requests.exceptions.RequestException as e:
        flash(f"Error al conectarse con la API: {e}", "error")
        return render_template("buscar.html")

if __name__ == '__main__':
    app.run(debug=True)
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
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.config["SECRET_KEY"] = "una_clave_secreta_muy_larga_y_dificil_de_adivinar"

mysql = MySQL(app)

USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "rfTd35c18oR2TY0uJOMRZpk6kPH9TsHy8Id90E3k" 

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
        estatura = float(request.form["estatura"])  # en cm
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
        objetivo = request.form["objetivo"]
        dieta = request.form["dieta"]
        alergias = request.form["alergias"]
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
    
@app.route("/search")
def search():
    return render_template("buscar.html")

@app.route("/search", methods=["POST"])
def search_food():
    query = request.form.get("food_name", "").strip()
    
    if not query:
        flash("Por favor ingresa un alimento para buscar.")
        return redirect(url_for("index"))
    
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
                return redirect(url_for("index"))

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
            return redirect(url_for("index"))

    except requests.exceptions.RequestException as e:
        flash(f"Error al conectarse con la API: {e}", "error")
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from werkzeug.security import generate_password_hash
from flaskext.mysql import MySQL
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Izakaya'

app.config["SECRET_KEY"] = "una_clave_secreta_muy_larga_y_dificil_de_adivinar"

mysql = MySQL(app)

USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "rfTd35c18oR2TY0uJOMRZpk6kPH9TsHy8Id90E3k" 


def crear_tabla_users():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                user_ID int(11) NOT NULL AUTO_INCREMENT,
                nombre varchar(50) NOT NULL,
                apellidos varchar(50) NOT NULL,
                dia tinyint(4) NOT NULL,
                mes tinyint(4) NOT NULL,
                anio int(11) NOT NULL,
                genero enum('H','M','O','P') NOT NULL,
                correo varchar(50) NOT NULL,
                contrasenia varchar(50) NOT NULL,
                PRIMARY KEY (`user_ID`)
            )
        ''')
        mysql.connection.commit()
        print("Tabla 'usuario' creada o ya existe")
    except Exception as e:
        print(f"Error creando tabla: {e}")

def email_existe(correo):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT correo FROM usuarios WHERE correo=%s", (correo,))
    return cursor.fetchone() is not None

def obtener_usuario_por_email(correo):
 try:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
    return cursor.fetchone()  
 except Exception as e:
    print(f"Error obteniendo usuario: {e}")
    return None

def registrar_usuario(nombre, genero, actFisica, peso, altura, correo, contrasena):
    try:
        cursor = mysql.connection.cursor()
        hashed = generate_password_hash(passw)
        cursor.execute(
            '''INSERT INTO usuarios(nombre, genero, actFisica, peso, altura, correo, contrasena)
               VALUES (%s, %s, %s, %s, %s, %s, %s,)''',
            (nombre, genero, actFisica, peso, altura, correo, hashed)
        )

        mysql.connection.commit()
        return True, f"Registrado con exito: {correo}"
    except Exception as e:
        if "Duplicate" in str(e):
            return False, "El correo ingresado ya esta siendo usado por otra cuenta"
        return False, f"Error al registrar usuario: {e}"

def actualizar_usuario_por_correo(correo, nombre, genero, actFisica, peso, altura):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE usuarios
                          SET nombre=%s, genero=%s, actFisica=%s, peso=%s, altura=%s
                          WHERE correo=%s''',
                       (nombre, genero, actFisica, peso, altura, correo))
        mysql.connection.commit()
        return True, "Cambios guardados exitosamente"
    except Exception as e:
        return False, f"Error al actualizar perfil: {e}"

def eliminar_usuario_por_correo(correo):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE correo=%s", (correo,))
        mysql.connection.commit()
        return True, "Tu cuenta ha sido eliminada exitosamente."
    except Exception as e:
        return False, f"Error al eliminar cuenta: {e}"

try:
    crear_tabla_users()
except:
    print("Advertencia: tabla usuarios no verificada.")



def necesita_sesion():
    return "email" not in session  # True si NO hay sesión

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

    cursor = mysql.connect().cursor()
    cursor.execute("INSERT INTO usuario (nombre, apellidos, dia, mes, anio, genero, correo, contrasena) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (nombre,apellidos,dia,mes,anio,genero,email,contrasena))
    cursor.connection.commit()
    flash("Registro exitoso!")
    return redirect(url_for("sesion"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    contrasena = request.form["contrasena"]

    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * FROM usuario WHERE correo=%s AND contrasenaa=%s",(email,contrasena))
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

@app.route("/search")
def search():
    if "email" not in session:
        return redirect(url_for("sesion"))
    return render_template("buscar.html")

@app.route("/search", methods=["POST"])
def search_food():
    if "email" not in session:
        return redirect(url_for("sesion"))
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
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import mysql.connector 
from werkzeug.security import generate_password_hash, check_password_hash 

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'izakaya',         
    'password': 'izakaya', 
    'database': 'izakaya',
}

app.config["SECRET_KEY"] = "una_clave_secreta_muy_larga_y_dificil_de_adivinar"

def get_db_connection():
    try:
        # Usa el conector nativo de MySQL
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        # Si falla, imprime el error EXACTO para el usuario 
        print(f"ERROR DE CONEXIÓN CRÍTICO: {err}")
        return None

def crear_tabla_users():
    conn = get_db_connection()
    if conn is None:
        print("Fallo al conectar para crear la tabla.")
        return
        
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                user_ID INT(11) NOT NULL AUTO_INCREMENT,
                nombre VARCHAR(50) NOT NULL,
                apellidos VARCHAR(50) NOT NULL,
                dia TINYINT(4) NOT NULL,
                mes TINYINT(4) NOT NULL,
                anio INT(11) NOT NULL,
                genero ENUM('H','M','O','P') NOT NULL,
                actFisica ENUM('Y','N') NOT NULL, 
                correo VARCHAR(50) NOT NULL UNIQUE,
                contrasena VARCHAR(255) NOT NULL, 
                PRIMARY KEY (user_ID)
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error al verificar o crear la tabla: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        
try:
    crear_tabla_users()
except Exception:
    pass

# Función de utilidad para obtener datos del usuario
def obtener_usuario_por_email(correo):
    conn = get_db_connection()
    if conn is None:
        return None
        
    user_dict = None
    try:
        cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para obtener resultados como dict
        cursor.execute("SELECT user_ID, nombre, apellidos, dia, mes, anio, genero, actFisica, correo, contrasena FROM usuario WHERE correo=%s", (correo,))
        user_data = cursor.fetchone()
        
        if user_data:
            user_dict = user_data
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        return user_dict

# --- Rutas de Navegación y Vistas ---

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

@app.route('/abo')
def nosotros():
    return render_template('acercaDe.html')

@app.route('/dat')
def datos():
    return render_template('usoDatos.html')

# --- Rutas de Calculadoras ---

@app.route('/masa')
def calculadora_imc():
    return render_template('calculadora_imc.html')

@app.route('/masa/calcular', methods=["GET", "POST"])
def calcular_imc():
    resultado = None
    if request.method == "POST":
        try:
            peso, estatura = float(request.form["peso"]), float(request.form["estatura"]) 
            imc = peso / ((estatura / 100) ** 2)
            resultado = round(imc, 2)
        except ValueError:
            flash("Por favor, introduce números válidos para peso y estatura.", 'error')
    return render_template("calculadora_imc.html", resultado=resultado)

@app.route('/basal')
def calculadora_basal():
    return render_template('calculadora_basal.html')

@app.route('/tmb', methods=["GET", "POST"])
def calcular_tmb():
    resultado = None
    if request.method == "POST":
        try:
            genero, peso, altura, edad = request.form["genero"], float(request.form["peso"]), float(request.form["altura"]), int(request.form["edad"])
            if genero == "hombre":
                resultado = 10 * peso + 6.25 * altura - 5 * edad + 5
            else: 
                resultado = 10 * peso + 6.25 * altura - 5 * edad - 161
            resultado = round(resultado, 2)
        except ValueError:
            flash("Por favor, introduce números válidos.", 'error')
    return render_template("calculadora_basal.html", resultado=resultado)

@app.route('/gasto')
def calculadora_gasto():
    return render_template('calculadora_gasto.html')

@app.route('/gct', methods=["GET", "POST"])
def calculadora_gct():
    resultado = None
    if request.method == "POST":
        try:
            tmb, factor = float(request.form["tmb"]), float(request.form["factor"])
            resultado = round(tmb * factor, 2)
        except ValueError:
            flash("Por favor, introduce números válidos.", 'error')
    return render_template("calculadora_gasto.html", resultado=resultado)

@app.route('/ideal')
def calculadora_ideal():
    return render_template('calculadora_ideal.html')

@app.route('/idea', methods=["GET", "POST"])
def calculadora_idea():
    resultado = None
    if request.method == "POST":
        try:
            genero, altura = request.form["genero"], float(request.form["altura"])
            if genero == "hombre":
                resultado = 50 + 0.91 * (altura - 152)
            else: 
                resultado = 45.5 + 0.91 * (altura - 152)
            resultado = round(resultado, 2)
        except ValueError:
            flash("Por favor, introduce números válidos.", 'error')
    return render_template("calculadora_ideal.html", resultado=resultado)

@app.route('/macro')
def calculadora_macro():
    if "email" not in session: return redirect(url_for("sesion"))
    return render_template('calculadora_macro.html')

@app.route('/calcular_macro', methods=["POST"])
def calcular_macro():
    resultado = None
    if "email" not in session: return redirect(url_for("sesion"))
    try:
        alimento = request.form["alimento"]
        grasas, proteinas, carbohidratos = float(request.form["grasas"]), float(request.form["proteinas"]), float(request.form["carbohidratos"])
        calorias_totales = (grasas * 9) + (proteinas * 4) + (carbohidratos * 4)
        resultado = {"alimento": alimento, "grasas": grasas, "proteinas": proteinas, "carbohidratos": carbohidratos, "calorias_totales": round(calorias_totales, 2)}
    except ValueError:
        flash("Por favor, introduce números válidos para los macronutrientes.", 'error')
    return render_template("calculadora_macro.html", resultado=resultado)

@app.route("/search", methods=["GET", "POST"])
def search_food():
    if "email" not in session and request.method == "POST": 
        flash("Debes iniciar sesión para realizar búsquedas.", 'warning')
        return redirect(url_for("sesion"))

    if request.method == "POST":
        query = request.form.get("food_name", "").strip()
        if not query:
            flash("Por favor ingresa un alimento para buscar.", "warning")
            return redirect(url_for("search_food"))
        try:
            params = {"api_key": "rfTd35c18oR2TY0uJOMRZpk6kPH9TsHy8Id90E3k", "query": query, "pageSize": 3}
            response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params=params)
            
            if response.status_code == 200:
                foods = response.json().get("foods", [])
                if not foods:
                    flash(f"No se encontraron resultados para '{query}'.", "info")
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
                flash(f"Error en la búsqueda (Código: {response.status_code}).", "error")
                return render_template("buscar.html")
        except requests.exceptions.RequestException as e:
            flash(f"Error al conectarse con la API de alimentos: {e}", "error")
            return render_template("buscar.html")
    
    return render_template("buscar.html")

# --- Rutas de Autenticación y Cuenta ---

@app.route("/registrame", methods=["POST"])
def registrame():
    conn = get_db_connection()
    if conn is None:
        flash("Error fatal de conexión a la base de datos.", 'error')
        return render_template("registro.html")

    try:
        nombre, apellidos = request.form["nombre"], request.form["apellidos"]
        dia, mes, anio = int(request.form["dia"]), int(request.form["mes"]), int(request.form["anio"])
        genero, actFisica = request.form["genero"], request.form["actFisica"] 
        email, contrasena, confirmar = request.form["email"], request.form["contrasena"], request.form["confirmar_contrasena"]

        if contrasena != confirmar:
            flash("La contraseña no coincide", 'warning')
            return render_template("registro.html")

        if obtener_usuario_por_email(email):
            flash("El correo ya está registrado.", 'warning')
            return render_template("registro.html")

        hashed_password = generate_password_hash(contrasena)
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuario (nombre, apellidos, dia, mes, anio, genero, actFisica, correo, contrasena)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ''', (nombre, apellidos, dia, mes, anio, genero, actFisica, email, hashed_password))
        
        conn.commit()
        flash("Registro exitoso! Ya puedes iniciar sesión.", 'success')
        return redirect(url_for("sesion"))

    except Exception as e:
        flash(f"Error al registrar usuario: {e}", 'error')
        return render_template("registro.html")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/login", methods=["POST"])
def login():
    email, contrasena_plana = request.form["email"], request.form["contrasena"] 
    user = obtener_usuario_por_email(email)
    
    if user and check_password_hash(user['contrasena'], contrasena_plana):
        session["email"], session["nombre"] = user['correo'], user['nombre']
        flash("Sesión iniciada", 'success')
        return redirect(url_for("index"))
    else:
        flash("Usuario o contraseña incorrecta.", 'error')
        return render_template("sesion.html")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear()  
    flash("Sesión cerrada.", 'info')
    return redirect(url_for("sesion"))

@app.route("/cue", methods=["GET"])
def cuenta():
    if "email" not in session: return redirect(url_for("sesion"))
    user = obtener_usuario_por_email(session['email'])
    
    if user:
        return render_template("cuentaUsuario.html", user=user) 
    
    flash("Error al cargar la información del usuario.", 'error')
    return redirect(url_for("index"))
    
@app.route("/cuenta/actualizar", methods=["POST"])
def actualizar_usuario():
    if "email" not in session:
        return redirect(url_for("sesion"))

    conn = get_db_connection()
    if conn is None:
        flash("Error fatal de conexión a la base de datos.", 'error')
        return redirect(url_for("cuenta"))

    try:
        nombre, apellidos = request.form["nombre"], request.form["apellidos"]
        dia, mes, anio = int(request.form["dia"]), int(request.form["mes"]), int(request.form["anio"])
        genero, actFisica = request.form["genero"], request.form["actFisica"] 
        contrasena_nueva = request.form.get("contrasena_nueva", "").strip()

        cursor = conn.cursor()
        
        sql = """
            UPDATE usuario SET 
                nombre=%s, apellidos=%s, dia=%s, mes=%s, anio=%s, genero=%s, actFisica=%s
            WHERE correo=%s
        """
        params = (nombre, apellidos, dia, mes, anio, genero, actFisica, session['email'])
        
        if contrasena_nueva:
            hashed_password = generate_password_hash(contrasena_nueva)
            sql = """
                UPDATE usuario SET 
                    nombre=%s, apellidos=%s, dia=%s, mes=%s, anio=%s, genero=%s, actFisica=%s, contrasena=%s
                WHERE correo=%s
            """
            params = (nombre, apellidos, dia, mes, anio, genero, actFisica, hashed_password, session['email'])

        cursor.execute(sql, params)
        conn.commit()
        
        flash("Tus datos han sido actualizados exitosamente.", 'success')
        return redirect(url_for("cuenta"))

    except Exception as e:
        flash(f"Error al actualizar la información: {e}", 'error')
        return redirect(url_for("cuenta"))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
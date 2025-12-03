from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash 

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         
    'password': '', 
    'database': 'izakaya',
}

# Clave secreta OBLIGATORIA para el manejo de sesiones de Flask
app.config["SECRET_KEY"] = "una_clave_secreta_muy_larga_y_dificil_de_adivinar"

# --- FUNCIONES DE BASE DE DATOS ---

def get_db_connection():
    """Establece una conexión con la base de datos MySQL."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        # Mensaje de error 
        print(f"ERROR CRÍTICO DE CONEXIÓN A LA BD: {err}")
        return None

def crear_tabla_users():
    """Asegura que la tabla 'usuario' exista, incluyendo todos los campos nutricionales."""
    conn = get_db_connection()
    if conn is None: return
        
    cursor = None
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
                
                -- CAMPOS DE NUTRICIÓN REQUERIDOS EN EL REGISTRO
                objetivo VARCHAR(100) NULL,
                dieta VARCHAR(100) NULL,
                alergias TEXT NULL,
                
                PRIMARY KEY (user_ID)
            )
        ''')
        conn.commit()
    except Exception as e:
        # Mensaje de error 
        print(f"Error al verificar o crear la tabla 'usuario': {e}")
    finally:
        if conn and conn.is_connected():
            if cursor: cursor.close()
            conn.close()

try:
    crear_tabla_users()
except Exception:
    pass

def obtener_usuario_por_email(correo):
    """Obtiene los datos completos del usuario por correo electrónico."""
    conn = get_db_connection()
    if conn is None: return None
        
    user_dict = None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # Se seleccionan todos los campos
        query = """
        SELECT user_ID, nombre, apellidos, dia, mes, anio, genero, actFisica, correo, contrasena, 
                objetivo, dieta, alergias 
        FROM usuario 
        WHERE correo=%s
        """
        cursor.execute(query, (correo,))
        user_data = cursor.fetchone()
        
        if user_data:
            user_dict = user_data
    except Exception as e:
        print(f"Error al buscar el usuario: {e}")
    finally:
        if conn and conn.is_connected():
            if cursor: cursor.close()
            conn.close()
        return user_dict

# --- RUTAS PRINCIPALES DE VISTA (GET) ---

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

# --- RUTAS DE CALCULADORAS ---

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
            flash("Oye, asegúrate de poner solo números válidos para tu peso y estatura.", 'error')
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
            flash("Necesitas ingresar valores numéricos válidos en todos los campos.", 'error')
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
            flash("Por favor, revisa que tus datos sean números válidos.", 'error')
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
            flash("Recuerda usar solo números para la altura.", 'error')
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
        flash("Asegúrate de que los valores de macronutrientes sean números.", 'error')
    return render_template("calculadora_macro.html", resultado=resultado)

@app.route("/search", methods=["GET", "POST"])
def search_food():
    if "email" not in session and request.method == "POST": 
        flash("Para buscar alimentos, primero debes iniciar sesión.", 'warning')
        return redirect(url_for("sesion"))

    if request.method == "POST":
        query = request.form.get("food_name", "").strip()
        if not query:
            flash("¡Ups! Olvidaste escribir el nombre del alimento.", "warning")
            return redirect(url_for("search_food"))
        try:
            params = {"api_key": "rfTd35c18oR2TY0uJOMRZpk6kPH9TsHy8Id90E3k", "query": query, "pageSize": 3}
            response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params=params)
            
            if response.status_code == 200:
                foods = response.json().get("foods", [])
                if not foods:
                    flash(f"No encontramos resultados para '{query}'. Intenta con otro nombre.", "info")
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
                flash(f"Ocurrió un error al intentar buscar la información (Código: {response.status_code}).", "error")
                return render_template("buscar.html")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con la base de datos de alimentos: {e}", "error")
            return render_template("buscar.html")
    
    return render_template("buscar.html")

# --- RUTAS DE AUTENTICACIÓN Y CUENTA ---

@app.route("/registrame", methods=["POST"])
def registrame():
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar a la base de datos para el registro. Intenta más tarde.", 'error')
        return render_template("registro.html")

    cursor = None
    try:
        # Campos de usuario básicos
        nombre, apellidos = request.form["nombre"], request.form["apellidos"]
        dia, mes, anio = int(request.form["dia"]), int(request.form["mes"]), int(request.form["anio"])
        genero, actFisica = request.form["genero"], request.form["actFisica"] 
        email, contrasena, confirmar = request.form["email"], request.form["contrasena"], request.form["confirmar_contrasena"]
        
        # Campos nutricionales (se toman del formulario, con default a vacío si no se envían)
        objetivo = request.form.get("objetivo", "")
        dieta = request.form.get("dieta", "")
        alergias = request.form.get("alergias", "")

        if contrasena != confirmar:
            flash("¡Ojo! Las contraseñas que escribiste noL2 coinciden.", 'warning')
            return render_template("registro.html")

        if obtener_usuario_por_email(email):
            flash("Parece que ese correo ya está registrado. ¿Quieres iniciar sesión?", 'warning')
            return render_template("registro.html")

        hashed_password = generate_password_hash(contrasena)
        
        cursor = conn.cursor()
        query = '''
            INSERT INTO usuario (nombre, apellidos, dia, mes, anio, genero, actFisica, correo, contrasena, objetivo, dieta, alergias)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        values = (nombre, apellidos, dia, mes, anio, genero, actFisica, email, hashed_password, objetivo, dieta, alergias)
        
        cursor.execute(query, values)
        
        conn.commit()
        
        flash("¡Registro completado! Ya puedes entrar a tu cuenta.", 'success')
        return redirect(url_for("sesion"))

    except Exception as e:
        flash(f"Hubo un problema al intentar registrarte. Error: {e}", 'error')
        return render_template("registro.html")
    finally:
        if conn and conn.is_connected():
            if cursor: cursor.close()
            conn.close()

@app.route("/login", methods=["POST"])
def login():
    email, contrasena_plana = request.form["email"], request.form["contrasena"] 
    user = obtener_usuario_por_email(email)
    
    if user and check_password_hash(user['contrasena'], contrasena_plana):
        # 🟢 CORRECCIÓN APLICADA: Aseguramos que la clave user_ID se establece de forma independiente
        session["email"] = user['correo']
        session["nombre"] = user['nombre']
        session["user_ID"] = user['user_ID'] 
        
        flash(f"¡Bienvenido, {user['nombre']}!", 'success')
        return redirect(url_for("index"))
    else:
        flash("El correo o la contraseña no son correctos.", 'error')
        return render_template("sesion.html")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear() 
    flash("Tu sesión ha sido cerrada. ¡Vuelve pronto!", 'info')
    return redirect(url_for("sesion"))

@app.route("/cue", methods=["GET"])
def cuenta():
    """Muestra la página de la cuenta del usuario logueado. Usa /cue y cuenta()."""
    if "email" not in session: return redirect(url_for("sesion"))
    user = obtener_usuario_por_email(session['email'])
    
    if user:
        return render_template("cuentaUsuario.html", user=user) 
    
    flash("No pudimos cargar la información de tu cuenta.", 'error')
    return redirect(url_for("index"))
    
@app.route("/cuenta/actualizar", methods=["POST"])
def actualizar_usuario():
    """Procesa el formulario de actualización de datos del usuario."""
    if "email" not in session:
        return redirect(url_for("sesion"))
    conn = get_db_connection()
    if conn is None:
        flash("Error fatal: No se puede conectar a la base de datos para actualizar tus datos.", 'error')
        return redirect(url_for("cuenta"))

    cursor = None
    try:
        # Campos de usuario básicos
        nombre, apellidos = request.form["nombre"], request.form["apellidos"]
        dia, mes, anio = int(request.form["dia"]), int(request.form["mes"]), int(request.form["anio"])
        genero, actFisica = request.form["genero"], request.form["actFisica"] 
        contrasena_nueva = request.form.get("contrasena_nueva", "").strip()
        
        # Campos nutricionales
        objetivo = request.form.get("objetivo", "")
        dieta = request.form.get("dieta", "")
        alergias = request.form.get("alergias", "")

        cursor = conn.cursor()
        
        # SQL para actualizar datos básicos y nutricionales
        sql = """
            UPDATE usuario SET 
                nombre=%s, apellidos=%s, dia=%s, mes=%s, anio=%s, genero=%s, actFisica=%s, 
                objetivo=%s, dieta=%s, alergias=%s
            WHERE correo=%s
        """
        params = [nombre, apellidos, dia, mes, anio, genero, actFisica, objetivo, dieta, alergias, session['email']]
        
        if contrasena_nueva:
            # Si hay contraseña nueva, la agregamos a la consulta
            hashed_password = generate_password_hash(contrasena_nueva)
            sql = """
                UPDATE usuario SET 
                    nombre=%s, apellidos=%s, dia=%s, mes=%s, anio=%s, genero=%s, actFisica=%s, 
                    objetivo=%s, dieta=%s, alergias=%s, contrasena=%s
                WHERE correo=%s
            """
            params.insert(10, hashed_password) # insertamos el hash antes del email
            
        cursor.execute(sql, params)
        conn.commit()
        
        flash("¡Perfecto! Tus datos han sido actualizados.", 'success')
        return redirect(url_for("cuenta")) # Redirección consistente a /cue
    except Exception as e:
        flash(f"No pudimos actualizar tu información. Revisa tus datos. Error: {e}", 'error')
        return redirect(url_for("cuenta")) # Redirección consistente a /cue
    finally:
        if conn and conn.is_connected():
            if cursor: cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
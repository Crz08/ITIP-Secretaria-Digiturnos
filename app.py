from flask import Flask 
from flask import render_template, redirect, request, Response, session
from flask_mysqldb import MySQL, MySQLdb

import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__,template_folder='templates')
app.permanent_session_lifetime = timedelta(days=30)
app.secret_key = 'hola'
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'itip'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'
mysql=MySQL(app)
CORREO = "TU CORREO"
CLAVE_APP = "TU CLAVE"


def enviar_codigo(correo_destino, codigo):

    mensaje = MIMEMultipart()

    mensaje['From'] = CORREO
    mensaje['To'] = correo_destino
    mensaje['Subject'] = "Código de verificación - ITIP"

    texto = f"""
Hola.

Tu código de verificación para crear tu cuenta en ITIP es:

{codigo}

Este código es necesario para completar tu registro.
"""

    mensaje.attach(MIMEText(texto, 'plain'))

    servidor = smtplib.SMTP('smtp.gmail.com', 587)
    servidor.starttls()
    servidor.login(CORREO, CLAVE_APP)
    servidor.send_message(mensaje)
    servidor.quit()
    
@app.route('/reenviar_codigo')
def reenviar_codigo():

    registro = session.get('registro')

    if not registro:
        return redirect('/iniciar_sesion.html')

    nuevo_codigo = str(random.randint(100000, 999999))

    session['registro']['codigo'] = nuevo_codigo
    session.modified = True

    enviar_codigo(
        registro['correo'],
        nuevo_codigo
    )

    return render_template(
        'verificar_codigo.html',
        mensaje2="Se ha enviado un nuevo código a tu correo"
    )
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/iniciar_sesion.html')
def iniciar():
    return render_template('iniciar_sesion.html')

@app.route('/agendar_citas.html')
def agendar():
    return render_template('agendar_citas.html')

@app.route('/admin.html')
def admin():
    return render_template('admin.html')

@app.route('/sedes.html')
def sedes():
    return render_template('sedes.html')
@app.route('/inicio.html')
def inicio():
    return render_template('inicio.html')
@app.route('/noticias.html')
def noticias():
    return render_template('noticias.html')
@app.route('/recuperar_password', methods=["GET", "POST"])
def recuperar_password():

    if request.method == "POST":

        correo = request.form['correo']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM usuarios WHERE correo = %s",
            (correo,)
        )

        usuario = cur.fetchone()
        cur.close()

        if not usuario:
            return render_template(
                'recuperar_password.html',
                mensaje4="No existe una cuenta con ese correo"
            )

        codigo = str(random.randint(100000, 999999))

        session['recuperacion'] = {
            'correo': correo,
            'codigo': codigo
        }

        enviar_codigo(correo, codigo)

        return redirect('/verificar_recuperacion')

    return render_template('recuperar_password.html')
@app.route('/verificar_recuperacion', methods=["GET", "POST"])
def verificar_recuperacion():

    recuperacion = session.get('recuperacion')

    if not recuperacion:
        return redirect('/recuperar_password')

    if request.method == "POST":

        codigo = request.form['codigo']

        if codigo == recuperacion['codigo']:

            session['recuperacion_verificada'] = True

            return redirect('/nueva_password')

        return render_template(
            'verificar_recuperacion.html',
            mensaje4="Código incorrecto"
        )

    return render_template('verificar_recuperacion.html')
@app.route('/nueva_password', methods=["GET", "POST"])
def nueva_password():

    recuperacion = session.get('recuperacion')

    if not recuperacion or not session.get('recuperacion_verificada'):
        return redirect('/recuperar_password')

    if request.method == "POST":

        password = request.form['password']
        confirmar_password = request.form['confirmar_password']

        if password != confirmar_password:

            return render_template(
                'nueva_password.html',
                mensaje4="Las contraseñas no coinciden"
            )

        if not re.match(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,}$',
            password
        ):

            return render_template(
                'nueva_password.html',
                mensaje4="La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo"
            )

        cur = mysql.connection.cursor()

        password_encriptada = generate_password_hash(password)


        cur.execute(
            """
            UPDATE usuarios
            SET password = %s
            WHERE correo = %s
            """,
            (
                password_encriptada,
                recuperacion['correo']
            )
        )

        mysql.connection.commit()
        cur.close()

        session.pop('recuperacion', None)
        session.pop('recuperacion_verificada', None)

        return render_template(
            'iniciar_sesion.html',
            mensaje2="Contraseña cambiada correctamente"
        )

    return render_template('nueva_password.html')
@app.route('/acceso', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form['correo']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT id, correo, password, id_rol FROM usuarios WHERE correo = %s",
            (correo,)
        )

        account = cur.fetchone()

        if account is None:
            cur.close()

            return render_template(
                'iniciar_sesion.html',
                mensaje4="El correo no existe"
            )

        print("CORREO:", account['correo'])
        print("HASH:", account['password'])
        print("PASSWORD:", password)

        resultado = check_password_hash(
            account['password'],
            password
        )

        print("RESULTADO:", resultado)

        if resultado:

            session.permanent = 'recordarme' in request.form

            session['logueado'] = True
            session['id'] = account['id']
            session['id_rol'] = account['id_rol']

            cur.close()

            if account['id_rol'] == 1:
                return render_template('admin.html')

            elif account['id_rol'] == 2:
                return render_template('inicio.html')

        cur.close()

        return render_template(
            'iniciar_sesion.html',
            mensaje4="Contraseña incorrecta"
        )

    return render_template('iniciar_sesion.html')
@app.route('/ver_turnos.html', methods=["GET","POST"])
def ver_turnos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM turnos")
    turnos = cur.fetchall()
    cur.close()
    return render_template("ver_turnos.html",turnos=turnos)
@app.route('/eliminar_turno/<int:id>')
def eliminar_turno(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM turnos WHERE id = %s",
        (id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/ver_turnos.html')
@app.route('/usuarios.html')
def usuarios():

    cur = mysql.connection.cursor()

    cur.execute("SELECT id, correo, id_rol FROM usuarios")

    usuarios = cur.fetchall()

    cur.close()

    return render_template(
        'usuarios.html',
        usuarios=usuarios
    )
@app.route('/cambiar_rol/<int:id>')
def cambiar_rol(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT id_rol FROM usuarios WHERE id = %s",
        (id,)
    )

    usuario = cur.fetchone()

    if usuario:

        if usuario['id_rol'] == 1:
            nuevo_rol = 2
        else:
            nuevo_rol = 1

        cur.execute(
            "UPDATE usuarios SET id_rol = %s WHERE id = %s",
            (nuevo_rol, id)
        )

        mysql.connection.commit()

    cur.close()

    return redirect('/usuarios.html')
@app.route('/agendar_cita', methods=["GET", "POST"])
def agendar_cita():
    if request.method == "POST":
        # 1. Obtener datos del formulario
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        servicio = request.form.get('servicio')
        descripcion = request.form.get('descripcion')

        cur = mysql.connection.cursor()

        # 2. Validar que no esté ocupada la fecha/hora en la tabla 'turnos'
        cur.execute(
            "SELECT * FROM turnos WHERE fecha = %s AND hora = %s",
            (fecha, hora)
        )
        cita_existente = cur.fetchone()

        if cita_existente:
            cur.close()
            return render_template(
                'agendar_citas.html',
                mensaje_error="Esta fecha y hora ya están ocupadas. Por favor elige otro horario."
            )

        # 3. Insertar el registro en la tabla 'turnos'
        try:
            cur.execute("""
                INSERT INTO turnos (servicio, descripcion, nombres, apellidos, tipo_documento, numero_documento, fecha, hora)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                servicio,
                descripcion,
                nombres,
                apellidos,
                tipo_documento,
                numero_documento,
                fecha,
                hora
            ))
            
            mysql.connection.commit()
            cur.close()

            return render_template('inicio.html', mensaje3="¡Cita agendada con éxito!")

        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            return render_template(
                'agendar_citas.html',
                mensaje_error=f"Error al guardar el turno"
            )

    return render_template('agendar_citas.html')
@app.route('/editar_turno/<int:id>', methods=["GET", "POST"])
def editar_turno(id):
    cur = mysql.connection.cursor()
    
    if request.method == "POST":
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        servicio = request.form.get('servicio')
        descripcion = request.form.get('descripcion')

        cur.execute("""
            UPDATE turnos 
            SET servicio=%s, descripcion=%s, nombres=%s, apellidos=%s, tipo_documento=%s, numero_documento=%s, fecha=%s, hora=%s
            WHERE id=%s
        """, (servicio, descripcion, nombres, apellidos, tipo_documento, numero_documento, fecha, hora, id))
        
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('ver_turnos'))

    # Para GET: Obtener los datos del turno a editar
    cur.execute("SELECT * FROM turnos WHERE id = %s", (id,))
    turno = cur.fetchone()
    cur.close()

    return render_template('editar_turno.html', turno=turno)
@app.route('/verificar_codigo', methods=["GET", "POST"])
def verificar_codigo():

    if request.method == "POST":

        codigo_ingresado = request.form['codigo']

        registro = session.get('registro')

        if not registro:
            return redirect('/iniciar_sesion.html')

        if codigo_ingresado == registro['codigo']:

            password_encriptada = generate_password_hash(
                registro['password']
            )

            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO usuarios (correo, password, id_rol) VALUES (%s, %s, %s)",
                (
                    registro['correo'],
                    password_encriptada,
                    2
                )
            )

            mysql.connection.commit()
            cur.close()

            session.pop('registro', None)

            return render_template(
                'iniciar_sesion.html',
                mensaje2="Usuario creado correctamente"
            )

        return render_template(
            'verificar_codigo.html',
            mensaje4="Código incorrecto"
        )

    return render_template('verificar_codigo.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5555, threaded=True)


    

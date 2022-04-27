import json
from flask import Flask, jsonify, request, render_template, redirect, session, url_for
from flask_cors import CORS
import datetime
import loaf
import random, string

app = Flask(__name__)
app.config["SECRET_KEY"] = "duchate"
CORS(app)

loaf.bake(
    host="ducha-y-ahorra.c6vxgsopricg.us-east-2.rds.amazonaws.com",
    port=3306,
    user="admin",
    pasw="duchate123",
    db="ducha_y_ahorra"
)

@app.route('/')
def index():
    try:
        #print(session["usuario"])
        if (session["usuario"] and session["password"]):
            return redirect(url_for("historial"))
    except KeyError:
        session["usuario"] = ""
        session["password"] = ""
    return redirect(url_for("login"))


@app.route('/login', methods=["POST","GET"])
def login():
    error = ''
    if request.method=='POST':
        if 'signIn' in request.form:
            correo = request.form.get('correo')
            password = request.form.get('passw')

            if not (correo and password):
                error = 'Faltan campos'
                return render_template('login.html', error = error)

            userInfo = loaf.query(f'''  SELECT usuarioID, maxWater 
                                        FROM usuario WHERE correo='{correo}' 
                                        AND password='{password}' ''')
            
            print(userInfo)
            
            if userInfo:
                session['usuario'] = correo
                session['password'] = password
                return redirect(url_for('historial'))

            else:
                if not userInfo:
                    error = 'Usuario o contrasenia incorrectos'
            
    return render_template('login.html', error = error)

@app.route('/historial', methods=["POST","GET"])
def historial():
    uid = session['usuario']
    mess = ''

    duchas = loaf.query(f'''    SELECT ducha.duchaID, fecha, duracion, agua
                                FROM ducha
                                INNER JOIN
                                    (SELECT duchaID
                                    FROM ducha_usuario
                                    INNER JOIN 
                                        (SELECT usuarioID 
                                        FROM usuario 
                                        WHERE correo='{uid}') AS uid 
                                    ON ducha_usuario.usuarioID = uid.usuarioID) AS du
                                ON ducha.duchaID = du.duchaID
                                ORDER BY fecha DESC
                        ''')

    if not duchas:
        duchas = []
        mess = 'No tines duchas registradas'
        
    return render_template('historial.html', historial=duchas, duchasReg=len(duchas), mess=mess)

@app.route('/perfil', methods=["POST","GET"])
def perfil():
    uid = session['usuario']
    error = ''

    if request.method == 'POST':
        if 'logout' in request.form:
            print('logout bitch')
            session['usuario'] = ''
            session['password'] = ''
            return redirect(url_for('index'))

        password = request.form.get('passw')
        confPassword = request.form.get('passw2')
        maxWater = float(request.form.get('maxWater'))
        valid = True

        if password != confPassword:
            error = 'Las contraseñas no coinciden'
            valid = False
        
        if valid:
            loaf.query(f''' UPDATE usuario SET password='{password}', maxWater='{maxWater}' WHERE correo='{uid}' ''')


    userInfo = loaf.query(f''' SELECT correo, password, maxWater
                                    FROM usuario
                                    WHERE correo='{uid}' ''')
        
    if not userInfo:
        error = 'El usuario no existe'
    
    userInfo=userInfo[0]
    print(userInfo)

    return render_template('perfil.html', error=error, usuario=userInfo)
    

@app.route('/registro', methods=["POST","GET"])
def registro():
    error = ''
    if request.method=='POST':
        correo = request.form.get('correo')
        password = request.form.get('passw')
        confPassword = request.form.get('passw2')
        maxWater = float(request.form.get('maxWater'))
        #print(correo, password, confPassword, maxWater)
        
        if not (correo and password and confPassword and maxWater):
            error = 'Faltan campos'
            return render_template('registro.html', error = error)
        
        if password != confPassword:
            error = 'Las contrasenias no coinciden'
            return render_template('registro.html', error = error)

        # Checa si el correo ya esta registrado
        checkExistencia = loaf.query(f''' SELECT usuarioID FROM usuario WHERE correo = '{correo}' ''')
        if checkExistencia:
            error = 'El correo ya esta registrado'
            return render_template('registro.html', error = error)
        
        loaf.query(f''' INSERT INTO usuario (correo, password, maxWater)
                        VALUES ('{correo}', '{password}', '{maxWater}')''')
        
        session['usuario'] = correo
        session['password'] = password

        return redirect(url_for("historial"))

    else:
        return render_template("Registro.html")
        

# Main
if __name__ == "__main__":
    app.run(debug=True)    
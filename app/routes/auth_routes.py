from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensiones import mysql
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):  # user[3] es la contraseña
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['rol_id'] = user[4]
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('public.index'))
        else:
            flash('Credenciales incorrectas', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (username, email, password, rol_id) VALUES (%s, %s, %s, %s)", 
                    (username, email, password, 3))  # 3 = cliente
        mysql.connection.commit()
        cur.close()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('public.index'))



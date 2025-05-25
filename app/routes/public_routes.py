from flask import Blueprint, flash, render_template, session, redirect, url_for
from app.extensiones import mysql
from datetime import datetime


public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/catalogo')
def catalogo():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    return render_template('public/catalogo.html', productos=productos)


@public_bp.route('/carrito')
def carrito():
    if 'user_id' not in session:
        return redirect(url_for('public.index'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.nombre, p.precio, p.imagen, cd.cantidad, (p.precio * cd.cantidad) AS total
        FROM carritos c
        JOIN carrito_detalle cd ON c.id = cd.carrito_id
        JOIN productos p ON p.id = cd.producto_id
        WHERE c.usuario_id = %s AND c.finalizado = 0
    """, (session['user_id'],))
    productos = cur.fetchall()
    cur.close()

    return render_template('public/carrito.html', productos=productos)


@public_bp.route('/agregar_carrito/<int:producto_id>')
def agregar_carrito(producto_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para agregar productos al carrito', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Verificar si ya hay un carrito activo (no finalizado)
    cur.execute("SELECT id FROM carritos WHERE usuario_id = %s AND finalizado = 0 LIMIT 1", (user_id,))
    carrito = cur.fetchone()

    if carrito:
        carrito_id = carrito[0]
    else:
        # Crear nuevo carrito si no existe uno activo
        cur.execute("INSERT INTO carritos (usuario_id, fecha, finalizado) VALUES (%s, %s, 0)", 
                    (user_id, datetime.now()))
        mysql.connection.commit()
        carrito_id = cur.lastrowid

    # Verificar si el producto ya está en el carrito
    cur.execute("""
        SELECT id FROM carrito_detalle 
        WHERE carrito_id = %s AND producto_id = %s
    """, (carrito_id, producto_id))
    existente = cur.fetchone()

    if existente:
        # Si ya está en el carrito, aumentar la cantidad
        cur.execute("UPDATE carrito_detalle SET cantidad = cantidad + 1 WHERE id = %s", (existente[0],))
    else:
        # Si no, agregarlo nuevo
        cur.execute("""
            INSERT INTO carrito_detalle (carrito_id, producto_id, cantidad)
            VALUES (%s, %s, 1)
        """, (carrito_id, producto_id))

    mysql.connection.commit()
    cur.close()

    flash("Producto agregado al carrito", "success")
    return redirect(url_for('public.catalogo'))

@public_bp.route('/finalizar_compra')
def finalizar_compra():
    if 'user_id' not in session:
        return redirect(url_for('public.index'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Obtener el carrito activo
    cur.execute("SELECT id FROM carritos WHERE usuario_id = %s AND finalizado = 0", (user_id,))
    carrito = cur.fetchone()

    if carrito:
        carrito_id = carrito[0]

        # 1. Borrar los productos del detalle del carrito
        cur.execute("DELETE FROM carrito_detalle WHERE carrito_id = %s", (carrito_id,))

        # 2. Marcar carrito como finalizado
        cur.execute("UPDATE carritos SET finalizado = 1 WHERE id = %s", (carrito_id,))

        mysql.connection.commit()

        flash("Compra finalizada. Gracias por tu pedido.", "success")
    else:
        flash("No tienes un carrito activo.", "warning")

    cur.close()
    return redirect(url_for('public.carrito'))

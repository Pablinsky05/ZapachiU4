from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensiones import mysql

editor_bp = Blueprint('editor', __name__, url_prefix='/editor')

# Función para verificar si el usuario es editor
def requiere_editor():
    return session.get('rol_id') == 2

@editor_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    if not requiere_editor():
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('public.catalogo'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        imagen = request.form['imagen']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO productos (nombre, descripcion, precio, stock, imagen)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, stock, imagen))
        mysql.connection.commit()
        cur.close()

        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('public.catalogo'))

    return render_template('editor/agregar_productos.html')

@editor_bp.route('/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    if not requiere_editor():
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('public.catalogo'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        imagen = request.form['imagen']

        cur.execute("""
            UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s, imagen=%s
            WHERE id=%s
        """, (nombre, descripcion, precio, stock, imagen, producto_id))
        mysql.connection.commit()
        cur.close()

        flash('Producto actualizado', 'success')
        return redirect(url_for('public.catalogo'))

    cur.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
    producto = cur.fetchone()
    cur.close()

    return render_template('editor/editar_productos.html', producto=producto)

@editor_bp.route('/eliminar/<int:producto_id>')
def eliminar_producto(producto_id):
    if not requiere_editor():
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('public.catalogo'))

    cur = mysql.connection.cursor()

    # 1. Eliminar registros relacionados en carrito_detalle
    cur.execute("DELETE FROM carrito_detalle WHERE producto_id = %s", (producto_id,))

    # 2. Eliminar el producto
    cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))

    mysql.connection.commit()
    cur.close()

    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('public.catalogo'))

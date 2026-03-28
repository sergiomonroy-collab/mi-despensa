from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuración de la Base de Datos
def init_db():
    conn = sqlite3.connect('despensa.db')
    cursor = conn.cursor()
    # Tabla de productos
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, tienda TEXT, actual INTEGER, meta INTEGER)''')
    # Tabla de compras realizadas para el historial anual
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, tienda TEXT, total REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('despensa.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    
    # Cálculo de gastos anuales y mensuales
    cursor.execute("SELECT strftime('%m', fecha) as mes, SUM(total) FROM compras GROUP BY mes")
    gastos_mensuales = cursor.fetchall()
    
    cursor.execute("SELECT SUM(total) FROM compras")
    total_anual = cursor.fetchone()[0] or 0
    
    conn.close()
    return render_template('index.html', productos=productos, gastos_mensuales=gastos_mensuales, total_anual=total_anual)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    tienda = request.form['tienda']
    actual = int(request.form['actual'])
    meta = int(request.form['meta'])
    
    conn = sqlite3.connect('despensa.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre, tienda, actual, meta) VALUES (?, ?, ?, ?)", 
                   (nombre, tienda, actual, meta))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/tienda/<nombre_tienda>')
def tienda(nombre_tienda):
    conn = sqlite3.connect('despensa.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE tienda = ? AND actual < meta", (nombre_tienda,))
    faltantes = cursor.fetchall()
    conn.close()
    return render_template('tienda.html', tienda=nombre_tienda, productos=faltantes)

@app.route('/registrar_compra', methods=['POST'])
def registrar_compra():
    tienda = request.form['tienda']
    total = float(request.form['total_gastado'])
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('despensa.db')
    cursor = conn.cursor()
    # Guardamos el gasto
    cursor.execute("INSERT INTO compras (fecha, tienda, total) VALUES (?, ?, ?)", (fecha, tienda, total))
    # Resetear el stock (asumimos que al comprar, el stock actual llega a la meta)
    cursor.execute("UPDATE productos SET actual = meta WHERE tienda = ?", (tienda,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

def conexionDB():
    conn = sqlite3.connect("biblioteca.db")
    # Activar el soporte para llaves foráneas en SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar_db():
    conn = conexionDB()
    cursor = conn.cursor()
    
    # Tabla 1: Autores (Entidad Independiente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nacionalidad TEXT NOT NULL
        )
    ''')
    
    # Tabla 2: Libros (Entidad Dependiente de Autores)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            anio INTEGER NOT NULL,
            autor_id INTEGER,
            FOREIGN KEY (autor_id) REFERENCES autores (id) ON DELETE CASCADE
        )
    ''')
    
    # Insertar datos de prueba si está vacía
    cursor.execute("SELECT COUNT(*) FROM autores")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO autores (nombre, nacionalidad) VALUES (?, ?)", ("Gabriel García Márquez", "Colombiana"))
        cursor.execute("INSERT INTO autores (nombre, nacionalidad) VALUES (?, ?)", ("J.K. Rowling", "Británica"))
        
        cursor.execute("INSERT INTO libros (titulo, anio, autor_id) VALUES (?, ?, ?)", ("Cien años de soledad", 1967, 1))
        cursor.execute("INSERT INTO libros (titulo, anio, autor_id) VALUES (?, ?, ?)", ("Harry Potter y la Piedra Filosofal", 1997, 2))
        conn.commit()
    
    conn.close()

# Ruta para servir la interfaz web
@app.route('/')
def home():
    return render_template('index.html')

# ENDPOINTS

@app.route("/autores", methods=["GET"])
def obtener_autores():
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM autores")
        datos = cursor.fetchall()
        
        autores = []
        for fila in datos:
            autores.append({
                "id": fila[0],
                "nombre": fila[1],
                "nacionalidad": fila[2]
            })
        return jsonify(autores), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
@app.route("/autores/<int:id>", methods=["GET"])
def obtener_autor_por_id(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM autores WHERE id = ?", (id,))
        fila = cursor.fetchone()
        
        if fila:
            autor = {
                "id": fila[0],
                "nombre": fila[1],
                "nacionalidad": fila[2]
            }
            return jsonify(autor), 200
        else:
            return jsonify({"error": "Autor no encontrado"}), 404
            
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
@app.route("/autores", methods=["POST"])
def agregar_autor():
    data = request.json
    # Validación de seguridad básica
    if not data or "nombre" not in data or "nacionalidad" not in data:
        return jsonify({"error": "Faltan datos requeridos (nombre, nacionalidad)"}), 400
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        # Uso de placeholders ? para evitar SQL Injection
        cursor.execute("INSERT INTO autores(nombre, nacionalidad) VALUES(?,?)", 
                       (data["nombre"], data["nacionalidad"]))
        conn.commit()
        return jsonify({"mensaje": "Autor agregado exitosamente"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
@app.route("/autores/<int:id>", methods=["PUT"])
def actualizar_autor(id):
    data = request.json
    
    # Validación
    if not data or not all(i in data for i in ("nombre", "nacionalidad")):
        return jsonify({"error": "Faltan datos requeridos (nombre, nacionalidad)"}), 400
        
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE autores SET nombre = ?, nacionalidad = ? WHERE id = ?", 
                       (data["nombre"], data["nacionalidad"], id))
        
        # Verificar si el autor existía y fue modificado
        if cursor.rowcount == 0:
            return jsonify({"error": "Autor no encontrado"}), 404
            
        conn.commit()
        return jsonify({"mensaje": "Autor actualizado exitosamente"}), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/autores/<int:id>", methods=["DELETE"])
def eliminar_autor(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM autores WHERE id=?", (id,))
        conn.commit()
        return jsonify({"mensaje": "Autor eliminado"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# ==========================================
# ENDPOINTS PARA LIBROS
# ==========================================

@app.route("/libros", methods=["GET"])
def obtener_libros():
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT libros.id, libros.titulo, libros.anio,    
            autores.nombre 
            FROM libros 
            JOIN autores ON libros.autor_id = autores.id
        ''')
        datos = cursor.fetchall()
        libros = []
        for fila in datos:
            libros.append({
                "id": fila[0], 
                "titulo": fila[1], 
                "anio": fila[2], 
                "autor": fila[3]
             })
        return jsonify(libros), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
@app.route("/libros/<int:id>", methods=["GET"])
def obtener_libro_por_id(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
        # Realizamos el JOIN para traer también el nombre del autor
        cursor.execute('''
            SELECT libros.id, libros.titulo, libros.anio, 
            autores.nombre 
            FROM libros 
            JOIN autores ON libros.autor_id = autores.id
            WHERE libros.id = ?
        ''', (id,))
        
        fila = cursor.fetchone()
        
        if fila:
            libro = {
                "id": fila[0], 
                "titulo": fila[1], 
                "anio": fila[2], 
                "autor": fila[3]
            }
            return jsonify(libro), 200
        else:
            return jsonify({"error": "Libro no encontrado"}), 404
            
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/libros", methods=["POST"])
def agregar_libro():
    data = request.json
    
    # Validaciones
    if not data or not all(i in data for i in ("titulo", "anio", "autor_id")):
        return jsonify({"error": "Faltan datos requeridos (titulo, anio, autor_id)"}), 400
        
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO libros (titulo, anio, autor_id) VALUES (?, ?, ?)", 
                       (data["titulo"], data["anio"], data["autor_id"]))
        conn.commit()
        return jsonify({"mensaje": "Libro agregado exitosamente"}), 201
    except sqlite3.Error as e:
        # Esto captura errores como un autor_id que no existe
        return jsonify({"error": "Error de BD. Verifique que el autor_id exista."}), 500
    finally:
        conn.close()

@app.route("/libros/<int:id>", methods=["PUT"])
def actualizar_libro(id):
    data = request.json
    if not data or not all(i in data for i in ("titulo", "anio")):
        return jsonify({"error": "Faltan datos requeridos"}), 400
        
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("UPDATE libros SET titulo = ?, anio = ? WHERE id = ?", 
                       (data["titulo"], data["anio"], id))
        conn.commit()
        return jsonify({"mensaje": "Libro actualizado"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/libros/<int:id>", methods=["DELETE"])
def eliminar_libro(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM libros WHERE id=?", (id,))
        conn.commit()
        return jsonify({"mensaje": "Libro eliminado"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)
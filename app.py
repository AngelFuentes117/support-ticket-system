#!/usr/bin/env python3
"""
Sistema de Tickets de Soporte Técnico
Aplicación Flask con SQLite para gestión de tickets de soporte.
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = 'support-ticket-system-secret-key-change-in-production'
DATABASE = 'tickets.db'

# Constantes para categorías y prioridades
CATEGORIAS = ['Hardware', 'Software', 'Red', 'Impresora', 'Otro']
PRIORIDADES = ['Baja', 'Media', 'Alta']
ESTADOS = ['Abierto', 'En proceso', 'Cerrado']


def get_db():
    """Obtiene una conexión a la base de datos SQLite."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Cierra la conexión a la base de datos al finalizar la petición."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Inicializa la base de datos creando las tablas necesarias."""
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Ejecuta una consulta SELECT y retorna los resultados."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Ejecuta una consulta INSERT/UPDATE/DELETE y retorna el ID de la última fila insertada."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


# ============================================
# RUTAS DE LA APLICACIÓN
# ============================================

@app.route('/')
def index():
    """Panel principal con estadísticas de tickets por estado."""
    # Contar tickets por estado
    stats = {}
    for estado in ESTADOS:
        count = query_db('SELECT COUNT(*) as cnt FROM tickets WHERE estado = ?', [estado], one=True)
        stats[estado] = count['cnt'] if count else 0
    
    # Total de tickets
    total = query_db('SELECT COUNT(*) as cnt FROM tickets', one=True)
    stats['Total'] = total['cnt'] if total else 0
    
    # Tickets recientes (últimos 5)
    recent_tickets = query_db(
        'SELECT id, titulo, estado, prioridad, fecha_creacion FROM tickets ORDER BY fecha_creacion DESC LIMIT 5'
    )
    
    return render_template('index.html', stats=stats, recent_tickets=recent_tickets, ESTADOS=ESTADOS)


@app.route('/tickets')
def list_tickets():
    """Lista de tickets con filtros por estado y prioridad."""
    estado_filter = request.args.get('estado', '')
    prioridad_filter = request.args.get('prioridad', '')
    
    query = 'SELECT * FROM tickets WHERE 1=1'
    params = []
    
    if estado_filter:
        query += ' AND estado = ?'
        params.append(estado_filter)
    
    if prioridad_filter:
        query += ' AND prioridad = ?'
        params.append(prioridad_filter)
    
    query += ' ORDER BY fecha_creacion DESC'
    
    tickets = query_db(query, params)
    
    return render_template('tickets.html', 
                         tickets=tickets, 
                         ESTADOS=ESTADOS, 
                         PRIORIDADES=PRIORIDADES,
                         current_estado=estado_filter,
                         current_prioridad=prioridad_filter)


@app.route('/ticket/new', methods=['GET', 'POST'])
def create_ticket():
    """Crear un nuevo ticket."""
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        reporter_name = request.form.get('reporter_name', '').strip()
        categoria = request.form.get('categoria', '')
        prioridad = request.form.get('prioridad', '')
        
        # Validaciones
        errors = []
        if not titulo:
            errors.append('El título es obligatorio')
        if not descripcion:
            errors.append('La descripción es obligatoria')
        if not reporter_name:
            errors.append('El nombre del reportador es obligatorio')
        if categoria not in CATEGORIAS:
            errors.append('Categoría inválida')
        if prioridad not in PRIORIDADES:
            errors.append('Prioridad inválida')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('create_ticket.html', CATEGORIAS=CATEGORIAS, PRIORIDADES=PRIORIDADES)
        
        # Insertar ticket en la base de datos
        fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ticket_id = execute_db(
            '''INSERT INTO tickets (titulo, descripcion, reporter_name, categoria, prioridad, estado, fecha_creacion)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            [titulo, descripcion, reporter_name, categoria, prioridad, 'Abierto', fecha_creacion]
        )
        
        flash(f'Ticket #{ticket_id} creado exitosamente', 'success')
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    return render_template('create_ticket.html', CATEGORIAS=CATEGORIAS, PRIORIDADES=PRIORIDADES)


@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    """Ver el detalle de un ticket con sus comentarios."""
    ticket = query_db('SELECT * FROM tickets WHERE id = ?', [ticket_id], one=True)
    
    if not ticket:
        flash('Ticket no encontrado', 'error')
        return redirect(url_for('list_tickets'))
    
    # Obtener comentarios/notas del ticket
    comments = query_db(
        'SELECT * FROM comments WHERE ticket_id = ? ORDER BY fecha_creacion ASC', 
        [ticket_id]
    )
    
    return render_template('ticket_detail.html', 
                         ticket=ticket, 
                         comments=comments,
                         ESTADOS=ESTADOS)


@app.route('/ticket/<int:ticket_id>/update_state', methods=['POST'])
def update_ticket_state(ticket_id):
    """Actualizar el estado de un ticket."""
    nuevo_estado = request.form.get('estado', '')
    
    if nuevo_estado not in ESTADOS:
        flash('Estado inválido', 'error')
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    ticket = query_db('SELECT * FROM tickets WHERE id = ?', [ticket_id], one=True)
    if not ticket:
        flash('Ticket no encontrado', 'error')
        return redirect(url_for('list_tickets'))
    
    execute_db('UPDATE tickets SET estado = ? WHERE id = ?', [nuevo_estado, ticket_id])
    flash(f'Estado actualizado a "{nuevo_estado}"', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/ticket/<int:ticket_id>/add_comment', methods=['POST'])
def add_comment(ticket_id):
    """Agregar una nota o comentario a un ticket."""
    contenido = request.form.get('contenido', '').strip()
    autor = request.form.get('autor', '').strip()
    
    if not contenido:
        flash('El comentario no puede estar vacío', 'error')
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    if not autor:
        flash('El nombre del autor es obligatorio', 'error')
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    ticket = query_db('SELECT * FROM tickets WHERE id = ?', [ticket_id], one=True)
    if not ticket:
        flash('Ticket no encontrado', 'error')
        return redirect(url_for('list_tickets'))
    
    fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    execute_db(
        'INSERT INTO comments (ticket_id, contenido, autor, fecha_creacion) VALUES (?, ?, ?, ?)',
        [ticket_id, contenido, autor, fecha_creacion]
    )
    
    flash('Comentario agregado exitosamente', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket(ticket_id):
    """Eliminar un ticket (opcional, para administración)."""
    ticket = query_db('SELECT * FROM tickets WHERE id = ?', [ticket_id], one=True)
    if not ticket:
        flash('Ticket no encontrado', 'error')
        return redirect(url_for('list_tickets'))
    
    # Eliminar comentarios asociados primero (por integridad referencial)
    execute_db('DELETE FROM comments WHERE ticket_id = ?', [ticket_id])
    # Eliminar el ticket
    execute_db('DELETE FROM tickets WHERE id = ?', [ticket_id])
    
    flash(f'Ticket #{ticket_id} eliminado', 'success')
    return redirect(url_for('list_tickets'))


# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == '__main__':
    # Crear la base de datos si no existe
    if not os.path.exists(DATABASE):
        init_db()
        print(f'Base de datos {DATABASE} creada e inicializada.')
    
    print('Iniciando servidor en http://127.0.0.1:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
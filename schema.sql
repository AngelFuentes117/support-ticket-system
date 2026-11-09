-- Esquema de base de datos para el Sistema de Tickets de Soporte Técnico
-- Base de datos: tickets.db

-- Tabla principal de tickets
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    reporter_name TEXT NOT NULL,
    categoria TEXT NOT NULL CHECK (categoria IN ('Hardware', 'Software', 'Red', 'Impresora', 'Otro')),
    prioridad TEXT NOT NULL CHECK (prioridad IN ('Baja', 'Media', 'Alta')),
    estado TEXT NOT NULL DEFAULT 'Abierto' CHECK (estado IN ('Abierto', 'En proceso', 'Cerrado')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de comentarios/notas en los tickets
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    contenido TEXT NOT NULL,
    autor TEXT NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento de consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_tickets_estado ON tickets(estado);
CREATE INDEX IF NOT EXISTS idx_tickets_prioridad ON tickets(prioridad);
CREATE INDEX IF NOT EXISTS idx_tickets_categoria ON tickets(categoria);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha_creacion ON tickets(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_comments_ticket_id ON comments(ticket_id);
CREATE INDEX IF NOT EXISTS idx_comments_fecha_creacion ON comments(fecha_creacion ASC);

-- Trigger para actualizar fecha_actualizacion automáticamente
CREATE TRIGGER IF NOT EXISTS update_ticket_timestamp
AFTER UPDATE ON tickets
BEGIN
    UPDATE tickets SET fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
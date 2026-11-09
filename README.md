# Support Ticket System

A simple yet complete technical support ticket system built with **Flask** and **SQLite**. Features a clean Spanish-language web interface for creating, managing, and tracking support tickets.

## Features

- **Create Tickets** – Title, description, reporter name, category (Hardware, Software, Network, Printer, Other), and priority (Low, Medium, High)
- **List Tickets** – Filter by status (Open, In Progress, Closed) and priority
- **Ticket Details** – View full ticket information, change status, add comments/notes
- **Dashboard** – Overview with ticket counts by status
- **Data Persistence** – SQLite database (`tickets.db`) with proper schema, indexes, and triggers
- **Clean Spanish UI** – Responsive Bootstrap 5 interface

## Requirements

- Python 3.8+
- Flask 3.0+

## Installation

1. **Clone or download** this project to a local folder
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python app.py
```

The application will:
- Create the SQLite database (`tickets.db`) on first run
- Initialize the database schema
- Start the development server on **http://127.0.0.1:5000**

Open your browser and navigate to: **http://127.0.0.1:5000**

## Project Structure

```
support-ticket-system/
├── app.py              # Main Flask application
├── schema.sql          # Database schema
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── templates/          # Jinja2 templates
    ├── base.html       # Base template with navigation
    ├── index.html      # Dashboard with statistics
    ├── tickets.html    # Ticket list with filters
    ├── ticket_detail.html  # Ticket detail + comments
    └── create_ticket.html  # Create ticket form
```

## Usage Guide

### Creating a Ticket
1. Click **"Nuevo Ticket"** in the navigation or dashboard
2. Fill in all required fields:
   - **Título**: Brief, descriptive summary
   - **Descripción**: Detailed problem description
   - **Tu nombre**: Your name
   - **Categoría**: Hardware, Software, Red, Impresora, or Otro
   - **Prioridad**: Alta, Media, or Baja
3. Click **"Crear Ticket"**

### Managing Tickets
- **Dashboard** (`/`): View statistics and recent tickets
- **All Tickets** (`/tickets`): Filter by status and priority
- **Ticket Detail** (`/ticket/<id>`): View details, change status, add comments

### Status Workflow
Tickets follow this workflow:
```
Abierto → En proceso → Cerrado
```
You can change status at any time from the ticket detail page.

## Database Schema

The system uses two main tables:

**tickets**
- `id` – Primary key
- `titulo` – Ticket title
- `descripcion` – Detailed description
- `reporter_name` – Person who reported
- `categoria` – Hardware, Software, Red, Impresora, Otro
- `prioridad` – Baja, Media, Alta
- `estado` – Abierto, En proceso, Cerrado
- `fecha_creacion` – Creation timestamp
- `fecha_actualizacion` – Last update timestamp (auto-updated via trigger)

**comments**
- `id` – Primary key
- `ticket_id` – Foreign key to tickets
- `contenido` – Comment text
- `autor` – Comment author
- `fecha_creacion` – Comment timestamp

Indexes and a trigger for auto-updating timestamps are included for performance.

## Security Notes

⚠️ **This is a development/demo application.** For production use:
- Change the `secret_key` in `app.py`
- Use a production WSGI server (Gunicorn, uWSGI)
- Enable HTTPS
- Add authentication/authorization
- Use environment variables for configuration
- Consider PostgreSQL/MySQL instead of SQLite for concurrent access

## License

This project is open source and available for educational and commercial use.

---

**Enjoy using the Support Ticket System!** 🎫
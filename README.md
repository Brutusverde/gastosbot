# 💸 PartyCash

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Fly.io](https://img.shields.io/badge/Deployed%20on-Fly.io-purple)
![License](https://img.shields.io/badge/License-MIT-green)

Bot de Telegram para gestionar gastos compartidos en un piso. Permite registrar gastos, calcular deudas automáticamente entre compañeros y obtener resúmenes mensuales por categoría.

## 🤖 Pruébalo

Busca **@gastospiso_bot** en Telegram y escribe `/start` para probarlo.

---

## ✨ Características

- Registro automático de usuarios al usar cualquier comando
- Sistema de grupos con código de invitación
- Cálculo automático de deudas al registrar un gasto, dividido entre los miembros del grupo
- Resumen mensual con total gastado, deudas pendientes y desglose por categoría
- Historial de los últimos 10 gastos del grupo
- Comandos de administración para el creador del grupo
- Logging estructurado con registro persistente en producción
- Soporte en chat privado con selector de grupo por botones inline
- Desplegado en producción con almacenamiento persistente en Fly.io

---

## 🛠️ Comandos

| Comando | Descripción |
|---|---|
| `/start` | Registrarte en el bot |
| `/gasto [cantidad] [descripción] [categoría]` | Registrar un gasto compartido |
| `/deudas` | Ver todas las deudas del grupo |
| `/misdeudas` | Ver solo tus deudas pendientes |
| `/saldar [@usuario]` | Saldar una deuda con un compañero |
| `/historial` | Ver los últimos 10 gastos del grupo |
| `/resumen` | Ver tu resumen del mes |
| `/crear_grupo [nombre]` | Crear un nuevo grupo |
| `/unirse [código]` | Unirse a un grupo con un código |
| `/misgrupos` | Ver los grupos a los que perteneces |
| `/reiniciar` | Reiniciar gastos y deudas del grupo (solo admin) |
| `/eliminar_grupo` | Eliminar el grupo (solo admin) |

---

## 🔧 Tecnologías

- Python 3.12
- python-telegram-bot 20.3
- SQLite
- Pandas
- python-dotenv
- Desplegado en Fly.io con volumen persistente

---

## 📁 Estructura del proyecto

```
PartyCash/
├── bot.py              # Punto de entrada, inicializa y arranca el bot
├── database.py         # Funciones de acceso a la base de datos SQLite
├── handlers.py         # Handlers de cada comando de Telegram
├── logica.py           # Lógica de negocio y cálculo de deudas
├── conftest.py         # Fixtures compartidas para los tests
├── test_logica.py      # Tests para logica.py
├── test_database.py    # Tests para database.py
├── requirements.txt    # Dependencias del proyecto
├── Dockerfile          # Configuración para despliegue con Docker
├── fly.toml            # Configuración de despliegue en Fly.io
└── README.md
```

---

## 🚀 Instalación local

1. Clona el repositorio
2. Crea un entorno virtual e instala las dependencias:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Crea un archivo `.env` en la raíz del proyecto con tu token de BotFather:

```
TOKEN=tu_token_aquí
```

4. Ejecuta el bot:

```bash
python bot.py
```

---

## 🗺️ Roadmap

### ✅ Completado
- Registro de usuarios
- Registro de gastos con categorías
- Cálculo automático de deudas
- Historial de gastos
- Resumen mensual
- Sistema de grupos con código de invitación
- Soporte en chat privado con selector de grupo por botones inline
- Comandos de administración (reiniciar, eliminar grupo)
- Mejoras visuales con Markdown y emojis
- Logging estructurado con registro persistente
- Despliegue en Fly.io con volumen persistente
- Tests con pytest

### 📋 Planificado
- Mejoras en gastos (editar, eliminar, splits personalizados)
- Recordatorios automáticos de deudas
- Lista de la compra compartida
- Tareas del hogar
- Exportar resumen en PDF

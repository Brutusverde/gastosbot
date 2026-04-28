# 🏠 GastosBot

Bot de Telegram para gestionar gastos compartidos en un piso. Permite registrar gastos, calcular deudas automáticamente entre compañeros y obtener resúmenes mensuales por categoría.

---

## ✨ Comandos

| Comando | Descripción |
|---|---|
| `/start` | Registrarte en el bot |
| `/gasto [cantidad] [descripción] [categoría]` | Registrar un gasto compartido |
| `/deudas` | Ver todas las deudas del grupo |
| `/misdeudas` | Ver solo tus deudas pendientes |
| `/saldar [@usuario]` | Saldar una deuda con un compañero |
| `/historial` | Ver los últimos 10 gastos del grupo |
| `/resumen` | Ver tu resumen del mes |

---

## 🛠️ Tecnologías

- Python 3.12
- python-telegram-bot 20.3
- SQLite
- Pandas

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

## 💡 Características

- Registro automático de usuarios al hacer `/start`
- Requiere username de Telegram para garantizar la identificación de cada usuario
- Cálculo automático de deudas al registrar un gasto, dividido entre todos los miembros del grupo
- Resumen mensual con total gastado, deudas pendientes y desglose por categoría
- Historial de los últimos 10 gastos del grupo

---

## 📁 Estructura del proyecto

```
gastosbot/
├── bot.py              # Punto de entrada, inicializa y arranca el bot
├── database.py         # Funciones de acceso a la base de datos SQLite
├── handlers.py         # Handlers de cada comando de Telegram
├── calculadora.py      # Lógica de cálculo y reparto de deudas
├── requirements.txt    # Dependencias del proyecto
└── README.md
```
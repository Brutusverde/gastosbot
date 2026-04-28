from telegram.ext import ApplicationBuilder, CommandHandler
from database import inicializar_db
import handlers
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

def main():
    inicializar_db()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("gasto", handlers.gasto))
    app.add_handler(CommandHandler("deudas", handlers.deudas))
    app.add_handler(CommandHandler("misdeudas", handlers.misdeudas))
    app.add_handler(CommandHandler("historial", handlers.historial))
    app.add_handler(CommandHandler("saldar", handlers.saldar))
    app.add_handler(CommandHandler("resumen", handlers.resumen))
    
    app.run_polling()

if __name__ == "__main__":
    main()
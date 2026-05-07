from database import obtener_gastos, obtener_deudas, registrar_usuario, registrar_gasto, saldar_deuda, obtener_deudas_usuario, obtener_id_por_username, obtener_usuario_en_grupo, obtener_grupos_usuario
from database import obtener_total_gastado, obtener_total_deuda, obtener_total_a_cobrar, obtener_gastos_por_categoria, crear_grupo, añadir_usuario_grupo, obtener_grupo, obtener_grupo_por_codigo
from database import usuario_es_admin, reiniciar_grupo, eliminar_grupo
from logica import calcular_deudas, crear_codigo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


import logging
logger = logging.getLogger(__name__)


async def start(update, context):
    """Registra a un usuario en la base de datos. Devuelve un mensaje distinto si el usuario ya existía en la base de datos con anterioridad"""
    if update.message.from_user.username is None:
        await update.message.reply_text("⚠️ Necesitas un nombre de usuario de Telegram (@username) para usar el bot.")
        return

    registro_usuario = registrar_usuario(update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.username)
    if registro_usuario == 0:
        await update.message.reply_text(f"¡Bienvenido de nuevo, {update.message.from_user.first_name}!")
    else:
        await update.message.reply_text("Bienvenido! Tu usuario ha sido registrado")

async def verificar_usuario(update):
    """Registra un usuario en la base de datos de forma silenciosa. Solo devuelve un mensaje si la creación ha fallado"""
    if update.message.from_user.username is None:
        await update.message.reply_text("⚠️ Necesitas un nombre de usuario de Telegram (@username) para usar el bot.")
        return False
    else:
        registrar_usuario(update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.username)
        return True

async def gasto(update, context, group_id = None):
    """Recoje un gasto y crea las correspondientes deudas. Controla que el usuario pertenezca a un grupo y valida que se han proporcionado los argumentos necesarios"""

    if not await verificar_usuario(update):
        return

    gasto_usuario = context.args
    id = update.message.from_user.id

    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "gasto")
            return
        group_id = grupo[0]

    if len(gasto_usuario) < 2:
        await update.message.reply_text("⚠️ Uso correcto: /gasto [cantidad] [descripción] [categoría opcional]")
        return
    

    if len(gasto_usuario) == 2:
        registrar_gasto(id, float(gasto_usuario[0]), gasto_usuario[1])
        
    else:
        registrar_gasto(id, float(gasto_usuario[0]), gasto_usuario[1], gasto_usuario[2])

    logger.info(f"Usuario {update.message.from_user.username} ha registrado un gasto de {gasto_usuario[0]}€ en {gasto_usuario[1]}")

    calcular_deudas(id, float(gasto_usuario[0]), group_id)

    await update.message.reply_text(f"✅ Gasto de *{gasto_usuario[0]}€* en *{gasto_usuario[1]}* registrado correctamente", parse_mode='Markdown')

async def deudas(update, context, group_id = None):
    """Muestra todas las deudas del grupo que no han sido saldadas. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "deudas")
            return
        group_id = grupo[0]


    deudas = obtener_deudas(group_id)
    mensaje = "Las deudas del grupo son:\n"

    if len(deudas) == 0:
        await update.message.reply_text("✅ No hay deudas pendientes en el grupo")
    else:
        mensaje = "💸 *Deudas del grupo*\n\n"
        
        for elemento in deudas:
            mensaje += f"👤 *{elemento[2]}* le debe *{elemento[5]}€* a *{elemento[4]}*\n"
        await update.message.reply_text(mensaje, parse_mode='Markdown')

async def misdeudas(update, context, group_id = None):
    """Muestra las deudas no pagadas de un usuario perteneciente a un grupo. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "misdeudas")
            return
        group_id = grupo[0]
    
    misdeudas = obtener_deudas_usuario(update.message.from_user.id, group_id)
    mensaje = "Tus deudas son:\n"

    if len(misdeudas) == 0:
        await update.message.reply_text("✅ No tienes deudas pendientes")
    else:
        mensaje = "💳 *Tus deudas pendientes*\n\n"
        for elemento in misdeudas:
            mensaje += f"• Le debes *{elemento[5]}€* a *{elemento[4]}*\n"
        await update.message.reply_text(mensaje, parse_mode='Markdown')

async def historial(update, context, group_id = None):
    """Muestra un historial de los últimos gastos del grupo. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "historial")
            return
        group_id = grupo[0]
    
    gastos = obtener_gastos(group_id)
    mensaje = "Los últimos gastos son:\n"

    if len(gastos) == 0:
        await update.message.reply_text("📋 Aún no hay ningún gasto registrado")
    else:
        mensaje = "📋 *Últimos gastos del grupo*\n\n"
        for gasto in gastos[:10]:
            mensaje += f"🛒 *{gasto[1]}* gastó *{gasto[2]}€* en {gasto[3]} el {gasto[5]}\n" 
        await update.message.reply_text(mensaje, parse_mode='Markdown')


async def saldar(update, context, group_id = None):
    """Salda una deuda utilizando el nombre de usuario de telegram del deudor. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Uso correcto: /saldar [@usuario]")
        return
    
    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "saldar")
            return
        group_id = grupo[0]
    
    usuario = context.args[0]
    acreedor_id = obtener_id_por_username(usuario)
    comprobacion_deuda = obtener_deudas_usuario(update.message.from_user.id, group_id)

    if not comprobacion_deuda:
        await update.message.reply_text("⚠️ No tienes deudas pendientes que saldar.")
        return
    
    if acreedor_id is None:
        await update.message.reply_text("⚠️ No encontré ese usuario. Asegúrate de que esté registrado en el bot.")
        return
    
    comprobacion_deuda_correcta = saldar_deuda(update.message.from_user.id, acreedor_id[0])
    
    if not comprobacion_deuda_correcta:
        await update.message.reply_text("No se ha encontrado la deuda que quieres saldar")
        return

    await update.message.reply_text(f"✅ *{update.message.from_user.first_name}* ha saldado su deuda con *{usuario}*", parse_mode='Markdown')
    logger.info(f"Usuario {update.message.from_user.username} ha saldado su deuda con {usuario}")


async def resumen(update, context):
    """Devuelve un resumen mensual de gastos totales, deudas y gastos por categorías de un usuario. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return

    id = update.message.from_user.id
    mensaje_categorias = ""

    gasto_total = obtener_total_gastado(id)
    deuda_total = obtener_total_deuda(id)
    total_a_cobrar = obtener_total_a_cobrar(id)
    gastos_categoria = obtener_gastos_por_categoria(id)

    for gasto in gastos_categoria:
        mensaje_categorias += f"• *{gasto[1]}*: {gasto[0]}€\n"

    await update.message.reply_text(
    f"📊 *Resumen de {update.message.from_user.first_name}*\n\n"
    f"💰 Total gastado este mes: *{gasto_total[0] or 0}€*\n"
    f"📉 Total deudas: *{deuda_total[0] or 0}€*\n"
    f"📈 Te deben: *{total_a_cobrar[0] or 0}€*\n\n"
    f"*Gastos por categoría*\n"
    f"{mensaje_categorias}",
    parse_mode='Markdown')
    
async def handler_crear_grupo(update, context):
    """Crea un grupo en la base de datos y añade al creador como administrador de este. Genera un código de invitación y comprueba que sea único"""
    if not await verificar_usuario(update):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Uso correcto: /crear_grupo [nombre]")
        return
    
    nombre_grupo = " ".join(context.args)
    
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if obtener_grupo(chat_id) is not None:
        await update.message.reply_text(f"Error al crear tu grupo. Ya existe un grupo en este chat")
        return
    
    codigo = crear_codigo()

    crear_grupo(nombre_grupo, codigo, chat_id)
    grupo = obtener_grupo(chat_id)

    añadir_usuario_grupo(user_id, grupo[0], 1)
    await update.message.reply_text(f"✅ Grupo *{grupo[1]}* creado correctamente\n\n🔑 Código de invitación: `{codigo}`", parse_mode='Markdown')
    logger.info(f"Usuario {update.message.from_user.username} ha creado un grupo {grupo[0]} con código de invitación {codigo}")

async def handler_unirse (update, context):
    """Añade a un usuario a un grupo mediante el código de invitación. Comprueba si este usuario ya se había unido antes y manda un mensaje diferente si es así"""
    if not await verificar_usuario(update):
        return
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Uso correcto: /unirse [código]")
        return
    
    id = update.message.from_user.id
    
    grupo_unirse = obtener_grupo_por_codigo(context.args[0])

    if grupo_unirse is None:
        await update.message.reply_text(f"El grupo al que intentas unirte no existe")
        return

    usuario_en_grupo = obtener_usuario_en_grupo(id, grupo_unirse[0])

    if usuario_en_grupo is not None:
        await update.message.reply_text(f"Ya perteneces a este grupo")
        return

    añadir_usuario_grupo(id,grupo_unirse[0], 0)
    await update.message.reply_text(f"✅ *{update.message.from_user.first_name}* se ha unido al grupo *{grupo_unirse[1]}*", parse_mode='Markdown')
    logger.info(f"Usuario {update.message.from_user.username} se ha unido al grupo {grupo_unirse[0]}")


async def misgrupos(update, context):
    """Muestra los grupos a los que pertenece un usuario y si es admin de alguno"""
    if not await verificar_usuario(update):
        return
    
    grupos = obtener_grupos_usuario(update.message.from_user.id)
    mensaje = "Grupos en los que participas:\n"

    if len(grupos) == 0:
        await update.message.reply_text("⚠️ No perteneces a ningun grupo")
    else:
        mensaje = "👥 *Grupos en los que participas:*\n\n"
        for elemento in grupos:
            if elemento[2] == True:
                mensaje += f"• *{elemento[1]}* - *Eres admin*\n"
            else:
                mensaje += f"• *{elemento[1]}* - *No eres admin*\n"
        await update.message.reply_text(mensaje, parse_mode='Markdown')

async def reiniciar(update, context, group_id = None):
    """Borra los gastos y deudas de un grupo si el usuario es administrador"""
    if not await verificar_usuario(update):
        return
    
    id = update.message.from_user.id
    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "reiniciar")
            return
        group_id = grupo[0]
    
    comprobar_admin = usuario_es_admin(id, group_id)

    if comprobar_admin == (1,):
        reiniciar_grupo(group_id)
        await update.message.reply_text("✅ Se han eliminado todos los gastos / deudas del grupo")
        logger.info(f"Usuario {update.message.from_user.username} ha reiniciado el grupo {group_id}")
    else:
        await update.message.reply_text("⚠️ No eres administrador del grupo")

async def eliminar(update, context, group_id = None):
    """Elimina un grupo si el usuario es administrador"""
    if not await verificar_usuario(update):
        return
    
    id = update.message.from_user.id
    if group_id is None: 
        chat_id = update.message.chat_id

        grupo = obtener_grupo(chat_id)
        if grupo is None:
            await mostrar_selector_grupo(update, context, "eliminar")
            return
        group_id = grupo[0]
    
    comprobar_admin = usuario_es_admin(id, group_id)

    if comprobar_admin == (1,):
        eliminar_grupo(group_id)
        await update.message.reply_text("✅ Se ha eliminado el grupo")
        logger.info(f"Usuario {update.message.from_user.username} ha eliminado el grupo {group_id}")
    else:
        await update.message.reply_text("⚠️ No eres administrador del grupo")


async def mostrar_selector_grupo(update, context, comando):
    """Muestra un selector de grupos al usuario para ejecutar un comando específico. Controla que el usuario pertenezca a algún grupo y muestra un mensaje distinto si no es así"""
    if not await verificar_usuario(update):
        return
    
    id = update.message.from_user.id
    grupos = obtener_grupos_usuario(id)

    if len(grupos) == 0:
        await update.message.reply_text("⚠️ No perteneces a ningun grupo")
        return
    
    botones = []
    for grupo in grupos:
        botones.append([InlineKeyboardButton(grupo[1], callback_data=f"{comando}:{grupo[0]}")])

    teclado = InlineKeyboardMarkup(botones)
    await update.message.reply_text("¿En qué grupo quieres ejecutar este comando?", reply_markup=teclado)


def es_chat_privado(chat_id):
    """Devuelve si un chat es privado o si es un grupo"""
    return obtener_grupo(chat_id) is None

comandos = {
    "deudas": deudas,
    "misdeudas": misdeudas,
    "historial": historial,
    "gasto": gasto,
    "saldar": saldar,
    "reiniciar": reiniciar,
    "eliminar": eliminar
}

async def procesar_seleccion_grupo(update, context):
    await update.callback_query.answer()
    data = update.callback_query.data
    comando, group_id = data.split(":")

    await comandos[comando](update, context, int(group_id))



from database import obtener_gastos, obtener_deudas, registrar_usuario, registrar_gasto, saldar_deuda, obtener_deudas_usuario, obtener_id_por_username, obtener_usuario_en_grupo
from database import obtener_total_gastado, obtener_total_deuda, obtener_total_a_cobrar, obtener_gastos_por_categoria, crear_grupo, añadir_usuario_grupo, obtener_grupo, obtener_grupo_por_codigo
from logica import calcular_deudas, crear_codigo


async def start(update, context):
    """Registra al usuario en la base de datos si es su primera vez"""
    if update.message.from_user.username is None:
        await update.message.reply_text("Para poder registrate, debes tener un nombre de usuario de Telegram (@username)")
        return

    registro_usuario = registrar_usuario(update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.username)
    if registro_usuario == 0:
        await update.message.reply_text(f"¡Bienvenido de nuevo, {update.message.from_user.first_name}!")
    else:
        await update.message.reply_text("Bienvenido! Tu usuario ha sido registrado")

async def verificar_usuario(update):
    """Registra al usuario en la base de datos si es su primera vez"""
    if update.message.from_user.username is None:
        await update.message.reply_text("Para poder registrate, debes tener un nombre de usuario de Telegram (@username)")
        return False
    else:
        registrar_usuario(update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.username)
        return True

async def gasto(update, context):
    """Recoje un gasto y crea las correspondientes deudas"""

    if not await verificar_usuario(update):
        return

    gasto_usuario = context.args
    id = update.message.from_user.id
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if len(gasto_usuario) < 2:
        await update.message.reply_text("Error al añadir tu gasto. Uso correcto: /gasto [cantidad] [descripción] [categoría opcional]")
        return
    
    if group_id is None:
        await update.message.reply_text("Error al añadir tu gasto. No perteneces a un grupo. Crea uno o únete")
        return

    if len(gasto_usuario) == 2:
        registrar_gasto(id, float(gasto_usuario[0]), gasto_usuario[1])
    else:
        registrar_gasto(id, float(gasto_usuario[0]), gasto_usuario[1], gasto_usuario[2])

    calcular_deudas(id, float(gasto_usuario[0]), group_id[0])

    await update.message.reply_text(f"Tu gasto de {gasto_usuario[0]} en {gasto_usuario[1]} se ha registrado")

async def deudas(update, context):
    """Muestra todas las deudas del grupo"""
    if not await verificar_usuario(update):
        return
    
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if group_id is None:
        await update.message.reply_text("Error al buscar tus deudas. No perteneces a un grupo. Crea uno o únete")
        return

    deudas = obtener_deudas(group_id[0])
    mensaje = "Las deudas del grupo son:\n"
    for elemento in deudas:
        mensaje += f"{elemento[2]} le debe {elemento[5]}€ a {elemento[4]}\n"
    await update.message.reply_text(mensaje)

async def misdeudas(update, context):
    """Muestra las deudas concretas del usuario"""
    if not await verificar_usuario(update):
        return

    misdeudas = obtener_deudas_usuario(update.message.from_user.id)
    mensaje = "Tus deudas son:\n"
    for elemento in misdeudas:
        mensaje += f"Le debes {elemento[5]}€ a {elemento[4]}\n"
    await update.message.reply_text(mensaje)

async def historial(update, context):
    """Muestra un historial de los ultimos gastos del grupo"""
    if not await verificar_usuario(update):
        return
    
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if group_id is None:
        await update.message.reply_text("Error al mostrar tu historial. No perteneces a un grupo. Crea uno o únete")
        return
    
    gastos = obtener_gastos(group_id[0])
    mensaje = "Los últimos gastos son:\n"

    for gasto in gastos[:10]:
        mensaje += f"{gasto[1]} ha gastado {gasto[2]}€ en {gasto[3]} el día {gasto[5]}\n"
    await update.message.reply_text(mensaje)    


async def saldar(update, context):
    """Salda una deuda de un usuario"""
    if not await verificar_usuario(update):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Error al saldar tu deuda. Uso correcto: /saldar [@usuario]")
        return
    
    usuario = context.args[0]
    acreedor_id = obtener_id_por_username(usuario)
    comprobacion_deuda = obtener_deudas_usuario(update.message.from_user.id)

    if not comprobacion_deuda:
        await update.message.reply_text("No se han encontrado deudas en tu usuario")
        return
    
    if acreedor_id is None:
        await update.message.reply_text("No encontré ese usuario. Asegúrate de que esté registrado en el bot.")
        return
    
    comprobacion_deuda_correcta = saldar_deuda(update.message.from_user.id, acreedor_id[0])
    
    if not comprobacion_deuda_correcta:
        await update.message.reply_text("No se ha encontrado la deuda que quieres saldar")
        return

    await update.message.reply_text(f"{update.message.from_user.first_name} ha saldado su deuda con {usuario} ")


async def resumen(update, context):
    """Obtener un resumen del mes de un usuario"""
    if not await verificar_usuario(update):
        return

    id = update.message.from_user.id
    mensaje_categorias = ""

    gasto_total = obtener_total_gastado(id)
    deuda_total = obtener_total_deuda(id)
    total_a_cobrar = obtener_total_a_cobrar(id)
    gastos_categoria = obtener_gastos_por_categoria(id)

    for gasto in gastos_categoria:
        mensaje_categorias += f"Has gastado {gasto[0]}€ en {gasto[1]}\n"

    await update.message.reply_text(f"""*{update.message.from_user.first_name}, aquí tienes tu resumen del mes:*

Has tenido un gasto total de {gasto_total[0] or 0}€
Tienes una deuda total de {deuda_total[0] or 0}€
Te deben {total_a_cobrar[0] or 0}€

*Tus gastos por categoría*
{mensaje_categorias}""",  parse_mode='Markdown')
    
async def handler_crear_grupo(update, context):
    """Crea el grupo en el bot"""
    if not await verificar_usuario(update):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(f"Error al crear tu grupo. Uso correcto: /crear_grupo [nombre]")
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
    await update.message.reply_text(f"El código para el grupo {grupo[1]} es {codigo}")

async def handler_unirse (update, context):
    """Añade a un usuario a un grupo"""
    if not await verificar_usuario(update):
        return
    if len(context.args) < 1:
        await update.message.reply_text(f"Necesitas un código para unirte a un grupo. Uso correcto: /unirse [código]")
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
    await update.message.reply_text(f"{update.message.from_user.first_name}, se te ha añadido al grupo {grupo_unirse[1]}")

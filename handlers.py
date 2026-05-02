from database import obtener_gastos, obtener_deudas, registrar_usuario, registrar_gasto, saldar_deuda, obtener_deudas_usuario, obtener_id_por_username, obtener_usuario_en_grupo
from database import obtener_total_gastado, obtener_total_deuda, obtener_total_a_cobrar, obtener_gastos_por_categoria, crear_grupo, añadir_usuario_grupo, obtener_grupo, obtener_grupo_por_codigo
from logica import calcular_deudas, crear_codigo


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

async def gasto(update, context):
    """Recoje un gasto y crea las correspondientes deudas. Controla que el usuario pertenezca a un grupo y valida que se han proporcionado los argumentos necesarios"""

    if not await verificar_usuario(update):
        return

    gasto_usuario = context.args
    id = update.message.from_user.id
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if len(gasto_usuario) < 2:
        await update.message.reply_text("⚠️ Uso correcto: /gasto [cantidad] [descripción] [categoría opcional]")
        return
    
    if group_id is None:
        await update.message.reply_text("⚠️ No perteneces a ningún grupo. Usa /crear_grupo o /unirse.")
        return

    if len(gasto_usuario) == 2:
        registrar_gasto(id, float(gasto_usuario[0]), gasto_usuario[1])
    else:
        registrar_gasto(id, float(gasto_usuario[0]), gasto_usuario[1], gasto_usuario[2])

    calcular_deudas(id, float(gasto_usuario[0]), group_id[0])

    await update.message.reply_text(f"✅ Gasto de *{gasto_usuario[0]}€* en *{gasto_usuario[1]}* registrado correctamente", parse_mode='Markdown')

async def deudas(update, context):
    """Muestra todas las deudas del grupo que no han sido saldadas. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if group_id is None:
        await update.message.reply_text("⚠️ No perteneces a ningún grupo. Usa /crear_grupo o /unirse.")
        return

    deudas = obtener_deudas(group_id[0])
    mensaje = "Las deudas del grupo son:\n"

    if len(deudas) == 0:
        await update.message.reply_text("✅ No hay deudas pendientes en el grupo")
    else:
        mensaje = "💸 *Deudas del grupo*\n\n"
        
        for elemento in deudas:
            mensaje += f"👤 *{elemento[2]}* le debe *{elemento[5]}€* a *{elemento[4]}*\n"
        await update.message.reply_text(mensaje, parse_mode='Markdown')

async def misdeudas(update, context):
    """Muestra las deudas no pagadas de un usuario perteneciente a un grupo. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return

    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if group_id is None:
        await update.message.reply_text("⚠️ No perteneces a ningún grupo. Usa /crear_grupo o /unirse.")
        return
    
    misdeudas = obtener_deudas_usuario(update.message.from_user.id, group_id[0])
    mensaje = "Tus deudas son:\n"

    if len(misdeudas) == 0:
        await update.message.reply_text("✅ No tienes deudas pendientes")
    else:
        mensaje = "💳 *Tus deudas pendientes*\n\n"
        for elemento in misdeudas:
            mensaje += f"• Le debes *{elemento[5]}€* a *{elemento[4]}*\n"
        await update.message.reply_text(mensaje, parse_mode='Markdown')

async def historial(update, context):
    """Muestra un historial de los últimos gastos del grupo. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if group_id is None:
        await update.message.reply_text("⚠️ No perteneces a ningún grupo. Usa /crear_grupo o /unirse.")
        return
    
    gastos = obtener_gastos(group_id[0])
    mensaje = "Los últimos gastos son:\n"

    if len(gastos) == 0:
        await update.message.reply_text("📋 Aún no hay ningún gasto registrado")
    else:
        mensaje = "📋 *Últimos gastos del grupo*\n\n"
        for gasto in gastos[:10]:
            mensaje += f"🛒 *{gasto[1]}* gastó *{gasto[2]}€* en {gasto[3]} el {gasto[5]}\n" 
        await update.message.reply_text(mensaje, parse_mode='Markdown')


async def saldar(update, context):
    """Salda una deuda utilizando el nombre de usuario de telegram del deudor. Controla que el usuario pertenezca a un grupo"""
    if not await verificar_usuario(update):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("⚠️ Uso correcto: /saldar [@usuario]")
        return
    
    chat_id = update.message.chat_id
    group_id =  obtener_grupo(chat_id)

    if group_id is None:
        await update.message.reply_text("⚠️ No perteneces a ningún grupo. Usa /crear_grupo o /unirse.")
        return
    
    usuario = context.args[0]
    acreedor_id = obtener_id_por_username(usuario)
    comprobacion_deuda = obtener_deudas_usuario(update.message.from_user.id, group_id[0])

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

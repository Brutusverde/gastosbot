import sqlite3
from datetime import datetime

DB_NAME = "/data/gastos.db"


def inicializar_db():
    """Inicializa la base de datos y crea las tablas si no existen"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute('''               
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            username TEXT
        )
        ''')

        cursor.execute('''               
        CREATE TABLE IF NOT EXISTS gastos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pagador_id INTEGER NOT NULL,
            cantidad REAL NOT NULL,
            descripcion TEXT,
            categoria TEXT DEFAULT 'general',
            fecha TEXT NOT NULL,
            FOREIGN KEY (pagador_id) REFERENCES usuarios(id)
        )
        ''')

        cursor.execute('''               
        CREATE TABLE IF NOT EXISTS deudas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deudor_id INTEGER NOT NULL,
            acreedor_id INTEGER NOT NULL,
            cantidad REAL NOT NULL,
            saldada INTEGER DEFAULT 0,
            FOREIGN KEY (deudor_id) REFERENCES usuarios(id),
            FOREIGN KEY (acreedor_id) REFERENCES usuarios(id)
        )
        ''')

        cursor.execute('''               
        CREATE TABLE IF NOT EXISTS grupos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            codigo_invitacion TEXT NOT NULL,
            telegram_chat_id TEXT NOT NULL
        )
        ''')

        cursor.execute('''               
        CREATE TABLE IF NOT EXISTS user_groups(
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            es_admin INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES usuarios(id),
            FOREIGN KEY (group_id) REFERENCES grupos(id)
        )
        ''')
        conn.commit()

def registrar_usuario(id, nombre, username):
    """Registra un usuario en la base de datos. Devuelve 1 si es nuevo o 0 si ya existía"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute('INSERT OR IGNORE INTO usuarios (id, nombre, username) VALUES (?,?,?)', (id, nombre, username))
        conn.commit()
        return cursor.rowcount

def registrar_gasto(pagador_id, cantidad, descripcion, categoria="general"):
    """Registra un gasto en la base de datos. Guarda el id del pagador, la descripcion del gasto, la categoría y la fecha"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('INSERT INTO gastos (pagador_id, cantidad, descripcion, categoria, fecha) VALUES (?, ?, ?, ?, ?)', (pagador_id, cantidad, descripcion, categoria, fecha))
        conn.commit()

def registrar_deuda(deudor_id, acreedor_id, cantidad):
    """Registra una deuda en la base de datos. Guarda el id del deudor, el id del acreedor y la cantidad de la deuda"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO deudas (deudor_id, acreedor_id, cantidad) VALUES (?, ?, ?)', (deudor_id, acreedor_id, cantidad))
        conn.commit()

def obtener_usuarios():
    """Devuelve todos los usuarios de la base de datos"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        return usuarios
    
def obtener_id_por_username(username):
    """Devuelve el id de un usuario buscándolo en la base de datos mediante su username"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id
            FROM usuarios
            WHERE username = ?
        ''', (username,))
        username_id = cursor.fetchone()
        return username_id

def obtener_gastos(group_id):
    """Devuelve todos los gastos de un grupo y los ordena de más actual a más antiguo"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT gastos.id, usuarios.nombre, gastos.cantidad, gastos.descripcion, gastos.categoria, gastos.fecha
            FROM gastos
            JOIN usuarios ON usuarios.id = gastos.pagador_id
            JOIN user_groups as grupos ON grupos.user_id = gastos.pagador_id
            WHERE grupos.group_id = ?
            ORDER BY gastos.fecha DESC
        ''',(group_id,))
        gastos = cursor.fetchall()
        return gastos
    
def obtener_deudas(group_id):
    """Obtiene todas las deudas de un grupo y devuelve las que no han sido saldadas"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT deudas.id, deudas.deudor_id, usuario1.nombre, deudas.acreedor_id, usuario2.nombre, deudas.cantidad, grupos.group_id
            FROM deudas
            JOIN usuarios as usuario1 ON usuario1.id = deudas.deudor_id
            JOIN usuarios as usuario2 ON usuario2.id = deudas.acreedor_id
            JOIN user_groups as grupos ON grupos.user_id = deudas.deudor_id
            WHERE saldada = 0 AND grupos.group_id = ?
        ''', (group_id,))
        deudas = cursor.fetchall()
        return deudas
    
def obtener_deudas_usuario(usuario_id, group_id):
    """Obtiene las deudas individuales de un usuario en un grupo y devuelve las que no han sido saldadas"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT deudas.id, deudas.deudor_id, usuario1.nombre, deudas.acreedor_id, usuario2.nombre, deudas.cantidad
            FROM deudas
            JOIN usuarios as usuario1 ON usuario1.id = deudas.deudor_id
            JOIN usuarios as usuario2 ON usuario2.id = deudas.acreedor_id
            JOIN user_groups as grupos ON grupos.user_id = deudas.deudor_id
            WHERE saldada = 0 AND deudas.deudor_id = ? AND grupos.group_id = ?
        ''', (usuario_id, group_id))
        deudas_usuario = cursor.fetchall()
        return deudas_usuario
    
def saldar_deuda(deudor_id, acreedor_id):
    """Marca como saldada la deuda entre un deudor y un acreedor. Devuelve el número de filas afectadas"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE deudas 
                       SET saldada = 1
                       WHERE deudor_id = ? AND acreedor_id = ?
                       ''', (deudor_id, acreedor_id))
        conn.commit()
        return cursor.rowcount

def obtener_total_gastado(usuario_id):
    """Devuelve el gasto total de un usuario en el mes actual"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sum(cantidad)
            FROM gastos
            WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now') AND pagador_id = ?
        ''', (usuario_id,))
        total_gastado = cursor.fetchone()
        return total_gastado
    
def obtener_total_deuda(usuario_id):
    """Devuelve las deudas totales no saldadas de un usuario"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sum(cantidad)
            FROM deudas
            WHERE deudor_id = ? AND saldada = 0
        ''', (usuario_id,))
        total_deuda = cursor.fetchone()
        return total_deuda
    
def obtener_total_a_cobrar(usuario_id):
    """Devuelve la suma de las cantidades pendientes que se deben a un usuario"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sum(cantidad)
            FROM deudas
            WHERE acreedor_id = ? AND saldada = 0
        ''', (usuario_id,))
        total_a_cobrar = cursor.fetchone()
        return total_a_cobrar
    
def obtener_gastos_por_categoria(usuario_id):
    """Devuelve los gastos totales del mes actual  de un usuario separados por su categoría"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sum(cantidad), categoria
            FROM gastos
            WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now') AND pagador_id = ?
            GROUP BY categoria
        ''', (usuario_id,))
        gastos_categoria = cursor.fetchall()
        return gastos_categoria

def crear_grupo(nombre, codigo_invitacion, telegram_chat_id):
    """Crea un grupo y guarda su contraseña de invitación. Devuelve 1 si se ha creado y 0 si el grupo ya existía"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute('INSERT OR IGNORE INTO grupos (nombre, codigo_invitacion, telegram_chat_id) VALUES (?,?,?)', (nombre, codigo_invitacion, telegram_chat_id))
        conn.commit()
        return cursor.rowcount 

def añadir_usuario_grupo(user_id, group_id, es_admin):
    """Añade un usuario a un grupo. Si el usuario ya formaba parte del grupo, devuelve 0. Si no, devuelve 1"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute('INSERT OR IGNORE INTO user_groups (user_id, group_id, es_admin) VALUES (?,?,?)', (user_id, group_id, es_admin))
        conn.commit()
        return cursor.rowcount 

def obtener_grupo(chat_id):
    """Devuelve la información completa de un grupo utilizando el id del chat de telegram para buscarlo en la base de datos"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
            FROM grupos
            WHERE telegram_chat_id = ?
        ''', (chat_id,))

        grupos = cursor.fetchone()
        return grupos

def obtener_miembros_grupo(group_id):
    """Devuelve todos los usuarios pertenecientes a un grupo"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT usuarios.id, usuarios.nombre, usuarios.username, user_groups.group_id
            FROM user_groups
            JOIN usuarios ON usuarios.id = user_groups.user_id 
            WHERE user_groups.group_id = ?
        ''', (group_id,))
        miembros_grupo = cursor.fetchall()
        return miembros_grupo

def obtener_grupo_por_codigo(codigo):
    """Devuelve la información completa de un grupo utilizando el código de invitación para buscarlo en la base de datos"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
            FROM grupos
            WHERE codigo_invitacion = ?
        ''', (codigo,))

        codigo_grupo = cursor.fetchone()
        return codigo_grupo

def obtener_usuario_en_grupo(user_id, group_id):
    """Devuelve todos datos que relacionan a un usuario con el grupo al que pertenece"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
            FROM user_groups
            WHERE group_id = ? AND user_id = ?
        ''', (group_id, user_id))

        usuario_grupo = cursor.fetchone()
        return usuario_grupo
    
def obtener_grupos_usuario(user_id):
    """Devuelve todos los grupos a los que pertenece un usuario y si es administrador de alguno"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_groups.group_id, grupos.nombre, user_groups.es_admin
            FROM user_groups
            JOIN grupos ON grupos.id = user_groups.group_id 
            WHERE user_id = ?
        ''', (user_id,))

        grupos_usuario = cursor.fetchall()
        return grupos_usuario
    
def usuario_es_admin(user_id, group_id):
    """Comprueba si el usuario es administrador de un grupo"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT es_admin
            FROM user_groups
            WHERE user_id = ? AND group_id = ?
        ''', (user_id, group_id))

        es_admin = cursor.fetchone()
        return es_admin

def reiniciar_grupo(group_id):
    """Borra los gastos y deudas de un grupo si el usuario es administrador"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM gastos WHERE pagador_id IN (SELECT user_id FROM user_groups WHERE group_id = ?)', (group_id,))
        cursor.execute('DELETE FROM deudas WHERE deudor_id IN (SELECT user_id FROM user_groups WHERE group_id = ?)', (group_id,))
        conn.commit()
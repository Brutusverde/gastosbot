from database import obtener_usuarios, registrar_usuario, obtener_id_por_username, obtener_deudas, registrar_deuda, crear_grupo, obtener_grupo, añadir_usuario_grupo
from database import obtener_grupo_por_codigo, registrar_gasto, obtener_gastos, obtener_grupos_usuario, saldar_deuda, obtener_deudas_usuario

def test_obtener_usuarios(fixture_inicializar_db):
    """Comprueba que obtener usuario devuelve bien los datos de los usuarios """
    registrar_usuario(10, "Luis", "Luis123")
    usuarios = obtener_usuarios()

    assert usuarios[0][0] == 10 and usuarios[0][1] == "Luis" and usuarios[0][2] == "Luis123"

def test_obtener_id_por_username(fixture_inicializar_db):
    
    registrar_usuario(10, "Luis", "Luis123")
    id = obtener_id_por_username("Luis123")

    assert id[0] == 10

def test_obtener_deudas(fixture_inicializar_db):
    
    registrar_deuda(10, 2, 100)
    crear_grupo("Prueba", "10000000", "1")
    registrar_usuario(10, "Luis", "Luis123")
    registrar_usuario(2, "Manolo", "Manolo123")
    group_id = obtener_grupo_por_codigo(10000000)
    añadir_usuario_grupo(10, group_id[0], 0)
    deuda = obtener_deudas(group_id[0])
    assert deuda[0][5] == 100

def test_obtener_gastos(fixture_inicializar_db):
    
    registrar_gasto(10, 234, "descripcion", categoria="general")
    crear_grupo("Prueba", "10000000", "1")
    registrar_usuario(10, "Luis", "Luis123")
    group_id = obtener_grupo_por_codigo(10000000)
    añadir_usuario_grupo(10, group_id[0], 0)
    gastos = obtener_gastos(group_id[0])
    assert gastos[0][2] == 234

def test_obtener_grupos_usuario(fixture_inicializar_db):
    
    crear_grupo("Prueba1", "10000000", "1")
    crear_grupo("Prueba2", "20000000", "2")
    crear_grupo("Prueba3", "30000000", "3")
    registrar_usuario(10, "Luis", "Luis123")
    group_id1 = obtener_grupo_por_codigo(10000000)
    group_id2 = obtener_grupo_por_codigo(20000000)
    group_id3 = obtener_grupo_por_codigo(30000000)
    añadir_usuario_grupo(10, group_id1[0], 0)
    añadir_usuario_grupo(10, group_id2[0], 0)
    añadir_usuario_grupo(10, group_id3[0], 0)

    grupos = obtener_grupos_usuario(10)

    assert grupos[0][1] == "Prueba1" and grupos[1][1] == "Prueba2" and grupos[2][1] == "Prueba3"

def test_saldar_deuda(fixture_inicializar_db):

    
    registrar_deuda(10, 2, 100)
    crear_grupo("Prueba", "10000000", "1")
    registrar_usuario(10, "Luis", "Luis123")
    registrar_usuario(2, "Manolo", "Manolo123")
    group_id = obtener_grupo_por_codigo(10000000)
    añadir_usuario_grupo(10, group_id[0], 0)
    saldar_deuda(10, 2)
    deuda = obtener_deudas_usuario(10, group_id[0])
    assert len(deuda) == 0
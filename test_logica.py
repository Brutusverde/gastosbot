from logica import crear_codigo, calcular_deudas

from database import obtener_usuarios, registrar_usuario, obtener_id_por_username, obtener_deudas, registrar_deuda, crear_grupo, obtener_grupo, añadir_usuario_grupo
from database import obtener_grupo_por_codigo, registrar_gasto, obtener_gastos, obtener_grupos_usuario, saldar_deuda, obtener_deudas_usuario

def test_crear_codigo():
    """Comprueba si el codigo de logica.py se crea correctamente"""
    resultado = crear_codigo()
    assert resultado.isupper() and len(resultado) == 8

def test_calcular_deudas(fixture_inicializar_db):

    crear_grupo("Prueba", "10000000", "1")
    registrar_usuario(10, "Luis", "Luis123")
    registrar_usuario(2, "Manolo", "Manolo123")

    group_id = obtener_grupo_por_codigo(10000000)
    añadir_usuario_grupo(10, group_id[0], 0)
    añadir_usuario_grupo(2, group_id[0], 0)

    calcular_deudas(10, 100, group_id[0])

    deuda_usuario_1 = obtener_deudas_usuario(10, group_id[0])
    deuda_usuario_2 = obtener_deudas_usuario(2, group_id[0])

    assert len(deuda_usuario_1) == 0 and deuda_usuario_2[0][5] == 50
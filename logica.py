from database import obtener_usuarios, registrar_deuda, obtener_grupo_por_codigo, obtener_miembros_grupo
import secrets


def calcular_deudas(pagador_id, cantidad, group_id):
    """Divide el gasto entre los usuarios pertenecientes a un grupo y crea una deuda para cada uno de ellos"""
    usuarios_grupo = obtener_miembros_grupo(group_id)

    deuda_individual = cantidad/ len(usuarios_grupo)
    for usuario in usuarios_grupo:
        if usuario[0] != pagador_id:
            registrar_deuda(usuario[0], pagador_id, deuda_individual)

def crear_codigo():
    """Crea un codigo de invitación exclusivo para un grupo"""
    codigo = secrets.token_hex(4).upper()  # genera algo como "A3F9B2C1"

    while obtener_grupo_por_codigo(codigo) is not None:
        codigo = secrets.token_hex(4).upper() 
    
    return codigo
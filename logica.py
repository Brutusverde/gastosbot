from database import obtener_usuarios, registrar_deuda, obtener_grupo_por_codigo, obtener_miembros_grupo
import secrets


def calcular_deudas(pagador_id, cantidad, group_id):
    """Divide la cantidad del gasto entre el numero de usuarios y crea una deuda a todos los usuarios que no sean el que ha pagado"""
    usuarios_grupo = obtener_miembros_grupo(group_id)

    deuda_individual = cantidad/ len(usuarios_grupo)
    for usuario in usuarios_grupo:
        if usuario[0] != pagador_id:
            registrar_deuda(usuario[0], pagador_id, deuda_individual)

def crear_codigo():
    """Crea un codigo exclusivo para el grupo"""
    codigo = secrets.token_hex(4).upper()  # genera algo como "A3F9B2C1"

    while obtener_grupo_por_codigo(codigo) is not None:
        codigo = secrets.token_hex(4).upper() 
    
    return codigo
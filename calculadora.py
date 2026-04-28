from database import obtener_usuarios, registrar_deuda

def calcular_deudas(pagador_id, cantidad):
    """Divide la cantidad del gasto entre el numero de usuarios y crea una deuda a todos los usuarios que no sean el que ha pagado"""
    usuarios = obtener_usuarios()
    deuda_individual = cantidad/ len(usuarios)
    for usuario in usuarios:
        if usuario[0] != pagador_id:
            registrar_deuda(usuario[0], pagador_id, deuda_individual)


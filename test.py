from database import inicializar_db, obtener_usuarios, obtener_gastos, obtener_deudas, registrar_usuario, registrar_gasto, registrar_deuda, saldar_deuda
from calculadora import calcular_deudas
inicializar_db()

#registrar_usuario(1, 'manolo')
#registrar_usuario(2, 'pepito')
#registrar_usuario(3, 'cesar')
#registrar_usuario(4, 'Panda')

#registrar_gasto(1, 100, "sopa de pollo")
#registrar_gasto(2, 4309349855, "ropa de cama", "casa")
#registrar_gasto(3, 34, "compra", "compra")
#registrar_gasto(4, 222, "juegos", "ocio")

#registrar_deuda(2, 1, 25)  # pepito le debe 25 a manolo
#registrar_deuda(3, 1, 25)  # cesar le debe 25 a manolo
#registrar_deuda(4, 1, 25)  # panda le debe 25 a manolo

#calcular_deudas(1, 200)

#print(obtener_usuarios())
#print(obtener_gastos())
#print(obtener_deudas())
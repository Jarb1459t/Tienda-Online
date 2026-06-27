import socket
from datetime import datetime

def escanear_puertos(host, puertos):
    print(f"[*] Escaneando host: {host}")
    print(f"[*] Inicio: {datetime.now()}\n")
    
    resultados = []

    for puerto in puertos:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        try:
            conexion = s.connect_ex((host, puerto))
            if conexion == 0:
                print(f"[+] Puerto abierto: {puerto}")
                resultados.append(f"Puerto {puerto}: ABIERTO")
            s.close()
        except Exception as e:
            print(f"[-] Error al escanear el puerto {puerto}: {e}")

    guardar_resultados(host, resultados)

def guardar_resultados(host, resultados):
    with open(f"reporte_{host}.txt", "w") as archivo:
        archivo.write(f"Escaneo de {host} - {datetime.now()}\n\n")
        for linea in resultados:
            archivo.write(linea + "\n")
    print(f"\n[✔] Resultados guardados en reporte_{host}.txt")

# --- CONFIGURACIÓN ---
host_objetivo = input("Ingresa la IP o dominio a escanear: ").strip()
puertos_comunes = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389]

escanear_puertos(host_objetivo, puertos_comunes)

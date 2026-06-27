import subprocess
import hashlib
import time

# Simular base de datos de hashes bloqueados
hashes_bloqueados = set()

# 1. Obtener procesos del dispositivo Android
def obtener_procesos_android():
    try:
        resultado = subprocess.check_output(["adb", "shell", "ps"], encoding='utf-8')
        lineas = resultado.strip().split("\n")
        encabezados = lineas[0].split()
        idx_pid = encabezados.index("PID") if "PID" in encabezados else 1
        idx_nombre = encabezados.index("NAME") if "NAME" in encabezados else -1

        procesos = []
        for linea in lineas[1:]:
            partes = linea.split()
            pid = partes[idx_pid]
            nombre = partes[idx_nombre] if idx_nombre != -1 else partes[-1]
            procesos.append({"pid": pid, "nombre": nombre})

        return procesos
    except Exception as e:
        print("Error al obtener procesos:", e)
        return []

# 2. Filtrar procesos sospechosos
def detectar_procesos_sospechosos(procesos):
    sospechosos = []
    whitelist = ["com.android.", "com.google.", "com.whatsapp", "com.facebook", "com.instagram"]
    for proc in procesos:
        nombre = proc["nombre"]
        if not any(app in nombre for app in whitelist) and not nombre.startswith("u0_"):
            sospechosos.append(proc)
    return sospechosos

# 3. Simular análisis del proceso
def analizar_proceso(proc):
    nombre = proc["nombre"]
    hash_proc = hashlib.sha256(nombre.encode()).hexdigest()

    if "malware" in nombre.lower() or "spy" in nombre.lower():
        return "malware", hash_proc
    elif any(c in nombre for c in ["tmp", "xyz", "abc123"]):
        return "sospechoso", hash_proc
    else:
        return "limpio", hash_proc

# 4. Contramedidas: registrar y bloquear
def aplicar_contramedidas(proc, hash_proc):
    print(f"\n⚠️ Contramedidas activadas para: {proc['nombre']} (PID: {proc['pid']})")
    
    # Registrar en log
    with open("registro_sospechosos.log", "a") as f:
        f.write(f"{time.ctime()} - Acción sospechosa: {proc['nombre']} (PID: {proc['pid']})\n")
    
    # Intentar matar el proceso
    try:
        subprocess.run(["adb", "shell", "kill", proc["pid"]])
        print(f"✅ Proceso terminado: {proc['nombre']}")
    except:
        print(f"❌ No se pudo terminar el proceso: {proc['nombre']}")

    # Bloqueo cifrado (añadir a lista de hashes)
    hashes_bloqueados.add(hash_proc)
    print(f"🔒 Acción bloqueada cifradamente (SHA256): {hash_proc}\n")

# --- Flujo principal ---
print("🔍 Iniciando análisis de segundo plano en dispositivo Android...\n")
procesos = obtener_procesos_android()
sospechosos = detectar_procesos_sospechosos(procesos)

if sospechosos:
    for proc in sospechosos:
        estado, hash_proc = analizar_proceso(proc)
        if estado == "limpio":
            print(f"✔️ Acción segura descartada: {proc['nombre']}")
        else:
            aplicar_contramedidas(proc, hash_proc)
else:
    print("✅ No se encontraron acciones sospechosas.")

# Mostrar bloqueos registrados
print("\n📄 Lista de acciones bloqueadas cifradamente:")
for h in hashes_bloqueados:
    print(f"🔐 {h}")

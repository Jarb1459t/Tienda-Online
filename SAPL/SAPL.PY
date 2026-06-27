### Proyecto base: Jarvis Desktop AI
# Asistente personal inteligente para Windows con interfaz y funciones básicas

# ESTRUCTURA BASE

# main.py: Punto de entrada del asistente
import tkinter as tk
from core.voice import listen_and_process
from core.tasks import add_task, list_tasks

def main():
    window = tk.Tk()
    window.title("Jarvis Asistente Personal")

    output = tk.Text(window, height=10, width=50)
    output.pack()

    def ejecutar_comando():
        comando = listen_and_process()
        output.insert(tk.END, f"\n>> {comando}")

    btn = tk.Button(window, text="Hablar", command=ejecutar_comando)
    btn.pack()

    window.mainloop()

if __name__ == "__main__":
    main()

# core/voice.py: reconocimiento de voz
import speech_recognition as sr

def listen_and_process():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
        try:
            texto = recognizer.recognize_google(audio, language="es-ES")
            print(f"Has dicho: {texto}")
            return texto
        except:
            return "No entendí el comando."

# core/tasks.py: gestión simple de tareas (memoria en texto plano)
import os

TASKS_FILE = "data/tareas.txt"

os.makedirs("data", exist_ok=True)

def add_task(tarea):
    with open(TASKS_FILE, "a") as f:
        f.write(f"{tarea}\n")

def list_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return f.readlines()

# requirements.txt
# Ejecuta: pip install -r requirements.txt
speechrecognition
pyaudio
tk

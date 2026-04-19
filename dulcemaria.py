import tkinter as tk
from tkinter import ttk
import json
import os
import csv
import sys

# ================= RUTAS SEGURAS PARA .EXE =================
def recurso_path(ruta_relativa):
    """Obtiene la ruta absoluta para archivos al usar PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)

# ================= RUTAS SEGURAS PARA .EXE =================
ARCHIVO = os.path.join(os.path.dirname(sys.executable), "dulcemaria.json")
CSV_FILE = os.path.join(os.path.dirname(sys.executable), "ventas.csv")  # mismo folder del exe

# ===== TIP PRO: crear JSON vacío si no existe =====
if not os.path.exists(ARCHIVO):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump({
            "pestana1": [["","","","",""] for _ in range(10)],
            "pestana2": [["","","",""] for _ in range(5)],
            "porcentaje": "50"
        }, f)

#============ VALIDACIONES =================
def validar_4_digitos(valor):
    if valor == "":
        return True
    return valor.isdigit() and len(valor) <= 8

def safe_float(valor):
    try:
        return float(valor)
    except ValueError:
        return 0

def formato_clp(valor):
    return f"${valor:,.0f}".replace(",", ".")

def limpiar_clp(texto):
    return safe_float(texto.replace("$", "").replace(".", ""))

# ================= PESTAÑA 1 =================
def calcular_fila(fila):
    try:
        precio = safe_float(entradas[fila][1].get())
        cantidad = safe_float(entradas[fila][2].get())
        receta = safe_float(entradas[fila][3].get())
        total = (precio / cantidad) * receta if cantidad != 0 else 0
        entradas[fila][4].config(state="normal")
        entradas[fila][4].delete(0, tk.END)
        entradas[fila][4].insert(0, formato_clp(total))
        entradas[fila][4].config(state="readonly")
    except Exception as e:
        print(f"Error calcular fila P1: {e}")
    calcular_total_general()

def calcular_total_general():
    suma = 0
    for fila in entradas:
        try:
            suma += limpiar_clp(fila[4].get())
        except Exception as e:
            print(f"Error sumar fila: {e}")
    total_general_var.set(formato_clp(suma))

def limpiar_columna_receta():
    for fila in entradas:
        fila[3].delete(0, tk.END)
    calcular_total_general()

def crear_fila(fila):
    fila_widgets = []
    for col in range(5):
        if col in [1, 2, 3]:
            e = tk.Entry(tab1, validate="key", validatecommand=vcmd)
            e.bind("<KeyRelease>", lambda event, f=fila: calcular_fila(f))
        elif col == 4:
            e = tk.Entry(tab1, state="readonly")
        else:
            e = tk.Entry(tab1, width=25)  # columna INGREDIENTES más ancha
        e.grid(row=fila + 1, column=col, padx=5, pady=5, sticky="we")
        fila_widgets.append(e)
    entradas.append(fila_widgets)

def agregar_fila():
    crear_fila(len(entradas))

def eliminar_fila():
    if entradas:
        fila = entradas.pop()
        for widget in fila:
            widget.destroy()
        calcular_total_general()

# ================= PESTAÑA 2 =================
def calcular_fila_tab2(fila):
    try:
        valor1 = safe_float(filas_tab2[fila][1].get())
        porcentaje = safe_float(porcentaje_var.get())
        valor_porcentaje = valor1 * (porcentaje / 100)
        total = valor1 + valor_porcentaje

        filas_tab2[fila][2].config(state="normal")
        filas_tab2[fila][2].delete(0, tk.END)
        filas_tab2[fila][2].insert(0, formato_clp(valor_porcentaje))
        filas_tab2[fila][2].config(state="readonly")

        filas_tab2[fila][3].config(state="normal")
        filas_tab2[fila][3].delete(0, tk.END)
        filas_tab2[fila][3].insert(0, formato_clp(total))
        filas_tab2[fila][3].config(state="readonly")
    except Exception as e:
        print(f"Error calcular fila P2: {e}")

def recalcular_todo_tab2():
    for i in range(len(filas_tab2)):
        calcular_fila_tab2(i)

def agregar_fila_tab2():
    fila = len(filas_tab2)
    fila_widgets = []
    for col in range(4):
        if col == 0:
            e = tk.Entry(tab2, width=25)  # columna Postre/Torta más ancha
        elif col == 1:
            e = tk.Entry(tab2, width=20, validate="key", validatecommand=vcmd)
            e.bind("<KeyRelease>", lambda event, f=fila: calcular_fila_tab2(f))
        else:
            e = tk.Entry(tab2, state="readonly")
        e.grid(row=fila + 2, column=col, padx=5, pady=5, sticky="we")
        fila_widgets.append(e)
    filas_tab2.append(fila_widgets)

def eliminar_fila_tab2():
    if filas_tab2:
        fila = filas_tab2.pop()
        for widget in fila:
            widget.destroy()

def exportar_csv_tab2():
    try:
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8-sig") as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["Postre/Torta", "Valor", "Porcentaje $", "Total CLP"])
            for fila in filas_tab2:
                if fila[0].get().strip() == "":
                    continue
                writer.writerow([fila[0].get(), fila[1].get(), fila[2].get(), fila[3].get()])
        print(f"Archivo exportado como {CSV_FILE}")
    except Exception as e:
        print(f"Error exportando CSV: {e}")

# ================= GUARDAR Y CARGAR =================
def guardar_datos():
    print("Guardando en:", ARCHIVO)
    try:
        datos = {
            "pestana1": [[e.get() for e in fila] for fila in entradas],
            "pestana2": [[e.get() for e in fila] for fila in filas_tab2],
            "porcentaje": porcentaje_var.get()
        }
        with open(ARCHIVO, "w") as f:
            json.dump(datos, f)
    except Exception as e:
        print(f"Error guardando datos: {e}")

def cargar_datos():
    if not os.path.exists(ARCHIVO):
        return
    try:
        with open(ARCHIVO, "r") as f:
            datos = json.load(f)
        for i, fila in enumerate(datos.get("pestana1", [])):
            while i >= len(entradas):
                agregar_fila()
            for j, valor in enumerate(fila):
                entradas[i][j].config(state="normal")
                entradas[i][j].delete(0, tk.END)
                entradas[i][j].insert(0, valor)
                if j == 4:
                    entradas[i][j].config(state="readonly")
        for i, fila in enumerate(datos.get("pestana2", [])):
            while i >= len(filas_tab2):
                agregar_fila_tab2()
            for j, valor in enumerate(fila):
                filas_tab2[i][j].config(state="normal")
                filas_tab2[i][j].delete(0, tk.END)
                filas_tab2[i][j].insert(0, valor)
                if j in [2, 3]:
                    filas_tab2[i][j].config(state="readonly")
        porcentaje_var.set(datos.get("porcentaje", "50"))
        recalcular_todo_tab2()
    except Exception as e:
        print(f"Error cargando datos: {e}")

# ================= CREACION DE PESTAÑA CON SCROLL =================
def _on_mousewheel(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def crear_tab_scroll(parent):
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)

    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0,0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda event: _on_mousewheel(event, canvas)))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    return frame

# ================= VENTANA =================
root = tk.Tk()
root.title("Sistema de Costos")
root.geometry("700x650")

vcmd = (root.register(validar_4_digitos), "%P")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ---- PESTAÑA 1 ----
tab1_container = tk.Frame(notebook)
tab1 = crear_tab_scroll(tab1_container)
notebook.add(tab1_container, text="Sistema Costos")

titulos = ["INGREDIENTES", "PRECIO (CLP)", "CANTIDAD", "RECETA", "TOTAL (CLP)"]
for col, t in enumerate(titulos):
    frame_header = tk.Frame(tab1)
    frame_header.grid(row=0, column=col, sticky="we")
    tk.Label(frame_header, text=t, font=("Arial",10,"bold")).pack(side="left")
    if col == 3:
        tk.Button(frame_header, text="🧹", command=limpiar_columna_receta, bg="orange").pack(side="left", padx=5)

entradas = []
for i in range(10):
    crear_fila(i)

tk.Label(tab1, text="TOTAL GENERAL", bg="yellow", font=("Arial",11,"bold")).grid(row=100,column=0,columnspan=4,sticky="we")
total_general_var = tk.StringVar()
tk.Entry(tab1, textvariable=total_general_var, bg="yellow", state="readonly").grid(row=100,column=4,padx=5,pady=5)

frame_botones = tk.Frame(tab1)
frame_botones.grid(row=101,column=0,columnspan=5,pady=10)
tk.Button(frame_botones, text="Agregar Fila", command=agregar_fila, bg="lightgreen").pack(side="left", padx=10)
tk.Button(frame_botones, text="Eliminar Última Fila", command=eliminar_fila, bg="salmon").pack(side="left", padx=10)

tab1.grid_columnconfigure(0, weight=1)

# ---- PESTAÑA 2 ----
tab2_container = tk.Frame(notebook)
tab2 = crear_tab_scroll(tab2_container)
notebook.add(tab2_container, text="50% + Total")

tk.Label(tab2, text="Porcentaje % :", font=("Arial",11,"bold")).grid(row=0,column=0,pady=10)
porcentaje_var = tk.StringVar(value="50")
entry_porcentaje = tk.Entry(tab2,textvariable=porcentaje_var,width=5)
entry_porcentaje.grid(row=0,column=1)
entry_porcentaje.bind("<KeyRelease>", lambda e: recalcular_todo_tab2())

encabezados2 = ["Postre/Torta","Valor","Porcentaje","Total CLP"]
for col, t in enumerate(encabezados2):
    tk.Label(tab2, text=t, font=("Arial",11,"bold")).grid(row=1,column=col, sticky="we")

filas_tab2 = []
for i in range(5):
    agregar_fila_tab2()

frame_botones2 = tk.Frame(tab2)
frame_botones2.grid(row=100,column=0,columnspan=4,pady=10)
tk.Button(frame_botones2, text="Exportar a Excel", command=exportar_csv_tab2, bg="lightblue").pack(side="left", padx=10)
tk.Button(frame_botones2, text="Agregar Fila", command=agregar_fila_tab2, bg="lightgreen").pack(side="left", padx=10)
tk.Button(frame_botones2, text="Eliminar Última Fila", command=eliminar_fila_tab2, bg="salmon").pack(side="left", padx=10)

tab2.grid_columnconfigure(0, weight=1)
tab2.grid_columnconfigure(1, weight=1)

# ---- Cargar y guardar datos ----
cargar_datos()
def cerrar_app():
    try:
        print("Guardando datos...")
        guardar_datos()
    except Exception as e:
        import tkinter.messagebox as mb
        mb.showerror("Error al guardar", str(e))
    root.destroy()

root.protocol("WM_DELETE_WINDOW", cerrar_app)
root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector, subprocess, os
from tkhtmlview import HTMLLabel

def on_tree_select(event, tree, t2, t3, t4, t5, t6, t7):
    if tree.selection():
        for t in (t2, t3, t4, t5, t6, t7): t.delete("1.0", tk.END)
        renglon = tree.item(tree.selection()[0], 'values')
        for i, t in enumerate((t2, t3, t4, t5, t6, t7)): t.insert(tk.END, renglon[i])
        
def BuscaVenta(tree, t1):
    t = str(t1.get("1.0", tk.END).strip())
    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ventas WHERE fechahora like '%" + t + "%'")
    resultados = cursor.fetchall()
    [tree.delete(i) for i in tree.get_children()]
    for f in resultados:
        tree.insert("", "end", values=(str(f[0]), str(f[1]), str(f[2]), str(f[3]), str(f[4]), str(f[5])))
    cursor.close()
    conexion.close()

def AgregaVenta(tree, t1, t2, t3, t4, t5, t6, t7):
    f = t6.get("1.0", tk.END).strip()
    fecha = f[0:4]+f[5:7]+f[8:10]+f[11:13]+f[14:16]+f[17:19]
    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO ventas VALUES (null," + t3.get("1.0", tk.END).strip() + ","
                    + t4.get("1.0", tk.END).strip() + "," + t5.get("1.0", tk.END).strip() + ","
                    + fecha + "," + t7.get("1.0", tk.END).strip() + ")")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    BuscaVenta(tree, t1)

def EliminaVenta(tree, t1, t2):
    t = t2.get("1.0", tk.END).strip()
    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ventas WHERE id_venta=" + t)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    BuscaVenta(tree, t1)

def ModificaVenta(tree, t1, t2, t3, t4, t5, t6, t7):
    t = t2.get("1.0", tk.END).strip()
    f = t6.get("1.0", tk.END).strip()
    fecha = f[0:4]+f[5:7]+f[8:10]+f[11:13]+f[14:16]+f[17:19]
    #message = messagebox.showinfo("Mensaje", fecha)
    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
    cursor = conexion.cursor()
    cursor.execute("UPDATE ventas SET id_cliente=" + t3.get("1.0", tk.END).strip() 
                   + ", id_producto=" + t4.get("1.0", tk.END).strip() 
                   + ", id_usuario=" + t5.get("1.0", tk.END).strip() 
                   + ", fechaventa=" + fecha 
                   + ", precioventa=" + t7.get("1.0", tk.END).strip() 
                   + " where id_venta=" + t)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    BuscaVenta(tree, t1)

def ReporteVentas(tree):
    with open("ventas.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_venta</td><td>id_cliente</td><td>id_lente</td><td>id_usuario</td><td>fechaventa</td><td>precioventa</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td><td>" + str(v[4]) + "</td><td>" + str(v[5]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelVentasTree(tree):
    ReporteVentas(tree)
    ruta = os.path.abspath("ventas.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelVentas():
    ruta = os.path.abspath("ventas.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeVentasTree(tree):
    ReporteVentas(tree)
    ruta = os.path.abspath("ventas.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeVentas():
    ruta = os.path.abspath("ventas.html")
    subprocess.Popen(["start", "chrome", ruta], shell=True)

def SalirVentas(ventas):
    ventas.destroy()

def Ventas():
    ventas = tk.Toplevel()
    ventas.config(width=600, height=400)
    ventas.minsize(600, 400)
    ventas.title("Información de Ventas")
    t1 = tk.Text(ventas, width=60, height=1)
    t1.place(x=12, y=12)
    t2 = tk.Text(ventas, width=8, height=1)
    t2.place(x=10, y=330)
    t3 = tk.Text(ventas, width=8, height=1)
    t3.place(x=80, y=330)
    t4 = tk.Text(ventas, width=8, height=1)
    t4.place(x=150, y=330)
    t5 = tk.Text(ventas, width=8, height=1)
    t5.place(x=220, y=330)
    t6 = tk.Text(ventas, width=23, height=1)
    t6.place(x=290, y=330)
    t7 = tk.Text(ventas, width=12, height=1)
    t7.place(x=480, y=330)
    b1 = tk.Button(ventas, text="Buscar", width=10, height=1, command=lambda: BuscaVenta(tree, t1))
    b1.place(x=510, y=8)
    b1.focus_set()
    b2 = tk.Button(ventas, text="Agregar", width=10, height=1, command=lambda:
                   AgregaVenta(tree, t1, t2, t3, t4, t5, t6, t7))
    b2.place(x=10, y=360)
    b3 = tk.Button(ventas, text="Eliminar", width=10, height=1, command=lambda: EliminaVenta(tree, t1, t2))
    b3.place(x=100, y=3600)
    b4 = tk.Button(ventas, text="Modificar", width=10, height=1, command=lambda: ModificaVenta(tree, t1, t2, t3, t4, t5, t6, t7))
    b4.place(x=190, y=360)
    b5 = tk.Button(ventas, text="Excel", width=10, height=1, command=lambda: ExcelVentasTree(tree))
    b5.place(x=280, y=360)
    b6 = tk.Button(ventas, text="Chrome", width=10, height=1, command=lambda: ChromeVentasTree(tree))
    b6.place(x=370, y=360)
    b7 = tk.Button(ventas, text="Salir", width=10, height=1, command=lambda: SalirVentas(ventas))
    b7.place(x=460, y=360)

    l1 = tk.Label(ventas, width=8, height=1, text="Id_venta")
    l1.place(x=8, y=305)
    l2 = tk.Label(ventas, width=8, height=1, text="Id_cliente")
    l2.place(x=80, y=305)
    l3 = tk.Label(ventas, width=8, height=1, text="Id_producto")
    l3.place(x=150, y=305)
    l4 = tk.Label(ventas, width=8, height=1, text="Id_usuario")
    l4.place(x=220, y=305)
    l5 = tk.Label(ventas, width=12, height=1, text="FechaVenta")
    l5.place(x=280, y=305)
    l6 = tk.Label(ventas, width=8, height=1, text="PrecioVenta")
    l6.place(x=480, y=305)

    canvas = tk.Canvas(ventas, width=524, height=130, bg='white')
    canvas.place(x=12, y=40)
    tree = ttk.Treeview(canvas, columns=("1", "2", "3", "4", "5", "6"), show="headings")
    tree.heading("1", text="Id_venta")
    tree.heading("2", text="Id_cliente")
    tree.heading("3", text="Id_producto")
    tree.heading("4", text="Id_usuario")
    tree.heading("5", text="FechaVenta")
    tree.heading("6", text="PrecioVenta")
    tree.column("1", width=90)
    tree.column("2", width=90)
    tree.column("3", width=90)
    tree.column("4", width=90)
    tree.column("5", width=124)
    tree.column("6", width=90)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select(e, tree, t2, t3, t4, t5, t6, t7))

def Clientes():
    clientes = tk.Toplevel()
    clientes.config(width=600, height=400)
    clientes.minsize(600,400)

    t1 = tk.Text(clientes, width=60, height=1)
    t1.place(x=12, y=12)
    t2 = tk.Text(clientes, width=8, height=1)
    t2.place(x=10, y=330)
    t3 = tk.Text(clientes, width=8, height=1)
    t3.place(x=80, y=330)
    t4 = tk.Text(clientes, width=8, height=1)
    t4.place(x=150, y=330)
    t5 = tk.Text(clientes, width=8, height=1)
    t5.place(x=220, y=330)
    t6 = tk.Text(clientes, width=23, height=1)
    t6.place(x=290, y=330)
    t7 = tk.Text(clientes, width=12, height=1)
    t7.place(x=480, y=330)
    b1 = tk.Button(clientes, text="Buscar", width=10, height=1, command=lambda: BuscaVenta(tree, t1))
    b1.place(x=510, y=8)
    b1.focus_set()
    b2 = tk.Button(clientes, text="Agregar", width=10, height=1, command=lambda:
                   AgregaVenta(tree, t1, t2, t3, t4, t5, t6, t7))
    b2.place(x=10, y=360)
    b3 = tk.Button(clientes, text="Eliminar", width=10, height=1, command=lambda: EliminaVenta(tree, t1, t2))
    b3.place(x=100, y=3600)
    b4 = tk.Button(clientes, text="Modificar", width=10, height=1, command=lambda: ModificaVenta(tree, t1, t2, t3, t4, t5, t6, t7))
    b4.place(x=190, y=360)
    b5 = tk.Button(clientes, text="Excel", width=10, height=1, command=lambda: ExcelVentasTree(tree))
    b5.place(x=280, y=360)
    b6 = tk.Button(clientes, text="Chrome", width=10, height=1, command=lambda: ChromeVentasTree(tree))
    b6.place(x=370, y=360)
    b7 = tk.Button(clientes, text="Salir", width=10, height=1, command=lambda: SalirVentas(clientes))
    b7.place(x=460, y=360)

    l1 = tk.Label(clientes, width=8, height=1, text="Id_cliente")
    l1.place(x=8, y=305)
    l2 = tk.Label(clientes, width=8, height=1, text="Cliente")
    l2.place(x=80, y=305)
    l3 = tk.Label(clientes, width=8, height=1, text="Celular")
    l3.place(x=150, y=305)
    l4 = tk.Label(clientes, width=8, height=1, text="Domicilio")
    l4.place(x=220, y=305)
    

    canvas = tk.Canvas(clientes, width=524, height=130, bg='white')
    canvas.place(x=12, y=40)
    tree = ttk.Treeview(canvas, columns=("1", "2", "3", "4", "5", "6"), show="headings")
    tree.heading("1", text="Id_cliente")
    tree.heading("2", text="Cliente")
    tree.heading("3", text="Celular")
    tree.heading("4", text="Domicilio")
    tree.column("1", width=90)
    tree.column("2", width=90)
    tree.column("3", width=90)
    tree.column("4", width=90)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select(e, tree, t2, t3, t4, t5, t6, t7))


    clientes.title("Informacion de clientes")
    t1 = tk.Text(clientes, width=60, height=1)
    t1.place(x=12,y=12)

def Lentes():
    lentes = tk.Toplevel()
    lentes.config(width=600, height=400)
    lentes.minsize(600,400)
    lentes.title("Informacion de lentes")
    t1 = tk.Text(lentes, width=60, height=1)
    t1.place(x=12,y=12)

def Usuarios():
    usuarios = tk.Toplevel()
    usuarios.config(width=600, height=400)
    usuarios.minsize(600,400)
    usuarios.title("Informacion de usuarios")
    t1 = tk.Text(usuarios, width=60, height=1)
    t1.place(x=12,y=12)

def Salir():
    root.destroy()

def GenVentas(repVentas):
    with open("ventas.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_venta</td><td>id_cliente</td><td>id_lente</td><td>id_usuario</td><td>fechaventa</td><td>precioventa</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM ventas")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td><td>" + str(v[4]) + "</td><td>" + str(v[5]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("ventas.html", "r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repVentas, width=680, height=540)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=370, height=270, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code)
    html_label.pack(padx=3, pady=3)

def SalirRepVentas(repVentas):
    repVentas.destroy()

def RepVentas():
    repVentas = tk.Toplevel()
    repVentas.geometry("580x400")
    repVentas.title("Reporte de Ventas")
    repVentas.minsize(600, 400)

    b1 = tk.Button(repVentas, text="Generar", width=10, height=1, command=lambda: GenVentas(repVentas))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(repVentas, text="Excel", width=10, height=1, command=ExcelVentas)
    b2.place(x=100, y=10)
    b3 = tk.Button(repVentas, text="Chrome", width=10, height=1, command=ChromeVentas)
    b3.place(x=190, y=10)
    b4 = tk.Button(repVentas, text="Salir", width=10, height=1, command=lambda: SalirRepVentas(repVentas))
    b4.place(x=280, y=10)
    GenVentas(repVentas)

def RepClientes():
    repClientes = tk.Tk()
    repClientes.geometry("600x400")
    repClientes.title("Reporte de Clientes")

def RepLentes():
    repLentes=tk.Tk()
    repLentes.geometry("600x400")
    repLentes.title("Reporte de Productos")

def RepUsuarios():
    repUsuarios=tk.Tk()
    repUsuarios.geometry("600x400")
    repUsuarios.title("Reporte de usuarios")

def repVentasPorCliente():
    rVentasPorCliente=tk.Tk()
    rVentasPorCliente.geometry("600x400")
    rVentasPorCliente.title("Reporte de Ventas por Cliente")

def repVentasPorProducto():
    rVentasPorProducto=tk.Tk()
    rVentasPorProducto.geometry("600x400")
    rVentasPorProducto.title("Reporte de Ventas por Cliente")

def repVentasPorUsuario():
    rVentasPorUsuario=tk.Tk()
    rVentasPorUsuario.geometry("600x400")
    rVentasPorUsuario.title("Reporte de Ventas por Cliente")
# --------------------- Funciones de el menu de Archivo ---------------------- #

# ------------------- Terminan funciones del menu de Archivo ---------------------- #

# --------------------- Funciones de el menu de Reportes ---------------------- #


# ------------------- Terminan funciones del menu de Reportes ---------------------- # 

# ------------------- Ventana principal -------------------------- #
root = tk.Tk()
root.state('zoomed')



root.title("Sistema de optica")
archivo = tk.Menu(root)
ini = tk.Menu(archivo, tearoff=100)
rep = tk.Menu(archivo, tearoff=100)
archivo.add_cascade(label="Archivo", menu=ini)
archivo.add_cascade(label="Reportes", menu=rep)
ini.add_command(label="Clientes", command=Clientes)
ini.add_command(label="Ventas", command=Ventas)
ini.add_command(label="Lentes", command=Lentes)
ini.add_command(label="Usuarios", command=Usuarios)
ini.add_command(label="Salir", command=Salir)
rep.add_command(label="Reporte de clientes", command=RepClientes)
rep.add_command(label="Reporte de ventas", command=RepVentas)
rep.add_command(label="Reporte de lentes", command=RepLentes)
rep.add_command(label="Reporte de usuarios", command=RepUsuarios)
rep.add_command(label="Reporte de Ventas por Cliente", command=repVentasPorCliente)
rep.add_command(label="Reporte de Ventas por Producto", command=repVentasPorProducto)
rep.add_command(label="Reporte de Ventas por Usuario", command=repVentasPorUsuario)
root.config(menu=archivo)
root.mainloop()


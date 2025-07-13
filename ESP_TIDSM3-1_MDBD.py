# Alumno: Efrain Sandoval Pitsakis
# Grupo: TIDSM 3-1
# Fecha: 29/06/2025
# Manejo de base de datos

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector, subprocess, os
from tkhtmlview import HTMLLabel
from datetime import datetime
from mariadb import *


def get_db_connection():
    """Devuelve un objeto conexión a la BD MySQL (puerto 3307)."""
    return mysql.connector.connect(
        host="localhost",
        port="3307",
        user="root",
        password="",
        database="optica",
        autocommit=True,
    )

def on_tree_select_clientes(event, tree, t2, t3, t4, t5):
    if tree.selection():
        for t in (t2, t3, t4, t5): t.delete("1.0", tk.END)
        renglon = tree.item(tree.selection()[0], 'values')
        for i, t in enumerate((t2, t3, t4, t5)): t.insert(tk.END, renglon[i])

def on_tree_select_ventas(event, tree, t2, t3, t4, t5, t6, t7):
    if tree.selection():
        for t in (t2, t3, t4, t5, t6, t7): t.delete("1.0", tk.END)
        renglon = tree.item(tree.selection()[0], 'values')
        for i, t in enumerate((t2, t3, t4, t5, t6, t7)): t.insert(tk.END, renglon[i])

def on_tree_select_lentes(event, tree, t2, t3, t4, t5):
    if tree.selection():
        for t in (t2, t3, t4, t5): t.delete("1.0", tk.END)
        renglon = tree.item(tree.selection()[0], 'values')
        for i, t in enumerate((t2, t3, t4, t5)): t.insert(tk.END, renglon[i])
    
# -------------------------------------------- clientes ---------------------------------------------------

def BuscaCliente(tree, txt_busqueda):
    """
    Llena el TreeView con los clientes cuyo nombre (o id) coincida
    con el texto que el usuario escribió.
    """
    termino = txt_busqueda.get("1.0", tk.END).strip()

    # 1. Construir la consulta preparada (parameterized) ─ evita SQL Injection
    sql = """
        SELECT id_cliente, cliente, celular, domicilio
        FROM clientes
        WHERE cliente LIKE %s OR id_cliente = %s
        ORDER BY id_cliente
    """

    like = f"%{termino}%"
    try:
        id_num = int(termino)        # si escribió un número, busca por id
    except ValueError:
        id_num = -1                  # -1 nunca coincide, pero mantiene el parámetro

    cnx = get_db_connection()
    cur = cnx.cursor()

    cur.execute(sql, (like, id_num))
    resultados = cur.fetchall()

    # 2. Vaciar el tree y volver a llenarlo
    for row in tree.get_children():
        tree.delete(row)

    for fila in resultados:
        tree.insert("", "end", values=fila)

    cur.close()
    cnx.close()

def AgregaCliente(tree, txt_id, txt_bus, txt_nombre, txt_cel, txt_dom):
    try:
        # ── 1. Leer campos ────────────────────────────────────────────────────
        id_text   = txt_id.get("1.0", tk.END).strip().lower()
        cliente   = txt_nombre.get("1.0", tk.END).strip()
        celular   = txt_cel.get("1.0", tk.END).strip()
        domicilio = txt_dom.get("1.0", tk.END).strip()

        # ── 2. Decidir si usamos None (NULL) o un número ──────────────────────
        if id_text == "" or id_text == "null":
            id_cliente = None          # dejar que la BD asigne el AUTO_INCREMENT
        else:
            id_cliente = int(id_text)  # usará el valor escrito

        # ── 3. Insertar ───────────────────────────────────────────────────────
        cnx = get_db_connection()
        cur = cnx.cursor()

        cur.execute(
            """
            INSERT INTO clientes (id_cliente, cliente, celular, domicilio)
            VALUES (%s, %s, %s, %s)
            """,
            (id_cliente, cliente, celular, domicilio)
        )

        txt_bus.delete("1.0", tk.END)          # limpiar caja de búsqueda
        BuscaCliente(tree, txt_bus)            # mostrar nuevos datos

    except ValueError as ve:
            messagebox.showerror("Error", f"Datos inválidos: {ve}")
    except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error de base de datos: {err}")
    finally:
            if 'cur' in locals(): cur.close()
            if 'cnx' in locals(): cnx.close()


def ModificaCliente(tree, txt_nombre, txt_cel, txt_dom):
    cnx = None
    try:
        # 1. Validar selección en Treeview
        seleccionado = tree.focus()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un cliente primero")
            return

        # 2. Obtener ID del cliente desde la primera columna del Treeview
        datos = tree.item(seleccionado, "values")
        if not datos or len(datos) < 1:
            messagebox.showerror("Error", "No se pudo obtener el ID del cliente")
            return

        id_cliente = datos[0]  # ID está en la primera columna

        # 3. Obtener nuevos valores de los campos
        cliente = txt_nombre.get("1.0", tk.END).strip()
        celular = txt_cel.get("1.0", tk.END).strip()
        domicilio = txt_dom.get("1.0", tk.END).strip()

        # 4. Validar que haya cambios
        if not any([cliente, celular, domicilio]):
            messagebox.showwarning("Advertencia", "No hay cambios para guardar")
            return

        # 5. Actualizar en la BD
        cnx = get_db_connection()
        cur = cnx.cursor()

        query = """
            UPDATE clientes 
            SET cliente = %s, celular = %s, domicilio = %s 
            WHERE id_cliente = %s
        """
        cur.execute(query, (cliente, celular, domicilio, id_cliente))
        cnx.commit()

        # 6. Actualizar Treeview (opcional)
        tree.item(seleccionado, values=(
            id_cliente,  # Mantener el mismo ID
            cliente,     # Nuevo nombre
            celular,     # Nuevo celular
            domicilio    # Nuevo domicilio
        ))


    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", f"No se pudo modificar: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    finally:
        if cnx:
            cnx.close()

def EliminaCliente(tree, txt_busqueda):
    """Borra el registro seleccionado en el Treeview y lo quita de la BD."""
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Eliminar", "Selecciona un cliente primero.")
        return

    item_id   = seleccion[0]
    valores   = tree.item(item_id, "values")
    id_cliente = valores[0]                  # primera columna del Treeview

    try:
        cnx = get_db_connection()
        cur = cnx.cursor()
        cur.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        cnx.commit()                         # confirma la operación

        tree.delete(item_id)                 # quita la fila de la interfaz


        txt_busqueda.delete("1.0", tk.END)   # limpia la caja de búsqueda
    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", err)
    finally:
        if 'cur' in locals(): cur.close()
        if 'cnx' in locals(): cnx.close()



def SalirClientes(clientes):
    clientes.destroy()

#----------------------------------------------- termina clientes --------------------------------------------------------
    
# ----------------------------------------------------- ventas -----------------------------------------------------------

def parse_fecha_usuario(valor):
    """
    Convierte lo que escriba el usuario a 'YYYY-MM-DD HH:MM:SS'.
    Acepta:
      • YYYYMMDDHHMM      → 202506251122
      • YYYYMMDDHHMMSS    → 20250625112233
      • HHMM o HH:MM      → 1122   / 11:22
      • Formatos ya completos (YYYY-MM-DD ...)
    """
    valor = valor.strip()
    ahora = datetime.now()

    # 1) yyyyMMddHHmm[ss]
    if valor.isdigit():
        if len(valor) in (12, 14):
            fmt = "%Y%m%d%H%M" if len(valor) == 12 else "%Y%m%d%H%M%S"
            return datetime.strptime(valor, fmt).strftime("%Y-%m-%d %H:%M:%S")
        elif len(valor) == 4:
            h, m = int(valor[:2]), int(valor[2:])
            return ahora.replace(hour=h, minute=m, second=0).strftime("%Y-%m-%d %H:%M:%S")

    # 2) HH:MM
    try:
        return ahora.strftime("%Y-%m-%d ") + datetime.strptime(valor, "%H:%M").strftime("%H:%M:%S")
    except ValueError:
        pass

    # 3) Formato completo ya válido
    try:
        dt = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Formato de fecha/hora no reconocido")
    

def BuscaVenta(tree, t1):
    t = str(t1.get("1.0", tk.END).strip())
    tt = str(t1.get("1.0", tk.END).strip())
    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ventas WHERE id_venta like '%" + t + "%'")
    resultados = cursor.fetchall()
    [tree.delete(i) for i in tree.get_children()]
    for f in resultados:
        tree.insert("", "end", values=(str(f[0]), str(f[1]), str(f[2]), str(f[3]), str(f[4]), str(f[5])))
    cursor.close()
    conexion.close()

#def BuscaVenta(tree, t1):
#    t = str(t1.get("1.0", tk.END).strip())
#    tt = str(t1.get("1.0", tk.END).strip())
#    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
#    cursor = conexion.cursor()
#    cursor.execute("SELECT * FROM ventas WHERE fechahora like '%" + t + "%' OR id_venta like '%"+ tt +"%'")
#    resultados = cursor.fetchall()
#    [tree.delete(i) for i in tree.get_children()]
#    for f in resultados:
#        tree.insert("", "end", values=(str(f[0]), str(f[1]), str(f[2]), str(f[3]), str(f[4]), str(f[5])))
#    cursor.close()
#    conexion.close()

def AgregaVenta(tree, t1, t2, t3, t4, t5, t6, t7):

    try:
        id_cliente = int(t3.get("1.0", tk.END).strip())
        id_lente = int(t4.get("1.0", tk.END).strip())
        id_usuario = int(t5.get("1.0", tk.END).strip())
        total = float(t6.get("1.0", tk.END).strip())

        fecha_val = t7.get("1.0", tk.END)
        fechahora = parse_fecha_usuario(fecha_val)

        cnx = get_db_connection()
        cur = cnx.cursor()

        cur.execute(
            "INSERT INTO ventas (id_cliente, id_lente, id_usuario, total, fechahora) VALUES (%s, %s, %s, %s, %s)",
            (id_cliente, id_lente, id_usuario, total, fechahora)
        )

        t1.delete("1.0", tk.END)  # limpiar filtro
        BuscaVenta(tree, t1)

    except ValueError as ve:
        messagebox.showerror("Error", f"Datos inválidos: {ve}")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error de base de datos: {err}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'cnx' in locals(): cnx.close()


def ModificaVenta(tree,txt_filtro,txt_lente, txt_user, txt_total):
    try:
        seleccionado = tree.focus()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona la venta primero")
            return

        id_venta, _, _, _, _ , _ = tree.item(seleccionado, "values")

        id_lente   = int(txt_lente.get("1.0", tk.END).strip())
        id_usuario = int(txt_user.get("1.0", tk.END).strip())
        total      = float(txt_total.get("1.0", tk.END).strip())

        cnx = get_db_connection()
        cur = cnx.cursor()
        cur.execute("""
            UPDATE ventas
            SET id_lente = %s, id_usuario = %s, total = %s
            WHERE id_venta = %s
        """, (id_lente, id_usuario, total, id_venta))

        # vuelve a cargar los datos si lo deseas

        BuscaVenta(tree, txt_filtro)
    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", err.msg)
    finally:
        if 'cur' in locals(): cur.close()
        if 'cnx' in locals(): cnx.close()


def EliminaVenta(tree, t1, t2):
    t = t2.get("1.0", tk.END).strip()
    conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ventas WHERE id_venta=" + t)
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()
    BuscaVenta(tree, t1)

def SalirVentas(ventas):
    ventas.destroy()

# -------------------- termina Archivo/ventas -----------------------------

#---------------------------------------- lente/funciones ----------------------------------------------

def BuscaLente(tree, txt_busqueda):
    """
    Llena el TreeView con los clientes cuyo nombre (o id) coincida
    con el texto que el usuario escribió.
    """
    termino = txt_busqueda.get("1.0", tk.END).strip()

    # 1. Construir la consulta preparada (parameterized) ─ evita SQL Injection
    sql = """
        SELECT id_lente, lente, precio, disponibilidad
        FROM lentes
        WHERE lente LIKE %s OR id_lente = %s
        ORDER BY id_lente
    """

    like = f"%{termino}%"
    try:
        id_num = int(termino)        # si escribió un número, busca por id
    except ValueError:
        id_num = -1                  # -1 nunca coincide, pero mantiene el parámetro

    cnx = get_db_connection()
    cur = cnx.cursor()

    cur.execute(sql, (like, id_num))
    resultados = cur.fetchall()

    # 2. Vaciar el tree y volver a llenarlo
    for row in tree.get_children():
        tree.delete(row)

    for fila in resultados:
        tree.insert("", "end", values=fila)

    cur.close()
    cnx.close()

def AgregaLente(tree, txt_id, txt_bus, txt_nombre, txt_precio, txt_disp):
    try:
        # ── 1. Leer campos ────────────────────────────────────────────────────
        id_text   = txt_id.get("1.0", tk.END).strip().lower()
        lente   = txt_nombre.get("1.0", tk.END).strip()
        precio   = txt_precio.get("1.0", tk.END).strip()
        disponibilidad = txt_disp.get("1.0", tk.END).strip()

        # ── 2. Decidir si usamos None (NULL) o un número ──────────────────────
        if id_text == "" or id_text == "null":
            id_lente = None          # dejar que la BD asigne el AUTO_INCREMENT
        else:
            id_lente = int(id_text)  # usará el valor escrito

        # ── 3. Insertar ───────────────────────────────────────────────────────
        cnx = get_db_connection()
        cur = cnx.cursor()

        cur.execute(
            """
            INSERT INTO lentes (id_lente, lente, precio, disponibilidad)
            VALUES (%s, %s, %s, %s)
            """,
            (id_lente, lente, precio, disponibilidad)
        )

        txt_bus.delete("1.0", tk.END)          # limpiar caja de búsqueda
        BuscaLente(tree, txt_bus)            # mostrar nuevos datos

    except ValueError as ve:
            messagebox.showerror("Error", f"Datos inválidos: {ve}")
    except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error de base de datos: {err}")
    finally:
            if 'cur' in locals(): cur.close()
            if 'cnx' in locals(): cnx.close()


def ModificaLente(tree, txt_nombre, txt_precio, txt_disp):
    cnx = None
    try:
        # 1. Validar selección en Treeview
        seleccionado = tree.focus()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un cliente primero")
            return

        # 2. Obtener ID del lente desde la primera columna del Treeview
        datos = tree.item(seleccionado, "values")
        if not datos or len(datos) < 1:
            messagebox.showerror("Error", "No se pudo obtener el ID del lente")
            return

        id_lente = datos[0]  # ID está en la primera columna

        # 3. Obtener nuevos valores de los campos
        lente = txt_nombre.get("1.0", tk.END).strip()
        precio = txt_precio.get("1.0", tk.END).strip()
        disponibilidad = txt_disp.get("1.0", tk.END).strip()

        # 4. Validar que haya cambios
        if not any([lente, precio, disponibilidad]):
            messagebox.showwarning("Advertencia", "No hay cambios para guardar")
            return

        # 5. Actualizar en la BD
        cnx = get_db_connection()
        cur = cnx.cursor()

        query = """
            UPDATE lentes 
            SET lente = %s, precio = %s, disponibilidad = %s 
            WHERE id_lente = %s
        """
        cur.execute(query, (lente, precio, disponibilidad, id_lente))
        cnx.commit()

        # 6. Actualizar Treeview (opcional)
        tree.item(seleccionado, values=(
            id_lente,  # Mantener el mismo ID
            lente,     # Nuevo nombre
            precio,     # Nuevo celular
            disponibilidad    # Nuevo domicilio
        ))


    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", f"No se pudo modificar: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    finally:
        if cnx:
            cnx.close()

def EliminaLente(tree, txt_busqueda):
    """Borra el registro seleccionado en el Treeview y lo quita de la BD."""
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Eliminar", "Selecciona un cliente primero.")
        return

    item_id   = seleccion[0]
    valores   = tree.item(item_id, "values")
    id_lente = valores[0]                  # primera columna del Treeview

    try:
        cnx = get_db_connection()
        cur = cnx.cursor()
        cur.execute("DELETE FROM lentes WHERE id_lente = %s", (id_lente,))
        cnx.commit()                         # confirma la operación

        tree.delete(item_id)                 # quita la fila de la interfaz

        txt_busqueda.delete("1.0", tk.END)   # limpia la caja de búsqueda
    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", err)
    finally:
        if 'cur' in locals(): cur.close()
        if 'cnx' in locals(): cnx.close()

def ReporteLente(tree):
    with open("Lentes.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE CLIENTES<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_cliente</td><td>cliente</td><td>celular</td><td>domicilio</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td><td>" + str(v[4]) + "</td><td>" + str(v[5]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def SalirLentes(lentes):
    lentes.destroy()

#---------------------------------------- termina lente/funciones ----------------------------------------




#----------------------------------------- usuario/funciones ---------------------------------------------
def BuscaUsuario(tree, txt_busqueda):
    """
    Llena el TreeView con los usuarios cuyo nombre (o id) coincida
    con el texto que el usuario escribió.
    """
    termino = txt_busqueda.get("1.0", tk.END).strip()

    # 1. Construir la consulta preparada (parameterized) ─ evita SQL Injection
    sql = """
        SELECT id_usuario, usuario, cuenta, clave, nivel, idioma
        FROM usuarios
        WHERE usuario LIKE %s OR id_usuario = %s
        ORDER BY id_usuario
    """

    like = f"%{termino}%"
    try:
        id_num = int(termino)        # si escribió un número, busca por id
    except ValueError:
        id_num = -1                  # -1 nunca coincide, pero mantiene el parámetro

    cnx = get_db_connection()
    cur = cnx.cursor()

    cur.execute(sql, (like, id_num))
    resultados = cur.fetchall()

    # 2. Vaciar el tree y volver a llenarlo
    for row in tree.get_children():
        tree.delete(row)

    for fila in resultados:
        tree.insert("", "end", values=fila)

    cur.close()
    cnx.close()

def AgregaUsuario(tree, t1, t2,t3, t4, t5, t6, t7):

    try:
        
        usuario = str(t3.get("1.0", tk.END).strip())
        cuenta = str(t4.get("1.0", tk.END).strip())
        clave = str(t5.get("1.0", tk.END).strip())
        nivel = int(t6.get("1.0", tk.END).strip())
        idioma = int(t7.get("1.0", tk.END).strip())

        cnx = get_db_connection()
        cur = cnx.cursor()

        cur.execute(
            "INSERT INTO usuarios (usuario, cuenta, clave, nivel, idioma) VALUES (%s, %s, %s, %s, %s)",
            (usuario, cuenta, clave, nivel, idioma)
        )

        t1.delete("1.0", tk.END)  # limpiar filtro
        BuscaUsuario(tree, t1)

    except ValueError as ve:
        messagebox.showerror("Error", f"Datos inválidos: {ve}")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error de base de datos: {err}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'cnx' in locals(): cnx.close()



def ModificaUsuario(tree, txt_usuario, txt_cuenta, txt_clave, txt_nivel, txt_idioma):
    cnx = None
    try:
        # 1. Validar selección en Treeview
        seleccionado = tree.focus()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un cliente primero")
            return

        # 2. Obtener ID del cliente desde la primera columna del Treeview
        datos = tree.item(seleccionado, "values")
        if not datos or len(datos) < 1:
            messagebox.showerror("Error", "No se pudo obtener el ID del cliente")
            return

        id_usuario = datos[0]  # ID está en la primera columna

        # 3. Obtener nuevos valores de los campos
        usuario = txt_usuario.get("1.0", tk.END).strip()
        cuenta = txt_cuenta.get("1.0", tk.END).strip()
        clave = txt_clave.get("1.0", tk.END).strip()
        nivel = txt_nivel.get("1.0", tk.END).strip()
        idioma = txt_idioma.get("1.0", tk.END).strip()

        # 4. Validar que haya cambios
        if not any([usuario, cuenta, clave, nivel, idioma]):
            messagebox.showwarning("Advertencia", "No hay cambios para guardar")
            return

        # 5. Actualizar en la BD
        cnx = get_db_connection()
        cur = cnx.cursor()

        query = """
            UPDATE usuarios 
            SET usuario = %s, cuenta = %s, clave = %s, nivel = %s, idioma = %s
            WHERE id_usuario = %s
        """
        cur.execute(query, (usuario, cuenta, clave, nivel, idioma, id_usuario))
        cnx.commit()

        # 6. Actualizar Treeview (opcional)
        tree.item(seleccionado, values=(
            id_usuario,  # Mantener el mismo ID
            usuario,     # Nuevo nombre
            cuenta,     # Nuevo celular
            clave,    # Nuevo domicilio
            nivel,    # Nuevo Nivel
            idioma    # Nuevo idioma
        ))


    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", f"No se pudo modificar: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    finally:
        if cnx:
            cnx.close()

def EliminaUsuario(tree, txt_busqueda):
    """Borra el registro seleccionado en el Treeview y lo quita de la BD."""
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Eliminar", "Selecciona un cliente primero.")
        return

    item_id   = seleccion[0]
    valores   = tree.item(item_id, "values")
    id_usuario = valores[0]                  # primera columna del Treeview

    try:
        cnx = get_db_connection()
        cur = cnx.cursor()
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        cnx.commit()                         # confirma la operación

        tree.delete(item_id)                 # quita la fila de la interfaz

        txt_busqueda.delete("1.0", tk.END)   # limpia la caja de búsqueda
    except mysql.connector.Error as err:
        messagebox.showerror("Error de BD", err)
    finally:
        if 'cur' in locals(): cur.close()
        if 'cnx' in locals(): cnx.close()

def ReporteUsuarios(tree):
    with open("Usuarios.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE CLIENTES<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_cliente</td><td>cliente</td><td>celular</td><td>domicilio</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td><td>" + str(v[4]) + "</td><td>" + str(v[5]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def SalirUsuarios(usuarios):
    usuarios.destroy()
#----------------------------------------- termina usuario/funciones --------------------------------------

def Ventas():
    ventas = tk.Toplevel()
    ventas.config(width=600, height=400)
    ventas.minsize(600, 400)
    ventas.lift()                  # ① la trae al frente
    ventas.grab_set()              # ya la hace modal
    ventas.attributes('-topmost', True)   # ② la marca como “always on top”
    ventas.after_idle(              # ③ opcional: quita el “always on top”
        lambda: ventas.attributes('-topmost', False)
    )
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
    t6 = tk.Text(ventas, width=15, height=1)
    t6.place(x=290, y=330)
    t7 = tk.Text(ventas, width=20, height=1)
    t7.place(x=410, y=330)
    
    b1 = tk.Button(ventas, text="Buscar", width=10, height=1, command=lambda: BuscaVenta(tree, t1))
    b1.place(x=510, y=8)
    b1.focus_set()
    b2 = tk.Button(ventas, text="Agregar", width=10, height=1, command=lambda:
                   AgregaVenta(tree, t1, t2, t3, t4, t5, t6, t7))
    b2.place(x=10, y=360)
    b3 = tk.Button(ventas, text="Eliminar", width=10, height=1, command=lambda: EliminaVenta(tree, t1, t2))
    b3.place(x=100, y=360)
    b4 = tk.Button(ventas, text="Modificar", width=10, height=1, command=lambda: ModificaVenta(tree, t1,t4, t5, t6))
    b4.place(x=190, y=360)
    b7 = tk.Button(ventas, text="Salir", width=10, height=1, command=lambda: SalirVentas(ventas))
    b7.place(x=280, y=360)

    l1 = tk.Label(ventas, width=8, height=1, text="Id_venta")
    l1.place(x=8, y=305)
    l2 = tk.Label(ventas, width=8, height=1, text="Id_cliente")
    l2.place(x=80, y=305)
    l3 = tk.Label(ventas, width=8, height=1, text="Id_lente")
    l3.place(x=150, y=305)
    l4 = tk.Label(ventas, width=8, height=1, text="Id_usuario")
    l4.place(x=220, y=305)
    l5 = tk.Label(ventas, width=8, height=1, text="Total")
    l5.place(x=280, y=305)
    l6 = tk.Label(ventas, width=8, height=1, text="FechaHora")
    l6.place(x=410, y=305)

    canvas = tk.Canvas(ventas, width=524, height=130, bg='white')
    canvas.place(x=12, y=40)
    tree = ttk.Treeview(canvas, columns=("1", "2", "3", "4", "5", "6"), show="headings")
    tree.heading("1", text="Id_venta")
    tree.heading("2", text="Id_cliente")
    tree.heading("3", text="Id_lente")
    tree.heading("4", text="Id_usuario")
    tree.heading("5", text="Total")
    tree.heading("6", text="FechaHora")
    tree.column("1", width=90)
    tree.column("2", width=90)
    tree.column("3", width=90)
    tree.column("4", width=90)
    tree.column("5", width=124)
    tree.column("6", width=90)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select_ventas(e, tree, t2, t3, t4, t5, t6, t7))


def Clientes():
    clientes = tk.Toplevel()
    clientes.lift()                  # ① la trae al frente
    clientes.grab_set()              # ya la hace modal
    clientes.attributes('-topmost', True)   # ② la marca como “always on top”
    clientes.after_idle(              # ③ opcional: quita el “always on top”
        lambda: clientes.attributes('-topmost', False)
    )
    clientes.config(width=600, height=400)
    clientes.minsize(600,400)

    t1 = tk.Text(clientes, width=60, height=1)
    t1.place(x=12, y=12)
    t2 = tk.Text(clientes, width=8, height=1)
    t2.place(x=10, y=330)
    t3 = tk.Text(clientes, width=20, height=1)
    t3.place(x=80, y=330)
    t4 = tk.Text(clientes, width=20, height=1)
    t4.place(x=240, y=330)
    t5 = tk.Text(clientes, width=20, height=1)
    t5.place(x=400, y=330)
    
    b1 = tk.Button(clientes, text="Buscar", width=10, height=1, command=lambda: BuscaCliente(tree, t1))
    b1.place(x=510, y=8)
    b1.focus_set()
    b2 = tk.Button(clientes, text="Agregar", width=10, height=1, command=lambda:
                   AgregaCliente(tree, t1, t2, t3, t4, t5))
    b2.place(x=10, y=360)
    b3 = tk.Button(clientes, text="Eliminar", width=10, height=1, command=lambda: EliminaCliente(tree, t1))
    b3.place(x=100, y=360)
    b4 = tk.Button(clientes, text="Modificar", width=10, height=1, command=lambda: ModificaCliente(tree, t3, t4, t5))
    b4.place(x=190, y=360)
    b7 = tk.Button(clientes, text="Salir", width=10, height=1, command=lambda: SalirClientes(clientes))
    b7.place(x=280, y=360)

    l1 = tk.Label(clientes, width=8, height=1, text="Id_cliente")
    l1.place(x=8, y=305)
    l2 = tk.Label(clientes, width=8, height=1, text="Cliente")
    l2.place(x=80, y=305)
    l3 = tk.Label(clientes, width=8, height=1, text="Celular")
    l3.place(x=240, y=305)
    l4 = tk.Label(clientes, width=8, height=1, text="Domicilio")
    l4.place(x=400, y=305)
    

    canvas = tk.Canvas(clientes, width=524, height=130, bg='white')
    canvas.place(x=12, y=40)
    tree = ttk.Treeview(canvas, columns=("1", "2", "3", "4",), show="headings")
    tree.heading("1", text="Id_cliente")
    tree.heading("2", text="Cliente")
    tree.heading("3", text="Celular")
    tree.heading("4", text="Domicilio")
    tree.column("1", width=90)
    tree.column("2", width=150)
    tree.column("3", width=90)
    tree.column("4", width=245)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select_clientes(e, tree, t2, t3, t4, t5))


    clientes.title("Informacion de clientes")
    t1 = tk.Text(clientes, width=60, height=1)
    t1.place(x=12,y=12)

def Lentes():
    lentes = tk.Toplevel()
    lentes.config(width=600, height=400)
    lentes.minsize(600,400)
    lentes.lift()                  # ① la trae al frente
    lentes.grab_set()              # ya la hace modal
    lentes.attributes('-topmost', True)   # ② la marca como “always on top”
    lentes.after_idle(              # ③ opcional: quita el “always on top”
        lambda: lentes.attributes('-topmost', False)
    )

    lentes.title("Información de lentes")
    t1 = tk.Text(lentes, width=60, height=1)
    t1.place(x=12, y=12)
    t2 = tk.Text(lentes, width=8, height=1)
    t2.place(x=10, y=330)
    t3 = tk.Text(lentes, width=30, height=1)
    t3.place(x=80, y=330)
    t4 = tk.Text(lentes, width=8, height=1)
    t4.place(x=200, y=330)
    t5 = tk.Text(lentes, width=10, height=1)
    t5.place(x=270, y=330)

    
    b1 = tk.Button(lentes, text="Buscar", width=10, height=1, command=lambda: BuscaLente(tree, t1))
    b1.place(x=510, y=8)
    b1.focus_set()
    b2 = tk.Button(lentes, text="Agregar", width=10, height=1, command=lambda:
                   AgregaLente(tree, t1, t2, t3, t4, t5))
    b2.place(x=10, y=360)
    b3 = tk.Button(lentes, text="Eliminar", width=10, height=1, command=lambda: EliminaLente(tree, t1))
    b3.place(x=100, y=360)
    b4 = tk.Button(lentes, text="Modificar", width=10, height=1, command=lambda: ModificaLente(tree, t3, t4, t5))
    b4.place(x=190, y=360)
    b7 = tk.Button(lentes, text="Salir", width=10, height=1, command=lambda: SalirLentes(lentes))
    b7.place(x=280, y=360)

    l1 = tk.Label(lentes, width=8, height=1, text="Id_lente")
    l1.place(x=8, y=305)
    l2 = tk.Label(lentes, width=8, height=1, text="Lente")
    l2.place(x=80, y=305)
    l3 = tk.Label(lentes, width=8, height=1, text="Precio")
    l3.place(x=200, y=305)
    l4 = tk.Label(lentes, width=10, height=1, text="Disponibilidad")
    l4.place(x=270, y=305)
    

    canvas = tk.Canvas(lentes, width=524, height=130, bg='white')
    canvas.place(x=12, y=40)
    tree = ttk.Treeview(canvas, columns=("1", "2", "3", "4"), show="headings")
    tree.heading("1", text="Id_lente")
    tree.heading("2", text="Lente")
    tree.heading("3", text="Precio")
    tree.heading("4", text="Disponibilidad")
    tree.column("1", width=135)
    tree.column("2", width=140)
    tree.column("3", width=150)
    tree.column("4", width=150)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select_lentes(e, tree, t2, t3, t4, t5))

    lentes.title("Informacion de lentes")
    t1 = tk.Text(lentes, width=60, height=1)
    t1.place(x=12,y=12)

def Usuarios():
    usuarios = tk.Toplevel()
    usuarios.config(width=600, height=400)
    usuarios.minsize(600,400)
    usuarios.lift()                  # ① la trae al frente
    usuarios.grab_set()              # ya la hace modal
    usuarios.attributes('-topmost', True)   # ② la marca como “always on top”
    usuarios.after_idle(              # ③ opcional: quita el “always on top”
        lambda: usuarios.attributes('-topmost', False)
    )

    t1 = tk.Text(usuarios, width=60, height=1)
    t1.place(x=12, y=12)
    t2 = tk.Text(usuarios, width=8, height=1)
    t2.place(x=10, y=330)
    t3 = tk.Text(usuarios, width=30, height=1)
    t3.place(x=80, y=330)
    t4 = tk.Text(usuarios, width=8, height=1)
    t4.place(x=220, y=330)
    t5 = tk.Text(usuarios, width=8, height=1)
    t5.place(x=290, y=330)
    t6 = tk.Text(usuarios, width=8, height=1)
    t6.place(x=360, y=330)
    t7 = tk.Text(usuarios, width=8, height=1)
    t7.place(x=430, y=330)
    
    b1 = tk.Button(usuarios, text="Buscar", width=10, height=1, command=lambda: BuscaUsuario(tree, t1))
    b1.place(x=510, y=8)
    b1.focus_set()
    b2 = tk.Button(usuarios, text="Agregar", width=10, height=1, command=lambda:
                   AgregaUsuario(tree, t1, t2, t3, t4, t5, t6, t7))
    b2.place(x=10, y=360) 
    b3 = tk.Button(usuarios, text="Eliminar", width=10, height=1, command=lambda: EliminaUsuario(tree, t1))
    b3.place(x=100, y=360)
    b4 = tk.Button(usuarios, text="Modificar", width=10, height=1, command=lambda: ModificaUsuario(tree, t3 ,t4, t5, t6, t7))
    b4.place(x=190, y=360)
    b7 = tk.Button(usuarios, text="Salir", width=10, height=1, command=lambda: SalirUsuarios(usuarios))
    b7.place(x=280, y=360)

    l1 = tk.Label(usuarios, width=8, height=1, text="Id_usuario")
    l1.place(x=8, y=305)
    l2 = tk.Label(usuarios, width=8, height=1, text="usuario")
    l2.place(x=80, y=305)
    l3 = tk.Label(usuarios, width=8, height=1, text="cuenta")
    l3.place(x=220, y=305)
    l4 = tk.Label(usuarios, width=8, height=1, text="Clave")
    l4.place(x=290, y=305)
    l5 = tk.Label(usuarios, width=8, height=1, text="Nivel")
    l5.place(x=360, y=305)
    l6 = tk.Label(usuarios, width=8, height=1, text="Idioma")
    l6.place(x=430, y=305)

    canvas = tk.Canvas(usuarios, width=524, height=130, bg='white')
    canvas.place(x=12, y=40)
    tree = ttk.Treeview(canvas, columns=("1", "2", "3", "4", "5", "6"), show="headings")
    tree.heading("1", text="Id_usuario")
    tree.heading("2", text="Usuario")
    tree.heading("3", text="Cuenta")
    tree.heading("4", text="Clave")
    tree.heading("5", text="Nivel")
    tree.heading("6", text="Idioma")
    tree.column("1", width=90)
    tree.column("2", width=90)
    tree.column("3", width=90)
    tree.column("4", width=90)
    tree.column("5", width=124)
    tree.column("6", width=90)
    tree.pack(fill="both", expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select_ventas(e, tree, t2, t3, t4, t5, t6, t7))

    usuarios.title("Informacion de usuarios")
    t1 = tk.Text(usuarios, width=60, height=1)
    t1.place(x=12,y=12)

def Salir():
    root.destroy()

# ---------------------------=----- Reportes Ventas ----------------------------------------

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
    subprocess.Popen(["start", "brave", ruta], shell=True)

def GenVentas(repVentas):
    with open("ventas.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS<br><br>")
        f.write("<table border='1' cellpadding='6' cellspacing='0' bordercolor='#d0d0d0'>")
        f.write("<tr><td>id_venta</td><td>id_cliente</td><td>id_lente</td><td>id_usuario</td><td>total</td><td>fechahora</td></tr>")
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
        html_code += f.read()
    f.close()
    canvas = tk.Canvas(repVentas, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=380, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code)
    html_label.pack(padx=3, pady=3)

def SalirRepVentas(repVentas):
    repVentas.destroy()

def RepVentas():
    repVentas = tk.Toplevel()
    repVentas.geometry("600x400")
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

#-------------------------------------- Termina repVentas ---------------------------------------------

#--------------------------------------- Reportes clientes ------------------------------------------------

def ReporteClientes(tree):
    with open("clientes.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE CLIENTES<br><br>")    
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_cliente</td><td>cliente</td><td>celular</td><td>domicilio</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelClientesTree(tree):
    ReporteClientes(tree)
    ruta = os.path.abspath("clientes.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelClientes():
    ruta = os.path.abspath("clientes.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeClientesTree(tree):
    ReporteVentas(tree)
    ruta = os.path.abspath("clientes.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeClientes():
    ruta = os.path.abspath("clientes.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def SalirRepClientes(repClientes):
    repClientes.destroy()

def GenClientes(repClientes):
    with open("clientes.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE CLIENTES<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_cliente</td><td>cliente</td><td>celular</td><td>domicilio</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM clientes")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("clientes.html", "r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repClientes, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=400, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code, font=("Arial", 10))
    html_label.pack(padx=3, pady=3)

def RepClientes():
    repClientes = tk.Tk()
    repClientes.geometry("600x400")
    repClientes.title("Reporte de Clientes")
    repClientes.minsize(600,400)

    b1 = tk.Button(repClientes, text="Generar", width=10, height=1, command=lambda: GenClientes(repClientes))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(repClientes, text="Excel", width=10, height=1, command=ExcelClientes)
    b2.place(x=100, y=10)
    b3 = tk.Button(repClientes, text="Chrome", width=10, height=1, command=ChromeClientes)
    b3.place(x=190, y=10)
    b4 = tk.Button(repClientes, text="Salir", width=10, height=1, command=lambda: SalirRepClientes(repClientes))
    b4.place(x=280, y=10)
    GenClientes(repClientes)

#------------------------------------------------ termina repClientes --------------------------------------------------------

#------------------------------------------------ Reportes lentes ----------------------------------------------------------

def ReporteLentes(tree):
    with open("lentes.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE LENTES<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_lente</td><td>lente</td><td>precio</td><td>disponibilidad</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelLentesTree(tree):
    ReporteVentas(tree)
    ruta = os.path.abspath("lentes.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelLentes():
    ruta = os.path.abspath("lentes.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeLentesTree(tree):
    ReporteVentas(tree)
    ruta = os.path.abspath("lentes.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeLentes():
    ruta = os.path.abspath("lentes.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def SalirRepLentes(repLentes):
    repLentes.destroy()

def GenLentes(repLentes):
    with open("lentes.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE LENTES<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_lente</td><td>lente</td><td>precio</td><td>disponibilidad</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM lentes")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("lentes.html", "r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repLentes, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=400, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code, font=("Arial", 8))
    html_label.pack(padx=3, pady=3)

def RepLentes():
    repLentes=tk.Tk()
    repLentes.geometry("600x400")
    repLentes.title("Reporte de Productos")
    repLentes.minsize(600,400)

    b1 = tk.Button(repLentes, text="Generar", width=10, height=1, command=lambda: GenLentes(repLentes))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(repLentes, text="Excel", width=10, height=1, command=ExcelLentes)
    b2.place(x=100, y=10)
    b3 = tk.Button(repLentes, text="Chrome", width=10, height=1, command=ChromeLentes)
    b3.place(x=190, y=10)
    b4 = tk.Button(repLentes, text="Salir", width=10, height=1, command=lambda: SalirRepLentes(repLentes))
    b4.place(x=280, y=10)
    GenLentes(repLentes)

#------------------------------------------------- Termina reportes lentes -------------------------------------------------

#--------------------------------------------- Reportes usuarios --------------------------------------------------

def ReporteUsuarios(tree):
    with open("usuarios.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE USUARIOS<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_usuario</td><td>usuario</td><td>cuenta</td><td>clave</td><td>nivel</td><td>idioma</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td><td>" + str(v[4]) + "</td><td>" + str(v[5]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelUsuariosTree(tree):
    ReporteUsuarios(tree)
    ruta = os.path.abspath("usuarios.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelUsuarios():
    ruta = os.path.abspath("usuarios.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeUsuariosTree(tree):
    ReporteVentas(tree)
    ruta = os.path.abspath("usuarios.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeUsuarios():
    ruta = os.path.abspath("usuarios.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def SalirRepUsuarios(repUsuarios):
    repUsuarios.destroy()

def GenUsuarios(repUsuarios):
    with open("usuarios.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE USUARIOS<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_usuario</td><td>usuario</td><td>cuenta</td><td>clave</td><td>nivel</td><td>idioma</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td><td>" + str(v[4]) + "</td><td>" + str(v[5]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("usuarios.html", "r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repUsuarios, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=400, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code, font=("Arial", 8))
    html_label.pack(padx=3, pady=3)

def RepUsuarios():
    repUsuarios=tk.Tk()
    repUsuarios.geometry("600x400")
    repUsuarios.title("Reporte de usuarios")
    repUsuarios.minsize(600,400)

    b1 = tk.Button(repUsuarios, text="Generar", width=10, height=1, command=lambda: GenUsuarios(repUsuarios))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(repUsuarios, text="Excel", width=10, height=1, command=ExcelUsuarios)
    b2.place(x=100, y=10)
    b3 = tk.Button(repUsuarios, text="Chrome", width=10, height=1, command=ChromeUsuarios)
    b3.place(x=190, y=10)
    b4 = tk.Button(repUsuarios, text="Salir", width=10, height=1, command=lambda: SalirRepUsuarios(repUsuarios))
    b4.place(x=280, y=10)
    GenUsuarios(repUsuarios)
#-------------------------------------------------- Termina reportes de usuarios --------------------------------------


#---------------------------------------------- Reportes ventas por cliente ------------------------------------------

def ReporteVpC(tree):
    with open("ventasporcliente.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS POR CLIENTE<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_cliente</td><td>cliente</td><td>veces</td><td>total</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelVpCTree(tree):
    ReporteVpC(tree)
    ruta = os.path.abspath("ventasporcliente.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelVpC():
    ruta = os.path.abspath("ventasporcliente.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeVpCTree(tree):
    ReporteVpC(tree)
    ruta = os.path.abspath("ventasporcliente.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeVpC():
    ruta = os.path.abspath("ventasporcliente.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def SalirRepVpC(repVpC):
    repVpC.destroy()

def GenVpC(repVpC):
    with open("ventasporcliente.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS POR CLIENTE<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_cliente</td><td>cliente</td><td>veces</td><td>total</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("select clientes.id_cliente, cliente, veces, total from clientes join(select id_cliente, count(id_venta) veces, sum(total) total from ventas group by id_cliente)t on t.id_cliente=clientes.id_cliente;")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("ventasporcliente.html", "r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repVpC, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=400, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code, font=("Arial", 8))
    html_label.pack(padx=3, pady=3)

def repVentasPorCliente():
    rVentasPorCliente=tk.Tk()
    rVentasPorCliente.geometry("600x400")
    rVentasPorCliente.title("Reporte de Ventas por Cliente")
    rVentasPorCliente.minsize(600,400)


    b1 = tk.Button(rVentasPorCliente, text="Generar", width=10, height=1, command=lambda: GenVpC(rVentasPorCliente))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(rVentasPorCliente, text="Excel", width=10, height=1, command=ExcelVpC)
    b2.place(x=100, y=10)
    b3 = tk.Button(rVentasPorCliente, text="Chrome", width=10, height=1, command=ChromeVpC)
    b3.place(x=190, y=10)
    b4 = tk.Button(rVentasPorCliente, text="Salir", width=10, height=1, command=lambda: SalirRepVpC(rVentasPorCliente))
    b4.place(x=280, y=10)
    GenVpC(rVentasPorCliente)

#---------------------------------------------- Termina Reportes ventas por cliente ------------------------------------------

#------------------------------------------------- Reportes de vetas por producto ------------------------------------------

def ReporteVpL(tree):
    with open("ventasporlente.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS POR LENTE<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_lente</td><td>lente</td><td>veces</td><td>total</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelVpLTree(tree):
    ReporteVpL(tree)
    ruta = os.path.abspath("ventasporlente.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelVpL():
    ruta = os.path.abspath("ventasporlente.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeVpLTree(tree):
    ReporteVpL(tree)
    ruta = os.path.abspath("ventasporlente.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeVpL():
    ruta = os.path.abspath("ventasporlente.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def SalirRepVpL(repVpL):
    repVpL.destroy()

def GenVpL(repVpL):
    with open("ventasporlente.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS POR LENTE<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_lente</td><td>lente</td><td>veces</td><td>total</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("select lentes.id_lente, lente, veces, total from lentes join(select id_lente, count(id_venta) veces, sum(total) total from ventas group by id_lente)t on t.id_lente=lentes.id_lente;")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("ventasporlente.html","r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repVpL, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=400, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code, font=("Arial", 8))
    html_label.pack(padx=3, pady=3)

def repVentasPorLente():
    rVentasPorLente=tk.Tk()
    rVentasPorLente.geometry("600x400")
    rVentasPorLente.title("Reporte de Ventas por Lente")
    rVentasPorLente.minsize(600,400)

    b1 = tk.Button(rVentasPorLente, text="Generar", width=10, height=1, command=lambda: GenVpL(rVentasPorLente))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(rVentasPorLente, text="Excel", width=10, height=1, command=ExcelVpL)
    b2.place(x=100, y=10)
    b3 = tk.Button(rVentasPorLente, text="Chrome", width=10, height=1, command=ChromeVpL)
    b3.place(x=190, y=10)
    b4 = tk.Button(rVentasPorLente, text="Salir", width=10, height=1, command=lambda: SalirRepVpL(rVentasPorLente))
    b4.place(x=280, y=10)
    GenVpL(rVentasPorLente)

# --------------------------------------------------- Termina Reportes de ventas por cliente -----------------------------------------

#------------------------------------------------ Reportes de ventas por Usuario ------------------------------------------------

def ReporteVpU(tree):
    with open("ventasporusuario.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS POR USUARIO<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_usuario</td><td>usuario</td><td>veces</td><td>total</td></tr>")
        for r in tree.get_children():
            v = tree.item(r)["values"]
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) 
                    + "</td><td>" + str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        f.close()

def ExcelVpUTree(tree):
    ReporteVpU(tree)
    ruta = os.path.abspath("ventasporusuario.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ExcelVpU():
    ruta = os.path.abspath("ventasporusuario.html")
    subprocess.Popen(["start", "excel", ruta], shell=True)

def ChromeVpUTree(tree):
    ReporteVpU(tree)
    ruta = os.path.abspath("ventasporusuariuo.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def ChromeVpU():
    ruta = os.path.abspath("ventasporusuario.html")
    subprocess.Popen(["start", "brave", ruta], shell=True)

def SalirRepVpU(repVpU):
    repVpU.destroy()

def GenVpU(repVpU):
    with open("ventasporusuario.html", "w", encoding="utf-8") as f:
        f.write("<html>REPORTE DE VENTAS POR USUARIO<br><br>")
        f.write("<table border=1 cellspacing=0>")
        f.write("<tr><td>id_usuario</td><td>usuario</td><td>veces</td><td>total</td></tr>")
        conexion = mysql.connector.connect(host="localhost", port="3307", user="root", password="", database="optica")
        cursor = conexion.cursor()
        cursor.execute("select usuarios.id_usuario, usuario, veces, total from usuarios join(select id_usuario, count(id_venta) veces, sum(total) total from ventas group by id_usuario)t on t.id_usuario=usuarios.id_usuario;")
        resultados = cursor.fetchall()
        for v in resultados:
            f.write("<tr><td>" + str(v[0]) + "</td><td>" + str(v[1]) + "</td><td>" + str(v[2]) + "</td><td>" +
                    str(v[3]) + "</td></tr>")
        f.write("</table></html>")
        cursor.close()
        conexion.close()
        f.close()
    html_code=""
    with open("ventasporusuario.html","r", encoding="utf-8") as f:
        html_code += f.readline()
    f.close()
    canvas = tk.Canvas(repVpU, width=570, height=380)
    canvas.place(x=12, y=40)
    frame = tk.Frame(canvas, width=570, height=400, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    html_label = HTMLLabel(frame, html=html_code, font=("Arial", 8))
    html_label.pack(padx=3, pady=3)


def repVentasPorUsuario():
    rVentasPorUsuario=tk.Tk()
    rVentasPorUsuario.geometry("600x400")
    rVentasPorUsuario.title("Reporte de Ventas por Usuario")
    rVentasPorUsuario.minsize(600, 400)

    b1 = tk.Button(rVentasPorUsuario, text="Generar", width=10, height=1, command=lambda: GenVpU(rVentasPorUsuario))
    b1.place(x=10, y=10)
    b1.focus_set()
    b2 = tk.Button(rVentasPorUsuario, text="Excel", width=10, height=1, command=ExcelVpU)
    b2.place(x=100, y=10)
    b3 = tk.Button(rVentasPorUsuario, text="Chrome", width=10, height=1, command=ChromeVpU)
    b3.place(x=190, y=10)
    b4 = tk.Button(rVentasPorUsuario, text="Salir", width=10, height=1, command=lambda: SalirRepVpL(rVentasPorUsuario))
    b4.place(x=280, y=10)
    GenVpU(rVentasPorUsuario)

#------------------------------------------------ Termina Reportes de ventas por usuario ----------------------------------------
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
rep.add_command(label="Reporte de Ventas por Lente", command=repVentasPorLente)
rep.add_command(label="Reporte de Ventas por Usuario", command=repVentasPorUsuario)
root.config(menu=archivo)
root.mainloop()


import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from db import MySQLClient

APP_TITLE = "Sistema de Generación de Proformas"

def resource_path(*parts):
    """
    Devuelve una ruta válida tanto en desarrollo como en .exe (PyInstaller).
    Busca dentro de sys._MEIPASS cuando está congelado (--onefile).
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)

def load_config(path="config.json"):
    """
    Carga el archivo de configuración JSON (host/port/user/password/database).
    Si no existe, devuelve un diccionario con valores por defecto.
    """
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"host": "localhost", "port": 3306, "user": "root", "password": "root", "database": "sistemaproforma"} # Cambiar Datos de path respectivamente.

def save_config(cfg, path="config.json"):
    """Guarda el diccionario de configuración en disco (UTF-8, identado)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def _init_database(self):
    sql_dir = resource_path("sql")
    files = [
        ("schema_seed.sql", False),
        ("procedures_all.sql", True),
        ("triggers.sql", True),
    ]
    ok, out = self.client.run_sql(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema='coteind' AND table_name='Empleado';",
        use_db=False
    )
    if ok and out.strip() == "1":
        ok2, out2 = self.client.run_sql("SELECT COUNT(*) FROM Empleado;", use_db=True)
        if ok2 and out2 and int(out2.strip().splitlines()[0]) > 0:
            files = [f for f in files if f[0] != "schema_seed.sql"]

    for fname, use_db in files:
        path = os.path.join(sql_dir, fname)
        if os.path.exists(path):
            okf, outf = self.client.run_sql_file(path, use_db=use_db)
            if not okf:
                messagebox.showerror("Inicialización SQL", f"Error en {fname}:\n{outf}")

class ConnectionWindow(tk.Toplevel):
    """
    Ventana modal de conexión.
    Permite editar parámetros de conexión, probarlos y continuar si son válidos.
    """
    def __init__(self, master, on_connected):
        super().__init__(master)
        self.title(f"{APP_TITLE} · Conexión")
        self.resizable(False, False)
        self.on_connected = on_connected
        self.cfg = load_config()
        self._build()

    def _build(self):
        """Construye los controles de la ventana de conexión."""
        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Host:").grid(row=0, column=0, sticky="w")
        self.e_host = ttk.Entry(frm, width=30)
        self.e_host.insert(0, self.cfg.get("host", "localhost"))
        self.e_host.grid(row=0, column=1, pady=2, sticky="ew")

        ttk.Label(frm, text="Puerto:").grid(row=1, column=0, sticky="w")
        self.e_port = ttk.Entry(frm, width=10)
        self.e_port.insert(0, str(self.cfg.get("port", 3306)))
        self.e_port.grid(row=1, column=1, pady=2, sticky="w")

        ttk.Label(frm, text="Usuario:").grid(row=2, column=0, sticky="w")
        self.e_user = ttk.Entry(frm, width=30)
        self.e_user.insert(0, self.cfg.get("user", "root"))
        self.e_user.grid(row=2, column=1, pady=2, sticky="ew")

        ttk.Label(frm, text="Contraseña (puede ir vacía):").grid(row=3, column=0, sticky="w")
        self.e_pwd = ttk.Entry(frm, show="*", width=30)
        self.e_pwd.insert(0, self.cfg.get("password", ""))
        self.e_pwd.grid(row=3, column=1, pady=2, sticky="ew")

        ttk.Label(frm, text="Base de Datos:").grid(row=4, column=0, sticky="w")
        self.e_db = ttk.Entry(frm, width=30)
        self.e_db.insert(0, self.cfg.get("database", "sistemaproforma"))
        self.e_db.grid(row=4, column=1, pady=2, sticky="ew")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=8, sticky="e")
        ttk.Button(btns, text="Probar conexión", command=self.test_conn).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Guardar y continuar", command=self.save_and_continue).grid(row=0, column=1, padx=4)

    def test_conn(self):
        """Ejecuta un SELECT 1 para validar parámetros. Muestra diálogo con el resultado."""
        client = MySQLClient(
            host=self.e_host.get().strip(),
            port=int(self.e_port.get().strip()),
            user=self.e_user.get().strip(),
            password=self.e_pwd.get(),
            database=self.e_db.get().strip()
        )
        ok, out = client.test_connection()
        if ok:
            messagebox.showinfo("Conexión", "¡Conexión exitosa!\nResultado:\n" + (out or "OK"))
        else:
            messagebox.showerror("Conexión", "Error de conexión:\n" + (out or "Desconocido"))

    def save_and_continue(self):
        """Persiste la config, cierra la ventana y notifica al callback `on_connected`."""
        cfg = {
            "host": self.e_host.get().strip(),
            "port": int(self.e_port.get().strip()),
            "user": self.e_user.get().strip(),
            "password": self.e_pwd.get(),
            "database": self.e_db.get().strip()
        }
        save_config(cfg)
        self.destroy()
        self.on_connected(cfg)

class LoginWindow(tk.Toplevel):
    """
    Ventana de login.
    El usuario escribe solo los 4 dígitos; el prefijo 'E' se fija y se valida.
    """
    def __init__(self, master, cfg, on_login_ok):
        super().__init__(master)
        self.title(f"{APP_TITLE} · Login")
        self.resizable(False, False)
        self.cfg = cfg
        self.client = MySQLClient(**cfg)
        self.on_login_ok = on_login_ok
        self._build()

    def _build(self):
        """Construye controles del formulario de login."""
        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Código (5) EXXXX").grid(row=0, column=0, sticky="w")
        code_frame = ttk.Frame(frm)
        code_frame.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        self.e_prefix = ttk.Entry(code_frame, width=2)
        self.e_prefix.insert(0, "E")
        self.e_prefix.configure(state="disabled")
        self.e_prefix.grid(row=0, column=0)

        vcmd = (self.register(self._validate_digits_len4), "%P")
        self.e_codigo_num = ttk.Entry(code_frame, width=6, validate="key", validatecommand=vcmd)
        self.e_codigo_num.grid(row=0, column=1)

        ttk.Button(frm, text="Ingresar", command=self._do_login).grid(row=1, column=1, sticky="e")

    def _validate_digits_len4(self, P):
        """Valida que solo se ingresen dígitos y como máximo 4 caracteres."""
        return P.isdigit() and len(P) <= 4

    def _compose_code(self, digits):
        """Compone el código completo (E####), rellenando con ceros si falta longitud."""
        digits = (digits or "").strip()
        if not digits.isdigit():
            return None
        if len(digits) < 4:
            digits = digits.zfill(4)
        return "E" + digits

    def _do_login(self):
        """Consulta el nombre del empleado por código; si existe, continúa a la app."""
        cod = self._compose_code(self.e_codigo_num.get())
        if not cod:
            messagebox.showwarning("Login", "Ingrese solo números (hasta 4).")
            return
        sql = f"SELECT Nombre FROM Empleado WHERE Codigo = {self.client.esc(cod)} LIMIT 1;"
        nombre = self.client.select_scalar(sql)
        if nombre:
            self.destroy()
            self.on_login_ok(self.cfg, cod, nombre)
        else:
            messagebox.showerror("Login", f"Código no encontrado: {cod}")

class MainApp(tk.Tk):
    """
    Ventana principal (Tk).
    Orquesta la conexión, inicialización SQL, login y construcción de pestañas (CRUD + reportes).
    """
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x760")
        self.minsize(1100, 700)
        self.cfg = None
        self.client = None
        self.current_user_code = None
        self.current_user_name = None
        # Abre primero la ventana de conexión
        self.after(100, self._open_connection_window)
    
    def _init_database(self):
        """
        Ejecuta los .sql de /sql:
        - schema_seed.sql (solo si la tabla Empleado existe y no está vacía se omite el seed)
        - procedures_all.sql
        - triggers.sql
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sql_dir = os.path.join(base_dir, "sql")
        files = [
            ("schema_seed.sql", False),   # se ejecuta sin forzar -D porque el script crea/usa el schema
            ("procedures_all.sql", True), # ya con -D
            ("triggers.sql", True)
        ]
        # Detecta si Empleado existe y tiene filas; si es así, evita correr el seed para no duplicar
        ok, out = self.client.run_sql(
            "SELECT COUNT(*) "
            "FROM information_schema.tables "
            "WHERE table_schema='sistemaproforma' AND table_name='Empleado';",
            use_db=False
        )
        if ok and out.strip() == "1":
            ok2, out2 = self.client.run_sql("SELECT COUNT(*) FROM Empleado;", use_db=True)
            if ok2 and out2 and int(out2.strip().splitlines()[0]) > 0:
                files = [f for f in files if f[0] != "schema_seed.sql"]

        # Ejecuta cada archivo
        for fname, use_db in files:
            path = os.path.join(sql_dir, fname)
            if os.path.exists(path):
                okf, outf = self.client.run_sql_file(path, use_db=use_db)
                if not okf:
                    messagebox.showerror("Inicialización SQL", f"Error en {fname}:\n{outf}")

    def _open_connection_window(self):
        """Lanza la ventana de conexión y pasa el callback `_on_connected`."""
        ConnectionWindow(self, self._on_connected)

    def _on_connected(self, cfg):
        """
        Recibe la config confirmada, crea MySQLClient,
        inicializa la BD (scripts SQL) y abre la ventana de login.
        """
        self.cfg = cfg
        self.client = MySQLClient(**cfg)
        self._init_database()
        LoginWindow(self, cfg, self._on_login_ok)

    def _on_login_ok(self, cfg, user_code, user_name):
        """Callback posterior al login exitoso: persiste contexto de usuario y construye UI."""
        self.cfg = cfg
        self.client = MySQLClient(**cfg)
        self.current_user_code = user_code
        self.current_user_name = user_name
        self._build_ui()

    def _build_ui(self):
        """Arma la barra superior y el Notebook con todas las pestañas de trabajo."""
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text=f"Conectado a {self.cfg['database']}@{self.cfg['host']}:{self.cfg['port']}").pack(side="left")
        ttk.Label(top, text=f" | Usuario BD: {self.cfg['user']}").pack(side="left")
        ttk.Label(top, text=f" | Empleado: {self.current_user_code} - {self.current_user_name}").pack(side="right")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Pestañas
        tab_empleados = ttk.Frame(nb)
        tab_inventario = ttk.Frame(nb)
        tab_proveedores = ttk.Frame(nb)
        tab_empresas = ttk.Frame(nb)
        tab_oc = ttk.Frame(nb)
        tab_proforma = ttk.Frame(nb)
        tab_reportes = ttk.Frame(nb)

        nb.add(tab_empleados, text="Empleados")
        nb.add(tab_inventario, text="Inventario")
        nb.add(tab_proveedores, text="Proveedores")
        nb.add(tab_empresas, text="Empresas (Clientes)")
        nb.add(tab_oc, text="Orden de Compra")
        nb.add(tab_proforma, text="Proforma")
        nb.add(tab_reportes, text="Reportes")

        # Construcción de cada tab
        self._build_tab_empleados(tab_empleados)
        self._build_tab_inventario(tab_inventario)
        self._build_tab_proveedores(tab_proveedores)
        self._build_tab_empresas(tab_empresas)
        self._build_tab_oc(tab_oc)
        self._build_tab_proforma(tab_proforma)
        self._build_tab_reportes(tab_reportes)

    # -------- Empleados -------------------------------------------------------
    def _build_tab_empleados(self, parent):
        """UI y eventos de CRUD de Empleado (y Contacto_Empleado)."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # Formulario
        fr_form = ttk.LabelFrame(parent, text="Registro / Edición", padding=10)
        fr_form.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        ttk.Label(fr_form, text="Código (5) EXXXX").grid(row=0, column=0, sticky="e")
        code_frame = ttk.Frame(fr_form)
        code_frame.grid(row=0, column=1, sticky="w", pady=2)
        self.emp_prefix = ttk.Entry(code_frame, width=2)
        self.emp_prefix.insert(0, "E")
        self.emp_prefix.configure(state="disabled")
        self.emp_prefix.grid(row=0, column=0)
        vcmd = (self.register(self._validate_digits_len4_global), "%P")
        self.e_emp_cod_num = ttk.Entry(code_frame, width=6, validate="key", validatecommand=vcmd)
        self.e_emp_cod_num.grid(row=0, column=1)

        ttk.Label(fr_form, text="Nombre").grid(row=1, column=0, sticky="e")
        self.e_emp_nom = ttk.Entry(fr_form, width=40)
        self.e_emp_nom.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Teléfono").grid(row=2, column=0, sticky="e")
        self.e_emp_tel = ttk.Entry(fr_form, width=20)
        self.e_emp_tel.grid(row=2, column=1, sticky="w", pady=2)

        fr_btns = ttk.Frame(fr_form)
        fr_btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=6)
        ttk.Button(fr_btns, text="Crear", command=self._registrar_empleado).grid(row=0, column=0, padx=4)
        ttk.Button(fr_btns, text="Actualizar", command=self._actualizar_empleado).grid(row=0, column=1, padx=4)
        ttk.Button(fr_btns, text="Eliminar", command=self._eliminar_empleado).grid(row=0, column=2, padx=4)

        # Tabla
        fr_tbl = ttk.LabelFrame(parent, text="Listado", padding=10)
        fr_tbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(0, weight=1)

        cols = ("Codigo", "Nombre", "Telefono")
        self.tv_emp = ttk.Treeview(fr_tbl, columns=cols, show="headings", height=12)
        for c in cols:
            self.tv_emp.heading(c, text=c)
            self.tv_emp.column(c, width=150, anchor="w")
        self.tv_emp.pack(fill="both", expand=True)
        self.tv_emp.bind("<<TreeviewSelect>>", self._emp_on_select)
        ttk.Button(fr_tbl, text="Refrescar", command=self._cargar_empleados).pack(anchor="e", pady=6)

        self._cargar_empleados()

    def _validate_digits_len4_global(self, P):
        """Valida entradas numéricas de 0–4 dígitos para códigos E####."""
        return P.isdigit() and len(P) <= 4

    def _compose_emp_code(self):
        """Construye el código E#### desde el campo numérico del formulario."""
        digits = (self.e_emp_cod_num.get() or "").strip()
        if not digits.isdigit():
            return None
        if len(digits) < 4:
            digits = digits.zfill(4)
        return "E" + digits

    def _emp_on_select(self, _evt):
        """Rellena el formulario con la fila seleccionada en la tabla."""
        sel = self.tv_emp.selection()
        if not sel:
            return
        vals = self.tv_emp.item(sel[0], "values")
        if len(vals) >= 3:
            code = vals[0]
            self.e_emp_cod_num.delete(0, tk.END)
            self.e_emp_cod_num.insert(0, code[1:])
            self.e_emp_nom.delete(0, tk.END)
            self.e_emp_nom.insert(0, vals[1])
            self.e_emp_tel.delete(0, tk.END)
            self.e_emp_tel.insert(0, vals[2])

    def _cargar_empleados(self):
        """Consulta y vuelca Empleado + Contacto_Empleado en la tabla."""
        for i in self.tv_emp.get_children():
            self.tv_emp.delete(i)
        sql = """
        SELECT e.Codigo, e.Nombre, IFNULL(c.Telefono,'')
        FROM Empleado e
        LEFT JOIN Contacto_Empleado c ON c.Codigo_Empleado = e.Codigo
        ORDER BY e.Codigo;
        """
        rows = self.client.select_rows(sql)
        for r in rows:
            self.tv_emp.insert("", tk.END, values=r)

    def _registrar_empleado(self):
        """Invoca sp_Agregar_Empleado."""
        cod = self._compose_emp_code()
        nom = self.e_emp_nom.get().strip()
        tel = self.e_emp_tel.get().strip()
        if not cod or not nom or not tel:
            messagebox.showwarning("Empleado", "Complete Código, Nombre y Teléfono.")
            return
        sql = "CALL sp_Agregar_Empleado(" + f"{self.client.esc(cod)}, {self.client.esc(nom)}, {self.client.esc(tel)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Empleado", "Creado.")
            self._cargar_empleados()
        else:
            messagebox.showerror("Empleado", out)

    def _actualizar_empleado(self):
        """Invoca sp_Actualizar_Empleado."""
        cod = self._compose_emp_code()
        nom = self.e_emp_nom.get().strip()
        tel = self.e_emp_tel.get().strip()
        if not cod or not nom or not tel:
            messagebox.showwarning("Empleado", "Complete Código, Nombre y Teléfono.")
            return
        sql = "CALL sp_Actualizar_Empleado(" + f"{self.client.esc(cod)}, {self.client.esc(nom)}, {self.client.esc(tel)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Empleado", "Actualizado.")
            self._cargar_empleados()
        else:
            messagebox.showerror("Empleado", out)

    def _eliminar_empleado(self):
        """Invoca sp_Eliminar_Empleado (con protección para el usuario logueado)."""
        cod = self._compose_emp_code()
        if not cod:
            messagebox.showwarning("Empleado", "Seleccione un empleado.")
            return
        if cod == self.current_user_code:
            messagebox.showwarning("Empleado", "No puedes eliminar al usuario con sesión activa.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar empleado {cod}?"):
            sql = "CALL sp_Eliminar_Empleado(" + f"{self.client.esc(cod)}" + ");"
            ok, out = self.client.call_sp(sql)
            if ok:
                messagebox.showinfo("Empleado", "Eliminado.")
                self._cargar_empleados()
            else:
                messagebox.showerror("Empleado", out)

    # -------- Inventario (Repuesto) ------------------------------------------
    def _build_tab_inventario(self, parent):
        """UI y eventos de CRUD de Repuesto + ajuste de stock."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # Formulario crear/actualizar/eliminar
        fr_left = ttk.LabelFrame(parent, text="Repuesto – Crear / Actualizar", padding=10)
        fr_left.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        ttk.Label(fr_left, text="Nro_Parte").grid(row=0, column=0, sticky="e")
        self.e_rep_np = ttk.Entry(fr_left, width=18)
        self.e_rep_np.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(fr_left, text="Descripción").grid(row=1, column=0, sticky="e")
        self.e_rep_desc = ttk.Entry(fr_left, width=35)
        self.e_rep_desc.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(fr_left, text="Marca").grid(row=2, column=0, sticky="e")
        self.e_rep_marca = ttk.Entry(fr_left, width=20)
        self.e_rep_marca.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(fr_left, text="Status").grid(row=3, column=0, sticky="e")
        self.e_rep_status = ttk.Entry(fr_left, width=12)
        self.e_rep_status.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Label(fr_left, text="Precio").grid(row=4, column=0, sticky="e")
        self.e_rep_precio = ttk.Entry(fr_left, width=12)
        self.e_rep_precio.grid(row=4, column=1, sticky="w", pady=2)

        ttk.Label(fr_left, text="Cantidad").grid(row=5, column=0, sticky="e")
        self.e_rep_cant = ttk.Entry(fr_left, width=12)
        self.e_rep_cant.grid(row=5, column=1, sticky="w", pady=2)

        fr_btns_l = ttk.Frame(fr_left)
        fr_btns_l.grid(row=6, column=0, columnspan=2, sticky="e", pady=6)
        ttk.Button(fr_btns_l, text="Crear", command=self._agregar_repuesto).grid(row=0, column=0, padx=4)
        ttk.Button(fr_btns_l, text="Actualizar", command=self._actualizar_repuesto).grid(row=0, column=1, padx=4)
        ttk.Button(fr_btns_l, text="Eliminar", command=self._eliminar_repuesto).grid(row=0, column=2, padx=4)

        # Ajuste stock
        fr_right = ttk.LabelFrame(parent, text="Ajuste de Stock", padding=10)
        fr_right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        ttk.Label(fr_right, text="Nro_Parte").grid(row=0, column=0, sticky="e")
        self.e_adj_np = ttk.Entry(fr_right, width=18)
        self.e_adj_np.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(fr_right, text="Cantidad (+/-)").grid(row=1, column=0, sticky="e")
        self.e_adj_cant = ttk.Entry(fr_right, width=12)
        self.e_adj_cant.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(fr_right, text="Operación").grid(row=2, column=0, sticky="e")
        self.op_var = tk.StringVar(value="SUMA")
        self.cmb_op = ttk.Combobox(fr_right, textvariable=self.op_var, values=["SUMA", "RESTA"], state="readonly", width=10)
        self.cmb_op.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Button(fr_right, text="Aplicar Ajuste", command=self._ajustar_stock).grid(row=3, column=1, sticky="e", pady=6)

        # Tabla inventario
        fr_tbl = ttk.LabelFrame(parent, text="Inventario (vista rápida)", padding=10)
        fr_tbl.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(1, weight=1)

        cols = ("Nro_Parte", "Descripcion", "Marca", "Status", "Precio_Unitario", "Cantidad")
        self.tv_inv = ttk.Treeview(fr_tbl, columns=cols, show="headings", height=10)
        for c in cols:
            self.tv_inv.heading(c, text=c)
            self.tv_inv.column(c, width=140, anchor="w")
        self.tv_inv.pack(fill="both", expand=True)
        self.tv_inv.bind("<<TreeviewSelect>>", self._rep_on_select)
        ttk.Button(fr_tbl, text="Refrescar", command=self._cargar_inventario).pack(anchor="e", pady=6)

        self._cargar_inventario()

    def _rep_on_select(self, _evt):
        """Carga en el formulario el repuesto seleccionado en la tabla."""
        sel = self.tv_inv.selection()
        if not sel:
            return
        vals = self.tv_inv.item(sel[0], "values")
        if len(vals) >= 6:
            self.e_rep_np.delete(0, tk.END); self.e_rep_np.insert(0, vals[0])
            self.e_rep_desc.delete(0, tk.END); self.e_rep_desc.insert(0, vals[1])
            self.e_rep_marca.delete(0, tk.END); self.e_rep_marca.insert(0, vals[2])
            self.e_rep_status.delete(0, tk.END); self.e_rep_status.insert(0, vals[3])
            self.e_rep_precio.delete(0, tk.END); self.e_rep_precio.insert(0, vals[4])
            self.e_rep_cant.delete(0, tk.END); self.e_rep_cant.insert(0, vals[5])

    def _agregar_repuesto(self):
        """Invoca sp_Agregar_Repuesto tras validar tipos básicos."""
        npart = self.e_rep_np.get().strip()
        desc = self.e_rep_desc.get().strip()
        marca = self.e_rep_marca.get().strip()
        status = self.e_rep_status.get().strip()
        precio = self.e_rep_precio.get().strip()
        cant = self.e_rep_cant.get().strip()
        if not (npart and desc and marca and status and precio and cant):
            messagebox.showwarning("Repuesto", "Complete todos los campos.")
            return
        try:
            float(precio); int(cant)
        except:
            messagebox.showwarning("Repuesto", "Precio decimal y Cantidad entero.")
            return
        sql = "CALL sp_Agregar_Repuesto(" + f"{self.client.esc(npart)}, {self.client.esc(desc)}, {self.client.esc(marca)}, {self.client.esc(status)}, {precio}, {cant}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Repuesto", "Creado.")
            self._cargar_inventario()
        else:
            messagebox.showerror("Repuesto", out)

    def _actualizar_repuesto(self):
        """Invoca sp_Actualizar_Repuesto."""
        npart = self.e_rep_np.get().strip()
        desc = self.e_rep_desc.get().strip()
        marca = self.e_rep_marca.get().strip()
        status = self.e_rep_status.get().strip()
        precio = self.e_rep_precio.get().strip()
        cant = self.e_rep_cant.get().strip()
        if not (npart and desc and marca and status and precio and cant):
            messagebox.showwarning("Repuesto", "Complete todos los campos.")
            return
        try:
            float(precio); int(cant)
        except:
            messagebox.showwarning("Repuesto", "Precio decimal y Cantidad entero.")
            return
        sql = "CALL sp_Actualizar_Repuesto(" + f"{self.client.esc(npart)}, {self.client.esc(desc)}, {self.client.esc(marca)}, {self.client.esc(status)}, {precio}, {cant}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Repuesto", "Actualizado.")
            self._cargar_inventario()
        else:
            messagebox.showerror("Repuesto", out)

    def _eliminar_repuesto(self):
        """Invoca sp_Eliminar_Repuesto con confirmación."""
        npart = self.e_rep_np.get().strip()
        if not npart:
            messagebox.showwarning("Repuesto", "Seleccione un repuesto.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar repuesto {npart}?"):
            sql = "CALL sp_Eliminar_Repuesto(" + f"{self.client.esc(npart)}" + ");"
            ok, out = self.client.call_sp(sql)
            if ok:
                messagebox.showinfo("Repuesto", "Eliminado.")
                self._cargar_inventario()
            else:
                messagebox.showerror("Repuesto", out)

    def _ajustar_stock(self):
        """Invoca sp_Actualizar_Stock (SUMA/RESTA) validando cantidad entera."""
        npart = self.e_adj_np.get().strip()
        cant = self.e_adj_cant.get().strip()
        op = (self.op_var.get() or "SUMA").upper()
        if not (npart and cant):
            messagebox.showwarning("Stock", "Complete Nro_Parte y Cantidad.")
            return
        try:
            icant = int(cant)
        except:
            messagebox.showwarning("Stock", "Cantidad entero.")
            return
        sql = "CALL sp_Actualizar_Stock(" + f"{self.client.esc(npart)}, {icant}, {self.client.esc(op)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Stock", "Ajuste aplicado.")
            self._cargar_inventario()
        else:
            messagebox.showerror("Stock", out)

    def _cargar_inventario(self):
        """Consulta y pinta la tabla de repuestos."""
        for i in self.tv_inv.get_children():
            self.tv_inv.delete(i)
        sql = "SELECT Nro_Parte, Descripcion, Marca, Status, Precio_Unitario, Cantidad FROM Repuesto ORDER BY Descripcion;"
        rows = self.client.select_rows(sql)
        for r in rows:
            self.tv_inv.insert("", tk.END, values=r)

    # -------- Proveedores -----------------------------------------------------
    def _build_tab_proveedores(self, parent):
        """UI y eventos de CRUD de Proveedor (con teléfono y email)."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        fr_form = ttk.LabelFrame(parent, text="Proveedor – Crear / Actualizar", padding=10)
        fr_form.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        ttk.Label(fr_form, text="RUC (11)").grid(row=0, column=0, sticky="e")
        self.e_prv_ruc = ttk.Entry(fr_form, width=18)
        self.e_prv_ruc.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Razón Social").grid(row=1, column=0, sticky="e")
        self.e_prv_raz = ttk.Entry(fr_form, width=40)
        self.e_prv_raz.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Dirección").grid(row=2, column=0, sticky="e")
        self.e_prv_dir = ttk.Entry(fr_form, width=40)
        self.e_prv_dir.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Teléfono").grid(row=3, column=0, sticky="e")
        self.e_prv_tel = ttk.Entry(fr_form, width=20)
        self.e_prv_tel.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Email").grid(row=4, column=0, sticky="e")
        self.e_prv_mail = ttk.Entry(fr_form, width=30)
        self.e_prv_mail.grid(row=4, column=1, sticky="w", pady=2)

        fr_btns = ttk.Frame(fr_form)
        fr_btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=6)
        ttk.Button(fr_btns, text="Crear", command=self._crear_proveedor).grid(row=0, column=0, padx=4)
        ttk.Button(fr_btns, text="Actualizar", command=self._actualizar_proveedor).grid(row=0, column=1, padx=4)
        ttk.Button(fr_btns, text="Eliminar", command=self._eliminar_proveedor).grid(row=0, column=2, padx=4)

        fr_tbl = ttk.LabelFrame(parent, text="Listado", padding=10)
        fr_tbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(0, weight=1)

        cols = ("RUC", "Raz_Soc", "Direccion", "Telefono", "Email")
        self.tv_prv = ttk.Treeview(fr_tbl, columns=cols, show="headings", height=12)
        for c in cols:
            self.tv_prv.heading(c, text=c)
            self.tv_prv.column(c, width=150, anchor="w")
        self.tv_prv.pack(fill="both", expand=True)
        self.tv_prv.bind("<<TreeviewSelect>>", self._prv_on_select)
        ttk.Button(fr_tbl, text="Refrescar", command=self._cargar_proveedores).pack(anchor="e", pady=6)

        self._cargar_proveedores()

    def _prv_on_select(self, _evt):
        """Carga el proveedor seleccionado en el formulario para editar."""
        sel = self.tv_prv.selection()
        if not sel:
            return
        r = self.tv_prv.item(sel[0], "values")
        if len(r) >= 5:
            self.e_prv_ruc.delete(0, tk.END); self.e_prv_ruc.insert(0, r[0])
            self.e_prv_raz.delete(0, tk.END); self.e_prv_raz.insert(0, r[1])
            self.e_prv_dir.delete(0, tk.END); self.e_prv_dir.insert(0, r[2])
            self.e_prv_tel.delete(0, tk.END); self.e_prv_tel.insert(0, r[3])
            self.e_prv_mail.delete(0, tk.END); self.e_prv_mail.insert(0, r[4])

    def _cargar_proveedores(self):
        """Lista proveedores con sus contactos (LEFT JOIN para no perder nulos)."""
        for i in self.tv_prv.get_children():
            self.tv_prv.delete(i)
        sql = """
        SELECT p.RUC, p.Raz_Soc, IFNULL(p.Direccion,''), IFNULL(t.Telefono,''), IFNULL(e.Email,'')
        FROM Proveedor p
        LEFT JOIN Telefono_Proveedor t ON t.RUC_Proveedor = p.RUC
        LEFT JOIN Email_Proveedor e ON e.RUC_Proveedor = p.RUC
        ORDER BY p.Raz_Soc;
        """
        rows = self.client.select_rows(sql)
        for r in rows:
            self.tv_prv.insert("", tk.END, values=r)

    def _crear_proveedor(self):
        """Invoca sp_Agregar_Proveedor."""
        ruc = self.e_prv_ruc.get().strip()
        raz = self.e_prv_raz.get().strip()
        dire = self.e_prv_dir.get().strip()
        tel = self.e_prv_tel.get().strip()
        mail = self.e_prv_mail.get().strip()
        if not (ruc and raz and dire):
            messagebox.showwarning("Proveedor", "RUC, Razón Social y Dirección son obligatorios.")
            return
        sql = "CALL sp_Agregar_Proveedor(" + f"{self.client.esc(ruc)}, {self.client.esc(raz)}, {self.client.esc(dire)}, {self.client.esc(tel)}, {self.client.esc(mail)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Proveedor", "Creado.")
            self._cargar_proveedores()
        else:
            messagebox.showerror("Proveedor", out)

    def _actualizar_proveedor(self):
        """Invoca sp_Actualizar_Proveedor."""
        ruc = self.e_prv_ruc.get().strip()
        raz = self.e_prv_raz.get().strip()
        dire = self.e_prv_dir.get().strip()
        tel = self.e_prv_tel.get().strip()
        mail = self.e_prv_mail.get().strip()
        if not (ruc and raz and dire):
            messagebox.showwarning("Proveedor", "RUC, Razón Social y Dirección son obligatorios.")
            return
        sql = "CALL sp_Actualizar_Proveedor(" + f"{self.client.esc(ruc)}, {self.client.esc(raz)}, {self.client.esc(dire)}, {self.client.esc(tel)}, {self.client.esc(mail)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Proveedor", "Actualizado.")
            self._cargar_proveedores()
        else:
            messagebox.showerror("Proveedor", out)

    def _eliminar_proveedor(self):
        """Invoca sp_Eliminar_Proveedor (valida ordenes asociadas en el SP)."""
        ruc = self.e_prv_ruc.get().strip()
        if not ruc:
            messagebox.showwarning("Proveedor", "Seleccione un proveedor.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar proveedor {ruc}?"):
            sql = "CALL sp_Eliminar_Proveedor(" + f"{self.client.esc(ruc)}" + ");"
            ok, out = self.client.call_sp(sql)
            if ok:
                messagebox.showinfo("Proveedor", "Eliminado.")
                self._cargar_proveedores()
            else:
                messagebox.showerror("Proveedor", out)

    # -------- Empresas (Clientes) --------------------------------------------
    def _build_tab_empresas(self, parent):
        """UI y eventos de CRUD de Empresa + dirección/teléfono/correo asociados."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        fr_form = ttk.LabelFrame(parent, text="Empresa (Cliente) – Crear / Actualizar", padding=10)
        fr_form.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        ttk.Label(fr_form, text="RUC (11)").grid(row=0, column=0, sticky="e")
        self.e_cli_ruc = ttk.Entry(fr_form, width=18)
        self.e_cli_ruc.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Razón Social").grid(row=1, column=0, sticky="e")
        self.e_cli_raz = ttk.Entry(fr_form, width=40)
        self.e_cli_raz.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="FAX").grid(row=2, column=0, sticky="e")
        self.e_cli_fax = ttk.Entry(fr_form, width=18)
        self.e_cli_fax.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Ciudad").grid(row=3, column=0, sticky="e")
        self.e_cli_ciudad = ttk.Entry(fr_form, width=20)
        self.e_cli_ciudad.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Calle").grid(row=4, column=0, sticky="e")
        self.e_cli_calle = ttk.Entry(fr_form, width=30)
        self.e_cli_calle.grid(row=4, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Distrito").grid(row=5, column=0, sticky="e")
        self.e_cli_distrito = ttk.Entry(fr_form, width=20)
        self.e_cli_distrito.grid(row=5, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Teléfono").grid(row=6, column=0, sticky="e")
        self.e_cli_tel = ttk.Entry(fr_form, width=18)
        self.e_cli_tel.grid(row=6, column=1, sticky="w", pady=2)

        ttk.Label(fr_form, text="Correo").grid(row=7, column=0, sticky="e")
        self.e_cli_mail = ttk.Entry(fr_form, width=28)
        self.e_cli_mail.grid(row=7, column=1, sticky="w", pady=2)

        fr_btns = ttk.Frame(fr_form)
        fr_btns.grid(row=8, column=0, columnspan=2, sticky="e", pady=6)
        ttk.Button(fr_btns, text="Crear", command=self._crear_empresa).grid(row=0, column=0, padx=4)
        ttk.Button(fr_btns, text="Actualizar", command=self._actualizar_empresa).grid(row=0, column=1, padx=4)
        ttk.Button(fr_btns, text="Eliminar", command=self._eliminar_empresa).grid(row=0, column=2, padx=4)

        # Tabla
        fr_tbl = ttk.LabelFrame(parent, text="Listado", padding=10)
        fr_tbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(0, weight=1)

        cols = ("RUC","Raz_Soc","FAX","Ciudad","Calle","Distrito","Telefono","Correo")
        self.tv_cli = ttk.Treeview(fr_tbl, columns=cols, show="headings", height=12)
        for c in cols:
            self.tv_cli.heading(c, text=c)
            self.tv_cli.column(c, width=130, anchor="w")
        self.tv_cli.pack(fill="both", expand=True)
        self.tv_cli.bind("<<TreeviewSelect>>", self._cli_on_select)
        ttk.Button(fr_tbl, text="Refrescar", command=self._cargar_empresas).pack(anchor="e", pady=6)

        self._cargar_empresas()

    def _cli_on_select(self, _evt):
        """Carga en el formulario la empresa seleccionada para edición."""
        sel = self.tv_cli.selection()
        if not sel:
            return
        v = self.tv_cli.item(sel[0], "values")
        if len(v) >= 8:
            self.e_cli_ruc.delete(0, tk.END); self.e_cli_ruc.insert(0, v[0])
            self.e_cli_raz.delete(0, tk.END); self.e_cli_raz.insert(0, v[1])
            self.e_cli_fax.delete(0, tk.END); self.e_cli_fax.insert(0, v[2])
            self.e_cli_ciudad.delete(0, tk.END); self.e_cli_ciudad.insert(0, v[3])
            self.e_cli_calle.delete(0, tk.END); self.e_cli_calle.insert(0, v[4])
            self.e_cli_distrito.delete(0, tk.END); self.e_cli_distrito.insert(0, v[5])
            self.e_cli_tel.delete(0, tk.END); self.e_cli_tel.insert(0, v[6])
            self.e_cli_mail.delete(0, tk.END); self.e_cli_mail.insert(0, v[7])

    def _cargar_empresas(self):
        """Lista empresas con sus datos vinculados (dirección/teléfono/correo)."""
        for i in self.tv_cli.get_children():
            self.tv_cli.delete(i)
        sql = """
        SELECT em.RUC, em.Raz_Soc, IFNULL(em.FAX,''), IFNULL(dir.Ciudad,''), IFNULL(dir.Calle,''), IFNULL(dir.Distrito,''),
               IFNULL(tel.Telefono,''), IFNULL(cor.Correo,'')
        FROM Empresa em
        LEFT JOIN Direccion_Empresa dir ON dir.RUC_Empresa = em.RUC
        LEFT JOIN Telefono_Empresa tel ON tel.RUC_Empresa = em.RUC
        LEFT JOIN Correo_Empresa cor ON cor.RUC_Empresa = em.RUC
        ORDER BY em.Raz_Soc;
        """
        rows = self.client.select_rows(sql)
        for r in rows:
            self.tv_cli.insert("", tk.END, values=r)

    def _crear_empresa(self):
        """Invoca sp_Agregar_Empresa (transaccional; crea empresa + datos relacionados)."""
        ruc = self.e_cli_ruc.get().strip()
        raz = self.e_cli_raz.get().strip()
        fax = self.e_cli_fax.get().strip()
        ciudad = self.e_cli_ciudad.get().strip()
        calle = self.e_cli_calle.get().strip()
        distrito = self.e_cli_distrito.get().strip()
        tel = self.e_cli_tel.get().strip()
        mail = self.e_cli_mail.get().strip()
        if not (ruc and raz):
            messagebox.showwarning("Empresa", "RUC y Razón Social son obligatorios.")
            return
        sql = "CALL sp_Agregar_Empresa(" + f"{self.client.esc(ruc)}, {self.client.esc(raz)}, {self.client.esc(fax)}, {self.client.esc(ciudad)}, {self.client.esc(calle)}, {self.client.esc(distrito)}, {self.client.esc(tel)}, {self.client.esc(mail)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Empresa", "Creada.")
            self._cargar_empresas()
        else:
            messagebox.showerror("Empresa", out)

    def _actualizar_empresa(self):
        """Invoca sp_Actualizar_Empresa (upserts en tablas relacionadas)."""
        ruc = self.e_cli_ruc.get().strip()
        raz = self.e_cli_raz.get().strip()
        fax = self.e_cli_fax.get().strip()
        ciudad = self.e_cli_ciudad.get().strip()
        calle = self.e_cli_calle.get().strip()
        distrito = self.e_cli_distrito.get().strip()
        tel = self.e_cli_tel.get().strip()
        mail = self.e_cli_mail.get().strip()
        if not (ruc and raz):
            messagebox.showwarning("Empresa", "RUC y Razón Social son obligatorios.")
            return
        sql = "CALL sp_Actualizar_Empresa(" + f"{self.client.esc(ruc)}, {self.client.esc(raz)}, {self.client.esc(fax)}, {self.client.esc(ciudad)}, {self.client.esc(calle)}, {self.client.esc(distrito)}, {self.client.esc(tel)}, {self.client.esc(mail)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Empresa", "Actualizada.")
            self._cargar_empresas()
        else:
            messagebox.showerror("Empresa", out)

    def _eliminar_empresa(self):
        """Invoca sp_Eliminar_Empresa (bloquea si hay OC asociadas; lo valida el SP)."""
        ruc = self.e_cli_ruc.get().strip()
        if not ruc:
            messagebox.showwarning("Empresa", "Seleccione una empresa.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar empresa {ruc}?"):
            sql = "CALL sp_Eliminar_Empresa(" + f"{self.client.esc(ruc)}" + ");"
            ok, out = self.client.call_sp(sql)
            if ok:
                messagebox.showinfo("Empresa", "Eliminada.")
                self._cargar_empresas()
            else:
                messagebox.showerror("Empresa", out)

    # -------- Orden de Compra -------------------------------------------------
    def _build_tab_oc(self, parent):
        """UI y eventos para registrar/actualizar/eliminar órdenes de compra."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        frm = ttk.LabelFrame(parent, text="Registrar / Actualizar / Eliminar Orden de Compra", padding=10)
        frm.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        # Formulario de OC (todos los campos)
        ttk.Label(frm, text="Nro_Orden").grid(row=0, column=0, sticky="e")
        self.oc_nro = ttk.Entry(frm, width=16); self.oc_nro.grid(row=0, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="Per_UM").grid(row=0, column=2, sticky="e")
        self.oc_perum = ttk.Entry(frm, width=12); self.oc_perum.grid(row=0, column=3, sticky="w", pady=2)
        ttk.Label(frm, text="Fecha_Entrega (YYYY-MM-DD)").grid(row=1, column=0, sticky="e")
        self.oc_fecha = ttk.Entry(frm, width=16); self.oc_fecha.grid(row=1, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="Precio_Neto").grid(row=1, column=2, sticky="e")
        self.oc_precio = ttk.Entry(frm, width=12); self.oc_precio.grid(row=1, column=3, sticky="w", pady=2)
        ttk.Label(frm, text="Item").grid(row=2, column=0, sticky="e")
        self.oc_item = ttk.Entry(frm, width=8); self.oc_item.grid(row=2, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="Cantidad").grid(row=2, column=2, sticky="e")
        self.oc_cant = ttk.Entry(frm, width=8); self.oc_cant.grid(row=2, column=3, sticky="w", pady=2)
        ttk.Label(frm, text="UM").grid(row=3, column=0, sticky="e")
        self.oc_um = ttk.Entry(frm, width=8); self.oc_um.grid(row=3, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="Forma_pago").grid(row=3, column=2, sticky="e")
        self.oc_fp = ttk.Entry(frm, width=18); self.oc_fp.grid(row=3, column=3, sticky="w", pady=2)
        ttk.Label(frm, text="Incoterms").grid(row=4, column=0, sticky="e")
        self.oc_incot = ttk.Entry(frm, width=18); self.oc_incot.grid(row=4, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="Desc_Orden").grid(row=4, column=2, sticky="e")
        self.oc_desc = ttk.Entry(frm, width=24); self.oc_desc.grid(row=4, column=3, sticky="w", pady=2)
        ttk.Label(frm, text="Codigo_Empleado").grid(row=5, column=0, sticky="e")
        self.oc_codemp = ttk.Entry(frm, width=10); self.oc_codemp.grid(row=5, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="RUC_Proveedor").grid(row=5, column=2, sticky="e")
        self.oc_rucprov = ttk.Entry(frm, width=14); self.oc_rucprov.grid(row=5, column=3, sticky="w", pady=2)
        ttk.Label(frm, text="RUC_Empresa").grid(row=6, column=0, sticky="e")
        self.oc_rucemp = ttk.Entry(frm, width=14); self.oc_rucemp.grid(row=6, column=1, sticky="w", pady=2)
        ttk.Label(frm, text="Nro_Parte").grid(row=6, column=2, sticky="e")
        self.oc_np = ttk.Entry(frm, width=14); self.oc_np.grid(row=6, column=3, sticky="w", pady=2)

        frb = ttk.Frame(frm); frb.grid(row=7, column=0, columnspan=4, sticky="e", pady=6)
        ttk.Button(frb, text="Registrar", command=self._registrar_oc).grid(row=0, column=0, padx=4)
        ttk.Button(frb, text="Actualizar", command=self._actualizar_oc).grid(row=0, column=1, padx=4)
        ttk.Button(frb, text="Eliminar", command=self._eliminar_oc).grid(row=0, column=2, padx=4)

        # Tabla de OC
        fr_tbl = ttk.LabelFrame(parent, text="Órdenes", padding=10)
        fr_tbl.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(1, weight=1)
        cols = ("Nro_Orden","Per_UM","Fecha_Entrega","Precio_Neto","Item","Cantidad","UM","Forma_pago","Incoterms_2000","Desc_Orden","Codigo_Empleado","RUC_Proveedor","RUC_Empresa")
        self.tv_oc = ttk.Treeview(fr_tbl, columns=cols, show="headings", height=10)
        for c in cols:
            self.tv_oc.heading(c, text=c)
            self.tv_oc.column(c, width=120, anchor="w")
        self.tv_oc.pack(fill="both", expand=True)
        self.tv_oc.bind("<<TreeviewSelect>>", self._oc_on_select)
        ttk.Button(fr_tbl, text="Refrescar", command=self._cargar_oc).pack(anchor="e", pady=6)

        self._cargar_oc()

    def _oc_on_select(self, _evt):
        """Carga en el formulario la OC seleccionada."""
        sel = self.tv_oc.selection()
        if not sel:
            return
        v = self.tv_oc.item(sel[0], "values")
        if len(v) >= 13:
            self.oc_nro.delete(0, tk.END); self.oc_nro.insert(0, v[0])
            self.oc_perum.delete(0, tk.END); self.oc_perum.insert(0, v[1])
            self.oc_fecha.delete(0, tk.END); self.oc_fecha.insert(0, v[2])
            self.oc_precio.delete(0, tk.END); self.oc_precio.insert(0, v[3])
            self.oc_item.delete(0, tk.END); self.oc_item.insert(0, v[4])
            self.oc_cant.delete(0, tk.END); self.oc_cant.insert(0, v[5])
            self.oc_um.delete(0, tk.END); self.oc_um.insert(0, v[6])
            self.oc_fp.delete(0, tk.END); self.oc_fp.insert(0, v[7])
            self.oc_incot.delete(0, tk.END); self.oc_incot.insert(0, v[8])
            self.oc_desc.delete(0, tk.END); self.oc_desc.insert(0, v[9])
            self.oc_codemp.delete(0, tk.END); self.oc_codemp.insert(0, v[10])
            self.oc_rucprov.delete(0, tk.END); self.oc_rucprov.insert(0, v[11])
            self.oc_rucemp.delete(0, tk.END); self.oc_rucemp.insert(0, v[12])

    def _cargar_oc(self):
        """Lista últimas órdenes (ordenadas por fecha y número)."""
        for i in self.tv_oc.get_children():
            self.tv_oc.delete(i)
        sql = "SELECT Nro_Orden, Per_UM, Fecha_Entrega, Precio_Neto, Item, Cantidad, UM, Forma_pago, IFNULL(Incoterms_2000,''), Desc_Orden, Codigo_Empleado, RUC_Proveedor, RUC_Empresa FROM Orden_Compra ORDER BY Fecha_Entrega DESC, Nro_Orden DESC;"
        rows = self.client.select_rows(sql)
        for r in rows:
            self.tv_oc.insert("", tk.END, values=r)

    def _registrar_oc(self):
        """Invoca sp_Registrar_OrdenCompra (inserta y actualiza stock SUMA)."""
        nro = self.oc_nro.get().strip()
        perum = self.oc_perum.get().strip()
        fecha = self.oc_fecha.get().strip()
        precio = self.oc_precio.get().strip()
        item = self.oc_item.get().strip()
        cant = self.oc_cant.get().strip()
        um = self.oc_um.get().strip()
        fp = self.oc_fp.get().strip()
        incot = self.oc_incot.get().strip()
        desc = self.oc_desc.get().strip()
        cod = self.oc_codemp.get().strip()
        rprov = self.oc_rucprov.get().strip()
        remp = self.oc_rucemp.get().strip()
        np = self.oc_np.get().strip()
        if not (nro and perum and fecha and precio and item and cant and um and fp and desc and cod and rprov and remp and np):
            messagebox.showwarning("Orden Compra", "Complete todos los campos obligatorios.")
            return
        try:
            int(item); int(cant); float(precio)
        except:
            messagebox.showwarning("Orden Compra", "Item/Cantidad enteros, Precio decimal.")
            return
        sql = (
            "CALL sp_Registrar_OrdenCompra("
            f"{self.client.esc(nro)}, {self.client.esc(perum)}, {self.client.esc(fecha)}, {precio}, {item}, {cant}, "
            f"{self.client.esc(um)}, {self.client.esc(fp)}, {self.client.esc(incot)}, {self.client.esc(desc)}, "
            f"{self.client.esc(cod)}, {self.client.esc(rprov)}, {self.client.esc(remp)}, {self.client.esc(np)});"
        )
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Orden Compra", "Registrada.")
            self._cargar_oc()
        else:
            messagebox.showerror("Orden Compra", out)

    def _actualizar_oc(self):
        """Invoca sp_Actualizar_OrdenCompra (ajusta stock según delta de cantidad)."""
        nro = self.oc_nro.get().strip()
        perum = self.oc_perum.get().strip()
        fecha = self.oc_fecha.get().strip()
        precio = self.oc_precio.get().strip()
        item = self.oc_item.get().strip()
        cant = self.oc_cant.get().strip()
        um = self.oc_um.get().strip()
        fp = self.oc_fp.get().strip()
        incot = self.oc_incot.get().strip()
        desc = self.oc_desc.get().strip()
        cod = self.oc_codemp.get().strip()
        rprov = self.oc_rucprov.get().strip()
        remp = self.oc_rucemp.get().strip()
        np = self.oc_np.get().strip()
        if not (nro and perum and fecha and precio and item and cant and um and fp and desc and cod and rprov and remp and np):
            messagebox.showwarning("Orden Compra", "Complete todos los campos obligatorios.")
            return
        try:
            int(item); int(cant); float(precio)
        except:
            messagebox.showwarning("Orden Compra", "Item/Cantidad enteros, Precio decimal.")
            return
        sql = (
            "CALL sp_Actualizar_OrdenCompra("
            f"{self.client.esc(nro)}, {self.client.esc(perum)}, {self.client.esc(fecha)}, {precio}, {item}, {cant}, "
            f"{self.client.esc(um)}, {self.client.esc(fp)}, {self.client.esc(incot)}, {self.client.esc(desc)}, "
            f"{self.client.esc(cod)}, {self.client.esc(rprov)}, {self.client.esc(remp)}, {self.client.esc(np)});"
        )
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Orden Compra", "Actualizada.")
            self._cargar_oc()
        else:
            messagebox.showerror("Orden Compra", out)

    def _eliminar_oc(self):
        """Invoca sp_Eliminar_OrdenCompra (revierte stock y borra la OC)."""
        nro = self.oc_nro.get().strip()
        np = self.oc_np.get().strip()
        if not (nro and np):
            messagebox.showwarning("Orden Compra", "Indique Nro_Orden y Nro_Parte.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar orden {nro}? Se revertirá el stock."):
            sql = "CALL sp_Eliminar_OrdenCompra(" + f"{self.client.esc(nro)}, {self.client.esc(np)}" + ");"
            ok, out = self.client.call_sp(sql)
            if ok:
                messagebox.showinfo("Orden Compra", "Eliminada.")
                self._cargar_oc()
            else:
                messagebox.showerror("Orden Compra", out)

    # -------- Proforma --------------------------------------------------------
    def _build_tab_proforma(self, parent):
        """UI y eventos de CRUD de Proforma."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        fr_form = ttk.LabelFrame(parent, text="Proforma – Crear / Actualizar / Eliminar", padding=10)
        fr_form.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        ttk.Label(fr_form, text="Nro_Proforma").grid(row=0, column=0, sticky="e")
        self.pf_nro = ttk.Entry(fr_form, width=16); self.pf_nro.grid(row=0, column=1, sticky="w", pady=2)
        ttk.Label(fr_form, text="Item").grid(row=1, column=0, sticky="e")
        self.pf_item = ttk.Entry(fr_form, width=8); self.pf_item.grid(row=1, column=1, sticky="w", pady=2)
        ttk.Label(fr_form, text="Cantidad").grid(row=2, column=0, sticky="e")
        self.pf_cant = ttk.Entry(fr_form, width=8); self.pf_cant.grid(row=2, column=1, sticky="w", pady=2)
        ttk.Label(fr_form, text="Fecha (YYYY-MM-DD)").grid(row=3, column=0, sticky="e")
        self.pf_fecha = ttk.Entry(fr_form, width=14); self.pf_fecha.grid(row=3, column=1, sticky="w", pady=2)
        ttk.Label(fr_form, text="Peso").grid(row=4, column=0, sticky="e")
        self.pf_peso = ttk.Entry(fr_form, width=10); self.pf_peso.grid(row=4, column=1, sticky="w", pady=2)
        ttk.Label(fr_form, text="Nro_Parte").grid(row=5, column=0, sticky="e")
        self.pf_np = ttk.Entry(fr_form, width=14); self.pf_np.grid(row=5, column=1, sticky="w", pady=2)
        ttk.Label(fr_form, text="Codigo_Empleado").grid(row=6, column=0, sticky="e")
        self.pf_cod = ttk.Entry(fr_form, width=10); self.pf_cod.grid(row=6, column=1, sticky="w", pady=2)

        fr_btns = ttk.Frame(fr_form)
        fr_btns.grid(row=7, column=0, columnspan=2, sticky="e", pady=6)
        ttk.Button(fr_btns, text="Crear", command=self._crear_proforma).grid(row=0, column=0, padx=4)
        ttk.Button(fr_btns, text="Actualizar", command=self._actualizar_proforma).grid(row=0, column=1, padx=4)
        ttk.Button(fr_btns, text="Eliminar", command=self._eliminar_proforma).grid(row=0, column=2, padx=4)

        fr_tbl = ttk.LabelFrame(parent, text="Listado", padding=10)
        fr_tbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(0, weight=1)

        cols = ("Nro_Proforma","Item","Cantidad","Fecha","Peso","Nro_Parte","Codigo_Empleado")
        self.tv_pf = ttk.Treeview(fr_tbl, columns=cols, show="headings", height=12)
        for c in cols:
            self.tv_pf.heading(c, text=c)
            self.tv_pf.column(c, width=130, anchor="w")
        self.tv_pf.pack(fill="both", expand=True)
        self.tv_pf.bind("<<TreeviewSelect>>", self._pf_on_select)
        ttk.Button(fr_tbl, text="Refrescar", command=self._cargar_proformas).pack(anchor="e", pady=6)

        self._cargar_proformas()

    def _pf_on_select(self, _evt):
        """Carga en el formulario la proforma seleccionada."""
        sel = self.tv_pf.selection()
        if not sel:
            return
        v = self.tv_pf.item(sel[0], "values")
        if len(v) >= 7:
            self.pf_nro.delete(0, tk.END); self.pf_nro.insert(0, v[0])
            self.pf_item.delete(0, tk.END); self.pf_item.insert(0, v[1])
            self.pf_cant.delete(0, tk.END); self.pf_cant.insert(0, v[2])
            self.pf_fecha.delete(0, tk.END); self.pf_fecha.insert(0, v[3])
            self.pf_peso.delete(0, tk.END); self.pf_peso.insert(0, v[4])
            self.pf_np.delete(0, tk.END); self.pf_np.insert(0, v[5])
            self.pf_cod.delete(0, tk.END); self.pf_cod.insert(0, v[6])

    def _cargar_proformas(self):
        """Lista proformas ordenadas por fecha y número."""
        for i in self.tv_pf.get_children():
            self.tv_pf.delete(i)
        sql = "SELECT Nro_Proforma, Item, Cantidad, Fecha, Peso, Nro_Parte, Codigo_Empleado FROM Proforma ORDER BY Fecha DESC, Nro_Proforma DESC;"
        rows = self.client.select_rows(sql)
        for r in rows:
            self.tv_pf.insert("", tk.END, values=r)

    def _crear_proforma(self):
        """Invoca sp_Agregar_Proforma validando tipos básicos."""
        nro = self.pf_nro.get().strip()
        item = self.pf_item.get().strip()
        cant = self.pf_cant.get().strip()
        fecha = self.pf_fecha.get().strip()
        peso = self.pf_peso.get().strip()
        np = self.pf_np.get().strip()
        cod = self.pf_cod.get().strip()
        if not (nro and item and cant and fecha and peso and np and cod):
            messagebox.showwarning("Proforma", "Complete todos los campos.")
            return
        try:
            int(item); int(cant); float(peso)
        except:
            messagebox.showwarning("Proforma", "Item/Cantidad enteros, Peso decimal.")
            return
        sql = "CALL sp_Agregar_Proforma(" + f"{self.client.esc(nro)}, {item}, {cant}, {self.client.esc(fecha)}, {peso}, {self.client.esc(np)}, {self.client.esc(cod)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Proforma", "Creada.")
            self._cargar_proformas()
        else:
            messagebox.showerror("Proforma", out)

    def _actualizar_proforma(self):
        """Invoca sp_Actualizar_Proforma."""
        nro = self.pf_nro.get().strip()
        item = self.pf_item.get().strip()
        cant = self.pf_cant.get().strip()
        fecha = self.pf_fecha.get().strip()
        peso = self.pf_peso.get().strip()
        np = self.pf_np.get().strip()
        cod = self.pf_cod.get().strip()
        if not (nro and item and cant and fecha and peso and np and cod):
            messagebox.showwarning("Proforma", "Complete todos los campos.")
            return
        try:
            int(item); int(cant); float(peso)
        except:
            messagebox.showwarning("Proforma", "Item/Cantidad enteros, Peso decimal.")
            return
        sql = "CALL sp_Actualizar_Proforma(" + f"{self.client.esc(nro)}, {item}, {cant}, {self.client.esc(fecha)}, {peso}, {self.client.esc(np)}, {self.client.esc(cod)}" + ");"
        ok, out = self.client.call_sp(sql)
        if ok:
            messagebox.showinfo("Proforma", "Actualizada.")
            self._cargar_proformas()
        else:
            messagebox.showerror("Proforma", out)

    def _eliminar_proforma(self):
        """Invoca sp_Eliminar_Proforma con confirmación."""
        nro = self.pf_nro.get().strip()
        if not nro:
            messagebox.showwarning("Proforma", "Indique Nro_Proforma.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar proforma {nro}?"):
            sql = "CALL sp_Eliminar_Proforma(" + f"{self.client.esc(nro)}" + ");"
            ok, out = self.client.call_sp(sql)
            if ok:
                messagebox.showinfo("Proforma", "Eliminada.")
                self._cargar_proformas()
            else:
                messagebox.showerror("Proforma", out)

    # -------- Reportes --------------------------------------------------------
    def _build_tab_reportes(self, parent):
        """UI de reportes parametrizables (combobox + parámetro numérico)."""
        frm = ttk.Frame(parent, padding=12)
        frm.pack(fill="both", expand=True)

        top = ttk.Frame(frm)
        top.pack(fill="x")

        ttk.Label(top, text="Reporte").pack(side="left")
        self.rep_var = tk.StringVar(value="Stock bajo")
        self.cmb_rep = ttk.Combobox(top, textvariable=self.rep_var, state="readonly",
                                    values=[
                                        "Stock bajo",
                                        "Proveedores y contacto",
                                        "Órdenes recientes",
                                        "Órdenes por empresa",
                                        "Top empresas por monto",
                                        "Repuestos más comprados",
                                        "Proformas por empleado",
                                        "Proformas por repuesto",
                                        "Empresas sin órdenes (N días)",
                                        "Proveedores sin órdenes"
                                    ], width=34)
        self.cmb_rep.pack(side="left", padx=8)

        ttk.Label(top, text=" Umbral/Parámetro:").pack(side="left")
        self.e_param = ttk.Entry(top, width=10); self.e_param.insert(0, "3"); self.e_param.pack(side="left")

        ttk.Button(top, text="Mostrar", command=self._refrescar_reporte).pack(side="left", padx=8)

        self.tv_rep = ttk.Treeview(frm, columns=(), show="headings")
        self.tv_rep.pack(fill="both", expand=True, pady=8)

        self._refrescar_reporte()

    def _set_report_columns(self, headers):
        """Configura columnas del Treeview de reportes y limpia las filas."""
        self.tv_rep["columns"] = headers
        self.tv_rep.delete(*self.tv_rep.get_children())
        for c in headers:
            self.tv_rep.heading(c, text=c)
            self.tv_rep.column(c, width=160, anchor="w")

    def _refrescar_reporte(self):
        """Genera el SQL según el tipo de reporte y vuelca los resultados al Treeview."""
        tipo = self.rep_var.get()

        if tipo == "Stock bajo":
            try:
                umbral = int(self.e_param.get().strip())
            except:
                messagebox.showwarning("Reporte", "Parámetro entero.")
                return
            self._set_report_columns(("Nro_Parte","Descripcion","Marca","Cantidad","Precio_Unitario"))
            sql = f"SELECT Nro_Parte, Descripcion, Marca, Cantidad, Precio_Unitario FROM Repuesto WHERE Cantidad < {umbral} ORDER BY Cantidad ASC, Descripcion ASC;"
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Proveedores y contacto":
            self._set_report_columns(("RUC","Raz_Soc","Direccion","Telefono","Email"))
            sql = """
            SELECT p.RUC, p.Raz_Soc, IFNULL(p.Direccion,''), IFNULL(t.Telefono,''), IFNULL(e.Email,'')
            FROM Proveedor p
            LEFT JOIN Telefono_Proveedor t ON t.RUC_Proveedor = p.RUC
            LEFT JOIN Email_Proveedor e ON e.RUC_Proveedor = p.RUC
            ORDER BY p.Raz_Soc;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Órdenes recientes":
            self._set_report_columns(("Nro_Orden","Fecha_Entrega","Precio_Neto","Empleado","Proveedor","Empresa"))
            sql = """
            SELECT oc.Nro_Orden, oc.Fecha_Entrega, oc.Precio_Neto, IFNULL(emp.Nombre,''), prov.Raz_Soc, empc.Raz_Soc
            FROM Orden_Compra oc
            LEFT JOIN Empleado emp ON emp.Codigo = oc.Codigo_Empleado
            LEFT JOIN Proveedor prov ON prov.RUC = oc.RUC_Proveedor
            LEFT JOIN Empresa empc ON empc.RUC = oc.RUC_Empresa
            ORDER BY oc.Fecha_Entrega DESC, oc.Nro_Orden DESC
            LIMIT 100;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Órdenes por empresa":
            self._set_report_columns(("RUC_Empresa","Empresa","Total_Ordenes","Suma_Precio_Neto"))
            sql = """
            SELECT oc.RUC_Empresa, em.Raz_Soc, COUNT(*) AS Total_Ordenes, SUM(oc.Precio_Neto) AS Suma_Precio_Neto
            FROM Orden_Compra oc
            LEFT JOIN Empresa em ON em.RUC = oc.RUC_Empresa
            GROUP BY oc.RUC_Empresa, em.Raz_Soc
            ORDER BY Suma_Precio_Neto DESC;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Top empresas por monto":
            self._set_report_columns(("Empresa","Monto_Total"))
            sql = """
            SELECT em.Raz_Soc, SUM(oc.Precio_Neto) AS Monto_Total
            FROM Orden_Compra oc
            INNER JOIN Empresa em ON em.RUC = oc.RUC_Empresa
            GROUP BY em.Raz_Soc
            ORDER BY Monto_Total DESC
            LIMIT 10;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Repuestos más comprados":
            # TOP N por cantidad en Proforma (parámetro en la caja)
            try:
                topn = int(self.e_param.get().strip() or "10")
            except:
                topn = 10
            self._set_report_columns(("Nro_Parte", "Descripcion", "Total_Cant"))
            sql = f"""
            SELECT r.Nro_Parte, r.Descripcion, SUM(pf.Cantidad) AS Total_Cant
            FROM Proforma pf
            INNER JOIN Repuesto r ON r.Nro_Parte = pf.Nro_Parte
            GROUP BY r.Nro_Parte, r.Descripcion
            ORDER BY Total_Cant DESC
            LIMIT {topn};
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Proformas por empleado":
            self._set_report_columns(("Empleado","Nro_Proformas","Total_Unidades"))
            sql = """
            SELECT e.Nombre, COUNT(*) AS Nro_Proformas, SUM(pf.Cantidad) AS Total_Unidades
            FROM Proforma pf
            INNER JOIN Empleado e ON e.Codigo = pf.Codigo_Empleado
            GROUP BY e.Nombre
            ORDER BY Nro_Proformas DESC;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Proformas por repuesto":
            self._set_report_columns(("Nro_Parte","Descripcion","Nro_Proformas","Total_Unidades"))
            sql = """
            SELECT r.Nro_Parte, r.Descripcion, COUNT(*) AS Nro_Proformas, SUM(pf.Cantidad) AS Total_Unidades
            FROM Proforma pf
            INNER JOIN Repuesto r ON r.Nro_Parte = pf.Nro_Parte
            GROUP BY r.Nro_Parte, r.Descripcion
            ORDER BY Total_Unidades DESC;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        elif tipo == "Empresas sin órdenes (N días)":
            # Lista empresas que no tienen OC en los últimos N días (param)
            try:
                ndias = int(self.e_param.get().strip())
            except:
                messagebox.showwarning("Reporte", "Parámetro entero (días).")
                return
            self._set_report_columns(("RUC","Empresa"))
            sql = f"""
            SELECT em.RUC, em.Raz_Soc
            FROM Empresa em
            LEFT JOIN Orden_Compra oc ON oc.RUC_Empresa = em.RUC AND oc.Fecha_Entrega >= DATE_SUB(CURDATE(), INTERVAL {ndias} DAY)
            WHERE oc.Nro_Orden IS NULL
            ORDER BY em.Raz_Soc;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

        else:
            # Proveedores sin órdenes
            self._set_report_columns(("RUC_Proveedor","Raz_Soc"))
            sql = """
            SELECT p.RUC, p.Raz_Soc
            FROM Proveedor p
            LEFT JOIN Orden_Compra oc ON oc.RUC_Proveedor = p.RUC
            WHERE oc.Nro_Orden IS NULL
            ORDER BY p.Raz_Soc;
            """
            rows = self.client.select_rows(sql)
            for r in rows:
                self.tv_rep.insert("", tk.END, values=r)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
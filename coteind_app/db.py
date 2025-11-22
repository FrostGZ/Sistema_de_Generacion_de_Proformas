import subprocess
import shlex
import os

class MySQLClient:
    """
    Pequeño wrapper alrededor del cliente de línea de comandos `mysql`.

    Parameters
    ----------
    host : str
        Host del servidor MySQL (por defecto 'localhost').
    port : int
        Puerto de conexión (por defecto 3306).
    user : str
        Usuario de MySQL.
    password : str
        Contraseña del usuario.
    database : str | None
        Base de datos por defecto. Si es None, algunos métodos pueden recibir use_db=False.
    """
    def __init__(self, host="localhost", port=3306, user="root", password="", database=None):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password or ""
        self.database = database

    def _base_cmd(self, use_db=True):
        """
        Construye la parte base del comando `mysql`.

        Params
        ------
        use_db : bool
            Si True y hay `self.database`, agrega `-D <db>` para usar esa BD.

        Returns
        -------
        list[str]
            Lista de argumentos para `subprocess.run`.
        """
        cmd = [
            "mysql",
            "-u", self.user,
            "-h", self.host,
            "-P", str(self.port),
            "--default-character-set=utf8mb4",  # evita problemas de acentos/emoji
            "-N", "-B", "-s"                    # salida sin encabezados/bonita/tab-separada
        ]
        if use_db and self.database:
            cmd += ["-D", self.database]
        if self.password:
            # Se pasa "-p<pwd>" sin espacio para que mysql no pregunte por prompt.
            cmd += ["-p" + self.password]
        return cmd

    def test_connection(self):
        """
        Realiza una consulta trivial para validar la conexión.

        Returns
        -------
        (bool, str)
            (ok, salida o error)
        """
        return self.run_sql("SELECT 1;")

    def run_sql(self, sql, use_db=True):
        """
        Ejecuta una sentencia SQL directa usando `mysql -e`.

        Params
        ------
        sql : str
            Sentencia(s) SQL a ejecutar.
        use_db : bool
            Si True, incluye `-D <database>` (si fue configurada).

        Returns
        -------
        (bool, str)
            True + stdout (sin espacios al final) si ok; False + stderr/stdout si error.
        """
        cmd = self._base_cmd(use_db) + ["-e", sql]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False
            )
            ok = (proc.returncode == 0)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            if ok:
                return True, out
            else:
                return False, (err or out)
        except FileNotFoundError:
            return False, "No se encontró el binario 'mysql' en el PATH."
        except Exception as ex:
            return False, f"Error ejecutando mysql: {ex}"
    
    def run_sql_file(self, path, use_db=True):
        """
        Ejecuta un archivo .sql enviándolo por STDIN al binario `mysql`.

        Params
        ------
        path : str
            Ruta del archivo .sql
        use_db : bool
            Si True, incluye `-D <database>` (si fue configurada).

        Returns
        -------
        (bool, str)
            True + stdout si ok; False + stderr/stdout si error.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as ex:
            return False, f"No se pudo leer {path}: {ex}"
        
        cmd = self._base_cmd(use_db)
        try:
            proc = subprocess.run(
                cmd,
                input=content,              # enviamos el SQL por STDIN
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False
            )
            ok = (proc.returncode == 0)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            return (True, out) if ok else (False, (err or out))
        except FileNotFoundError:
            return False, "No se encontró el binario 'mysql' en el PATH."
        except Exception as ex:
            return False, f"Error ejecutando mysql con {os.path.basename(path)}: {ex}"
        
    @staticmethod
    def esc(value):
        """
        Escapa un valor para interpolarlo en SQL simple.

        Nota:
        - Esta función es básica (comillas simples -> duplicadas). Para casos complejos,
          es preferible usar parámetros preparados (en drivers como pymysql/mysqlclient).

        Params
        ------
        value : Any

        Returns
        -------
        str
            'NULL' si value es None, o el literal con comillas simples escapadas.
        """
        if value is None:
            return "NULL"
        return "'" + str(value).replace("'", "''") + "'"

    def select_scalar(self, sql):
        """
        Ejecuta un SELECT que devuelve una sola celda (primera fila, primera columna).

        Returns
        -------
        Any | None
            Valor como string (o None si no hay filas / error).
        """
        ok, out = self.run_sql(sql)
        if not ok or not out:
            return None
        line = out.splitlines()[0]
        return line.split("\t")[0] if line else None

    def select_rows(self, sql):
        """
        Ejecuta un SELECT y retorna una lista de filas, cada fila como lista de strings.

        Returns
        -------
        list[list[str]]
            Filas separadas por tabuladores (por `-B -s -N`), o [] si error/sin datos.
        """
        ok, out = self.run_sql(sql)
        if not ok or not out:
            return []
        rows = []
        for line in out.splitlines():
            rows.append(line.split("\t"))
        return rows

    def call_sp(self, call_sql):
        """
        Ejecuta una llamada a procedimiento almacenado (CALL ...).

        Returns
        -------
        (bool, str)
            Proxy de `run_sql`.
        """
        return self.run_sql(call_sql)
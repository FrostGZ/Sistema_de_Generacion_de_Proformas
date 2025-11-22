import subprocess
import shlex

class MySQLClient:
    def __init__(self, host="localhost", port=3306, user="root", password="", database=None):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password or ""
        self.database = database

    def _base_cmd(self):
        cmd = ["mysql",
               "-u", self.user,
               "-h", self.host,
               "-P", str(self.port),
               "--default-character-set=utf8mb4"] 
        if self.database:
            cmd += ["-D", self.database]
        cmd += ["-N", "-B", "-s"]
        if self.password:
            cmd += ["-p" + self.password]
        return cmd

    def test_connection(self):
        return self.run_sql("SELECT 1;")

    def run_sql(self, sql):
        cmd = self._base_cmd() + ["-e", sql]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
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

    @staticmethod
    def esc(value):
        if value is None:
            return "NULL"
        return "'" + str(value).replace("'", "''") + "'"

    def select_scalar(self, sql):
        ok, out = self.run_sql(sql)
        if not ok or not out:
            return None
        line = out.splitlines()[0]
        return line.split("\t")[0] if line else None

    def select_rows(self, sql):
        ok, out = self.run_sql(sql)
        if not ok or not out:
            return []
        rows = []
        for line in out.splitlines():
            rows.append(line.split("\t"))
        return rows

    def call_sp(self, call_sql):
        return self.run_sql(call_sql)
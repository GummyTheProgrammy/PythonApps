import os
import sys
import ctypes
import subprocess
import eel
import traceback

# =============================================================================
# Configurações Iniciais e Elevação de Privilégios
# =============================================================================

def requires_admin():
    """
    Verifica se o processo atual possui privilegios de administrador.
    Caso negativo, reinicia o processo solicitando elevacao (UAC).
    """
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        print("Privilégios administrativos não detectados. Solicitando elevação...")
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        sys.exit()

requires_admin()

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"Processo em execução com privilégios administrativos.")
print(f"Diretório de trabalho fixado em: {script_dir}")

# =============================================================================
# Inicialização do Eel
# =============================================================================

eel.init('web')

LOG_FILE = "log.txt"
ERROR_LOG_FILE = "error_log.txt"

def registrar_erro(mensagem):
    """
    Registra erros em um arquivo de log para depuracao.
    """
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(mensagem + "\n")
    except Exception as e:
        print(f"Falha ao escrever no log de erros: {e}")

@eel.expose
def pick_folder_native():
    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$dialog = New-Object System.Windows.Forms.OpenFileDialog;"
        "$dialog.ValidateNames = $false;"
        "$dialog.CheckFileExists = $false;"
        "$dialog.CheckPathExists = $true;"
        "$dialog.FileName = 'Pasta_Selecionada';"
        "$dialog.Title = 'Selecione a pasta raiz';"
        "$dialog.Filter = 'Pastas|*.none';"
        "if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {"
        "    [System.IO.Path]::GetDirectoryName($dialog.FileName)"
        "}"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

@eel.expose
def map_and_log_directory(target_directory):
    try:
        if not target_directory:
            msg = "Caminho não fornecido."
            registrar_erro(msg)
            return {"success": False, "error": msg}
            
        if not os.path.exists(target_directory):
            msg = f"O caminho não existe ou o sistema não tem permissão de acesso: {target_directory}"
            registrar_erro(msg)
            return {"success": False, "error": "Caminho inacessível. Verifique o error_log.txt"}

        all_files = []
        
        # Funcao callback para registrar pastas que derem erro de permissao sem travar o loop
        def on_walk_error(os_err):
            registrar_erro(f"Falha ao acessar diretorio: {os_err}")

        for root, dirs, files in os.walk(target_directory, onerror=on_walk_error):
            for file in files:
                all_files.append(os.path.join(root, file))

        total_files = len(all_files)
        if total_files == 0:
            eel.update_left_progress(100.0)()
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
            return {"success": True, "error": None}

        for index, file_path in enumerate(all_files):
            progress_float = float(index + 1) / float(total_files) * 100.0
            
            if index % 50 == 0 or index == total_files - 1:
                eel.update_left_progress(progress_float)()
                eel.sleep(0.001)

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for path in all_files:
                f.write(path + "\n")
            
        return {"success": True, "error": None}

    except Exception as e:
        trace = traceback.format_exc()
        registrar_erro(f"Erro critico em map_and_log_directory:\n{trace}")
        return {"success": False, "error": f"Erro critico: {str(e)}"}

@eel.expose
def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
    return []

@eel.expose
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        registrar_erro(f"Erro ao remover arquivo {file_path}: {e}")
    return False

if __name__ == '__main__':
    eel.start('index.html', size=(1000, 600))
import subprocess
from datetime import datetime
import os

PASTA_RELATORIOS = "auditoria/relatorios/"
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

data_atual = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
arquivo_saida = os.path.join(PASTA_RELATORIOS, f"relatorio_so_{data_atual}.txt")

comandos = {
    "Usuários Conectados (who)": "who",
    "Histórico de Logins (last)": "last -n 10",
    "Portas e Serviços (ss -tulpn)": "ss -tulpn",
    "Interfaces de Rede (ip a)": "ip a"
}

with open(arquivo_saida, "w") as f:
    f.write(f"--- RELATÓRIO DE AUDITORIA DO SO (RF06) ---\n")
    f.write(f"Data/Hora: {data_atual}\n\n")
    
    for titulo, cmd in comandos.items():
        f.write(f"=== {titulo} ===\n")
        try:
            resultado = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            f.write(resultado + "\n")
        except subprocess.CalledProcessError as e:
            f.write(f"Erro ao executar o comando: {e.output}\n")
        f.write("-" * 50 + "\n")

print(f"[SUCESSO] Relatório do SO (RF06) gerado em: {arquivo_saida}")

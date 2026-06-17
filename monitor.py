import os
import hashlib
import json
import time
from datetime import datetime

DIR_DOCUMENTOS = 'documentos'
ARQUIVO_ESTADO = 'documentos/estado_hashes.json'
# Novo caminho para o relatório de auditoria
ARQUIVO_LOG = "auditoria/relatorios/relatorio_de_auditoria_atual.txt"

def registrar_alerta(mensagem):
    """Grava o alerta tanto no terminal quanto no arquivo de log."""
    # Garante que o diretório de relatórios exista
    os.makedirs(os.path.dirname(ARQUIVO_LOG), exist_ok=True)
    
    msg_formatada = f"[{datetime.now().isoformat()}] {mensagem}"
    print(msg_formatada)
    
    with open(ARQUIVO_LOG, 'a') as f:
        f.write(msg_formatada + "\n")

def calcular_hash(caminho_arquivo):
    """Calcula o hash SHA-256 de um arquivo em blocos."""
    sha256_hash = hashlib.sha256()
    try:
        with open(caminho_arquivo, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def mapear_diretorio():
    """Mapeia os arquivos atuais e seus hashes SHA-256."""
    estado_atual = {}
    for root, _, files in os.walk(DIR_DOCUMENTOS):
        for file in files:
            if file == 'estado_hashes.json':
                continue
            caminho = os.path.join(root, file)
            file_hash = calcular_hash(caminho)
            if file_hash:
                estado_atual[caminho] = file_hash
    return estado_atual

def inicializar_monitoramento():
    """Cria o estado inicial (baseline) dos hashes."""
    if not os.path.exists(DIR_DOCUMENTOS):
        os.makedirs(DIR_DOCUMENTOS)
        
    estado_inicial = mapear_diretorio()
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado_inicial, f, indent=4)
    print(f"[{datetime.now().isoformat()}] Baseline criada com {len(estado_inicial)} arquivo(s).")

def verificar_integridade():
    """Compara o diretório com a baseline e detecta anomalias."""
    if not os.path.exists(ARQUIVO_ESTADO):
        inicializar_monitoramento()
        return

    with open(ARQUIVO_ESTADO, 'r') as f:
        estado_salvo = json.load(f)

    estado_atual = mapear_diretorio()
    inconsistencias = False

    for caminho, hash_salvo in estado_salvo.items():
        if caminho not in estado_atual:
            registrar_alerta(f"[ALERTA CRÍTICO] Arquivo EXCLUÍDO: {caminho}")
            inconsistencias = True
        elif estado_atual[caminho] != hash_salvo:
            registrar_alerta(f"[ALERTA CRÍTICO] Arquivo ALTERADO: {caminho}")
            inconsistencias = True

    for caminho in estado_atual:
        if caminho not in estado_salvo:
            registrar_alerta(f"[ALERTA CRÍTICO] Arquivo INCLUÍDO: {caminho}")
            inconsistencias = True

    if not inconsistencias:
        print(f"[{datetime.now().isoformat()}] Integridade OK: Nenhuma anomalia detectada.")
    else:
        # Atualiza a baseline após detectar alterações
        with open(ARQUIVO_ESTADO, 'w') as f:
            json.dump(estado_atual, f, indent=4)

if __name__ == "__main__":
    print("--- SecureChain Audit: Monitoramento de Integridade ---")
    
    # Prepara o ambiente de teste
    if not os.path.exists(DIR_DOCUMENTOS): os.makedirs(DIR_DOCUMENTOS)
    arquivo_teste = os.path.join(DIR_DOCUMENTOS, "contrato_base.txt")
    with open(arquivo_teste, "w") as f:
        f.write("Informacao sigilosa original.")
    
    inicializar_monitoramento()
    verificar_integridade()
    
    print("\n[Simulação] Modificando o arquivo contrato_base.txt...")
    time.sleep(1)
    with open(arquivo_teste, "a") as f:
        f.write("\nClausula maliciosa inserida secretamente!")
        
    verificar_integridade()

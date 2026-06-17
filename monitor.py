import os
import hashlib
import json
import time
from datetime import datetime

DIR_DOCUMENTOS = 'documentos'
ARQUIVO_ESTADO = 'documentos/estado_hashes.json'
ARQUIVO_CHAIN_AUDITORIA = "blockchain/chain.json"

def calcular_hash_bloco(bloco):
    """Calcula o hash SHA-256 de um bloco transformado em string."""
    bloco_string = json.dumps(bloco, sort_keys=True).encode()
    return hashlib.sha256(bloco_string).hexdigest()

def registrar_alerta(mensagem):
    """Grava o alerta garantindo o encadeamento (hash_anterior e hash_atual)."""
    os.makedirs(os.path.dirname(ARQUIVO_CHAIN_AUDITORIA), exist_ok=True)
    
    chain = []
    if os.path.exists(ARQUIVO_CHAIN_AUDITORIA):
        with open(ARQUIVO_CHAIN_AUDITORIA, 'r') as f:
            try:
                chain = json.load(f)
            except json.JSONDecodeError:
                chain = []

    hash_anterior = "0" * 64
    if len(chain) > 0:
        hash_anterior = chain[-1].get("hash_atual", "0"*64)

    novo_bloco = {
        "timestamp": datetime.now().isoformat(),
        "evento": mensagem,
        "hash_anterior": hash_anterior
    }

    novo_bloco["hash_atual"] = calcular_hash_bloco(novo_bloco)
    
    chain.append(novo_bloco)
    with open(ARQUIVO_CHAIN_AUDITORIA, 'w') as f:
        json.dump(chain, f, indent=4)
        
    print(f"[{novo_bloco['timestamp']}] {mensagem}")
    print(f" -> Bloco gerado | Hash atual: {novo_bloco['hash_atual'][:15]}...")

def calcular_hash_arquivo(caminho_arquivo):
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
            file_hash = calcular_hash_arquivo(caminho)
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
        with open(ARQUIVO_ESTADO, 'w') as f:
            json.dump(estado_atual, f, indent=4)

if __name__ == "__main__":
    print("--- SecureChain Audit: Monitoramento Contínuo Iniciado ---")
    
    # Prepara o ambiente caso não exista
    if not os.path.exists(DIR_DOCUMENTOS): 
        os.makedirs(DIR_DOCUMENTOS)
    
    inicializar_monitoramento()
    
    print("[INFO] Monitoramento em background ativado. Pressione Ctrl+C para sair.")
    
    # Loop infinito rodando a cada 10 segundos
    try:
        while True:
            verificar_integridade()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[INFO] Monitoramento encerrado pelo usuário.")

#!/bin/bash
# SecureChain Audit - Script de Backup e Criptografia (RF05)

DIRETORIOS="documentos/ auditoria/"
PASTA_BACKUP="."
DATA=$(date +"%Y-%m-%dT%H-%M-%S")
ARQUIVO_TAR="$PASTA_BACKUP/securechain_backup_$DATA.tar.gz"
ARQUIVO_ENC="$PASTA_BACKUP/securechain_backup_$DATA.enc"
LOG_LOCAL="$PASTA_BACKUP/backup_log.txt"
CHAIN_JSON="../blockchain/chain.json"

SENHA_AES="SecureChain2026"

echo "--- Iniciando processo de Backup (RF05) ---"
mkdir -p $PASTA_BACKUP
mkdir -p auditoria/relatorios/

# 1. Compactação dos arquivos (.tar.gz)
tar -czf $ARQUIVO_TAR documentos/ auditoria/ 2>/dev/null

# 2. Aplicação de Criptografia Simétrica (AES-256 via OpenSSL)
openssl enc -aes-256-cbc -salt -pbkdf2 -in $ARQUIVO_TAR -out $ARQUIVO_ENC -pass pass:$SENHA_AES

# 3. Log Local (Calcula tamanho e registra)
TAMANHO=$(du -h $ARQUIVO_ENC | cut -f1)
STATUS="SUCESSO"
MENSAGEM_LOG="[$DATA] STATUS: $STATUS | ARQUIVO: $ARQUIVO_ENC | TAMANHO: $TAMANHO"
echo "$MENSAGEM_LOG" >> $LOG_LOCAL

# 4. Registro do Evento na Blockchain (Injeção de script Python)
python3 -c "
import json, hashlib, os
from datetime import datetime

arquivo_chain = '$CHAIN_JSON'
mensagem = 'BACKUP REALIZADO: $ARQUIVO_ENC (Tamanho: $TAMANHO)'

os.makedirs(os.path.dirname(arquivo_chain), exist_ok=True)

def calcular_hash_bloco(bloco):
    bloco_string = json.dumps(bloco, sort_keys=True).encode()
    return hashlib.sha256(bloco_string).hexdigest()

chain = []
if os.path.exists(arquivo_chain):
    with open(arquivo_chain, 'r') as f:
        try: chain = json.load(f)
        except: pass

hash_anterior = chain[-1].get('hash_atual', '0'*64) if chain else '0'*64

novo_bloco = {
    'timestamp': datetime.now().isoformat(),
    'evento': mensagem,
    'hash_anterior': hash_anterior
}
novo_bloco['hash_atual'] = calcular_hash_bloco(novo_bloco)
chain.append(novo_bloco)

with open(arquivo_chain, 'w') as f:
    json.dump(chain, f, indent=4)
"

# 5. Limpeza do arquivo não criptografado
rm $ARQUIVO_TAR

echo "[SUCESSO] Backup protegido gerado: $ARQUIVO_ENC"
echo "[SUCESSO] Log local salvo em: $LOG_LOCAL"
echo "[SUCESSO] Evento de backup registrado na Blockchain."

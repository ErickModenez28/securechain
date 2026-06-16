import hashlib
import json
import os
from datetime import datetime

ARQUIVO_CHAIN = 'blockchain/chain.json'

class SecureChain:
    def __init__(self):
        self.cadeia = self.carregar_cadeia()
        if not self.cadeia:
            self.criar_bloco_genesis()

    def carregar_cadeia(self):
        """Carrega a blockchain do arquivo JSON, se existir."""
        if not os.path.exists(ARQUIVO_CHAIN):
            return []
        try:
            with open(ARQUIVO_CHAIN, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def salvar_cadeia(self):
        """Salva a cadeia atualizada no disco."""
        os.makedirs(os.path.dirname(ARQUIVO_CHAIN), exist_ok=True)
        with open(ARQUIVO_CHAIN, 'w') as f:
            json.dump(self.cadeia, f, indent=4)

    def calcular_hash_bloco(self, bloco):
        """Gera o SHA-256 dos dados do bloco para travar sua integridade."""
        conteudo = {
            "ID": bloco["ID"],
            "timestamp": bloco["timestamp"],
            "evento": bloco["evento"],
            "hash_anterior": bloco["hash_anterior"]
        }
        bloco_string = json.dumps(conteudo, sort_keys=True).encode()
        return hashlib.sha256(bloco_string).hexdigest()

    def criar_bloco_genesis(self):
        """O primeiro bloco da blockchain."""
        bloco = {
            "ID": 0,
            "timestamp": datetime.now().isoformat(),
            "evento": "Bloco Genesis - Inicializacao da SecureChain Audit",
            "hash_anterior": "0" * 64
        }
        bloco["hash_atual"] = self.calcular_hash_bloco(bloco)
        self.cadeia.append(bloco)
        self.salvar_cadeia()

    def registrar_evento(self, evento):
        """Gera um novo bloco contendo o evento."""
        bloco_anterior = self.cadeia[-1]
        novo_bloco = {
            "ID": bloco_anterior["ID"] + 1,
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            "hash_anterior": bloco_anterior["hash_atual"]
        }
        novo_bloco["hash_atual"] = self.calcular_hash_bloco(novo_bloco)
        self.cadeia.append(novo_bloco)
        self.salvar_cadeia()
        print(f"[*] Blockchain: Evento registrado no Bloco {novo_bloco['ID']}")

    def validar_cadeia(self):
        """RF07: Percorre a cadeia verificando a integridade criptográfica."""
        print("\n--- Iniciando Validação da Blockchain ---")
        for i in range(1, len(self.cadeia)):
            bloco_anterior = self.cadeia[i-1]
            bloco_atual = self.cadeia[i]

            # 1. Verifica quebra de encadeamento
            if bloco_atual['hash_anterior'] != bloco_anterior['hash_atual']:
                print(f"[ALERTA CRÍTICO] Quebra de encadeamento detectada no Bloco {bloco_atual['ID']}!")
                print(f"   -> O 'hash_anterior' não bate com o bloco {bloco_anterior['ID']}.")
                return False

            # 2. Verifica adulteração direta nos dados
            hash_recalculado = self.calcular_hash_bloco(bloco_atual)
            if bloco_atual['hash_atual'] != hash_recalculado:
                print(f"[ALERTA CRÍTICO] Adulteração direta detectada no Bloco {bloco_atual['ID']}!")
                print(f"   -> Hash original armazenado: {bloco_atual['hash_atual']}")
                print(f"   -> Hash recalculado: {hash_recalculado}")
                return False

        print("[OK] A Blockchain está íntegra e não foi violada.")
        return True


# Bloco de testes e simulação para o vídeo de apresentação
if __name__ == "__main__":
    chain = SecureChain()
    
    # Valida a cadeia normal que você gerou no passo anterior
    chain.validar_cadeia()
    
    print("\n[Simulação] Hackeando o arquivo chain.json sorrateiramente...")
    # Lendo o arquivo diretamente para simular um ataque externo contornando o sistema
    with open(ARQUIVO_CHAIN, 'r') as f:
        dados_corrompidos = json.load(f)
    
    # Alterando o texto do último bloco sem recalcular o hash
    if len(dados_corrompidos) > 1:
        dados_corrompidos[-1]['evento'] = "HACKER: Apagando rastros do sistema!"
        with open(ARQUIVO_CHAIN, 'w') as f:
            json.dump(dados_corrompidos, f, indent=4)
            
        print("Ataque concluído. O administrador dispara a validação novamente...")
        
        # Recarregando a classe para ler o arquivo hackeado e rodar a auditoria
        chain_hackeada = SecureChain()
        chain_hackeada.validar_cadeia()

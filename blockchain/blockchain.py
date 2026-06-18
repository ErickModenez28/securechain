import hashlib
import json
import os
import time
from datetime import datetime

ARQUIVO_CHAIN = 'blockchain/chain.json'

class SecureChain:
    def __init__(self):
        self.cadeia = self.carregar_cadeia()
        if not self.cadeia:
            self.criar_bloco_genesis()

    def carregar_cadeia(self):
        if not os.path.exists(ARQUIVO_CHAIN):
            return []
        try:
            with open(ARQUIVO_CHAIN, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def salvar_cadeia(self):
        os.makedirs(os.path.dirname(ARQUIVO_CHAIN), exist_ok=True)
        with open(ARQUIVO_CHAIN, 'w') as f:
            json.dump(self.cadeia, f, indent=4)

    def calcular_hash_bloco(self, bloco):
        bloco_copia = bloco.copy()
        if 'hash_atual' in bloco_copia:
            del bloco_copia['hash_atual']
        
        bloco_string = json.dumps(bloco_copia, sort_keys=True).encode()
        return hashlib.sha256(bloco_string).hexdigest()

    def criar_bloco_genesis(self):
        bloco = {
            "timestamp": datetime.now().isoformat(),
            "evento": "Bloco Genesis - Inicializacao da SecureChain Audit",
            "hash_anterior": "0" * 64
        }
        bloco["hash_atual"] = self.calcular_hash_bloco(bloco)
        self.cadeia.append(bloco)
        self.salvar_cadeia()

    def registrar_evento(self, evento):
        self.cadeia = self.carregar_cadeia() 
        bloco_anterior = self.cadeia[-1]
        novo_bloco = {
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            "hash_anterior": bloco_anterior["hash_atual"]
        }
        novo_bloco["hash_atual"] = self.calcular_hash_bloco(novo_bloco)
        self.cadeia.append(novo_bloco)
        self.salvar_cadeia()

    def validar_cadeia(self):
        self.cadeia = self.carregar_cadeia() 
        
        for i in range(len(self.cadeia)):
            bloco_atual = self.cadeia[i]

            # 1. Verifica adulteração direta (PARA TODOS OS BLOCOS)
            hash_recalculado = self.calcular_hash_bloco(bloco_atual)
            if bloco_atual.get('hash_atual') != hash_recalculado:
                print("\n" + "="*70)
                print("[ALERTA CRÍTICO PARA O ADMINISTRADOR]")
                print(f"FRAUDE DETECTADA! Adulteração direta de dados no Bloco {i}!")
                print(f" -> Os dados originais deste bloco foram modificados de forma ilícita.")
                print(f" -> Hash original armazenado: {bloco_atual.get('hash_atual')}")
                print(f" -> Hash recalculado agora:   {hash_recalculado}")
                print(f" -> Timestamp da anomalia: {bloco_atual.get('timestamp')}")
                print("="*70 + "\n")
                return False

            # 2. Verifica quebra de encadeamento (APENAS DO BLOCO 1 EM DIANTE)
            if i > 0:
                bloco_anterior = self.cadeia[i-1]
                if bloco_atual.get('hash_anterior') != bloco_anterior.get('hash_atual'):
                    print("\n" + "="*70)
                    print("[ALERTA CRÍTICO PARA O ADMINISTRADOR]")
                    print(f"FRAUDE DETECTADA! Quebra de encadeamento no Bloco {i}!")
                    print(f" -> O 'hash_anterior' não bate com a assinatura do bloco passado.")
                    print(f" -> Timestamp da anomalia: {bloco_atual.get('timestamp')}")
                    print("="*70 + "\n")
                    return False

        return True

    def iniciar_auditoria_continua(self, intervalo_segundos=5):
        print(f"--- Iniciando Auditoria Contínua da Blockchain (Verificação a cada {intervalo_segundos}s) ---")
        print("Pressione Ctrl+C para interromper o monitoramento.\n")
        try:
            while True:
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if self.validar_cadeia():
                    print(f"[{data_hora}] Auditoria executada: Blockchain perfeitamente íntegra.")
                else:
                    print(f"[{data_hora}] AUDITORIA INTERROMPIDA: Cadeia comprometida!")
                    print("Aguardando ação do Administrador...")
                    break 
                
                time.sleep(intervalo_segundos)
        except KeyboardInterrupt:
            print("\n[INFO] Auditoria contínua paralisada pelo administrador.")

if __name__ == "__main__":
    chain = SecureChain()
    chain.iniciar_auditoria_continua(5)

import json
import os
import hashlib
import uuid
from datetime import datetime

ARQUIVO_USUARIOS = 'usuarios/dados.json'
ARQUIVO_CHAIN = 'blockchain/chain.json'
PERFIS_PERMITIDOS = ['administrador', 'analista', 'visitante']

def calcular_hash_bloco(bloco):
    bloco_string = json.dumps(bloco, sort_keys=True).encode()
    return hashlib.sha256(bloco_string).hexdigest()

def registrar_blockchain(mensagem):
    """Registra o evento de login/cadastro na Blockchain."""
    os.makedirs(os.path.dirname(ARQUIVO_CHAIN), exist_ok=True)
    chain = []
    if os.path.exists(ARQUIVO_CHAIN):
        with open(ARQUIVO_CHAIN, 'r') as f:
            try: chain = json.load(f)
            except json.JSONDecodeError: pass

    hash_anterior = chain[-1].get("hash_atual", "0"*64) if chain else "0"*64

    novo_bloco = {
        "timestamp": datetime.now().isoformat(),
        "evento": mensagem,
        "hash_anterior": hash_anterior
    }
    novo_bloco["hash_atual"] = calcular_hash_bloco(novo_bloco)
    chain.append(novo_bloco)

    with open(ARQUIVO_CHAIN, 'w') as f:
        json.dump(chain, f, indent=4)

def gerar_hash_senha(senha, salt=None):
    """Gera um hash SHA-256 com salt para a senha."""
    if salt is None:
        salt = uuid.uuid4().hex
    hash_senha = hashlib.sha256((salt + senha).encode()).hexdigest()
    return hash_senha, salt

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    with open(ARQUIVO_USUARIOS, 'r') as f:
        try: return json.load(f)
        except: return {}

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, 'w') as f:
        json.dump(dados, f, indent=4)

def cadastrar_usuario(username, senha, perfil):
    if perfil not in PERFIS_PERMITIDOS:
        print(f"[ERRO] Perfil inválido. Escolha entre: {', '.join(PERFIS_PERMITIDOS)}")
        return

    usuarios = carregar_usuarios()
    if username in usuarios:
        print("[ERRO] Usuário já existe!")
        return

    hash_senha, salt = gerar_hash_senha(senha)
    usuarios[username] = {
        "hash": hash_senha,
        "salt": salt,
        "perfil": perfil
    }
    salvar_usuarios(usuarios)
    
    msg_audit = f"Usuário criado: {username} (Perfil: {perfil})"
    registrar_blockchain(msg_audit)
    print(f"[SUCESSO] {msg_audit}")

def login(username, senha):
    usuarios = carregar_usuarios()
    
    if username not in usuarios:
        msg_audit = f"Tentativa de acesso negada: usuário '{username}' inexistente"
        registrar_blockchain(msg_audit)
        print("[ACESSO NEGADO] Usuário ou senha incorretos.")
        return False

    dados_usuario = usuarios[username]
    hash_calculado, _ = gerar_hash_senha(senha, dados_usuario["salt"])

    if hash_calculado == dados_usuario["hash"]:
        msg_audit = f"Login realizado com sucesso: {username} (Perfil: {dados_usuario['perfil']})"
        registrar_blockchain(msg_audit)
        print(f"[ACESSO PERMITIDO] Bem-vindo, {username}! Perfil ativo: {dados_usuario['perfil']}")
        return True
    else:
        msg_audit = f"Tentativa de acesso negada: senha incorreta para '{username}'"
        registrar_blockchain(msg_audit)
        print("[ACESSO NEGADO] Usuário ou senha incorretos.")
        return False

if __name__ == "__main__":
    print("--- SecureChain Audit: Módulo de Autenticação (RF02) ---")
    
    # Simulação automática para evidenciar o funcionamento para o professor
    print("\n1. Cadastrando usuários de teste...")
    cadastrar_usuario("admin_master", "SenhaSuperForte123", "administrador")
    cadastrar_usuario("visitante01", "senha123", "visitante")
    
    print("\n2. Testando Logins...")
    login("admin_master", "SenhaSuperForte123") # Deve funcionar
    login("visitante01", "senha_errada")        # Deve falhar e registrar na blockchain
    login("hacker", "123456")                   # Deve falhar e registrar na blockchain

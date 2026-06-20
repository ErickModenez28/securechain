import json
import os
import hashlib
import uuid
import subprocess
from datetime import datetime
import getpass

ARQUIVO_USUARIOS = 'usuarios/dados.json'
ARQUIVO_CHAIN = 'blockchain/chain.json'
PERFIS_PERMITIDOS = ['administrador', 'analista', 'visitante']

def calcular_hash_bloco(bloco):
    bloco_copia = bloco.copy()
    if 'hash_atual' in bloco_copia:
        del bloco_copia['hash_atual']
    bloco_string = json.dumps(bloco_copia, sort_keys=True).encode()
    return hashlib.sha256(bloco_string).hexdigest()

def registrar_blockchain(mensagem):
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

def aplicar_permissoes_automaticas():
    """Aplica as regras do Zero Trust no Linux baseando-se nos usuários cadastrados."""
    usuarios = carregar_usuarios()
    
    admin = next((u for u, d in usuarios.items() if d['perfil'] == 'administrador'), None)
    analista = next((u for u, d in usuarios.items() if d['perfil'] == 'analista'), None)
    visitante = next((u for u, d in usuarios.items() if d['perfil'] == 'visitante'), None)

    if not admin: return

    grupo_base = analista if analista else admin

    try:
        os.makedirs('documentos', exist_ok=True)
        os.makedirs('auditoria/relatorios', exist_ok=True)

        # 1. Base - Admin dono, Analista grupo (750)
        subprocess.run(['chown', '-R', f'{admin}:{grupo_base}', '.'], stderr=subprocess.DEVNULL)
        subprocess.run(['chmod', '-R', '750', '.'], stderr=subprocess.DEVNULL)

        # 2. Documentos - Trancado só para Admin (700)
        subprocess.run(['chown', '-R', f'{admin}:{admin}', 'documentos/'], stderr=subprocess.DEVNULL)
        subprocess.run(['chmod', '-R', '700', 'documentos/'], stderr=subprocess.DEVNULL)

        # 3. Relatórios - Admin dono, Visitante grupo (750)
        if visitante:
            subprocess.run(['chown', '-R', f'{admin}:{visitante}', 'auditoria/relatorios/'], stderr=subprocess.DEVNULL)
            subprocess.run(['chmod', '-R', '750', 'auditoria/relatorios/'], stderr=subprocess.DEVNULL)

        # 4. Travessia
        subprocess.run(['chmod', 'o+x', '.'], stderr=subprocess.DEVNULL)
        subprocess.run(['chmod', 'o+x', 'auditoria'], stderr=subprocess.DEVNULL)
    except Exception: pass

def cadastrar_usuario(username, senha, perfil):
    if perfil not in PERFIS_PERMITIDOS:
        print(f"[ERRO] Perfil inválido.")
        return

    usuarios = carregar_usuarios()
    if username in usuarios:
        print("[ERRO] Usuário já existe!")
        return

    print(f"\n[*] Integrando '{username}' ao Linux...")
    try:
        args = ['useradd', '-m', '-s', '/bin/bash']
        if perfil == 'administrador': args.extend(['-G', 'sec_docs,sudo'])
        elif perfil == 'analista': args.extend(['-G', 'sec_docs'])
        args.append(username)
        subprocess.run(args, check=True, stderr=subprocess.DEVNULL)
        
        proc = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE, text=True)
        proc.communicate(f"{username}:{senha}")
        
        hash_senha, salt = gerar_hash_senha(senha)
        usuarios[username] = {"hash": hash_senha, "salt": salt, "perfil": perfil}
        salvar_usuarios(usuarios)
        
        aplicar_permissoes_automaticas()
        registrar_blockchain(f"Usuário criado: {username} ({perfil})")
        print("[SUCESSO] Usuário integrado.")
    except Exception as e:
        print(f"[ERRO] Falha: {e}")

def remover_usuario(username):
    usuarios = carregar_usuarios()
    if username not in usuarios:
        print("[ERRO] Usuário não encontrado.")
        return

    subprocess.run(['userdel', '-r', username], stderr=subprocess.DEVNULL)
    del usuarios[username]
    salvar_usuarios(usuarios)
    aplicar_permissoes_automaticas()
    registrar_blockchain(f"Usuário removido: {username}")
    print("[SUCESSO] Usuário removido.")

def login(username, senha):
    usuarios = carregar_usuarios()
    if username not in usuarios:
        print("[ERRO] Acesso negado.")
        return

    dados = usuarios[username]
    h, _ = gerar_hash_senha(senha, dados["salt"])

    if h == dados["hash"]:
        registrar_blockchain(f"Login: {username}")
        print(f"\n[ACESSO PERMITIDO] Bem-vindo, {username}!")
        subprocess.run(['su', username])
    else:
        print("[ERRO] Senha incorreta.")

if __name__ == "__main__":
    while True:
        print("\n" + "="*50 + "\n🛡️ SECURECHAIN AUDIT\n" + "="*50)
        print("1. Fazer Login\n2. Cadastrar Novo Usuário\n3. Remover Usuário\n4. Sair")
        op = input("Escolha: ")
        if op == '1':
            user = input("Usuário: "); senha = getpass.getpass("Senha: ")
            login(user, senha)
        elif op == '2':
            user = input("Novo Usuário: "); senha = getpass.getpass("Senha: "); perfil = input("Perfil (admin/analista/visitante): ").lower()
            cadastrar_usuario(user, senha, perfil)
        elif op == '3':
            user = input("Usuário a remover: "); remover_usuario(user)
        elif op == '4': break


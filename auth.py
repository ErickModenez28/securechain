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

def cadastrar_usuario(username, senha, perfil):
    if perfil not in PERFIS_PERMITIDOS:
        print(f"[ERRO] Perfil inválido. Escolha entre: {', '.join(PERFIS_PERMITIDOS)}")
        return

    if len(senha) < 6:
        print("[ERRO] A senha é muito curta. Use no mínimo 6 caracteres por segurança.")
        return

    usuarios = carregar_usuarios()
    if username in usuarios:
        print("[ERRO] Usuário já existe no banco de dados!")
        return

    try:
        resultado = subprocess.run(['id', username], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if resultado.returncode == 0:
            print(f"[ERRO] O usuário '{username}' já existe no Linux!")
            return
    except Exception:
        pass

    # ================================================================
    # INTEGRAÇÃO DE PERMISSÕES REAIS (RBAC) NO LINUX
    # ================================================================
    print(f"\n[*] Solicitando criação do usuário '{username}' ao Linux...")
    try:
        # Prepara o comando base
        argumentos_useradd = ['useradd', '-m', '-s', '/bin/bash']
        
        # Mapeamento de Perfis para Grupos do Linux
        if perfil == 'administrador':
            argumentos_useradd.extend(['-G', 'sec_docs,sudo']) # Acesso aos docs + Poder de Root
        elif perfil == 'analista':
            argumentos_useradd.extend(['-G', 'sec_docs'])      # Acesso aos docs apenas
        # Se for visitante, não adiciona flag -G (fica isolado)
            
        argumentos_useradd.append(username)
        
        # Dispara a criação no SO com os privilégios corretos
        subprocess.run(argumentos_useradd, check=True, stderr=subprocess.DEVNULL)
        
        process = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(f"{username}:{senha}")
        
        if process.returncode != 0:
            print(f"[ERRO CRÍTICO] O Linux recusou a senha definida: {stderr.strip()}")
            subprocess.run(['userdel', '-r', username], stderr=subprocess.DEVNULL) 
            return
            
        print(f"[*] Usuário '{username}' integrado ao SO com privilégios de '{perfil.upper()}'.")
    except subprocess.CalledProcessError:
        print(f"\n[ERRO CRÍTICO] Falha ao criar usuário. Rodou com 'sudo'?")
        return
    # ================================================================

    hash_senha, salt = gerar_hash_senha(senha)
    usuarios[username] = {
        "hash": hash_senha,
        "salt": salt,
        "perfil": perfil
    }
    salvar_usuarios(usuarios)
    
    msg_audit = f"Usuário REAL criado no SO com privilégios: {username} (Perfil: {perfil})"
    registrar_blockchain(msg_audit)
    print(f"[SUCESSO] {msg_audit}")

def remover_usuario(username):
    usuarios = carregar_usuarios()
    
    if username not in usuarios:
        print(f"[ERRO] O usuário '{username}' não existe no banco de dados do sistema.")
        return

    print(f"\n[*] Solicitando remoção do usuário '{username}' ao Linux...")
    try:
        # Remove o usuário e o diretório home (-r) no SO
        subprocess.run(['userdel', '-r', username], check=True, stderr=subprocess.DEVNULL)
        print(f"[*] Usuário '{username}' removido do SO com sucesso.")
    except subprocess.CalledProcessError:
        print(f"[AVISO] O usuário '{username}' não foi encontrado no SO ou ocorreu um erro de permissão. Certifique-se de usar sudo.")

    # Remove do banco de dados local
    del usuarios[username]
    salvar_usuarios(usuarios)
    
    msg_audit = f"Usuário removido do sistema: {username}"
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
        msg_audit = f"Login realizado no script e SO acessado: {username} (Perfil: {dados_usuario['perfil']})"
        registrar_blockchain(msg_audit)
        print(f"\n[ACESSO PERMITIDO] Bem-vindo, {username}! Perfil ativo: {dados_usuario['perfil']}")
        
        # Inicia a sessão real no Sistema Operacional
        print(f"[*] Abrindo terminal seguro para {username}... (Digite 'exit' para encerrar a sessão e voltar ao menu)")
        try:
            # O subprocesso chama o 'su -' que abre o shell com as variáveis de ambiente do usuário logado
            subprocess.run(['su', username])
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar a sessão no SO: {e}")
            
        print(f"\n[*] Sessão de {username} encerrada. Retornando ao menu do SecureChain Audit.")
        return True
    else:
        msg_audit = f"Tentativa de acesso negada: senha incorreta para '{username}'"
        registrar_blockchain(msg_audit)
        print("[ACESSO NEGADO] Usuário ou senha incorretos.")
        return False

if __name__ == "__main__":
    # Garante que o arquivo de usuários foi modificado no topo para 'usuarios/dado.json' conforme validado no relatório.
    os.makedirs('usuarios', exist_ok=True)
    
    while True:
        print("\n" + "="*50)
        print("🛡️  SECURECHAIN AUDIT - MÓDULO DE ACESSO")
        print("="*50)
        print("1. Fazer Login")
        print("2. Cadastrar Novo Usuário")
        print("3. Remover Usuário")
        print("4. Sair")
        print("="*50)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            print("\n--- TELA DE LOGIN ---")
            user = input("Usuário: ")
            senha = getpass.getpass("Senha: ")
            login(user, senha)
            
        elif opcao == '2':
            print("\n--- NOVO CADASTRO (REQUER SUDO) ---")
            user = input("Novo Usuário: ")
            senha = getpass.getpass("Senha: ")
            print("Perfis disponíveis: administrador, analista, visitante")
            perfil = input("Perfil escolhido: ").lower()
            cadastrar_usuario(user, senha, perfil)
            
        elif opcao == '3':
            print("\n--- REMOVER USUÁRIO (REQUER SUDO) ---")
            user = input("Digite o nome do usuário que deseja excluir: ")
            confirmacao = input(f"Tem certeza que deseja apagar '{user}' permanentemente? (s/n): ").lower()
            if confirmacao == 's':
                remover_usuario(user)
            else:
                print("[INFO] Operação cancelada.")
                
        elif opcao == '4':
            print("\n[INFO] Encerrando Módulo de Acesso. Até logo!")
            break
            
        else:
            print("\n[ERRO] Opção inválida. Digite 1, 2, 3 ou 4.")

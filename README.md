# 🛡️ SecureChain Audit

Plataforma de Auditoria e Segurança de Sistemas Baseada em Blockchain, desenvolvida em ambiente Linux.
 
**Autor:** Erick Domingos Modenez

---

## 📋 Pré-requisitos

* Sistema Operacional: **Linux Debian 13**
* **Python 3** instalado nativamente.
* **OpenSSL**.
* Privilégios de Administrador (`sudo`) para gerenciamento de contas.

---

## 📂 Estrutura do Projeto

O sistema é modular e dividido nas seguintes responsabilidades:

```text
securechain/
├── auditoria/          # Scripts de auditoria do sistema operacional (who, last, ss)
│   ├── auditor.py
│   └── relatorios/     # Saída dos relatórios gerados
├── backup/             # Rotinas de contingência e criptografia
│   └── backup.sh
├── blockchain/         # Motor de rastreabilidade imutável e validação contínua
│   ├── blockchain.py
│   └── chain.json      # Arquivo de persistência da cadeia (gerado automaticamente)
├── documentos/         # Diretório restrito de arquivos monitorados pelo sistema
├── usuarios/           # Banco de dados local de senhas com Hash + Salt
│   └── dados.json
├── auth.py             # Rotina para logar, cadastrar ou excluir usuários
└── monitor.py          # Monitoramento de integridade de arquivos baseado em SHA-256

🚀 Como Utilizar o Sistema (Manual de Operação)
O sistema deve ser operado através do terminal do Linux. Abaixo estão os comandos para inicializar cada camada de segurança.

1. Autenticação e Controle de Acesso (Zero Trust)
O acesso às funções da máquina é blindado por um script Python que valida credenciais e delega a sessão diretamente no Sistema Operacional.
Comando:

Bash
sudo python3 auth.py
O que faz: Permite realizar login seguro, criar usuários com perfis pré-definidos (Administrador, Analista, Visitante) integrados ao controle de grupos do Linux, ou remover usuários.

2. Monitoramento de Integridade de Arquivos (FIM)
Vigia a pasta de documentos sigilosos contra adulterações em tempo real.
Comando:

Bash
python3 monitor.py
O que faz: Calcula os hashes (SHA-256) dos arquivos. Se detectar alterações, inclusões ou exclusões, registra um evento crítico na blockchain. Deve ser mantido rodando em background.

3. Validador Contínuo da Blockchain
Garante que os logs de segurança não foram fraudados ou apagados.
Comando:

Bash
python3 blockchain/blockchain.py
O que faz: Varre o arquivo chain.json a cada 5 segundos. Recalcula os hashes e verifica o encadeamento. Se um invasor adulterar o arquivo JSON manualmente, o sistema trava e emite um alerta vermelho acusando o bloco corrompido.

4. Auditoria Ativa do Sistema Operacional
Gera relatórios de conformidade da própria máquina virtual.
Comando:

Bash
python3 auditoria/auditor.py
O que faz: Executa varreduras de rede e sessões (who, last, ss -tulpn, ip a) e exporta os dados limpos para a pasta auditoria/relatorios/.

5. Backup Seguro e Automatizado
Garante a disponibilidade e a confidencialidade dos dados em caso de desastre.
Comando:

Bash
sudo ./backup/backup.sh
O que faz: Compacta a pasta de documentos e relatórios (.tar.gz), aplica criptografia militar AES-256-CBC, gera um arquivo blindado .enc e registra a operação na blockchain.

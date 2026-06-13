#!/bin/bash
# Script para resolver o RF01 - Criacao de usuarios e Controle de Acesso

echo "Criando os usuarios no sistema..."
# Cria os usuários com diretório home e shell padrão
sudo useradd -m -s /bin/bash administrador
sudo useradd -m -s /bin/bash analista
sudo useradd -m -s /bin/bash visitante

# Define uma senha padrão para os testes do professor (securechain123)
echo "administrador:Securechain123@!" | sudo chpasswd
echo "analista:Securechain123@!" | sudo chpasswd
echo "visitante:Securechain123@!" | sudo chpasswd

echo "Aplicando as permissoes nos diretorios..."

# Garante que a pasta de relatorios existe
mkdir -p auditoria/relatorios

# 1. O 'administrador' passa a ser o dono da pasta inteira, e 'analista' o grupo principal
sudo chown -R administrador:analista .

# 2. Permissão base: Administrador (Lê/Grava/Executa), Analista (Lê/Executa), Outros (Nada)
sudo chmod -R 750 .

# 3. Tratamento especial para a pasta de relatórios (Acesso do visitante)
# Muda o grupo especificamente dessa pasta para 'visitante'
sudo chown -R administrador:visitante auditoria/relatorios

# Permissão da pasta relatorios: Admin (Tudo), Visitante como grupo (Lê e Acessa), Outros (Nada)
sudo chmod 750 auditoria/relatorios

# 4. Para o visitante conseguir CHEGAR na pasta relatorios, ele precisa da permissão 
# de execução (x) (apenas travessia, sem leitura) nas pastas pai
sudo chmod o+x .
sudo chmod o+x auditoria

echo "Configuracao de usuarios e permissoes concluida!"

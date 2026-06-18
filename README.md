# Prova Prática - SecureChain Audit - Plataforma de Auditoria Baseada em Blockchain

**Nome:** Erick Domingos Modanez - **RA:** 201710299

---

## 1. Gerenciamento de Identidades e Controle de Acesso (RF01)
A primeira linha de defesa do nosso projeto é a própria configuração de permissões do Linux. A ideia foi organizar os usuários locais e garantir que cada um só consiga acessar as pastas e arquivos que realmente precisa, evitando que alguém mexa onde não deve.

### 1.1. Regra do Privilégio Mínimo
Nesse sistema, ninguém tem acesso total logo de cara. Cada usuário recebeu apenas as permissões necessárias para o seu papel:

* **Usuário `visitante`:** É o mais restrito. O Linux bloqueia ele de ver os códigos em Python ou as senhas. A única coisa que ele consegue fazer é abrir a pasta de relatórios públicos para leitura.
* **Usuário `analista`:** Usado para o dia a dia do sistema. Ele tem permissão para rodar os scripts e verificar a integridade da blockchain, mas não tem poder para alterar configurações gerais da máquina ou apagar o histórico de logs.
* **Usuário `administrador`:** É o dono do sistema. Tem controle total sobre as pastas, códigos e configurações do Linux.

### 1.2. Divisão de Tarefas
Para evitar problemas, separamos o que cada perfil pode fazer:

| Perfil | O que faz | O que não pode fazer |
| :--- | :--- | :--- |
| **`administrador`** | Cuida do código e das configurações principais do Linux. | Não deve ser usado para tarefas comuns do dia a dia, apenas para manutenção. |
| **`analista`** | Roda a verificação da blockchain e os scripts de auditoria. | Não consegue alterar o código principal nem mudar as permissões dos arquivos. |
| **`visitante`** | Apenas lê os relatórios gerados. | Bloqueado de rodar qualquer script ou acessar o sistema por dentro. |

### 1.3. Configurando Permissões (`chmod` e `chown`)
Para fazer essas regras funcionarem na prática, usamos os comandos nativos do Linux (`chown` para definir o dono e `chmod` para definir quem lê, escreve ou executa):

| Diretório / Arquivo | Dono | Grupo | Permissão | Resumo |
| :--- | :--- | :--- | :--- | :--- |
| `securechain/` (Raiz) | `administrador` | `analista` | `750` | O admin manda em tudo, o analista pode ler, e o visitante é barrado de entrar na pasta principal. |
| `blockchain/` | `administrador` | `analista` | `750` | Impede que pessoas de fora leiam ou alterem o código da nossa blockchain. |
| `auditoria/relatorios/` | `administrador` | `visitante` | `750` | Liberamos essa pasta específica para que o visitante possa entrar e ler os relatórios. |

*Observação:* Para o visitante conseguir chegar na pasta de relatórios sem poder listar o que tem nas pastas anteriores, liberamos apenas a permissão de "execução/travessia" (`--x`) no caminho principal.

## 2. Sistema de Autenticação em Python (RF02)
A segunda parte da segurança acontece no nosso código Python. Ele garante que os scripts do SecureChain só rodem se a pessoa estiver logada corretamente.

### 2.1. Criptografia das Senhas
Para não deixar as senhas fáceis de ler no banco de dados (em texto puro), usamos a biblioteca `bcrypt`. 

* Em vez de salvar a senha real, o sistema gera um "hash" (um código bagunçado e irreversível) misturado com caracteres aleatórios (*salt*).
* As senhas ficam salvas no arquivo `usuarios/dados.json` apenas nesse formato criptografado (ex: `$2b$12$...`). Se alguém roubar esse arquivo, não vai conseguir descobrir qual era a senha original digitada pelo usuário.

### 2.2. Telas e Perfis
Quando o usuário tenta logar, o arquivo `auth.py` pega a senha digitada, transforma em hash na hora e compara com o que está salvo. Se bater, ele libera o acesso de acordo com o nível da pessoa (Administrador, Analista ou Visitante). Se a senha estiver errada, o sistema bloqueia o acesso e registra a tentativa de invasão.

## 3. Monitoramento de Integridade de Arquivos (RF03)
O foco deste requisito é garantir total visibilidade sobre o que acontece com os documentos sigilosos da infraestrutura, mantendo um registro histórico acessível para conferência de segurança.

### 3.1. Monitoramento e Registro
A auditoria é realizada pelo script `monitor.py`, que atua como um observador silencioso dos arquivos.
* **Detecção:** O script monitora a pasta `/documentos`. Ele calcula o hash original de tudo e, se houver alterações, inclusões ou exclusões de arquivos, ele detecta a anomalia imediatamente.
* **Relatórios:** Quando uma inconsistência é detectada (como a injeção de uma cláusula maliciosa em um contrato), o sistema dispara um alerta crítico e salva isso diretamente na nossa trilha de auditoria imutável.

## 4. Blockchain de Auditoria (RF04)
Um log normal em arquivo de texto pode ser facilmente editado e apagado por um invasor. Para resolver isso, nosso sistema salva cada evento em "blocos".
* Cada bloco de evento recebe uma assinatura digital única gerada pela matemática do **SHA-256**.
* O truque da segurança é que o código de um novo bloco sempre carrega um pedaço do código do bloco anterior (`hash_anterior`), formando uma corrente inquebrável.

### 4.2. Detecção de Alterações
Se alguém abrir o arquivo `chain.json` e tentar alterar uma data ou apagar um registro de invasão do passado, a assinatura daquele bloco vai mudar na mesma hora. Como o bloco da frente depende da assinatura antiga, a alteração quebra a corrente inteira matematicamente, avisando o administrador que o arquivo foi fraudado.

## 5. Backup Seguro Automatizado (RF05)
Para garantir a continuidade do negócio e a recuperação em caso de desastres, implementamos um mecanismo robusto de backup e proteção dos artefatos críticos.

### 5.1. Criptografia e Armazenamento
Os documentos e logs do sistema são processados de forma a garantir a confidencialidade dos dados em repouso.
* **Compactação:** Antes do armazenamento, os diretórios críticos são compactados para otimizar o uso do disco.
* **Segurança:** Aplicamos um padrão de criptografia AES nos arquivos de backup (ex: `backup/documentos_2026-06-13T...enc`), assegurando que apenas usuários com a chave correta consigam descriptografar e visualizar o conteúdo original.

## 6. Auditoria do Sistema Operacional (RF06)
Para fechar o cerco e ver o que está acontecendo "por debaixo dos panos" no servidor Debian, desenvolvemos um script de coleta de dados locais.

### 6.1. Coleta de Rede e Usuários
Através do arquivo `auditoria/auditor.py`, automatizamos a execução de comandos vitais do Linux:
* **Usuários Ativos:** Usamos o `who` para saber quem está logado no momento e o `last` para puxar o histórico recente de acessos.
* **Rede e Portas:** Disparamos o `ss -tulpn` para ver quais portas e serviços estão abertos, e o `ip a` para verificar os endereços IP e as interfaces de rede.
* **Evidências:** Os dados processados são exportados automaticamente para relatórios datados em formato `.txt` na pasta `auditoria/relatorios/`. Isso permite que o usuário `visitante` valide o status de conformidade sem expor dados internos sensíveis e sem ter permissão para digitar os comandos diretamente no terminal.

## 7. Validação da Integridade da Blockchain (RF07)
Para fechar o ciclo de segurança e provar que ninguém adulterou os nossos próprios logs, desenvolvemos o script `blockchain/blockchain.py`. Ele serve para auditar a própria ferramenta de auditoria.

### 7.1. Auditoria Contínua
Quando o script é executado, ele percorre toda a cadeia do arquivo `chain.json`, recalculando os blocos matematicamente do zero para validar se:
1. **Adulteração Direta:** Ocorreu alguma mudança nos dados (o hash recalculado na hora é diferente do `hash_atual` armazenado).
2. **Quebra de Encadeamento:** Alguém tentou inserir ou remover um bloco inteiro (o `hash_anterior` de um bloco não reflete a assinatura do bloco passado).

Se qualquer uma dessas regras for quebrada, o sistema acusa fraude imediatamente, indicando qual bloco exato foi corrompido.

---

## 8. Princípios de Segurança Aplicados

### 8.1. Zero Trust Security
Aplicamos o conceito de "Confiança Zero" em todas as camadas do projeto. Respondendo às exigências da avaliação:

**1. Como o sistema verifica a identidade dos usuários em cada acesso?**
Através do script `auth.py`, que exige as credenciais a cada execução. A identidade é verificada calculando o hash SHA-256 da senha fornecida somada ao *salt* específico daquele usuário, comparando o resultado com a base de dados criptografada.

**2. Como as permissões são controladas e auditadas?**
São controladas no nível do Sistema Operacional usando `chown` e `chmod`, garantindo isolamento total de pastas (RF01). São auditadas através da nossa Blockchain (RF04), que registra de forma permanente quem fez login, quando fez, e quais tentativas falhas ocorreram.

**3. Como o princípio do menor privilégio foi aplicado na prática?**
Configurando o usuário `visitante` apenas com permissão de travessia (`--x`) no diretório raiz e permissão de leitura exclusiva na pasta de relatórios. Ele não possui acesso de escrita, nem consegue ler o código-fonte principal ou os documentos.

**4. Como as ações dos usuários são registradas de forma imutável?**
Através do encadeamento criptográfico da nossa Blockchain. Qualquer tentativa de editar um log passado no arquivo JSON fará com que a matemática do hash SHA-256 mude, quebrando o `hash_anterior` do bloco seguinte e disparando os alertas do nosso script de validação (RF07).

### 8.2. Engenharia de Software Segura (Mitigações)

| Falha / Vulnerabilidade | Como foi mitigada no projeto |
| :--- | :--- |
| **Senhas em texto puro** | Implementação de Hash SHA-256 com *Salt* individual aleatório na base de dados (`usuarios/dados.json`). |
| **Permissões excessivas de arquivos/diretórios** | Aplicação estrita de `chmod 750` e separação rigorosa de donos e grupos (`administrador`, `analista`, `visitante`). |
| **Ausência de logs de eventos** | Criação de uma Blockchain local que atua como registro descentralizado e imutável de eventos críticos do sistema. |
| **Ausência de validação de entrada** | O perfil do usuário durante o cadastro é validado contra uma lista estrita (`PERFIS_PERMITIDOS`), impedindo a injeção indevida de privilégios. |

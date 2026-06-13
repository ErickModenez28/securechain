# Prova Prática - SecureChain Audit - Plataforma de Auditoria Baseada em Blockchain

Nome : Erick Domingos Modenez - RA : 201710299 
---

## 1. Gerenciamento de Identidades e Controle de Acesso (RF01)

A primeira camada de defesa do ecossistema baseia-se no hardening do sistema operacional. A mitigação de ameaças internas, adulteração de evidências e elevação injustificada de privilégios foi implementada por meio de uma política rigorosa de controle de acesso discricionário (DAC), mapeando identidades locais a papéis organizacionais estritos.

### 1.1. Princípio do Menor Privilégio (Least Privilege)
Sob a ótica da arquitetura *Zero Trust*, nenhuma entidade possui privilégios implícitos. Cada identidade possui apenas os direitos de acesso operacionais mínimos necessários para o cumprimento de suas obrigações funcionais, limitando o raio de destruição (*blast radius*) em caso de comprometimento de credenciais:

* **Usuário `visitante`:** Possui o maior nível de restrição do sistema. Seu escopo de atuação é estritamente passivo. O sistema operacional bloqueia completamente sua capacidade de visualizar o código-fonte da blockchain, ler arquivos de configuração ou acessar diretórios de credenciais. Seu privilégio estende-se única e exclusivamente à leitura de artefatos de auditoria finais contidos no subdiretório de relatórios públicos.
* **Usuário `analista`:** Destinado à operação técnica regular e monitoramento operacional. Possui permissões de leitura e execução de módulos lógicos (módulos Python e scripts Bash), permitindo-lhe validar a integridade da cadeia e disparar rotinas. Contudo, não detém privilégios de escrita sobre o histórico consolidado de logs ou permissão para reconfigurar políticas globais do sistema.
* **Usuário `administrador`:** Detém a custódia da infraestrutura de auditoria e controle total sobre o ecossistema, atuando como o proprietário dos processos críticos de escrita, provisionamento de chaves e reconfiguração de integridade.

### 1.2. Segregação de Funções (Segregation of Duties)
A separação impede o acúmulo de responsabilidades incompatíveis por um único indivíduo, mitigando fraudes e ocultação de ações maliciosas:

| Perfil | Função Operacional | Restrição de Controle Base |
| :--- | :--- | :--- |
| **`administrador`** | Gerenciamento de chaves, manutenção de código, governança do SO e escrita inicial de parâmetros. | Não realiza análises rotineiras sob a conta administrativa, segregando ações cotidianas de manutenções estruturais. |
| **`analista`** | Execução de rotinas de verificação de integridade, checagem da blockchain e disparo de auditorias periódicas. | Totalmente incapaz de modificar o código de validação ou alterar permissões de segurança de arquivos críticos. |
| **`visitante`** | Visualização externa e independente do status de conformidade da organização através de relatórios. | Bloqueio absoluto de execução de ferramentas, modificação de arquivos ou visibilidade de metadados internos. |

### 1.3. Mecanismos de Controle de Acesso Técnico (`chmod`, `chown` e Grupos)
A materialização das políticas lógicas em controles técnicos rígidos foi efetuada através da manipulação da estrutura de permissões nativas do Linux (POSIX ACLs/DAC), empregando o utilitário `chown` para atribuição de propriedade e `chmod` para calibração de máscaras de bits de acesso:

| Diretório / Arquivo | Dono (Owner) | Grupo (Group) | Permissão (Octal) | Justificativa de Segurança |
| :--- | :--- | :--- | :--- | :--- |
| `securechain/` (Raiz) | `administrador` | `analista` | `750` (`drwxr-x---`) | O dono possui acesso total; o grupo de analistas pode ler e transitar; qualquer outro usuário (incluindo o visitante) é bloqueado por padrão. |
| `blockchain/` | `administrador` | `analista` | `750` (`drwxr-x---`) | Impede a leitura ou adulteração da lógica da cadeia de blocos por usuários externos ou processos não autorizados. |
| `auditoria/relatorios/` | `administrador` | `visitante` | `750` (`drwxr-x---`) | Sobrescreve a herança superior, permitindo que o grupo de visitantes possa ler os relatórios gerados sem expor os códigos da pasta pai. |

Para viabilizar que o usuário `visitante` acesse a pasta profunda de relatórios sem obter visibilidade sobre o conteúdo intermediário do diretório raiz, aplicou-se a técnica de **permissão de travessia**, concedendo apenas o bit de execução (`--x`) para "Outros" (*Others*) na raiz do projeto e na pasta de auditoria:

```bash
# Concessão restrita do bit de execução para viabilizar navegação direcionada
sudo chmod o+x .
sudo chmod o+x auditoria

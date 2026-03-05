# Regras de Desenvolvimento Assistido por Inteligência Artificial (AI Rules)

Este documento dita as regras estritas de arquitetura e design que qualquer Agente de Inteligência Artificial (IA) deve seguir ao sugerir mudanças, refatorações ou implementar novas features neste projeto.

## 1. Arquitetura do Projeto (MVC / Modular)
- **NUNCA** reverta o projeto para um script monolítico (ex: um único `migrador.py`).
- O sistema é dividido estritamente em três camadas:
  1. `src/gui/`: Lida EXCLUSIVAMENTE com a interface visual (`app.py`). Não deve conter regras de regex.
  2. `src/core/`: O "cérebro" do sistema. O `migrator_engine.py` processa os arquivos. O `constants.py` centraliza padrões como de/para de componentes BDE para FireDAC e Unit Scopes. O `i18n.py` gerencia idiomas.
  3. `src/utils/`: Ferramentas auxiliares de Sistema Operacional, como cópia de pastas e detecção de encoding (`file_utils.py`).

## 2. Interface Visual (CustomTkinter)
- O projeto usa `customtkinter` (CTK) para garantir uma UI moderna (estilo Dribbble).
- **NÃO** importe `tkinter` padrão (`tk.Button`, `tk.Frame`). Use sempre os equivalentes em `ctk` (`ctk.CTkButton`, etc.).
- **Regras Práticas de Design UI (Definidas pelo Usuário):**
  - Mantenha o design compacto: Menos espaços vazios mortos. Cards de Origem e Destino devem ficar empilhados verticalmente (um em cima do outro) e não lado a lado se possível, para economizar largura.
  - Utilize `CTkOptionMenu` (Combobox) ao invés de `CTkRadioButton` quando criar opções longas exclusivas para minimizar poluição visual.
  - Mantenha Checkboxes esteticamente uniformes (ex: todos devem usar cor primária neutra na marcação) a menos que lidem com remoção física de disco.
- Não quebre o Layout do "Console Verbose" no fundo do Dashboard. Ele deve permanecer full-width (`columnspan=2`) na linha 4, e receber a maior área útil expansível possível.

## 3. Lógica do Motor de Migração (Engine)
- O motor não deve "travar" a UI (Interface do Usuário). Todas as chamadas do motor a partir de `app.py` devem acontecer em uma Thread separada (`threading.Thread`).
- Os logs do motor para a UI devem usar a função de callback fornecida pelo `app.py` (`log_thread_safe`) com o `.after(0)` do Tkinter, para não causar erros de violação de Thread Access.
- **Modos de Operação Exigidos**:
  1. Extração Segura: Copia a origem para o destino e atua no destino.
  2. In-Place: Modifica diretamente a Origem, `safe_copy_tree` deve ser bypassado.

## 4. Persistência de Dados e Privacidade
- O arquivo `migrador_config.json` salva as preferências do usuário.
- Esse arquivo está no `.gitignore`. **Nunca altere o .gitignore para rastreá-lo**, respeite a privacidade dos caminhos locais do usuário.

## 5. Internacionalização (i18n)
- Se você adicionar um botão novo, janela ou aviso no sistema, **NÃO FAÇA HARDCODE** de strings em `app.py`.
- Adicione a chave correspondente em `src/locales/en.json` e `src/locales/pt.json` e acesse via `self._("sua_chave")`.

## 6. Evolução Viva das Regras (Mandatório)
- Se o usuário pedir para adicionar um novo comportamento arquitetural, preferência de design, ou regra de negócio geral, **VOCÊ DEVE ATUALIZAR ESTE ARQUIVO (`AI_RULES.md`) IMEDIATAMENTE**.
- Este arquivo deve refletir exatamente o que o usuário quer do projeto. Seja proativo e anote os novos desejos do usuário aqui para que as futuras sessões saibam o que fazer.

> Siga estas regras rigorosamente para manter a escalabilidade, estabilidade e profissionalismo desta base de código.

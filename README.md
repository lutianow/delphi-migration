# Migrador Delphi 7 para Delphi 12 (Athens)

Uma ferramenta de interface gráfica desenvolvida em Python + CustomTkinter para converter e modernizar projetos legados em Delphi 7 para as versões mais recentes (ex: Delphi 11/12).

## Funcionalidades Atuais

- **Interface Visual Moderna**: Interface amigável em Dark Mode para seleção de pastas.
- **Cópias Seguras**: O sistema replica a pasta do projeto inteiro para não corromper fontes originais do seu projeto Delphi 7.

*Módulo Funcionalidades (em desenvolvimento):*
- Conversão de *Encoding* (ANSI para UTF-8).
- Atualização e substituição de classes antigas de Banco de Dados BDE (`TQuery`, `TTable`) para FireDAC (`TFDQuery`, `TFDTable`).

## Requisitos

- **Sistema Operacional:** Windows.
- **Ambiente:** Python 3.10 ou superior.
- **Bibliotecas:** `customtkinter` (pode ser instalada via `pip install customtkinter`).

## Como usar

1. Execute o script principal:
   ```bash
   python src/main.py
   # ou
   py src/main.py
   ```
2. Na interface:
   - Escolha a pasta onde está seu projeto original (Delphi 7).
   - Escolha a pasta de destino (onde o projeto migrado deverá ser salvo).
   - Selecione as opções desejadas (UTF-8, Migração BDE).
   - Clique em **"Iniciar Migração"**.

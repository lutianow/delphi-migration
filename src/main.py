# src/main.py

import sys
import os

# Adiciona o diretório base 'delphi-migration' ao path dinamicamente
# para que o python encontre o pacote 'src' sem precisar rodar dentro da pasta.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.app import DelphiMigratorApp

def main():
    app = DelphiMigratorApp()
    app.mainloop()

if __name__ == "__main__":
    main()

import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.append(r"C:\Users\Luciano\Desktop\delphi-migration")

from src.core.migrator_engine import DelphiMigratorEngine

if __name__ == "__main__":
    src_dir = r"C:\Users\Luciano\Desktop\migrador\desen\progs\siap\fontes\master"
    dst_dir = r"C:\Users\Luciano\Desktop\migrador\desen\progs\siap\fontes\master_migrated"
    
    print(f"Buscando arquivos em {src_dir}...")
    
    config = {
        'utf8': True,
        'clean_dir': True,
        'db_main': True,
        'bde': True,
        'dbx': True,
        'ibx': True,
        'ado': True,
        'cds': True,
        'scopes': True,
        'advanced': True,
        'precompile': False, # Don't test the old version
        'include_filters': [],
        'banned_files': ['*.~*', '*.dcu', '*.identcache', '*.local', '*.stat'],
    }
    
    def on_log(msg):
        print(msg)
        
    def on_progress(current, total, file):
        if current % 10 == 0 or current == total:
            print(f"[{current}/{total}] Processando: {file}")

    engine = DelphiMigratorEngine(src_dir, dst_dir, config, on_log, on_progress)
    
    print("Iniciando migração...")
    try:
        engine.start_migration()
        print("Done!")
    except Exception as e:
        print(f"Falha na migracao: {e}")

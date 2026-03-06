import os
import sys

sys.path.append(os.path.abspath("src"))

from core.migrator_engine import DelphiMigratorEngine

if __name__ == "__main__":
    if len(sys.argv) > 2:
        src_dir = sys.argv[1]
        dst_dir = sys.argv[2]
    else:
        src_dir = r"C:\Users\Luciano\Desktop\migrador\desen\progs\siap\fontes\alm"
        dst_dir = r"C:\Users\Luciano\Desktop\migrador\desen\progs\siap\fontes\alm_migrated"
    
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
        'precompile': False,
        'include_filters': [],
        'ignore_filters': ["*.~pas", "*.~dfm", "*.dcu", "*.identcache", "*.local", "*.stat", "__history/", "*.ddp"]
    }

    def cli_logger(msg):
        print(msg)

    engine = DelphiMigratorEngine(src_dir, dst_dir, config, cli_logger)
    print("--- INICIANDO TESTE DO MIGRADOR NO ALM ---")
    try:
        engine.start_migration()
        print("--- TESTE CONCLUIDO COM SUCESSO ---")
    except Exception as e:
        print(f"--- ERRO DURANTE A MIGRACAO --- \n{e}")

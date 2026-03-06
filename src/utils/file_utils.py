# src/utils/file_utils.py

import os
import shutil
import stat

def _remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_copy_tree(src: str, dst: str, log_callback=None, is_allowed_callback=None, clean_dst=True):
    """Copia a estrutura de diretórios avaliando o callback de allow-list antes de transferir o arquivo."""
    if clean_dst and os.path.exists(dst):
        if log_callback:
            log_callback(f"Removendo diretório de destino existente: {dst}")
        shutil.rmtree(dst, onerror=_remove_readonly)
    
    if log_callback:
        log_callback(f"Copiando arquivos de {src} para {dst} ...")
        
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        # Allow filtering dirs? Here we focus heavily on files but ignoring a dir early saves time
        if is_allowed_callback:
            dirs[:] = [d for d in dirs if is_allowed_callback(d)]
            
        for file in files:
            if not is_allowed_callback or is_allowed_callback(file):
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(root, src)
                dst_dir = os.path.join(dst, rel_path)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src_file, os.path.join(dst_dir, file))

def read_file_content(filepath: str) -> tuple[str, bool]:
    """Tenta ler um arquivo em utf-8, cai para windows-1252 em caso de erro. Retorna (conteudo, era_ansi)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), False
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='windows-1252', errors='replace') as f:
            return f.read(), True

def write_file_content(filepath: str, content: str, encoding: str = 'utf-8'):
    """Escreve um arquivo forçando o encoding (Padrão: utf-8) e manipulando permissões Read-Only."""
    try:
        os.chmod(filepath, stat.S_IWRITE)
    except Exception:
        pass
        
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)

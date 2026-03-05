# src/utils/file_utils.py

import os
import shutil

def safe_copy_tree(src: str, dst: str, log_callback=None):
    """Copia a estrutura de diretórios, recriando caso já exista o destino."""
    if os.path.exists(dst):
        if log_callback:
            log_callback(f"Removendo diretório de destino existente: {dst}")
        shutil.rmtree(dst)
    
    if log_callback:
        log_callback(f"Copiando arquivos de {src} para {dst} ...")
        
    shutil.copytree(src, dst)

def read_file_content(filepath: str) -> tuple[str, bool]:
    """Tenta ler um arquivo em utf-8, cai para windows-1252 em caso de erro. Retorna (conteudo, era_ansi)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), False
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='windows-1252') as f:
            return f.read(), True

def write_file_content(filepath: str, content: str, encoding: str = 'utf-8'):
    """Escreve um arquivo forçando o encoding (Padrão: utf-8)"""
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)

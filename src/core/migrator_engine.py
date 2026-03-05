# src/core/migrator_engine.py

import os
import re
from src.core.constants import BDE_TO_FD_COMPONENTS, DBTABLES_REPLACEMENT, UNIT_SCOPES, ADVANCED_PAS_REPLACEMENTS, DEPRECATED_THREAD_METHODS, LEGACY_DFM_PROPERTIES
from src.utils.file_utils import safe_copy_tree, read_file_content, write_file_content

class DelphiMigratorEngine:
    def __init__(self, src: str, dst: str, config: dict, log_callback):
        self.src = src
        self.dst = dst
        self.do_utf8 = config.get('utf8', True)
        self.do_bde = config.get('bde', True)
        self.do_scopes = config.get('scopes', True)
        self.do_advanced = config.get('advanced', True) # Inject Phase 3 advanced rules natively
        self.log = log_callback

        self.count_utf8 = 0
        self.count_bde_fixes = 0
        self.count_scope_fixes = 0
        self.count_advanced_fixes = 0

    def start_migration(self):
        try:
            self.log(">> Iniciando motor de migração...")
            
            if self.src != self.dst:
                self.log(f">> Extração Segura Ativada. Copiando para: {self.dst}")
                safe_copy_tree(self.src, self.dst, self.log)
            else:
                self.log(f">> Modo In-Place Ativado. Analisando e modificando DIRETAMENTE em: {self.src}")
            
            self.log(">> Analisando e processando arquivos (.pas, .dfm, .dpr)...")
            
            for root, _, files in os.walk(self.dst):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.pas', '.dfm', '.dpr']:
                        filepath = os.path.join(root, file)
                        self._process_file(filepath, ext)

            self.log(">> Conversão de texto finalizada.")
            if self.do_utf8:
                self.log(f"   ✓ Arquivos recodificados (UTF-8): {self.count_utf8}")
            if self.do_bde:
                self.log(f"   ✓ Ocorrências BDE substituídas: {self.count_bde_fixes}")
            if self.do_scopes:
                self.log(f"   ✓ Unit Scope Names atualizados: {self.count_scope_fixes}")
            if self.do_advanced:
                self.log(f"   ✓ Refatorações Avançadas (Unicode/Threads/.dfm): {self.count_advanced_fixes}")

            self.log("\n=== MIGRAÇÃO FINALIZADA COM SUCESSO! ===")

        except Exception as e:
            self.log(f"ERRO CRÍTICO NO MOTOR: {str(e)}")
            raise e

    def _process_file(self, filepath: str, ext: str):
        content, era_ansi = read_file_content(filepath)
        if self.do_utf8 and era_ansi:
            self.count_utf8 += 1

        nova_string = content

        if self.do_bde:
            nova_string = self._apply_bde_replacements(nova_string, ext)

        if self.do_scopes and ext in ['.pas', '.dpr']:
            nova_string = self._apply_unit_scopes(nova_string)

        if self.do_advanced:
            if ext in ['.pas', '.dpr']:
                nova_string = self._apply_advanced_pas_fixes(nova_string)
            elif ext == '.dfm':
                nova_string = self._apply_advanced_dfm_fixes(nova_string)

        write_enc = 'utf-8' if self.do_utf8 else 'windows-1252'
        
        if content != nova_string or (self.do_utf8 and era_ansi):
            write_file_content(filepath, nova_string, encoding=write_enc)

    def _apply_bde_replacements(self, code: str, ext: str) -> str:
        for old_comp, new_comp in BDE_TO_FD_COMPONENTS.items():
            if re.search(old_comp, code):
                code = re.sub(old_comp, new_comp, code)
                self.count_bde_fixes += 1
                
        if ext in ['.pas', '.dpr']:
            if re.search(r'\bDBTables\b', code, re.IGNORECASE):
                code = re.sub(r'\bDBTables\b', DBTABLES_REPLACEMENT, code, flags=re.IGNORECASE)
        
        return code

    def _apply_unit_scopes(self, code: str) -> str:
        for prefix, units in UNIT_SCOPES.items():
            for unit in units:
                pattern = r'(?i)(?<!\.)\b' + unit + r'\b'
                clean_unit = unit.replace("\\", "")
                replacement = f'{prefix}.{clean_unit}'
                
                if re.search(pattern, code):
                    code = re.sub(pattern, replacement, code)
                    self.count_scope_fixes += 1
        return code

    def _apply_advanced_pas_fixes(self, code: str) -> str:
        # PChar castes / FormatSettings mapping
        for old_rule, new_rule in ADVANCED_PAS_REPLACEMENTS.items():
            if re.search(old_rule, code, re.IGNORECASE):
                code = re.sub(old_rule, new_rule, code, flags=re.IGNORECASE)
                self.count_advanced_fixes += 1

        # Warn/Comment deprecated thread calls
        for thr_method in DEPRECATED_THREAD_METHODS:
            regex = r'(\w+)' + thr_method
            def thr_repl(match):
                self.count_advanced_fixes += 1
                return f"{match.group(0)} // TODO: Upgrade thread method for Delphi 12"
            
            if re.search(regex, code, re.IGNORECASE):
                code = re.sub(regex, thr_repl, code, flags=re.IGNORECASE)

        return code

    def _apply_advanced_dfm_fixes(self, code: str) -> str:
        # Strip old VCL and 3rd party D7 specific UI properties
        for prop in LEGACY_DFM_PROPERTIES:
            if re.search(prop, code, re.IGNORECASE | re.MULTILINE):
                code = re.sub(prop, '', code, flags=re.IGNORECASE | re.MULTILINE)
                self.count_advanced_fixes += 1
        return code

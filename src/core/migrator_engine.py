# src/core/migrator_engine.py

import os
import re
import fnmatch
import subprocess
from src.core.constants import (
    UNIT_SCOPES,
    BDE_TO_FIREDAC,
    DBX_TO_FIREDAC,
    IBX_TO_FIREDAC,
    ADO_TO_FIREDAC,
    CDS_TO_FIREDAC,
    ADVANCED_PAS_REPLACEMENTS,
    DEPRECATED_THREAD_METHODS,
    LEGACY_DFM_PROPERTIES
)
from src.utils.file_utils import safe_copy_tree, read_file_content, write_file_content

class DelphiMigratorEngine:
    def __init__(self, src: str, dst: str, config: dict, log_callback):
        self.src = src
        self.dst = dst
        # Feature Flags
        self.do_utf8 = config.get('utf8', True)
        
        self.do_db_main = config.get('db_main', True)
        self.db_flags = {
            'bde': config.get('bde', True),
            'dbx': config.get('dbx', False),
            'ibx': config.get('ibx', False),
            'ado': config.get('ado', False),
            'cds': config.get('cds', False)
        }
        
        self.do_scopes = config.get('scopes', True)
        self.do_advanced = config.get('advanced', True)
        self.do_precompile = config.get('precompile', False)
        self.include_filters = config.get('include_filters', [])
        self.ignore_filters = config.get('ignore_filters', [])
        self.delphi_bin = config.get('delphi_bin', r"C:\Program Files (x86)\Embarcadero\Studio\23.0\bin")
        self.log = log_callback

        self.count_utf8 = 0
        self.count_bde_fixes = 0
        self.count_scope_fixes = 0
        self.count_advanced_fixes = 0

    def _is_allowed(self, filename: str) -> bool:
        # Check Exclusions (Blacklist) First
        if self.ignore_filters:
            for pattern in self.ignore_filters:
                if fnmatch.fnmatch(filename, pattern):
                    return False
        
        # Check Inclusions (Whitelist) Second
        if self.include_filters:
            matched = False
            for pattern in self.include_filters:
                if fnmatch.fnmatch(filename, pattern):
                    matched = True
                    break
            if not matched:
                return False
                
        return True

    def start_migration(self):
        try:
            self.log(">> Iniciando motor de migração...")

            if self.do_precompile:
                self._run_precompilation_hook()
            
            if self.src != self.dst:
                self.log(f">> Extração Segura Ativada. Copiando para: {self.dst}")
                safe_copy_tree(self.src, self.dst, self.log, self._is_allowed)
            else:
                self.log(f">> Modo In-Place Ativado. Analisando e modificando DIRETAMENTE em: {self.src}")
            
            if self.do_db_main:
                active_techs = [k.upper() for k, v in self.db_flags.items() if v]
                if active_techs:
                    self.log(f">> Migração de Acesso a Dados (FireDAC) Ativa para: {', '.join(active_techs)}")

            self.log(">> Analisando e processando arquivos (.pas, .dfm, .dpr)...")
            
            for root, dirs, files in os.walk(self.dst):
                # Optionally filter dirs here too if In-Place was used since copy_tree was bypassed
                dirs[:] = [d for d in dirs if self._is_allowed(d)]
                for file in files:
                    if not self._is_allowed(file):
                        continue
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.pas', '.dfm', '.dpr']:
                        filepath = os.path.join(root, file)
                        self._process_file(filepath, ext)

            self.log(">> Conversão de texto finalizada.")
            if self.do_utf8:
                self.log(f"   * Arquivos recodificados (UTF-8): {self.count_utf8}")
            if self.do_db_main:
                self.log(f"   * Ocorrências BDE/DBX/IBX/ADO/CDS substituídas: {self.count_bde_fixes}")
            if self.do_scopes:
                self.log(f"   * Unit Scope Names atualizados: {self.count_scope_fixes}")
            if self.do_advanced:
                self.log(f"   * Refatorações Avançadas (Unicode/Threads/.dfm): {self.count_advanced_fixes}")

            self.log("\n=== MIGRAÇÃO FINALIZADA COM SUCESSO! ===")

        except Exception as e:
            self.log(f"ERRO CRÍTICO NO MOTOR: {str(e)}")
            raise e

    def _run_precompilation_hook(self):
        self.log(">> [PRE-COMPILE] Buscando arquivo de projeto na Origem...")
        target_file = None
        
        for file in os.listdir(self.src):
            if file.lower().endswith('.dproj'):
                target_file = file
                break
        
        if not target_file:
            for file in os.listdir(self.src):
                if file.lower().endswith('.dpr'):
                    target_file = file
                    break
        
        if not target_file:
            self.log("   [AVISO] Nenhum .dproj ou .dpr encontrado na raiz. Pulando teste de compilação.")
            return

        rsvars_path = os.path.join(self.delphi_bin, "rsvars.bat")
        if not os.path.exists(rsvars_path):
            self.log(f"   [ERRO] Ambiente Delphi não localizado em: {rsvars_path}")
            self.log("   Falha ao chamar o compilador. Pulando etapa de teste.")
            return

        self.log(f">> [PRE-COMPILE] Iniciando MSBuild Mock em: {target_file}")
        
        # Build command: Call rsvars.bat to setup env, then MSBuild
        full_command = f'"{rsvars_path}" && MSBuild "{target_file}" /t:Build /p:Config=Debug'
        
        process = subprocess.Popen(
            full_command,
            cwd=self.src,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='windows-1252',
            errors='replace'
        )

        for line in iter(process.stdout.readline, ''):
            clean_line = line.strip()
            if clean_line:
                self.log(f"| {clean_line}")

        process.stdout.close()
        process.wait()

        self.log(f">> [PRE-COMPILE] Fim do teste de compilação. Código de Saída: {process.returncode}\n")

    def _process_file(self, filepath: str, ext: str):
        content, era_ansi = read_file_content(filepath)
        if self.do_utf8 and era_ansi:
            self.count_utf8 += 1

        nova_string = content
        # 2) Text Conversion
        all_changes = []

        if self.do_db_main:
            nova_string, changes = self._apply_data_access_replacements(nova_string, ext)
            all_changes.extend(changes)

        if self.do_scopes and ext in ['.pas', '.dpr']:
            nova_string, changes = self._apply_unit_scopes(nova_string)
            all_changes.extend(changes)

        if self.do_advanced:
            if ext in ['.pas', '.dpr']:
                nova_string, changes = self._apply_advanced_pas_fixes(nova_string)
                all_changes.extend(changes)
            elif ext == '.dfm':
                nova_string, changes = self._apply_advanced_dfm_fixes(nova_string)
                all_changes.extend(changes)

        write_enc = 'utf-8' if self.do_utf8 else 'windows-1252'
        
        filename = os.path.basename(filepath)
        
        if all_changes:
            self.log(f"\n Processando: {filename}")
            for change in all_changes:
                self.log(f"  Regra aplicada: {change['rule']}")
                self.log(f"  Alteração: {change['details']}")
            self.log("  Status: arquivo modificado\n")
            
        if content != nova_string or (self.do_utf8 and era_ansi):
            write_file_content(filepath, nova_string, encoding=write_enc)

    def _apply_data_access_replacements(self, code: str, ext: str) -> tuple:
        changes = []
        
        active_rules = []
        if self.db_flags.get('bde'):
            active_rules.append(('BDE -> FireDAC', BDE_TO_FIREDAC))
        if self.db_flags.get('dbx'):
            active_rules.append(('DBExpress -> FireDAC', DBX_TO_FIREDAC))
        if self.db_flags.get('ibx'):
            active_rules.append(('IBX -> FireDAC', IBX_TO_FIREDAC))
        if self.db_flags.get('ado'):
            active_rules.append(('ADO -> FireDAC', ADO_TO_FIREDAC))
        if self.db_flags.get('cds'):
            active_rules.append(('ClientDataSet -> FireDAC', CDS_TO_FIREDAC))
            
        for rule_name, rule_dict in active_rules:
            for old_comp, new_comp in rule_dict.items():
                if ext == '.dfm' and not new_comp:
                    # Often uses are stripped to empty (''), but in DFM we skip empty replacements
                    # unless it's a specific component deletion rule.
                    continue
                    
                code, num_subs = re.subn(old_comp, new_comp, code, flags=re.IGNORECASE)
                if num_subs > 0:
                    self.count_bde_fixes += num_subs
                    strip_comp = old_comp.replace(r"\b", "")
                    
                    if new_comp == '':
                        action = f"{strip_comp} removido"
                    else:
                        action = f"{strip_comp} \u2192 {new_comp}"
                        
                    changes.append({'rule': rule_name, 'details': f'{action} ({num_subs} ocorrências)'})
                    
        return code, changes

    def _apply_unit_scopes(self, code: str) -> tuple:
        changes = []
        for prefix, units in UNIT_SCOPES.items():
            for unit in units:
                pattern = r'(?i)(?<!\.)\b' + unit + r'\b'
                clean_unit = unit.replace("\\", "")
                replacement = f'{prefix}.{clean_unit}'
                
                code, num_subs = re.subn(pattern, replacement, code)
                if num_subs > 0:
                    self.count_scope_fixes += num_subs
                    changes.append({'rule': 'Adicionar Unit Scopes Modernos', 'details': f'{clean_unit} -> {replacement} ({num_subs} ocorrências)'})
        return code, changes

    def _apply_advanced_pas_fixes(self, code: str) -> tuple:
        changes = []
        # PChar castes / FormatSettings mapping
        for old_rule, new_rule in ADVANCED_PAS_REPLACEMENTS.items():
            code, num_subs = re.subn(old_rule, new_rule, code, flags=re.IGNORECASE)
            if num_subs > 0:
                self.count_advanced_fixes += num_subs
                changes.append({'rule': 'Regra Avançada .PAS (Unicode/FormatSettings/Series)', 'details': f'Padrão regex "{old_rule}" modificado ({num_subs} ocorrências)'})

        # Warn/Comment deprecated thread calls
        for thr_method in DEPRECATED_THREAD_METHODS:
            regex = r'(\w+)' + thr_method
            def thr_repl(match):
                return f"{match.group(0)} // TODO: Upgrade thread method for Delphi 12"
            
            code, num_subs = re.subn(regex, thr_repl, code, flags=re.IGNORECASE)
            if num_subs > 0:
                self.count_advanced_fixes += num_subs
                changes.append({'rule': 'Métodos Restritos de Thread', 'details': f'Adicionado aviso de TODO na chamada de {thr_method} ({num_subs} ocorrências)'})

        return code, changes

    def _apply_advanced_dfm_fixes(self, code: str) -> tuple:
        changes = []
        # Strip old VCL and 3rd party D7 specific UI properties
        for prop in LEGACY_DFM_PROPERTIES:
            code, num_subs = re.subn(prop, '', code, flags=re.IGNORECASE | re.MULTILINE)
            if num_subs > 0:
                self.count_advanced_fixes += num_subs
                changes.append({'rule': 'Limpeza Avançada de .DFM', 'details': f'Propriedade ou bloco legado ignorado ({num_subs} ocorrências)'})
        return code, changes

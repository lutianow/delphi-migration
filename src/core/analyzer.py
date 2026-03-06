# src/core/analyzer.py
import os
import re
from src.utils.file_utils import read_file_content

class ProjectAnalyzer:
    """Pre-flight module to analyze Delphi projects before migration."""
    
    def __init__(self, src_dir: str, log_callback):
        self.src = src_dir
        self.log = log_callback
        
        self.total_files = 0
        self.pas_files = 0
        self.dfm_files = 0
        self.dpr_files = 0
        self.total_dirs = 0
        self.est_lines = 0
        
        self.techs = {
            'BDE': 0,
            'DBExpress': 0,
            'IBX': 0,
            'ADO': 0,
            'ClientDataSet': 0,
            'SimpleDataSet': 0
        }
        
        self.est_units_mod = 0
        self.est_comp_subs = 0

    def run_analysis(self):
        self.log(f"[ANÁLISE DO PROJETO]\nIniciando escaneamento no diretório:\n{self.src}\n")
        
        for root, dirs, files in os.walk(self.src):
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
                
            self.total_dirs += len(dirs)
            self.total_files += len(files)
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext == '.pas':
                    self.pas_files += 1
                elif ext == '.dfm':
                    self.dfm_files += 1
                elif ext in ['.dpr', '.dproj']:
                    self.dpr_files += 1
                    
                if ext in ['.pas', '.dfm', '.dpr', '.dpk']:
                    self._analyze_file(os.path.join(root, file))
                    
        self._print_report()

    def _analyze_file(self, filepath: str):
        content, _ = read_file_content(filepath)
        
        # Estimate LOC
        lines = content.count('\n') + 1
        self.est_lines += lines
        
        # Tech detections (simple substring/regex searches for speed)
        has_mod = False
        hits = 0
        
        # 1. BDE
        if re.search(r'\b(TTable|TQuery|TStoredProc|TDatabase|TUpdateSQL|TBatchMove|dbE:\s*Exception|E(?:BDE)?EngineError)\b', content, re.IGNORECASE):
            self.techs['BDE'] += 1
            has_mod = True
            hits += content.count('TTable') + content.count('TQuery') + content.count('BDE')

        # 2. DBExpress
        if re.search(r'\b(TSQLConnection|TSQLQuery|TSQLStoredProc|TSQLDataSet|Dbx|SqlExpr)\b', content, re.IGNORECASE):
            self.techs['DBExpress'] += 1
            has_mod = True
            hits += content.count('TSQLConnection') + content.count('TSQLQuery')

        # 3. IBX
        if re.search(r'\b(TIBDatabase|TIBQuery|TIBTable|TIBStoredProc|TIBTransaction)\b', content, re.IGNORECASE):
            self.techs['IBX'] += 1
            has_mod = True
            hits += content.count('TIBDatabase') + content.count('TIBQuery')

        # 4. ADO
        if re.search(r'\b(TADOConnection|TADOQuery|TADOTable|TADOStoredProc)\b', content, re.IGNORECASE):
            self.techs['ADO'] += 1
            has_mod = True
            hits += content.count('TADOConnection') + content.count('TADOQuery')

        # 5. CDS
        if re.search(r'\b(TClientDataSet|DBClient)\b', content, re.IGNORECASE):
            self.techs['ClientDataSet'] += 1
            has_mod = True
            hits += content.count('TClientDataSet')

        if re.search(r'\b(TSimpleDataSet|SimpleDS)\b', content, re.IGNORECASE):
            self.techs['SimpleDataSet'] += 1
            has_mod = True
            hits += content.count('TSimpleDataSet')

        if has_mod:
            self.est_units_mod += 1
        
        self.est_comp_subs += hits

    def _print_report(self):
        report = []
        report.append(f"Arquivos encontrados: {self.total_files}")
        report.append(f"Units Delphi (.pas): {self.pas_files}")
        report.append(f"Forms (.dfm): {self.dfm_files}")
        report.append(f"Projetos (.dpr/.dproj): {self.dpr_files}")
        report.append(f"Diretórios: {self.total_dirs}")
        # Formata com separador de milhar
        report.append(f"Linhas estimadas de código: {self.est_lines:n}\n")
        
        report.append("Tecnologias detectadas:")
        active_techs = {k: v for k, v in self.techs.items() if v > 0}
        
        if not active_techs:
            report.append("- Nenhuma tecnologia legada de banco de dados detectada.")
        else:
            for tech, count in active_techs.items():
                report.append(f"- {tech} ({count} ocorrências)")
                
        report.append("\nEstimativa de impacto da migração:")
        report.append(f"Units que devem ser modificadas: ~{self.est_units_mod}")
        report.append(f"Substituições de componentes previstas: ~{self.est_comp_subs}\n")
        
        comp_ratio = self.est_units_mod / (self.pas_files + self.dfm_files) if (self.pas_files + self.dfm_files) > 0 else 0
        
        if comp_ratio < 0.1:
            complexidade = "BAIXA"
        elif comp_ratio <= 0.3:
            complexidade = "MÉDIA"
        else:
            complexidade = "ALTA"
            
        report.append(f"Complexidade estimada da migração: {complexidade}\n")
        
        self.log('\n'.join(report))

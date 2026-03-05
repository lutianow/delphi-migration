# src/core/constants.py

# Mapeamento BDE para FireDAC simples
BDE_TO_FD_COMPONENTS = {
    r'\bTQuery\b': 'TFDQuery',
    r'\bTTable\b': 'TFDTable',
    r'\bTDatabase\b': 'TFDConnection',
    r'\bTStoredProc\b': 'TFDStoredProc'
}

# Injeção de dependência básica das uses do FireDAC quando encontrar DBTables
DBTABLES_REPLACEMENT = 'FireDAC.Comp.Client, FireDAC.Stan.Intf, FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf, FireDAC.DApt.Intf, FireDAC.Stan.Async, FireDAC.DApt, FireDAC.Comp.DataSet'

# Unit Scope Names principais do Delphi XE2+
UNIT_SCOPES = {
    'System': ['SysUtils', 'Classes', 'Variants', 'Math', 'StrUtils', 'TypInfo', 'SyncObjs', 'Generics\.Collections', 'Generics\.Defaults', 'IOUtils'],
    'Vcl': ['Forms', 'Controls', 'Graphics', 'Dialogs', 'StdCtrls', 'ExtCtrls', 'ComCtrls', 'Menus', 'Buttons', 'Grids', 'ActnList'],
    'Winapi': ['Windows', 'Messages', 'ShellAPI', 'ActiveX', 'CommCtrl'],
    'Data': ['DB', 'DBClient', 'FMTBcd', 'SqlExpr']
}

# --- ADVANCED FASE 3 RULES ---

# Substituições críticas para quebra de retrocompatibilidade ANSI vs Unicode e Globals
ADVANCED_PAS_REPLACEMENTS = {
    # Unicode: Trocar cast PChar para PWideChar (Padrão Delphi 2009+)
    r'\bPChar\(': 'PWideChar(',
    # FormatSettings: Variáveis globais de formatação monetária/numérica agora são de Record
    r'\bDecimalSeparator\b': 'FormatSettings.DecimalSeparator',
    r'\bThousandSeparator\b': 'FormatSettings.ThousandSeparator',
    r'\bDateSeparator\b': 'FormatSettings.DateSeparator',
    r'\bTimeSeparator\b': 'FormatSettings.TimeSeparator',
    r'\bShortDateFormat\b': 'FormatSettings.ShortDateFormat',
    r'\bLongDateFormat\b': 'FormatSettings.LongDateFormat',
}

# Métodos de Threads clássicos do D7 depreciados para injetar aviso do compilador
DEPRECATED_THREAD_METHODS = [
    r'\.Resume\b',
    r'\.Suspend\b'
]

# Propriedades de formulários antigos de terceiros que quebram o parsing do Delphi 12
LEGACY_DFM_PROPERTIES = [
    r'^\s*ExplicitWidth\s*=\s*\d+\r?\n',
    r'^\s*ExplicitHeight\s*=\s*\d+\r?\n',
    r'^\s*ExplicitLeft\s*=\s*\d+\r?\n',
    r'^\s*ExplicitTop\s*=\s*\d+\r?\n',
    r'^\s*OldCreateOrder\s*=\s*\w+\r?\n' # Old D7 forms specific
]

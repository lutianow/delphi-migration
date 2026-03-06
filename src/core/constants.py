# src/core/constants.py

# Dicionários de Substituição para Múltiplas Tecnologias de Acesso a Dados (Fase 15)

# 1) BDE -> FireDAC
BDE_TO_FIREDAC = {
    # Componentes base do BDE
    r'\bTQuery\b': 'TFDQuery',
    r'\bTTable\b': 'TFDTable',
    r'\bTDatabase\b': 'TFDConnection',
    r'\bTStoredProc\b': 'TFDStoredProc',
    r'\bTBatchMove\b': 'TFDBatchMove',
    r'\bTSession\b': 'TFDSession', 
    r'\bTUpdateSQL\b': 'TFDUpdateSQL',
    
    # Remoções de Uses legadas + Injeção de core do FireDAC
    r'\bDBTables\b': 'FireDAC.Comp.Client, FireDAC.Stan.Intf, FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf, FireDAC.DApt.Intf, FireDAC.Stan.Async, FireDAC.DApt, FireDAC.Comp.DataSet',
    r'\bBDE\b': 'FireDAC.Phys.IBBase, FireDAC.Phys.IB'
}

# 2) DBExpress -> FireDAC
DBX_TO_FIREDAC = {
    r'\bTSQLConnection\b': 'TFDConnection',
    r'\bTSQLQuery\b': 'TFDQuery',
    r'\bTSQLDataSet\b': 'TFDQuery',
    r'\bTSQLStoredProc\b': 'TFDStoredProc',
    
    # Mudanças de declaração uses do DBX
    r'\bSqlExpr\b': 'FireDAC.Comp.Client, FireDAC.Stan.Intf, FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf, FireDAC.DApt.Intf, FireDAC.Stan.Async, FireDAC.DApt, FireDAC.Comp.DataSet',
    r'\bDBXCommon\b': ''
}

# 3) IBX -> FireDAC
IBX_TO_FIREDAC = {
    r'\bTIBDatabase\b': 'TFDConnection',
    r'\bTIBQuery\b': 'TFDQuery',
    r'\bTIBTable\b': 'TFDTable',
    r'\bTIBTransaction\b': 'TFDTransaction',
    r'\bTIBStoredProc\b': 'TFDStoredProc',
    
    # Uses IBX genéricas substituídas pelo motor principal FireDAC
    r'\bIBDatabase\b': 'FireDAC.Comp.Client, FireDAC.Stan.Intf, FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf, FireDAC.DApt.Intf, FireDAC.Stan.Async, FireDAC.DApt, FireDAC.Comp.DataSet',
    r'\bIBQuery\b': '',
    r'\bIBTable\b': '',
    r'\bIBStoredProc\b': '',
    r'\bIBX\b': ''
}

# 4) ADO -> FireDAC
ADO_TO_FIREDAC = {
    r'\bTADOConnection\b': 'TFDConnection',
    r'\bTADOQuery\b': 'TFDQuery',
    r'\bTADOTable\b': 'TFDTable',
    r'\bTADOStoredProc\b': 'TFDStoredProc',
    
    r'\bADODB\b': 'FireDAC.Comp.Client, FireDAC.Stan.Intf, FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf, FireDAC.DApt.Intf, FireDAC.Stan.Async, FireDAC.DApt, FireDAC.Comp.DataSet'
}

# 5) ClientDataSet / SimpleDataSet -> FireDAC (Memory Tables)
CDS_TO_FIREDAC = {
    r'\bTClientDataSet\b': 'TFDMemTable',
    r'\bTSimpleDataSet\b': 'TFDQuery', # Pode ser mapeado para query dependendo do uso
    
    r'\bDBClient\b': 'FireDAC.Comp.Client, FireDAC.Stan.Intf, FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS, FireDAC.Phys.Intf, FireDAC.DApt.Intf, FireDAC.Stan.Async, FireDAC.DApt, FireDAC.Comp.DataSet',
    r'\bSimpleDS\b': '',
    r'\bProvider\b': ''
}
# Unit Scope Names principais do Delphi XE2+
UNIT_SCOPES = {
    'System': ['SysUtils', 'Classes', 'Variants', 'Math', 'StrUtils', 'TypInfo', 'SyncObjs', 'Generics\.Collections', 'Generics\.Defaults', 'IOUtils'],
    'Vcl': ['Forms', 'Controls', 'Graphics', 'Dialogs', 'StdCtrls', 'ExtCtrls', 'ComCtrls', 'Menus', 'Buttons', 'Grids', 'ActnList'],
    'Winapi': ['Windows', 'Messages', 'ShellAPI', 'ActiveX', 'CommCtrl'],
    'Data': ['DB', 'DBClient', 'FMTBcd', 'SqlExpr'],
    'VclTee': ['TeeProcs', 'TeEngine', 'Chart', 'DBChart', 'Series']
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
    # Series: Comentar variáveis de séries gráficas órfãs nos formulários após remoção ou rebaixamento do TDBChart
    r'^(\s*)([a-zA-Z0-9_]+)\s*:\s*T\w*Series\s*;': r'\1// \2: T...Series; { migrated: orphaned series }',
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
    r'^\s*OldCreateOrder\s*=\s*\w+\r?\n', # Old D7 forms specific
    r'^\s*object\s+[a-zA-Z0-9_]+\s*:\s*T\w*Series\b.*?\r?\n', # TeeChart series objects that often corrupt 
    r'^\s*GetDriverFunc\s*=\s*\'.*?\'\r?\n', # DBExpress legacy property
    r'^\s*LibraryName\s*=\s*\'.*?\'\r?\n',     # DBExpress legacy property
    r'^\s*VendorLib\s*=\s*\'.*?\'\r?\n'       # DBExpress legacy property
]

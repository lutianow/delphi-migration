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

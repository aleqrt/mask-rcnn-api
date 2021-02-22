import pandas as pd


def parser_component(facts_name):
    """Parsificatore del file di fatti ASP.
       Return:
           - component, lista contentente [Label, Id, Xs1, Ys1, Xd2, Yd2]
    """
    component = []
    with open(facts_name, 'r') as f:
        for i, line in enumerate(f):
            cmp = line.split('(')[1].split(')')[0].split(',')
            component.append([cmp[0].replace('\"-', '').replace('\"', ''), int(cmp[1]),
                              int(cmp[2]), int(cmp[3]),
                              int(cmp[4]), int(cmp[5])])
    return component


facts = parser_component('cad.asp')
df = pd.read_excel('registro_componenti.xlsx', sheet_name='ECB_Distinta SEF Articoli ', engine='openpyxl')

desc = df['DESCRIZIONE']
sef = df['SEF']

cod = [c[0] for c in facts]

for id, label in sef.items():
    if label in cod:
        print(f'Componente con label {label} e descrizione {desc[id]} presente')


import os
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


facts = parser_component(os.path.join('reasoner', 'cad', 'cad.asp'))
df = pd.read_excel(os.path.join('utils', 'registro_componenti.xlsx'), sheet_name='ECB_Distinta SEF Articoli '
                   , engine='openpyxl')
sef = df['SEF']

# Se le label nel file cad.asp sono corrispondenti a valori alfanumerici delle colonna SEF del file excel allora
# mostro la corrispondente descrizione del componente così da poter fare un match con l'output della rete neurale
cod = [c[0] for c in facts]
for j, label in sef.items():
    if label in cod:
        print(f"Componente con label {label} e descrizione {df['DESCRIZIONE'][j]} presente")

# Per ogni componente la tupla formata da DESCRIZIONE, NUMERO ARTICOLO, FORNITORE lo identifica univocamente
tpl = [(df['DESCRIZIONE'][i], df['NUMERO ARTICOLO'][i], df['FORNITORE'][i]) for i in range(df.shape[0])]
print(*tpl, sep="\n")

#Readme
Il seguente repository contient un'implementazione python della rete neurale Mask-RCNN, utilizzata per effettuare 
instance segmentation su immagini.

Il codice sorgente è scaricabile da github al link https://github.com/matterport/Mask_RCNN.

#Requisiti
- **python 3.6**
- **anaconda3** oppure **miniconda3**

#Installazione
A seguire, le direttive di come installare l'ambiente utilizzando python 3.6 e miniconda3.

Creare un enviromnent conda contenente python 3.6
`conda create -n mask-rcnn python=3.6 --channel conda-forge`

Attivare l'environment appena generato
`conda activate mask-rcnn`

Posizionarsi nella root folder del progetto e installare i pacchetti python richiesti (elencati nel file requirements.txt)
`pip install -r requirements.txt`

#Preparazione del dataset
Per realizzare le annotazioni di ogni immagine del dataset, utilizziamo un tool open-source ad hoc per annotare ed etichettare gli ogetti di un immagine: microsoft VoTT. 

Il software è basato su tecnologia React, per cui è possibile utilizzarlo tramite interfaccia web. Tuttavia quest'ultima non ha accesso al file system del computer, per cui è consigliabile scaricare l'installer, che fornisce una versione desktop del progetto con la possibilità di leggere il dataset dal filesystem. Per informazioni sul suo utilizzo, visitare https://github.com/microsoft/VoTT.

Una volta effettuata la procedura di labelling delle immagini, è possibile esportare le annotazioni in vari formati. Scegliamo come Provider "VoTT JSON". 

![Screenshot](https://github.com/AlessandroQuarta/Mask_RCNN/blob/develop/assets/vott_export_format.PNG)

Il programma esporterà le annotazioni in formato JSON, generando un file nella sottocartella `vott-json-export`.

Fatto ciò, è necessario effettuare una conversione delle annotazioni del file generato da Microsoft VoTT, in modo da poter estrarre per ogni immagine un file json contenente le anotazione della singola immagine.

`python utils/convert_annots.py -i <input_folder> -o <output_folder>`

Dove <input_folder> è il path alla folder di annotazioni JSON e <output_folder> è il path alla folder in cui lo script salverà le annotazioni delle singole immagini nel formato JSON previsto da Mask-RCNN.

`NOTA: per la conversione delle annotazioni dell'intera immagine o della singola componente seguire le istruzioni contenute nello script`

#Augmentation
Sono state implementate alcune tecniche di data augmentation che permettono di manipolare le immagini del dataset o di creare immagini sintetiche.

`python utils/augmentation.py -i <image_folder> -a <annotation_folder>`

`python utils/synthetic_dataset.py -i <image_component_folder> -a <annotation_component_folder>`

#Reasoner
Nella directory `reasoner` sono presenti le cartelle:

- **encoding**: contenente le regole del programma logico
- **graph**: immagine del risultato del confronto tra i grafi del CAD Reasoner e della rete neurale
- **ground truth**: contenente il file di fatti e le posizioni relative in output dal CAD Reasoner
- **inferred**: contenente i fatti e le posizioni relative in output dal modulo di Instance Segmentation
- **dlv2**: eseguibile del programma dlv2

#Graph Comparator
E' stato implementato un algoritmo di comparazione dei grafi.

`python utils/graph_comparator.py`


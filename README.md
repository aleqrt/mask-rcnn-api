# Mask RCNN
Python implementation of Mask-RCNN for instance segmentation. This code was used in *"Neuro-Symbolic AI for Compliance Checking of Electrical Control Panels"* (Theory and Practice of Logic Programming, 2023). Based on https://github.com/matterport/Mask_RCNN.

# Requirements
- **Python 3.7**
- **Anaconda3** or **Miniconda3**

# Installation

Install the package using conda and pip:

```bash
conda create -n mask-rcnn python=3.7 --channel conda-forge
conda activate mask-rcnn
pip install -r requirements.txt
python setup.py install
```

# Data Preparation

Export annotations in JSON format and convert them:

```bash
python utils/convert_annots.py -i <input_folder> -o <output_folder>
```

# Training & Prediction

Train on the "elettrocablaggi" dataset:
```bash
python samples/elettrocablaggi/train.py
```

Make predictions:
```bash
python samples/elettrocablaggi/predict.py
```


# Advanced Features

## Augmentation

```bash
python utils/data_augmentation.py -i <image_folder> -a <annotation_folder>
python utils/data_generation.py -i <image_component_folder> -a <annotation_component_folder>
```

Before augmentation, mask the PNG images of components:

```bash
python utils/component_definition.py
```

## Auto-labeling

SIFT-based auto-labeling:

```bash
python utils/image_sift.py \
-a <path_to_annotation>/annots/ \
-i <path_to_dataset>/images/ \
-w <path_to_warp_dir>/warp_images/
```

## Reasoner

The `reasoner` directory contains:
- **encoding**: Logical program rules
- **graph**: Comparison results (CAD vs. neural network)
- **cad**: CAD Reasoner output facts
- **net**: Instance Segmentation module output
- **dlv2**: dlv2 executable

## Graph Comparator

Logical program for compliance checking:

```bash
./reasoner/dlv2 \
reasoner/net/<file_net.asp> \
reasoner/cad/<file_cad.asp> \
reasoner/encoding/encoding.asp \
--filter=posRelNet/5,posRelCad/5,compNonPresente/2,compInEccesso/2,noRelCad/4,noRelNet/4 \
> reasoner/graph/<file_compliance.asp>
```

Then compare:

```bash
python utils/graph_comparator.py
```

## Reference

Please cite this publication if you use this code:

```bibtex
@article{BARBARA_GUARASCIO_LEONE_MANCO_QUARTA_RICCA_RITACCO_2023,
  title={Neuro-Symbolic AI for Compliance Checking of Electrical Control Panels},
  volume={23},
  DOI={10.1017/S1471068423000170},
  number={4},
  journal={Theory and Practice of Logic Programming},
  author={BARBARA, VITO and GUARASCIO, MASSIMO and LEONE, NICOLA and MANCO, GIUSEPPE and QUARTA, ALESSANDRO and RICCA, FRANCESCO and RITACCO, ETTORE},
  year={2023},
  pages={748–764}
}

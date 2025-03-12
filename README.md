# Mask RCNN
This repository contains a Python implementation of the Mask-RCNN neural network, used for instance segmentation on images.

The source code can be downloaded from GitHub at the link: https://github.com/matterport/Mask_RCNN.

# Requirements
- **Python 3.7**
- **Anaconda3** or **Miniconda3**

# Installation
Below are the instructions for setting up the environment using Python 3.7 and Miniconda3.

Create a Conda environment with Python 3.7:

```bash
conda create -n mask-rcnn python=3.7 --channel conda-forge
```

Activate the newly created environment:

```bash
conda activate mask-rcnn
```

Navigate to the project's root folder and install the required Python packages listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
python setup.py install
```

# Dataset Preparation
To annotate each image in the dataset, we use the open-source tool Microsoft VoTT, designed for object annotation and labeling.

The software is based on React technology and can be used via a web interface. However, since the web version cannot access the local filesystem, it is recommended to download the installer for the desktop version, which allows reading the dataset from the filesystem. For usage information, visit: https://github.com/microsoft/VoTT.

After completing the image labeling process, export the annotations in the "VoTT JSON" format.

![Export Format](assets/vott_export_format.jpg)

The program will export the annotations in JSON format, generating a file within the `vott-json-export` subfolder.

Then, convert the annotations from the Microsoft VoTT format to a JSON format suitable for Mask-RCNN:

```bash
python utils/convert_annots.py -i <input_folder> -o <output_folder>
```

Where `<input_folder>` is the path to the folder containing the JSON annotations, and `<output_folder>` is the destination folder for the converted annotations.

**Note:**
Follow the instructions in the script for converting either full-image annotations or single-component annotations.

# Augmentation
Several data augmentation techniques have been implemented to manipulate dataset images and generate synthetic images.

```bash
python utils/data_augmentation.py -i <image_folder> -a <annotation_folder>
python utils/data_generation.py -i <image_component_folder> -a <annotation_component_folder>
```

**Note:**
Before performing augmentation, run the script to mask the PNG images of the components. Ensure the correct path is set in the script.

```bash
python utils/component_definition.py
```

# Auto-labeling
To speed up the dataset labeling process, an image processing algorithm using SIFT has been implemented. It allows for calculating the Homography matrix between two images of the same object taken from different angles.

Given that the Mask-RCNN model's training dataset consists of images of a panel taken from various angles, you can use the `image_sift.py` script to label all images based on a single reference image.

```bash
python utils/component_definition.py \
-a <path_to_annotation>/annots/ \
-i <path_to_dataset>/images/ \
-w <path_to_warp_dir>/warp_images/
```

# Reasoner
The `reasoner` directory includes the following folders:

- **encoding**: Contains the logical program rules.
- **graph**: Contains images resulting from the comparison between CAD Reasoner and neural network graphs.
- **cad**: Contains fact files and relative positions from the CAD Reasoner output.
- **net**: Contains facts and relative positions from the Instance Segmentation module output.
- **dlv2**: Executable of the dlv2 program.

# Graph Comparator
For graph compliance, use the logical program *encoding.asp*:

```bash
./reasoner/dlv2 \
reasoner/net/<file_net.asp> \
reasoner/cad/<file_cad.asp> \
reasoner/encoding/encoding.asp \
--filter=posRelNet/5,posRelCad/5,compNonPresente/2,compInEccesso/2,noRelCad/4,noRelNet/4 \
> reasoner/graph/<file_compliance.asp>
```

A graph comparison algorithm has been implemented:

```bash
python utils/graph_comparator.py
```

# Training
To train the model on the "elettrocablaggi" dataset:

```bash
python samples/elettrocablaggi/train.py
```

# Prediction
To make predictions on a new image from the "elettrocablaggi" dataset:

```bash
python samples/elettrocablaggi/predict.py
```

**Note:** Place the annotation file in `.JSON` format in the appropriate folder.
- The image name field **must** be present.
- Component annotations are **not** required.
- The correct image path is **not** necessary.


"""
 Il dataset contenete le immagini con i ritagli dei singoli componenti deve trovarsi nella cartella con il seguente path
   - ../../images/data augmentation/componenti/
"""

import os
import numpy as np
from PIL import Image

path = os.path.join(os.getcwd(), '..', '..', 'images', 'data_augmentation', 'componenti')
components = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

for cmp in components:
    img = Image.open(os.path.join(path, cmp))
    img = np.array(img.convert("RGBA"))

    white = np.sum(img[:, :, :3], axis=2)
    white_mask = np.where(white == 255 * 3, 1, 0)

    alpha = np.where(white_mask, 0, img[:, :, -1])

    img[:, :, -1] = alpha
    img = Image.fromarray(np.uint8(img))
    img.save(os.path.join(path, cmp), "PNG")

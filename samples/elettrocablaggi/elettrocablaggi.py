"""Mask R-CNN
Configurations and data loading code for Elettrocablaggi.
"""

import numpy as np
import skimage.draw
import warnings
import glob
import json
import sys
import os

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("../../")

    # Import Mask RCNN
    sys.path.append(ROOT_DIR)  # To find local version of the library
    from mrcnn.config import Config
    from mrcnn import utils


class ElettrocablaggiDataset(utils.Dataset):

    def __init__(self):
        self.__source = "elettrocablaggi"
        super(self.__class__, self).__init__()

    def load_elettrocablaggi(self, label_file_path, annotation_dir, images_dir):
        # Read classes from file
        class_labels = []
        with open(label_file_path, encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                class_labels.append(stripped_line)

        # Add classes
        for i in range(len(class_labels)):
            self.add_class(self.__source, i, class_labels[i])

        # Add images
        asset_names = glob.glob("{}*.json".format(annotation_dir))

        image_id = 0
        for asset_name in asset_names:
            # read the annotation file
            f = open(asset_name, encoding='utf-8')
            data = json.load(f)
            f.close()

            # parse the content of the annotation file to create mask info
            width, height = (data['asset']['size']['width'], data['asset']['size']['height'])
            path = '{}{}'.format(images_dir, data['asset']['name'])
            annotations = data['regions']
            polygons = list()
            for ant in annotations:
                if ant['type'] != "POLYGON":
                    continue
                class_name = ant['tags'][0]
                all_x = [a['x'] for a in ant['points']]
                all_y = [a['y'] for a in ant['points']]
                polygons.append({"all_x": all_x,
                                 "all_y": all_y,
                                 "class_name": class_name})
            # add image
            self.add_image(
                self.__source,
                image_id=image_id,
                path=path,
                width=width,
                height=height,
                polygons=polygons)

            image_id += 1

        return self.class_info, self.image_info

    def load_mask(self, image_id):
        """Generate instance masks for an image.
        Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a elettrocablaggi dataset image, delegate to parent class.
        info = self.image_info[image_id]
        if info["source"] != self.__source:
            return super(self.__class__, self).load_mask(image_id)

        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        class_ids = []
        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            rr, cc = skimage.draw.polygon(p['all_y'], p['all_x'])
            mask[rr, cc, i] = 1
            class_id = self.map_source_class_id("{}.{}".format(self.__source, p['class_name']))
            class_ids.append(class_id)

        if class_ids:
            # Return mask, and array of class IDs of each instance.
            return mask.astype(np.bool), np.array(class_ids, dtype=np.int32)
        else:
            # Call super class to return an empty mask
            return super(self.__class__, self).load_mask(image_id)


class ElettrocablaggiConfig(Config):
    """Configuration for training on the elettrocablaggi dataset.
    Derives from the base Config class and overrides values specific
    to elettrocablaggi dataset.
    """
    # Give the configuration a recognizable name
    NAME = "elettrocablaggi"

    # Train on 1 GPU and 2 images per GPU. Batch size is 2 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 2

    # Number of classes (including background)
    NUM_CLASSES = 1 + 13  # background + 12 components (the 0 component not exist in current dataset, but is necessary)

    # Use small images for faster training. Set the limits of the small side
    # the large side, and that determines the image shape.
    IMAGE_RESIZE_MODE = "square"
    IMAGE_MIN_DIM = 320
    IMAGE_MAX_DIM = 320

    # Use smaller anchors because our image and objects are small
    RPN_ANCHOR_SCALES = (8, 16, 32, 64, 128)  # anchor side in pixels

    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    TRAIN_ROIS_PER_IMAGE = 32

    # Use a small epoch since the data is simple
    STEPS_PER_EPOCH = 150

    # use small validation steps since the epoch is small
    VALIDATION_STEPS = 15

    # Learning rate and momentum
    # The Mask RCNN paper uses lr=0.02, but on TensorFlow it causes
    # weights to explode. Likely due to differences in optimizer
    # implementation.
    LEARNING_RATE = 1e-4
    LEARNING_MOMENTUM = 0.9

    # Weight decay regularization
    WEIGHT_DECAY = 5e-4

    # Remove mini_mask in order to evaluate the performance of the model
    USE_MINI_MASK = False

    # Minimum probability value to accept a detected instance
    # ROIs below this threshold are skipped
    DETECTION_MIN_CONFIDENCE = 0.9


class ElettrocablaggiInferenceConfig(ElettrocablaggiConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

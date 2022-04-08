import os
import sys
import warnings
import elettrocablaggi
import tensorflow as tf

tf.compat.v1.disable_eager_execution()

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("../../")
    sys.path.append(ROOT_DIR)  # To find local version of the library
    from mrcnn.model import MaskRCNN

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    # Restrict TensorFlow to only use the first GPU
    try:
        tf.config.set_visible_devices(gpus[0], 'GPU')
        logical_gpus = tf.config.list_logical_devices('GPU')
        print(len(gpus), " Physical GPUs,", len(logical_gpus), " Logical GPU")
    except RuntimeError as e:
        # Visible devices must be set before GPUs have been initialized
        print(e)

if __name__ == '__main__':
    info = {'train': {'label_file_path': "dataset/elettrocablaggi_20200921/GRETA_230V/train/annots/labels.txt",
                      'annotation_dir': "dataset/elettrocablaggi_20200921/GRETA_230V/train/annots/",
                      'images_dir': "dataset/elettrocablaggi_20200921/GRETA_230V/train/images/"},
            'test': {'label_file_path': "dataset/elettrocablaggi_20200921/GRETA_230V/test/annots/labels.txt",
                     'annotation_dir': "dataset/elettrocablaggi_20200921/GRETA_230V/test/annots/",
                     'images_dir': "dataset/elettrocablaggi_20200921/GRETA_230V/test/images/"},
            'saved_model_dir': "weights/elettrocablaggi/GRETA_230V/",
            'coco_weights_path': "weights/mask_rcnn_coco.h5"}

    # Training dataset
    dataset_train = elettrocablaggi.ElettrocablaggiDataset()
    class_info, train_image_info = dataset_train.load_elettrocablaggi(info['train']['label_file_path'],
                                                                      info['train']['annotation_dir'],
                                                                      info['train']['images_dir'])
    dataset_train.prepare()

    # Validation dataset
    dataset_val = elettrocablaggi.ElettrocablaggiDataset()
    class_info, val_image_info = dataset_val.load_elettrocablaggi(info['test']['label_file_path'],
                                                                  info['test']['annotation_dir'],
                                                                  info['test']['images_dir'])
    dataset_val.prepare()

    # Create config class containing training properties
    config = elettrocablaggi.ElettrocablaggiConfig()
    config.display()

    # Create model in training mode
    # with tf.device('/device:GPU:0'):
    model = MaskRCNN(mode="training",
                     config=config,
                     model_dir=info['saved_model_dir'])

    # sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(allow_soft_placement=True, log_device_placement=True))

    model.load_weights(info['coco_weights_path'],
                       by_name=True,
                       exclude=["mrcnn_class_logits", "mrcnn_bbox_fc",
                                "mrcnn_bbox", "mrcnn_mask"])

    """Training
            Only the heads. Here we're freezing all the backbone layers and training only the randomly initialized 
            layers (i.e. the ones that we didn't use pre-trained weights from MS COCO). To train only the head layers, 
            pass layers='heads' to the train() function.
    """
    # Train the head branches
    # Passing layers="heads" freezes all layers except the head
    # layers. You can also pass a regular expression to select
    print("Train network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=150,
                layers='heads')

    # Fine tune from layers 5+ because GPU used not have sufficient RAM to train all net
    # print("Train layers from 5+")
    # model.train(dataset_train, dataset_val,
    #             learning_rate=config.LEARNING_RATE,
    #             epochs=100,
    #             layers="5+")

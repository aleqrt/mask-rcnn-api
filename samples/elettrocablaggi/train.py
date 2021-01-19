import os
import sys
import warnings
import elettrocablaggi

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("../../")
    sys.path.append(ROOT_DIR)  # To find local version of the library
    from mrcnn.model import MaskRCNN

if __name__ == '__main__':
    info = {'train': {'label_file_path': "dataset/elettrocablaggi_20200921/train/annots/labels.txt",
                      'annotation_dir': "dataset/elettrocablaggi_20200921/train/annots/",
                      'images_dir': "dataset/elettrocablaggi_20200921/train/images/"},
            'test': {'label_file_path': "dataset/elettrocablaggi_20200921/test/annots/labels.txt",
                     'annotation_dir': "dataset/elettrocablaggi_20200921/test/annots/",
                     'images_dir': "dataset/elettrocablaggi_20200921/test/images/"},
            'saved_model_dir': "weights/elettrocablaggi_20200921/",
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
    model = MaskRCNN(mode="training",
                     config=config,
                     model_dir=info['saved_model_dir'])

    model.load_weights(info['coco_weights_path'],
                       by_name=True,
                       exclude=["mrcnn_class_logits", "mrcnn_bbox_fc",
                                "mrcnn_bbox", "mrcnn_mask"])

    """Training
            Train in two stages:
            Only the heads. Here we're freezing all the backbone layers and training only the randomly initialized layers (i.e. the ones that we didn't use pre-trained weights from MS COCO). To train only the head layers, pass layers='heads' to the train() function.

            Fine-tune all layers. Simply pass layers="all to train all layers.
    """
    # Train the head branches
    # Passing layers="heads" freezes all layers except the head
    # layers. You can also pass a regular expression to select
    print("Train network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=100,
                layers='heads')

    # Fine tune all layers
    # Passing layers="all" trains all layers. You can also 
    # pass a regular expression to select which layers to
    # train by name pattern.
    # print("Train all layers")
    # model.train(dataset_train, dataset_val,
    #             learning_rate=config.LEARNING_RATE,
    #             epochs=50,
    #             layers="all")

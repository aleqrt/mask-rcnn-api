import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    
    import svhn
    from mrcnn import visualize
    from mrcnn import utils
    from mrcnn.config import Config
    from mrcnn.model import MaskRCNN

    import numpy as np



if __name__ == '__main__':
    info = {'train': {'label_file_path':"../../dataset/SVHN/train/annots/labels.txt",
                   'annotation_dir': "../../dataset/SVHN/train/annots/",
                   'images_dir': "../../dataset/SVHN/train/images/"},
         'test':{'label_file_path':"../../dataset/SVHN/test/annots/labels.txt",
                   'annotation_dir': "../../dataset/SVHN/test/annots/",
                   'images_dir': "../../dataset/SVHN/test/images/"},
         'saved_model_dir': "../../weights/SVHN/",
         'coco_weights_path': "../../weights/mask_rcnn_coco.h5"}
    
    
    # Training dataset
    dataset_train = svhn.SVHNDataset()
    class_info, train_image_info = dataset_train.load_svhn(info['train']['label_file_path'], 
                                                     info['train']['annotation_dir'], 
                                                     info['train']['images_dir'])
    dataset_train.prepare()

    # Validation dataset
    dataset_val = svhn.SVHNDataset()
    class_info, val_image_info = dataset_val.load_svhn(info['test']['label_file_path'], 
                                                     info['test']['annotation_dir'], 
                                                     info['test']['images_dir'])
    dataset_val.prepare()
    
    
    
    # Create config class containing training properties
    config = svhn.SVHNConfig()
    config.display()
    
    
    # Create model in training mode
    model = MaskRCNN(mode="training", 
                     config = config,
                     model_dir = info['saved_model_dir'])
                     
    
    # Train the head branches
    # Passing layers="heads" freezes all layers except the head
    # layers. You can also pass a regular expression to select
    # which layers to train by name pattern.
    model.train(dataset_train, dataset_val, 
                learning_rate=config.LEARNING_RATE, 
                epochs=100, 
                layers='heads')
                
    # Fine tune all layers
    # Passing layers="all" trains all layers. You can also 
    # pass a regular expression to select which layers to
    # train by name pattern.
    model.train(dataset_train, dataset_val, 
                learning_rate=config.LEARNING_RATE / 10,
                epochs=100, 
                layers="all")
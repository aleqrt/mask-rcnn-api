import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    
    import svhn
    from mrcnn import visualize
    from mrcnn import utils
    from mrcnn.config import Config
    from mrcnn.model import MaskRCNN
    import mrcnn.model as modellib

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


    inference_config = svhn.SVHNInferenceConfig()

    # create the model in inference mode
    model = modellib.MaskRCNN(mode="inference", 
                              config=inference_config,
                              model_dir=info['saved_model_dir'])

    # Get path to saved weights
    # Either set a specific path or find last trained weights
    # model_path = os.path.join(ROOT_DIR, ".h5 file name here")
    model_path = model.find_last()

    # Load trained weights
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)


    # Validation dataset
    dataset_val = svhn.SVHNDataset()
    class_info, val_image_info = dataset_val.load_svhn(info['test']['label_file_path'], 
                                                     info['test']['annotation_dir'], 
                                                     info['test']['images_dir'])
    dataset_val.prepare()



    # Compute VOC-Style mAP @ IoU=0.5
    # Running on 10 images. Increase for better accuracy.
    # image_ids = np.random.choice(dataset_val.image_ids, 10)
    image_ids = dataset_val.image_ids
    APs = []
    for image_id in image_ids:
        # Load image and ground truth data
        image, image_meta, gt_class_id, gt_bbox, gt_mask =\
            modellib.load_image_gt(dataset_val, inference_config,
                                   image_id, use_mini_mask=False)
        molded_images = np.expand_dims(modellib.mold_image(image, inference_config), 0)
        # Run object detection
        results = model.detect([image], verbose=0)
        r = results[0]
        # Compute AP
        AP, precisions, recalls, overlaps =\
            utils.compute_ap(gt_bbox, gt_class_id, gt_mask,
                             r["rois"], r["class_ids"], r["scores"], r['masks'])
        APs.append(AP)
        
    print("mAP: ", np.mean(APs))
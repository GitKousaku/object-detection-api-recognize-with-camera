import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
 
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
 
# This is needed to display the images.
#%matplotlib inline
 
 
# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
 
from utils import label_map_util
from utils import visualization_utils as vis_util
 
# What model to download.
#MODEL_NAME = 'ssd_mobilenet_v2_coco_2018_03_29'
MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
 
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = '/home/copal/tensorflow-fish-model/output_inference_graph/frozen_inference_graph.pb'
 
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = '/home/copal/tensorflow-fish-model/annotations/label_map.pbtxt'
 
NUM_CLASSES = 1

#opener = urllib.request.URLopener()
#opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
#tar_file = tarfile.open(MODEL_FILE)
#for file in tar_file.getmembers():
#    file_name = os.path.basename(file.name)
#    if 'frozen_inference_graph.pb' in file_name:
#        tar_file.extract(file, os.getcwd())
        
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

#------------------------以下、大きく修正-------------------------------------------------------------------
 
import cv2
 
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("v4l2src device=/dev/video1 ! avdec_h264 ! videoconvert ! appsink")
#cap = cv2.VideoCapture("/home/copal/FishVideo/fish1.avi")

#height = 720
#width  = 1280
height = 976
width  = 1392


 
def main():
    nn=151
    while(True):
 
        # 動画ストリームからフレームを取得
        ret, frame = cap.read()
        #frame = cv2.imread('/home/copal/tensorflow-fish-model/test_images/image1.jpg')
        
        # カメラ画像をリサイズ
        #image_np = cv2.resize(frame,(width,height))
        #frame  = cv2.imread('/home/copal/tensorflow-fish-model/test_images/image1.jpg')
        image_np=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)        

        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = detection_graph.get_tensor_by_name('detection_scores:0')
                classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                #print('bibibi',boxes)
                # Visualization of the results of a detection.
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)
                     
        #cv2.imshow("camera window", image_np) 
        image_npx=cv2.cvtColor(image_np,cv2.COLOR_BGR2RGB) 
        cv2.imshow('object detection', cv2.resize(image_npx, (1080, 720)))
        fname='DDDATA/img'+str(nn)+'.jpg' 
        print(fname)
        cv2.imwrite(fname,image_npx)
        nn=nn+1   

        # escを押したら終了。
        if cv2.waitKey(1) == 27:
            break
    
    #終了
    #cap.release()
    #cv2.destroyAllWindows()
 
 
if __name__ == '__main__':
    main()

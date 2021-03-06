import logging
import numpy as np
import cv2

from predict_client.prod_client import ProdClient

# This file capture video from webcam and sends it to model_server
# The server returns boxes
# This client visualise them

# Load coco label map!
# UCYEK = Ugliest code you ever know!
# ugly solution to inread classify list to list!
Path_to_label_map="./classify_data/mscoco_label_map.pbtxt"
f = open(Path_to_label_map)
lines = f.readlines()
class_list = list()
for i in range(0,len(lines)-1):

    temp = lines[i];
    temp.replace('\n','')
    if(temp.__contains__("id")):
        name = lines[i+1].replace('\n','').replace('display_name:','').replace('"','').replace(' ','')
        class_list.append(name);

#print(class_list)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# In each file/module, do this to get the module name in the logs
logger = logging.getLogger(__name__)

# Make sure you have a model running on localhost:9000
host = '192.168.0.1:9000'
model_name = 'ssd'
model_version = 1

# Capture
cap = cv2.VideoCapture(0);

# Image size
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH )   # float
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float


client = ProdClient(host, model_name, model_version)


while True:
    ret, im = cap.read();
    img = np.zeros((1, int(height), int(width),3), dtype = np.int8)
    img[0][:,:,:3] = im


    req_data = [{'in_tensor_name': 'inputs', 'in_tensor_dtype': 'DT_UINT8', 'data': img}]


    prediction = client.predict(req_data, request_timeout=10)


    det_box_array = prediction['detection_boxes'];
    i = 0.0;
    print("Detection result: ")
    while (i < prediction['num_detections']):
        box = det_box_array[0][int(i)];
        # Print out rectangles on image
        cv2.rectangle(im,(int(height*box[1]),int(width*box[0])),
        (int(height*box[3]),int(width*box[2])),(0,255,0),3)

        score = prediction['detection_scores'][0]
        class_temp = prediction['detection_classes'][0]  #default class = 1

        cv2.putText(im, class_list[int(class_temp[int(i)]-1)] + " : " + str(int(score[int(i)]*100)) + " %", (int(height*box[1]),int(width*box[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        print(class_list[int(class_temp[int(i)]-1)] + " : " + str(int(score[int(i)]*100)) + " % at x:" + str(int(height*box[1])) + ",y:" +str(int(width*box[0])))


        i += 1.0

    cv2.imshow('input', im)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break;

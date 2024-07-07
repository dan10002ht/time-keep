from deepface import DeepFace
import numpy as np
import os
import faiss
import json
import time
import cv2
import time

def find_key_by_value(input_dict, target_value):
    for key, values in input_dict.items():
        if target_value in values:
            return key
    return None

def face_detection(image):
    threshold = 0.5 # human face's confidence threshold
    current_dir = os.path.dirname(os.path.realpath(__file__))
    prototxt_file = os.path.join(current_dir,'Face_detection/SSD_deploy.prototxt')
    caffemodel_file = os.path.join(current_dir,'Face_detection/model.caffemodel')
    net = cv2.dnn.readNetFromCaffe(prototxt_file, caffeModel=caffemodel_file)
    origin_h, origin_w = image.shape[:2]

    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    tic = time.time()
    net.setInput(blob)
    detections = net.forward()
    print('net forward time: {:.4f}'.format(time.time() - tic))
    # detections.shape = (1,1,num_bbox,7) with 7 is 2 output is face or non_face and (x,y,w,h,conf) 
    bounding_boxs = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2] 
        if confidence > threshold:
            bounding_box = detections[0, 0, i, 3:7] * np.array([origin_w, origin_h, origin_w, origin_h])
            bounding_boxs.append(list(bounding_box.astype('int')))

    print(bounding_boxs)
    largest_face = None
    largest_area = 0
    
    for i in bounding_boxs:
        for (x, y, x1, y1) in [i]:
            area = (x1-x) * (y1-y)
            if area > largest_area:
                largest_area = area
                largest_face = [x, y, x1, y1]

    x_start, y_start, x_end, y_end = largest_face
    cropped_image = image[y_start:y_end, x_start:x_end]
                
    cv2.rectangle(image, (x_start, y_start), (x_end, y_end), (0,255,0), 3)
    # cv2.imwrite(current_dir + '/face{}.jpg'.format(i), cropped_image)
    if not bounding_boxs:
        return None
    else:
        bounding_boxs.remove(largest_face)

        # for j in bounding_boxs:
        #     for (x, y, x1, y1) in [j]:
        #         cv2.rectangle(image, (x, y), (x1, y1), (0, 0, 0), -1)
        
        image_path = current_dir + '/recog.jpg'
        cv2.imwrite(image_path, image)
                
        return image_path
    


def add_new_member(img , Face_ID, database = "/embedded_vectors.json"):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database = current_dir + database
    with open(database, "r") as json_file:
        embedded_vectors = json.load(json_file)
        
    imgs_path = face_detection(img)
    print(imgs_path)
    if imgs_path == None:
        #os.remove(img_path)
        print("Please try Again")
    
    else:
        query_embedding = DeepFace.represent(imgs_path, model_name="Facenet512", detector_backend="ssd", enforce_detection=False)
        query_embeddings = query_embedding[0]['embedding']

        print("Enter Member: ", Face_ID)

        if Face_ID in embedded_vectors:
            print("Face Found!!!")
            embedded_vectors['{}'.format(Face_ID)].append(query_embeddings)
        else:
            new_data = {
                '{}'.format(Face_ID) : [query_embeddings]
            }

            embedded_vectors.update(new_data)

        with open(database, "w") as json_file:
            json.dump(embedded_vectors, json_file, indent=4)
        
        os.remove(imgs_path)
        
        return print("Successfully added")
        
        
def embed(image_path):
    query_embedding = DeepFace.represent(image_path, model_name="Facenet512", detector_backend="ssd", enforce_detection=False)
    query_embeddings = np.array(query_embedding[0]['embedding'])
    print(query_embeddings)
    return query_embeddings


def recognition(image_path, database = "/embedded_vectors.json"):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    database = current_dir + database
    query_embeddings = embed(image_path)

    image_embeddings = []

    with open(database, "r") as json_file:
        embedded_vectors = json.load(json_file)

    for i in list(embedded_vectors.keys()):
        for j in embedded_vectors[i]:
            embedding = np.array(j, dtype=np.float32)
            image_embeddings.append(embedding)
            
    image_embeddings = np.array(image_embeddings)

    # Build the FAISS index
    embedding_dim = query_embeddings.shape[0]
    index = faiss.IndexFlatL2(embedding_dim)  # L2 distance index
    index.add(image_embeddings)

    # Query the index with the query embedding
    k = 1 # Number of nearest neighbors to retrieve
    distances, indices = index.search(np.array([query_embeddings], dtype=np.float32), k)

    if distances[0][0] > 300:
        print("Get out")
    else:
        vector = list(image_embeddings[indices[0][0]])

        name = find_key_by_value(embedded_vectors, vector)
        print("Name from recog:",name)
        return name


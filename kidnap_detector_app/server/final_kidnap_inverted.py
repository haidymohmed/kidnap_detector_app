import cv2
import numpy as np
from keras.applications.vgg19 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from pytz import timezone
from datetime import datetime
import torch
from utils.general import non_max_suppression, scale_coords
import math


def Predict(model , config , x):
  expected_frames = config['expected_frames']
  labels_idx2word = dict([(idx, word) for word, idx in config['labels'].items()])
  frames = x.shape[0]
  if frames > expected_frames:
      x = x[0 : expected_frames, :]
  elif frames < expected_frames:
      temp = np.zeros(shape=(expected_frames, x.shape[1]))
      temp[0 : frames, :] = x
      x = temp
  predicted_class = np.argmax(model.predict(np.array([x]))[0])
  predicted_label = labels_idx2word[predicted_class]
  return predicted_label


def detect_multi_boundary(model, img, conf_thres=0.25, iou_thres=0.5, device='cpu'):
    # Convert the image to a tensor
    img = torch.from_numpy(img.transpose(2, 0, 1)).float().div(255.0).unsqueeze(0).to(device)
    p = []
    # Run the YOLOv7 model on the input image
    pred = model(img)[0]
    pred = non_max_suppression(pred, conf_thres, iou_thres)
    p.append(pred)
    # Extract the list of boundaries of the annotated frame which have more than one boundary
    boundary_list = []
    for i, det in enumerate(pred):  # detections per image
        if det is not None and len(det):
            # Get bounding box coordinates for each detection
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img.shape[2:]).round()

            # Get the list of boundaries of the annotated frame
            for *xyxy, conf, cls in det:
              if int(cls) == 0:
                boundary_list.append([int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])])
    #multi_boundary_list = [boundary for boundary in boundary_list if boundary_list.count(boundary) > 1]
    return boundary_list

def person_recognizer(model, Cases, persones):
    #for case in Cases:
    results = model.predict(Cases, conf=0.5, save=False, save_crop=False, classes=[0])
    found_persones = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        found_persones.append([int(x1), int(y1), int(x2), int(y2)])
    persones.append(found_persones)

def cars_recognizer(model, Frame, kidnap_cases):
    results = model.predict(Frame, conf=0.5, save=False, save_crop=False, classes=[2])
    if(len(results[0].boxes) > 0):
        included_vehicles = []
        for car in results[0].boxes:
            cx, cy, cx2, cy2 = car.xyxy[0]
            cx, cy, cx2, cy2 = int(cx), int(cy), int(cx2), int(cy2)
            area_list = []
            #distance_list = []
            if(len(kidnap_cases) > 0):
                for case in kidnap_cases:
                    for person in case:
                        kx, ky, kx2, ky2 = person
                        intersects = intersect_counter(cx, cy, cx2, cy2, kx, ky, kx2, ky2)
                        if(len(intersects) == 4):
                            area_list.append(intersect_area(cx, cy, cx2, cy2, intersects))
                            #distance_list.append(distance_cal(cx, cy, cx2, cy2, kx, ky, kx2, ky2))
                if(len(area_list) > 0):
                    included_vehicles.append({
                        "image": Frame[cy:cy2, cx:cx2],
                        "area": np.mean(area_list),
                    })
            '''
            if(len(area_list) >= 2 or len(distance_list) >= 2):
                included_vehicles.append({
                        "image": Frame[cy:cy2, cx:cx2],
                        "area": np.mean(area_list),
                        "distance": np.median(distance_list)
                        })
            '''
        if(len(included_vehicles) > 0):
            return best_car(included_vehicles)
    return None
        
def best_car(cars):
    best = cars[0]
    for car in cars:
        if(car['area'] > best['area']):
            best = car
    return best

def distance_cal(cx, cy, cx2, cy2, kx, ky, kx2, ky2):
    ch = abs(cy2 - cy)
    cw = abs(cx2 - cx)
    kh = abs(ky2 - ky)
    kw = abs(kx2 - kx)
    cyy = int(cy + ch/2)
    cxx = int(cx + cw/2)
    kyy = int(ky + kh/2)
    kxx = int(kx + kw/2)
    return math.sqrt(pow(abs(cxx - kxx), 2) + pow(abs(cyy - kyy), 2))

def intersect_counter(cx, cy, cx2, cy2, kx, ky, kx2, ky2):
    intersections = []
    if(kx > cx and kx < cx2):
        intersections.append(kx)
    if(cx > kx and cx < kx2):
        intersections.append(cx)
    if(ky > cy and ky < cy2):
        intersections.append(ky)
    if(cy > ky and cy < ky2):
        intersections.append(cy)
    if(kx2 > cx and kx2 < cx2):
        intersections.append(kx2)
    if(cx2 > kx and cx2 < kx2):
        intersections.append(cx2)
    if(ky2 > cy and ky2 < cy2):
        intersections.append(ky2)
    if(cy2 > ky and cy2 < ky2):
        intersections.append(cy2)
    return intersections

def intersect_area(cx, cy, cx2, cy2, intersects):
    width = abs(intersects[0] - intersects[2])
    height = abs(intersects[1] - intersects[3])
    area = width * height
    car_area = abs(cx2-cx) * abs(cy2-cy)
    if(car_area > area):
        return area
    else:
        return car_area

#def process_frame(frame, models, cameraID, socketio):
def process_frame(frame, models, cameraID):
    img = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_NEAREST)
    width_factor = len(frame[0]) / 224
    height_factor = len(frame) / 224
    input = img_to_array(img)
    input = np.expand_dims(input, axis=0)
    input = preprocess_input(input)
    feature = models["Fmodel"].predict(input).ravel()
    x = np.array([feature])

    if Predict(models["Violence Model"], models["Violence Config"], x) == 'Non_Violence':
        #socketio.emit('frame_processed', {'kidnap': cameraID})
        print("Violence")
        multi_boundary_list = detect_multi_boundary(models["Boundry Model"] ,img)
        cropped_frames = []
        for area in multi_boundary_list:
            cropped_frames.append(frame[int(area[1]*height_factor): int(area[3]*height_factor), int(area[0]*width_factor): int(area[2]*width_factor)])
        if(len(cropped_frames) > 0):
            people = []
            person_recognizer(models['Yolo v8'], frame, people)
            if(len(people[0]) > 0):
                print("kidnap")
                data = {
                    'original_frame': frame,
                    'cropped_frames': cropped_frames,
                    'camera_id': cameraID,
                    'time': datetime.now(timezone('Africa/Cairo')),
                    'faces': people
                    }
                people_croped = []
                person_recognizer(models['Yolo v8'], data['cropped_frames'], people_croped)
                if(len(people_croped) > 0):
                    car = cars_recognizer(models['Yolo v8'], data['original_frame'], data['faces'])
                    if(car):
                        data['cars'] = car
                if('cars' in data.keys()):
                    license_plate = models['License detector'](data['cars']["image"], models['License Location'])
                    if(isinstance(license_plate, np.ndarray)):
                        data['license plate'] = license_plate
                        data['license_number'] = []
                        models['License recognizer'](license_plate, models['License Reader'], data['license_number'])
                return data
            else:
                return "Violence and kidnap but no people where found"
        else :
            #socketio.emit('frame_processed', {'kidnap': 0})
            return "Non_Kidnap"
    else:
        #socketio.emit('frame_processed', {'kidnap': 0})
        return "Non_Violence"
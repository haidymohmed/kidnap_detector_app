from flask import Flask
from flask_socketio import SocketIO
import base64
import numpy as np
from PIL import Image
import io
import sys
import numpy as np
import cv2
from keras.applications.vgg19 import VGG19
from keras.models import Model, load_model
import torch
import easyocr
from ultralytics import YOLO
import pickle
import os
import datetime
from pytz import timezone

sys.path.append(r".\kidnap_detection")
sys.path.append(r".\Vehicle_Tracking")

from kidnap_detection.final_kidnap import process_frame, best_car
from Vehicle_Tracking.vehicle_tracking import compare_lisence_numbers, License_number_Recognition
from models.experimental import attempt_load

Violence_Model = load_model(r".\kidnap_detection\violence\vgg19_lstm_attention.h5")
Violence_Config = np.load(r".\kidnap_detection\violence\config.npy",allow_pickle=True).item()
Kidnap_Model = load_model(r".\kidnap_detection\kidnap\vgg19_lstm_attention.h5")
Kidnap_Config = np.load(r".\kidnap_detection\kidnap\config.npy",allow_pickle=True).item()
Fmodel = VGG19(include_top=False, weights='imagenet')
boundry_model = attempt_load([r".\kidnap_detection\Exp1\runs\train\yolov7-tiny\weights\best.pt"], map_location=torch.device('cpu')).autoshape()
license_detection = attempt_load(r".\Vehicle_Tracking\weights\best.pt", map_location='cpu')
easyOCR_reader = easyocr.Reader(['ar'])
yolov8 = YOLO("./Yolo8/yolov8n.pt", task='detect',) 
Models = {
    "Violence Model":Violence_Model,
    "Violence Config":Violence_Config,
    "Kidnap Model":Kidnap_Model,
    "Kidnap Config":Kidnap_Config,
    "Fmodel":Fmodel,
    "Boundry Model":boundry_model,
    "License Location":license_detection,
    "License Reader":easyOCR_reader,
    "License Number":License_number_Recognition,
    "Yolo v8":yolov8,
}
app = Flask(__name__)
socketio = SocketIO(app)

def save_data(data, file_path, file_name):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open((file_path+file_name), 'wb') as file:
        pickle.dump(data, file)

def load_data(file_path):
    if(os.path.exists(file_path)):
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    else:
        return "file doesn't exist"

dataMap_file = ".\\saved data\\dataMapsave.pkl"
reports_file = ".\\saved data\\reports.pkl"

data_map = load_data(dataMap_file)
if(not isinstance(data_map, dict)):
    data_map = {}
global reported_cases
reported_cases = load_data(reports_file)
if(not isinstance(reported_cases, list)):
    reported_cases = []

def frame_encoder(numpy_frame):
    pil_image = Image.fromarray(numpy_frame)
    frame_bytes = io.BytesIO()
    pil_image.save(frame_bytes, format="JPEG")
    frame_bytes = frame_bytes.getvalue()
    return base64.b64encode(frame_bytes)

def frame_decoder(base64_frame):
    frame_bytes = base64.b64decode(base64_frame)
    pil_image = Image.open(io.BytesIO(frame_bytes))
    return np.array(pil_image)

def Report(case):
    kidnap_video = []
    used_cars = []
    captured_licenses = []
    people = []
    for frame in case:
        kidnap_video.append(frame_encoder(frame['original_frame']))
        if('cars' in frame.keys()):
            used_cars.append(frame['cars'])
        no_of_kidnaps = len(frame['faces'])
        for kidnap in range(no_of_kidnaps):
            for face in frame['faces'][kidnap]:
                x1, y1, x2, y2 = face
                if(len(frame['cropped_frames']) > 0):
                    people.append(frame_encoder(frame['cropped_frames'][kidnap][y1:y2, x1:x2]))
                else:
                    people.append(frame_encoder(frame['original_frame'][y1:y2, x1:x2]))
        if len(frame["license_number"]) > 0:
            captured_licenses.append(frame["license_number"])
    repo = {
        'Case number': (len(reported_cases) + 1),
        'Camera id': case[0]['camera_id'],
        'Involved people': (len(people) > 0),
        'Used car': (len(used_cars) > 0),
    }
    if(len(captured_licenses) > 0):
        repo['Car license'] = compare_lisence_numbers(captured_licenses)
    
    socketio.emit('Kidnap_case', repo)
    
    if(len(people) > 0):
        repo['Involved people'] = people
    if(len(used_cars) > 0):
        repo['Used car'] = frame_encoder(best_car(used_cars)['image'])
    repo['Kidnap video'] = kidnap_video
    
    reported_cases.append(repo)
    global data_map
    data_map[case[0]['camera_id']] = []
    save_data(reported_cases, ".\\saved data", "reports.pkl")
    save_data(data_map, ".\\saved data", "dataMapsave.pkl")
    '''
    repo = {
        'Case number': number of case,
        'Camera id': camera number where case happened,
        'Kidnap video': list of encoded kidnap frames,
        'Involved people': list of encoded images of involved people without modification,
        'Car license': result of comparing the license numbers of cars with the biggest intersect area in each frame,
        'Used car': the car with the biggest intersect area with the involved people across the frames
    }
    '''

def check_cases():
    for case in data_map.keys():
        time_diff = datetime.datetime.now(timezone('Africa/Cairo')) - data_map[case][-1]['time']    
        if(int(time_diff.total_seconds()) >= 30):
            Report(data_map[case])



@socketio.on('frame')
def handle_frame(frame_data):
    # frame_data { 'frame': 'base64 encoded image',
    #             'camera_id': ' id'}
    check_cases()
    image = frame_decoder(frame_data['frame'])
    # add socketio as a fourth parameter for process_frame to respond using sockets
    result = process_frame(image, Models, frame_data['camera_id'], socketio)
    if(frame_data['camera_id'] not in data_map.keys):
        data_map[frame_data['camera_id']] = []
    data_map[frame_data['camera_id']].append(result)
    save_data(data_map, ".\\saved data", "dataMapsave.pkl")

@socketio.on('play_video')
def handle_frame(case_number):
    for frame in reported_cases[(case_number-1)]['Kidnap video']:
        socketio.emit('video_frame', {
            'frame': frame,
            'case_number':case_number
        })

@socketio.on('show_people')
def handle_frame(case_number):
    for person in reported_cases[(case_number-1)]['Involved people']:
        socketio.emit('show_people', person)

@socketio.on('show_cars')
def handle_frame(case_number):
    for car in reported_cases[(case_number-1)]['Used car']:
        socketio.emit('show_cars', car)


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1' , port=5000, allow_unsafe_werkzeug=True )
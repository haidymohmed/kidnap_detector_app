from flask import Flask, request ,send_file
import base64
import numpy as np
from PIL import Image
import io
import sys
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

from kidnap_detection.final_kidnap_inverted import process_frame, best_car
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

global data_map
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
    image = np.array(pil_image)
    if(len(image[0][0]) > 3):
        image = image[:, :, :3]
    return image

def Report(case):
    kidnap_video = []
    used_cars = []
    captured_licenses = []
    people = []
    for frame in case:
        kidnap_video.append(frame['original_frame'])
        if('cars' in frame.keys()):
            used_cars.append(frame['cars'])
        for case in frame['faces']:
            for person in case:
                x1, y1, x2, y2 = person
                people.append(frame['original_frame'][y1:y2, x1:x2])  
        if len(frame["license_number"]) > 0:
            captured_licenses.append(frame["license_number"])
    repo = {
        'Case number': (len(reported_cases) + 1),
        'Camera id': case[0]['camera_id'],
        'Kidnap video': kidnap_video,
        'Involved people': people,
        'Used car': best_car(used_cars)['image'],
        'Car license': ''.join(compare_lisence_numbers(captured_licenses)),
    }
    
    reported_cases.append(repo)
    
    socketio.emit('Kidnap_case', {
        'Case number': repo['Case number'],
        'Camera id': repo['Camera id'],
        'Car license': repo['Car license'],
        'Involved people': (len(repo['Involved people']) > 0),
        'Used car': (len(repo['Used car']) > 0),
    })
    
    global data_map
    data_map[case[0]['camera_id']] = []
    save_data(reported_cases, ".\\saved data", "reports.pkl")
    save_data(data_map, ".\\saved data", "dataMapsave.pkl")

def check_cases():
    for case in data_map.keys():
        time_diff = datetime.datetime.now(timezone('Africa/Cairo')) - data_map[case][-1]['time']
        if(int(time_diff.total_seconds()) >= 2):
            Report(data_map[case])

app = Flask(__name__)
# socketio = SocketIO(app)

@socketio.on('frame')
def handle_frame(frame_data):
    check_cases()
    image = frame_decoder(frame_data['frame'])
    result = process_frame(image, Models, frame_data['camera_id'], socketio)
    if(frame_data['camera_id'] not in data_map.keys()):
        data_map[frame_data['camera_id']] = []
    data_map[frame_data['camera_id']].append(result)
    save_data(data_map, ".\\saved data", "dataMapsave.pkl")
    
@app.route('/api/get_image', methods=['GET'])
def play_video():
    # Access query parameters from the request object
    case_number = request.args.get('caseNumber')
    for frame in reported_cases[(case_number-1)]['Kidnap video']:
        socketio.emit('video_frame', frame_encoder(frame))

@socketio.on('show_people')
def show_people(case_number):
    for person in reported_cases[(case_number-1)]['Involved people']:
        socketio.emit('show_people', frame_encoder(person))

@socketio.on('show_cars')
def show_cars(case_number):
    for car in reported_cases[(case_number-1)]['Used car']:
        socketio.emit('show_cars', frame_encoder(car))


if __name__ == '__main__':
    # socketio.run(app, host='127.0.0.1' , port=5000,allow_unsafe_werkzeug=True )
    app.run(debug=True)
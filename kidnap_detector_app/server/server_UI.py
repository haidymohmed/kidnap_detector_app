from flask import Flask, request ,send_file ,jsonify ,send_from_directory
from flask_socketio import SocketIO
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
import matplotlib.pyplot as plt
import json
import cv2

sys.path.append(r".\kidnap_detection")
sys.path.append(r".\Vehicle_Tracking")

from kidnap_detection.final_kidnap_inverted import process_frame, best_car
from Vehicle_Tracking.vehicle_tracking import compare_lisence_numbers, License_number_detection, License_number_Recognition
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
    "License detector":License_number_detection,
    "License recognizer":License_number_Recognition,
    "Yolo v8":yolov8,
}

def save_data(data, file_path, file_name):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(os.path.join(file_path,file_name), 'wb') as file:
        pickle.dump(data, file)

def load_data(file_path):
    if(os.path.exists(file_path)):
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    else:
        return "file doesn't exist"

def save_images(images, case_number, type):
    if(type == 'people'):
        counter = 0
        for img in images:
            if not os.path.isdir(f".\\Reports\\Case {case_number}\\Involved_People"):
                os.makedirs(f".\\Reports\\Case {case_number}\\Involved_People")
            plt.imsave(f".\\Reports\\Case {case_number}\\Involved_People\\{type}{counter}.jpg", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            counter += 1
    else:
        if not os.path.isdir(f".\\Reports\\Case {case_number}"):
                os.makedirs(f".\\Reports\\Case {case_number}")
        plt.imsave(f".\\Reports\\Case {case_number}\\{type}.jpg", cv2.cvtColor(images, cv2.COLOR_BGR2RGB))

def save_video(video, case_number):
    frame_width = len(video[0][0])
    frame_height = len(video[0])
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    file_path = f".\\Reports\\Case {case_number}\\Kidnap_video.mp4"
    if(not os.path.isdir(f".\\Reports\\Case {case_number}")):
        os.makedirs(f".\\Reports\\Case {case_number}")
    try:
        out = cv2.VideoWriter(file_path, fourcc, 24, (frame_width, frame_height))
        for frame in video:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
        out.release()
    except Exception as e:
        print(f"Error saving video: {str(e)}")

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

def compare_imgs(images):
    best_img = images[0]
    best_area = len(best_img)*len(best_img[0])
    for img in images:
        img_width = len(img[0])
        img_height = len(img)
        if((img_width*img_height) > best_area):
            best_img = img
            best_area = (img_height*img_width)
    return best_img

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

def get_case_number():
    cases = load_data(r".\\Reports\\number of cases.pkl")
    if(isinstance(cases, str)):
        save_data(1, ".\\Reports", "number of cases.pkl")
        return 1
    else:
        save_data(cases+1, ".\\Reports", "number of cases.pkl")
        return cases+1
    
def Report(case):
    case_number = get_case_number()
    kidnap_video = []
    used_cars = []
    license_plates = []
    captured_licenses = []
    license_number = None
    people = []
    for frame in case:
        kidnap_video.append(frame['original_frame'])
        if('cars' in frame.keys()):
            used_cars.append(frame['cars'])
        if('license plate' in frame.keys()):
            license_plates.append(frame['license plate'])
        for k_case in frame['faces']:
            for person in k_case:
                x1, y1, x2, y2 = person
                people.append(frame['original_frame'][y1:y2, x1:x2])  
        if("license_number" in frame.keys()):
            captured_licenses.append(frame["license_number"])
    save_video(kidnap_video, case_number)
    save_images(people, case_number, 'people')
    if(len(used_cars) > 0):
        save_images(best_car(used_cars)["image"], case_number, 'car')
        if(len(license_plates) > 0):
            save_images(compare_imgs(license_plates), case_number, 'plate')
    
    if(len(captured_licenses) > 0):
        lisence_number = compare_lisence_numbers(captured_licenses)
        if(lisence_number):
            license_number = ''.join(lisence_number)

    with open(f".\\Reports\\Case {case_number}\\data.json", "w") as json_file:
        json.dump({
            'Case number': case_number,
            'Camera id': case[0]['camera_id'],
            'Case time': str(case[0]['time'].date())+' '+str(case[0]['time'].time()),
            'License number': license_number,
            'License plate':(len(license_plates) > 0),
            'Involved people': (len(people) > 0),
            'Used car': (len(used_cars) > 0),
        }, json_file)
    
    global data_map
    data_map[case[0]['camera_id']] = []
    save_data(data_map, ".\\saved data", "dataMapsave.pkl")

def check_cases():
    for case in data_map.keys():
        if(len(data_map[case]) > 0):
            time_diff = datetime.datetime.now(timezone('Africa/Cairo')) - data_map[case][-1]['time']
            if(int(time_diff.total_seconds()) >= 10):
                Report(data_map[case])

def handle_frame(frame_data):
    check_cases()
    result = process_frame(frame_decoder(frame_data['frame']), Models, frame_data['camera_id'])
    if(isinstance(result, dict)):
        if(frame_data['camera_id'] not in data_map.keys()):
            data_map[frame_data['camera_id']] = []
        data_map[frame_data['camera_id']].append(result)
        save_data(data_map, ".\\saved data", "dataMapsave.pkl")
        return 'kidnap'
    else:
        return 'no_kidnap'



app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
    

@app.route('/api/send_frame', methods=['POST'])
def upload_image():
    data = request.get_json()
    if data is not None:
        handle_frame(data)
        return 'JSON data received'
    return 'No JSON data received', 400
    
@app.route('/api/get_cases', methods=['GET'])
def get_cases():
    reports_folder = '.\\Reports'
    cases_list = []
    for filename in os.listdir(reports_folder):
        if(filename.endswith('.pkl')):
            continue
        cases_list.append(os.path.join(reports_folder,filename))
    cases = []
    for case in cases_list:
        with open(case +'\\data.json' , 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        cases.append(json_data)  
    return jsonify(cases)

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    frame_bytes = io.BytesIO()
    pil_img.save(frame_bytes, format='JPEG')
    frame_bytes = frame_bytes.getvalue() # convert the PIL image to byte array
    return base64.b64encode(frame_bytes).decode('utf-8')

@app.route('/api/get_kidnap_video', methods=['GET'])
def get_kidnap_video():
    case_number = request.args.get('case_number')
    video_path = f'Reports\\Case {case_number}\\kidnap_video.mp4'
    mime_type = 'video/mp4'
    return send_file(video_path, mimetype=mime_type)

@app.route('/api/get_persons' , methods=['GET'])
def get_persons():
    case_number = request.args.get('case_number')
    folder = f'Reports\\Case {case_number}\\Involved_People'    
    result = []
    print(folder)
    for filename in os.listdir(folder):
        result.append(os.path.join(folder,filename))
    ##reuslt  contains list of path images
    encoded_imges = []
    for image_path in result:
        # print(image_path)
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'result': encoded_imges})

@app.route('/api/get_used_car' , methods=['GET'])
def get_used_car():
    case_number = request.args.get('case_number')
    image_path = f'.\\Reports\\Case {case_number}\\car.jpg'    
    encoded_imge = get_response_image(image_path)
    return jsonify({'result': encoded_imge})

@app.route('/api/get_licence' , methods=['GET'])
def get_licence():
    case_number = request.args.get('case_number')
    image_path = f'Reports\\Case {case_number}\\plate.jpg'    
    encoded_imge = get_response_image(image_path)
    return jsonify({'result': encoded_imge})

if __name__ == '__main__':
    app.run(debug=True)
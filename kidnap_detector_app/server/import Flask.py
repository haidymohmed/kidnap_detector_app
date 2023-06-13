from flask import Flask, request ,send_file ,jsonify ,send_from_directory
import os
from PIL import Image
import io
import base64
import json
import numpy as np


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def frame_decoder(base64_frame):
    frame_bytes = base64.b64decode(base64_frame)
    pil_image = Image.open(io.BytesIO(frame_bytes))
    return np.array(pil_image)


ind = 0
@app.route('/api/send_frame', methods=['POST'])
def upload_image():
    # Check if the request contains a file
    # if 'image' not in request.files:
    #     return 'No image file provided', 400
    global ind 
    ind = ind +1
    data = request.get_json()

    if data is not None:
        image = frame_decoder(data['frame'])
        frame_number = data['time']
        camera_id = data['camera_id']
        # image_array = np.frombuffer(image_file, np.uint8)
        # width = 2
        # height = 2
        # image_array = image_array.reshape((height, width, -1))
        image = Image.fromarray(image)
        image.save('server\saved_image\image_'+str(ind)+'.png') 
        return 'JSON data received'
    

    return 'No JSON data received', 400



@app.route('/api/get_kidnap_video', methods=['GET'])
def get_kidnap_video():
    case_number = request.args.get('case_number')
    video_path = '../assets/Reports/Case '+case_number+'/kidnap video.mp4'
    mime_type = 'video/mp4'
    return send_file(video_path, mimetype=mime_type)






@app.route('/api/get_cases', methods=['GET'])
def get_cases():
    
    '''
    {
        'Case number': repo['Case number'],
        'Camera id': repo['Camera id'],
        'Car license': repo['Car license'],
        'Involved people': (len(repo['Involved people']) > 0),
        'Used car': (len(repo['Used car']) > 0),
    }
    '''
    # Specify the path to your JSON file
    reports_folder = os.getcwd()+'/assets/Reports'
    cases_list = []
    for filename in os.listdir(reports_folder):
        cases_list.append(os.path.join(reports_folder,filename))
    cases = []
    for case in cases_list:
        with open(case +'/Data.json' , 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        cases.append(json_data)  
    return jsonify(cases)

    
def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    frame_bytes = io.BytesIO()
    pil_img.save(frame_bytes, format='JPEG')
    frame_bytes = frame_bytes.getvalue() # convert the PIL image to byte array
    return base64.b64encode(frame_bytes).decode('utf-8')



@app.route('/api/get_persons')
def get_persons():
    case_number = request.args.get('case_number')
    folder = os.getcwd()+'/assets/Reports/Case '+ case_number +'/Involved poeple'    
    result = []

    for filename in os.listdir(folder):
        result.append(os.path.join(folder,filename))

    encoded_imges = []
    for image_path in result:
        
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'result': encoded_imges})
    


@app.route('/api/get_used_car')
def get_used_car():
    case_number = request.args.get('case_number')
    image_path = os.getcwd()+'/assets/Reports/Case '+ case_number +'/Used car.jpg'    
    encoded_imge = get_response_image(image_path)
    return jsonify({'result': encoded_imge})

@app.route('/api/get_licence')
def get_licence():
    case_number = request.args.get('case_number')
    image_path = os.getcwd()+'/assets/Reports/Case '+ case_number +'/License8.jpg'    
    encoded_imge = get_response_image(image_path)
    return jsonify({'result': encoded_imge})

if __name__ == '__main__':
    # arabic_text_bytes = b'\xd9\x85\xd8\xb5\xd8\xb1 \xd9\x87\xd9\x8a \xd8\xa7\xd9\x85\xd9\x8a'

    # encodings = ['utf-8', 'cp1256']

    # for encoding in encodings:
    #     try:
    #         arabic_text = arabic_text_bytes.decode(encoding)
    #         print(f"Decoded with {encoding}: {arabic_text}")
    #     except UnicodeDecodeError:
    #         print(f"Failed to decode with {encoding}")
    app.run(debug=True)
    
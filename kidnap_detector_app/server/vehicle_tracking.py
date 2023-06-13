import cv2
import torch
import numpy as np
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.torch_utils import select_device, time_synchronized
from torch.functional import Tensor
import unicodedata

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    shape = img.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:
        r = min(r, 1.0)
    ratio = r, r
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    if auto:
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)
    elif scaleFill:
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]
    dw /= 2
    dh /= 2
    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, ratio, (dw, dh)

def compare_license_easyOCR(test_license, Plate_license):
  test_license.reverse()
  for index in range(len(test_license)):
    if(index in Plate_license.keys()):
      if(test_license[index] in Plate_license[index].keys()):
        Plate_license[index][test_license[index]] = Plate_license[index][test_license[index]] + 1
      else:
        Plate_license[index][test_license[index]] = 1
    else:
      Plate_license[index] = {test_license[index] : 1}
  return Plate_license

def biggest_repeat_easyOCR(Plate_map):
  best_lis = []
  for v in Plate_map.values():
    character = ""
    repeat = 0
    for char, r in v.items():
      if(r > repeat):
        character = char
        repeat = r
    best_lis.append(character)
  return best_lis

def is_arabic(char):
    if char.isalpha():
        try:
            char_name = unicodedata.name(char)
            if char_name.startswith('ARABIC'):
                return True
        except ValueError:
            pass
    return False

def easyocr_right_lisence(liscense):
  license_plate = ''.join(liscense)
  word_without_spaces = license_plate.replace(' ', '')
  right_list = []
  letters = []
  for char in word_without_spaces:
    if(char.isascii() and char.isalnum()):
      continue
    elif(is_arabic(char)):
      letters.append(char)
    else:
      right_list.append(char)
  letters.reverse()
  for i in letters:
    right_list.append(i)
  right_list.reverse()
  return right_list

def compare_lisence_numbers(Video):
  Lnumber = {}
  final_number = []
  for Frame in Video:
    if(len(Frame) > 0):  
      if(len(Lnumber.keys()) > 1):
        compare_license_easyOCR(Frame[0], Lnumber)
      else:
        for i in range(len(Frame[0])):
          Lnumber[i] = {Frame[0][i] : 1}
      final_number = biggest_repeat_easyOCR(Lnumber)
      return final_number

def License_number_detection(Frame, model):
  with torch.no_grad():
    imgsz = 640
    set_logging()
    device = select_device('cpu')
    half = device.type != 'cpu'
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    if half:
      model.half()
    if device.type != 'cpu':
      model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

    img = letterbox(Frame, imgsz, stride=stride)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
      img = img.unsqueeze(0)
      
    t1 = time_synchronized()
    pred = model(img, augment= False)[0]
    pred = non_max_suppression(pred, 0.25, 0.45, agnostic= False)
    t2 = time_synchronized()
      
    for i, det in enumerate(pred):
      gn = torch.tensor(Frame.shape)[[1, 0, 1, 0]]
      if len(det):
        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], Frame.shape).round()
    
    for p in pred[0]:
      x = np.array(Tensor.cpu(p))
      x1, y1, x2, y2 ,ac ,c = x
      if(x2-x1 > 30 and ac > 0.7):
        return Frame[int(y1):int(y2), int(x1):int(x2)]
    return None
        
        

def License_number_Recognition(license_plate, reader, result):
  easyocr_result = reader.readtext(license_plate, detail=1)
  if(len(easyocr_result) > 0 and easyocr_result[0][2] > 0.5):
    lisence_number = easyocr_right_lisence(easyocr_result[0][1])
    result.append(lisence_number)
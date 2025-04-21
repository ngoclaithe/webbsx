import cv2
import torch
import os
import uuid
import function.utils_rotate as utils_rotate
import function.helper as helper
from schemas import LicensePlateResponse

class LicensePlateDetectionService:
    def __init__(self, default_confidence=0.8):
        self.default_confidence = default_confidence
        self.yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector.pt', force_reload=True, source='local')
        self.yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr.pt', force_reload=True, source='local')
        self.yolo_license_plate.conf = 0.60
        
        os.makedirs("static/uploads", exist_ok=True)
        os.makedirs("static/results", exist_ok=True)
        
    def process_image(self, image_path, confidence=None):
        conf = confidence if confidence is not None else self.default_confidence
        
        img = cv2.imread(image_path)
        result_img = img.copy()
        license_plates = []
        
        plates = self.yolo_LP_detect(img, size=640)
        list_plates = plates.pandas().xyxy[0].values.tolist()
        
        if len(list_plates) == 0:
            lp = helper.read_plate(self.yolo_license_plate, img)
            if lp != "unknown":
                cv2.putText(result_img, lp, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                license_plates.append(
                    LicensePlateResponse(
                        license_plate=lp,
                        confidence=conf,
                        coordinates=None
                    )
                )
        else:
            for plate in list_plates:
                confidence_value = float(plate[4]) if len(plate) > 4 else conf
                
                if confidence_value >= conf:
                    x = int(plate[0])
                    y = int(plate[1])
                    w = int(plate[2] - plate[0])
                    h = int(plate[3] - plate[1])
                    
                    cv2.rectangle(result_img, (x, y), (x+w, y+h), color=(0, 0, 225), thickness=2)
                    
                    crop_img = img[y:y+h, x:x+w]
                    temp_crop_path = "static/uploads/crop_temp.jpg"
                    cv2.imwrite(temp_crop_path, crop_img)
                    
                    flag = 0
                    lp = "unknown"
                    for cc in range(0, 2):
                        for ct in range(0, 2):
                            rotated_img = utils_rotate.deskew(crop_img, cc, ct)
                            lp = helper.read_plate(self.yolo_license_plate, rotated_img)
                            if lp != "unknown":
                                cv2.putText(result_img, lp, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                                flag = 1
                                break
                        if flag == 1:
                            break
                    
                    license_plates.append(
                        LicensePlateResponse(
                            license_plate=lp,
                            confidence=confidence_value,
                            coordinates={
                                "x": x,
                                "y": y,
                                "width": w,
                                "height": h
                            }
                        )
                    )
        
        result_image_name = f"{uuid.uuid4()}.jpg"
        result_image_path = f"static/results/{result_image_name}"
        cv2.imwrite(result_image_path, result_img)
        
        return license_plates, result_image_path
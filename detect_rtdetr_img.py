import cv2
from ultralytics import RTDETR
import time
import numpy as np

# Load a model
model = RTDETR('./pt/rtdetr/signboard2_x.pt')  # COCO dataset으로 pretrained된 model을 불러옴

# Display model information (optional)
model.info()

# Use the model
results = model("../!DATASET/images/0.jpg",
                conf=0.5,
                save = True)
annotated = results[0].plot()
#print(f'모든 데이터 : \n{results}')
# print(f'좌상단 우하단 xyxy tensor : \n{results[0].boxes.xyxy}')
while True:
   cv2.imshow("RT_DETR", annotated)
   key = cv2.waitKey(1) & 0xFF
   if key == ord('q'):
       break
cv2.destroyAllWindows()


import cv2
from ultralytics import RTDETR
import easyocr
import urllib.request
import json
import numpy as np
from googletrans import Translator

# def of translate
def translate_korean_to_english(text):
    try:
        translator = Translator()
        translation = translator.translate(text, src='ko', dest='en')
        return translation.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

# RTDETR model load
model = RTDETR('pt/rtdetr/signboard_l.pt')
test_img = "datasets/images/0.jpg"

# detect
results = model(test_img, conf=0.4, save=True)
annotated = results[0].plot()
boxes = results[0].boxes.xyxy  # 좌상단과 우하단의 xyxy coordinate

# EasyOCR load
reader = easyocr.Reader(['ko'])

# 이미지 로드
image = cv2.imread(test_img)
if image is None:
    print(f"Error: Can't load image. please check path: {test_img}")
    exit()

# check bounding box
if len(boxes) == 0:
    print("Signboard not detected.")
else:
    # crop with bounding box
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cropped_image = image[y1:y2, x1:x2]

        # ocr for cropped img
        result = reader.readtext(cropped_image)
        for detection in result:
            coords = detection[0]
            text = detection[1]
            print("Detected Text:", text)

            # Papago Translation
            client_id = "9tuyFZTn8vDDqcz8b37G"  # Replace with your Client ID
            client_secret = "IanBk_lW_r"  # Replace with your Client Secret
            encText = urllib.parse.quote(text)
            data = "source=ko&target=en&text=" + encText
            url = "https://openapi.naver.com/v1/papago/n2mt"
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", client_id)
            request.add_header("X-Naver-Client-Secret", client_secret)
            try:
                response = urllib.request.urlopen(request, data=data.encode("utf-8"))
                rescode = response.getcode()
                if rescode == 200:
                    response_body = response.read()
                    parsed_json = json.loads(response_body)
                    t_text = parsed_json['message']['result']['translatedText']
                    print("Papago Translated Text:", t_text)
                else:
                    print("Papago Error Code:", rescode)
            except Exception as e:
                print(f"Papago Translation Error: {e}")

            # Google Translate
            google_translation = translate_korean_to_english(text)
            if google_translation:
                print("Google Translated Text:", google_translation)
            else:
                print("Google Translation failed.")

while True:
   cv2.imshow("RT_DETR", annotated)
   key = cv2.waitKey(1) & 0xFF
   if key == ord('q'):
       break
cv2.destroyAllWindows()
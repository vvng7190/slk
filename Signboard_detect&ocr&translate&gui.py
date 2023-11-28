import easyocr
import tkinter as tk
from tkinter import scrolledtext, filedialog, Listbox
from tkinter import messagebox, filedialog, scrolledtext
from PIL import Image, ImageTk
import os
import pyttsx3
import cv2
from ultralytics import RTDETR
from googletrans import Translator
import urllib.request
import json
import webbrowser
import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as tkFont
import numpy as np

reader = easyocr.Reader(['ko'])
translator = Translator()

# RTDETR model load
model = RTDETR('pt/rtdetr/signboard_l.pt')

def load_images():
    image_folder_path = filedialog.askdirectory()
    if not image_folder_path:
        return
    image_list = os.listdir(image_folder_path)
    for image in image_list:
        listbox_images.insert(tk.END, os.path.join(image_folder_path, image))

def detect_text(image_path):
    results = model(image_path)
    boxes = results[0].boxes.xyxy
    annotated = results[0].plot()

    image = cv2.imread(image_path)
    detected_texts = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cropped_image = image[y1:y2, x1:x2]

        ocr_results = reader.readtext(cropped_image,
                                 allowlist = '{소망동물병원삼화페인트\
                                 서부슈퍼지영선한복맛깔명성안경콘택트\
                                 공덕커피애월식당새진테크')
        for detection in ocr_results:
            detected_texts = detection[1]

    return detected_texts, annotated

def google_translate(text):
    try:
        translator = Translator()
        translation = translator.translate(text, src='ko', dest='en')
        return translation.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

def papago_translate(text):
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
            p_text = parsed_json['message']['result']['translatedText']
            return p_text
        else:
            print("Papago Error Code:", rescode)
    except Exception as e:
        print(f"Papago Translation Error: {e}")

def ocr_and_translate(image_path):
    detected_text, annotated = detect_text(image_path)
    g_translated_text = google_translate(detected_text)
    p_translated_text = papago_translate(detected_text)
    print(p_translated_text)
    return detected_text, g_translated_text, p_translated_text, annotated

def open_link(url):
    webbrowser.open_new(url)

def display_results():
    selected_index = listbox_images.curselection()
    if not selected_index:
        return
    image_path = listbox_images.get(selected_index[0])
    text_translate_scrolled.delete(1.0, tk.END)
    infomation_scrolled.delete(1.0, tk.END)
    detected, g_translated, p_translated, annotated = ocr_and_translate(image_path)

    default_font = tkFont.Font(family="Helvetica", size=20)
    text_translate_scrolled.config(font=default_font)
    text_translate_scrolled.insert(tk.END,
                                  f"Detected text : {detected}\n")
    text_translate_scrolled.insert(tk.END,
                                    f"Google Translate : {g_translated}\n")
    text_translate_scrolled.insert(tk.END,
                                    f"Papago Translate : {p_translated}")

    hyperlink_font = tkFont.Font(family="Helvetica", size=20, underline=True)
    infomation_scrolled.tag_configure("hyperlink", font=hyperlink_font, foreground="blue")
    infomation_scrolled.insert(tk.END, "Search on Naver Link\n")
    infomation_scrolled.insert(tk.END, "Click here", "hyperlink")
    infomation_scrolled.tag_bind("hyperlink", "<Button-1>", lambda e: open_link(
        f"https://papago.naver.net/website?locale=ko&source=ko&target=en&url=https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={detected}"))
    update_image_display(annotated)

def update_image_display(annotated):
    # OpenCV 이미지 (BGR)를 RGB로 변환합니다.
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
    # RGB 이미지를 PIL 형식으로 변환합니다.
    annotated_pil = Image.fromarray(annotated_rgb)

    # 이미지 크기를 조정합니다.
    annotated_pil.thumbnail((640, 640))

    # Tkinter에서 사용할 수 있는 형태로 변환합니다.
    photo = ImageTk.PhotoImage(annotated_pil)

    # 이미지를 라벨 위젯에 표시합니다.
    label_image.config(image=photo)
    label_image.image = photo

def submit_feedback():
    feedback = feedback_entry.get("1.0", tk.END).strip()

    if feedback == "":
        engine = pyttsx3.init()
        engine.say("Please enter the feedback")
        engine.runAndWait()
    else:
        print("Feedback received:", feedback)
        messagebox.showinfo("Feedback", "Thank you for your feedback!")
        feedback_entry.delete("1.0", tk.END)

root = tk.Tk()
root.title("Image OCR and Translation GUI")

left_frame = tk.Frame(root)
right_frame = tk.Frame(root)
listbox_frame = tk.Frame(root)
feedback_frame = tk.Frame(root)

left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
listbox_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
feedback_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

listbox_images = Listbox(listbox_frame, width=50, height=20)
listbox_images.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
button_load_images = tk.Button(listbox_frame, text="Load Images", command=load_images)
button_load_images.pack()

label_image = tk.Label(left_frame)
label_image.pack()

text_translate_scrolled = scrolledtext.ScrolledText(right_frame, height=20, width=50)
text_translate_scrolled.pack()
infomation_scrolled = scrolledtext.ScrolledText(right_frame, height=20, width=50)
infomation_scrolled.pack()

button_ocr_translate = tk.Button(right_frame, text="Translate Text", command=display_results)
button_ocr_translate.pack()

feedback_label = tk.Label(feedback_frame, text="Your Feedback:")
feedback_label.pack()
feedback_entry = tk.Text(feedback_frame, height=5, width=40)
feedback_entry.pack()
submit_button = tk.Button(feedback_frame, text="Submit Feedback", command=submit_feedback)
submit_button.pack()

root.mainloop()
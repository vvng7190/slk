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
    # RTDETR 모델을 사용하여 이미지에서 객체를 탐지합니다.
    results = model(image_path)
    boxes = results[0].boxes.xyxy  # 좌상단과 우하단의 xyxy 좌표

    image = cv2.imread(image_path)
    detected_texts = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cropped_image = image[y1:y2, x1:x2]

        # Cropped 이미지에 대해 OCR 수행
        ocr_results = reader.readtext(cropped_image,
                                 allowlist = '{소망동물병원삼화페인트\
                                 서부슈퍼지영선한복맛깔명성안경콘택트\
                                 공덕커피애월식당새진테크')
        for detection in ocr_results:
            detected_texts = detection[1]

    return detected_texts

def google_translate(text):
    try:
        translator = Translator()
        translation = translator.translate(text, src='ko', dest='en')
        return translation.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

def ocr_and_translate(image_path):
    detected_text = detect_text(image_path)
    g_translated_text = google_translate(detected_text)

    return detected_text, g_translated_text

def display_results():
    selected_index = listbox_images.curselection()
    if not selected_index:
        return
    image_path = listbox_images.get(selected_index[0])
    original_text_scrolled.delete(1.0, tk.END)
    translated_text_scrolled.delete(1.0, tk.END)
    detected, g_translated = ocr_and_translate(image_path)
    original_text_scrolled.insert(tk.END, detected)
    translated_text_scrolled.insert(tk.END, g_translated)
    update_image_display(image_path)

def update_image_display(image_path):
    image = Image.open(image_path)
    image.thumbnail((500, 500))  # Resizing for display
    photo = ImageTk.PhotoImage(image)
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

original_text_scrolled = scrolledtext.ScrolledText(right_frame, height=20, width=50)
original_text_scrolled.pack()
translated_text_scrolled = scrolledtext.ScrolledText(right_frame, height=20, width=50)
translated_text_scrolled.pack()

button_ocr_translate = tk.Button(right_frame, text="Translate Text", command=display_results)
button_ocr_translate.pack()

feedback_label = tk.Label(feedback_frame, text="Your Feedback:")
feedback_label.pack()
feedback_entry = tk.Text(feedback_frame, height=5, width=40)
feedback_entry.pack()
submit_button = tk.Button(feedback_frame, text="Submit Feedback", command=submit_feedback)
submit_button.pack()

root.mainloop()
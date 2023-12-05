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
import webview

engine = pyttsx3.init()
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
    results = model(image_path, conf=0.8)
    boxes = results[0].boxes.xyxy

    image = cv2.imread(image_path)
    if len(boxes) == 0:  # No signboards detected
        return "", image  # Return empty string and original image

    annotated = results[0].plot()
    detected_texts = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cropped_image = image[y1:y2, x1:x2]

        ocr_results = reader.readtext(cropped_image, allowlist='경곱공금깔노뉴다당덕동맛망맥명물별병복부붕비빵삼새서선성소슈시식아안애야어영욕원월이인장주지진창청치카커콘크택테트퍼페피한홍화')
        for detection in ocr_results:
            detected_texts.append(detection[1].replace(' ', ''))

    return ' '.join(detected_texts), annotated  # Join all detected texts into a single string

def google_translate(text):
    try:
        translator = Translator()
        translation = translator.translate(text, src='ko', dest='en')
        return translation.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return "Translation Error"

def papago_translate(text):
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
            return parsed_json['message']['result']['translatedText']
        else:
            print("Papago Error Code:", rescode)
            return "Papago Translation Error"
    except Exception as e:
        print(f"Papago Translation Error: {e}")
        return "Papago Translation Error"

def ocr_and_translate(image_path):
    detected_text, annotated = detect_text(image_path)
    g_translated_text = google_translate(detected_text)
    p_translated_text = papago_translate(detected_text)
    return detected_text, g_translated_text, p_translated_text, annotated

def open_hyperlink(url):
    webbrowser.open_new(url)

def display_results():
    selected_index = listbox_images.curselection()
    if not selected_index:
        return

    image_path = listbox_images.get(selected_index[0])
    combined_scrolled_text.delete(1.0, tk.END)

    detected_text, annotated = detect_text(image_path)

    if detected_text:  # Text is detected
        g_translated_text = google_translate(detected_text)
        p_translated_text = papago_translate(detected_text)

        default_font = tkFont.Font(family="Helvetica", size=20)
        combined_scrolled_text.config(font=default_font)

        combined_scrolled_text.insert(tk.END, f"Detected text : {detected_text}\n\n")
        combined_scrolled_text.insert(tk.END, f"Google Translate : {g_translated_text}\n\n")
        combined_scrolled_text.insert(tk.END, f"Papago Translate : {p_translated_text}\n\n")

        # Adding hyperlinks for Naver and Google Maps
        hyperlink_font = tkFont.Font(family="Helvetica", size=20, underline=True)
        combined_scrolled_text.tag_configure("hyperlink", font=hyperlink_font, foreground="blue")
        combined_scrolled_text.insert(tk.END, "Search on Naver Link\n", "hyperlink")
        combined_scrolled_text.tag_bind("hyperlink", "<Button-1>", lambda e: open_link_in_webview(f"https://papago.naver.net/website?locale=ko&source=ko&target=en&url=https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={detected_text}"))

        google_maps_link_font = tkFont.Font(family="Helvetica", size=20, underline=True)
        combined_scrolled_text.tag_configure("google_maps_link", font=google_maps_link_font, foreground="blue")
        google_maps_url = f"https://www.google.com/maps/search/{detected_text}?hl=en&entry=ttu"
        combined_scrolled_text.insert(tk.END, "Search on Google Maps\n", "google_maps_link")
        combined_scrolled_text.tag_bind("google_maps_link", "<Button-1>", lambda e: open_link_in_webview(google_maps_url))

        update_image_display(annotated)  # Display annotated image

    else:  # No text detected
        combined_scrolled_text.insert(tk.END, "Signboard not detected\n")
        update_image_display(image_path, original=True)  # Display original image


def update_image_display(image_or_path, original=False):
    if original:
        image = Image.open(image_or_path)
    else:
        annotated_rgb = cv2.cvtColor(image_or_path, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(annotated_rgb)

    image.thumbnail((640, 640))
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

def pronounce_text():
    selected_index = listbox_images.curselection()
    if not selected_index:
        return
    image_path = listbox_images.get(selected_index[0])
    detected, _, _, _ = ocr_and_translate(image_path)
    engine.say(detected)
    engine.runAndWait()

def open_link_in_webview(url):
    webview.create_window('Web View', url, width=800, height=600)
    webview.start()

root = tk.Tk()
root.title("Image OCR and Translation GUI")

# frame
left_frame = tk.Frame(root, width=200, height=200)
center_frame = tk.Frame(root, width=400, height=200)
right_frame = tk.Frame(root, width=200, height=200)

# frame.pack
left_frame.pack(side=tk.LEFT, fill=tk.Y)
center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right_frame.pack(side=tk.LEFT, fill=tk.Y)

# left_frame
listbox_images = Listbox(left_frame, width=40, height=20)
listbox_images.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
button_load_images = tk.Button(left_frame, text="Load Images", command=load_images)
button_load_images.pack()

# center_frame
label_image = tk.Label(center_frame)
label_image.pack()

feedback_label = tk.Label(center_frame, text="Your Feedback:")
feedback_label.pack()
feedback_entry = tk.Text(center_frame, height=5, width=40)
feedback_entry.pack()
submit_button = tk.Button(center_frame, text="Submit Feedback", command=submit_feedback)
submit_button.pack()

# right_frame
combined_scrolled_text = scrolledtext.ScrolledText(right_frame, width=40, height=20)
combined_scrolled_text.pack()

button_ocr_translate = tk.Button(right_frame, text="Translate Text", command=display_results)
button_ocr_translate.pack()

# pronounce
button_pronounce = tk.Button(right_frame, text="Pronounce", command=pronounce_text)
button_pronounce.pack()

root.mainloop()
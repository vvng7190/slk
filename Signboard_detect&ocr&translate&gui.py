import easyocr
import tkinter as tk
from tkinter import scrolledtext, filedialog, Listbox
from tkinter import Listbox, messagebox, filedialog, scrolledtext
from googletrans import Translator
from PIL import Image, ImageTk
import os
from tkinter import Tk, Label
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import messagebox
import pyttsx3  # Initialize the OCR reader for Korean


reader = easyocr.Reader(['ko'])
translator = Translator()

def ocr_and_translate(image_path):
    results = reader.readtext(image_path)
    detected_text = ""
    translated_text = ""
    for detection in results:
        text = detection[1]
        detected_text += f'{text}\n'
        translation = translator.translate(text, src='ko', dest='en')
        translated_text += f'{translation.text}\n'
    return detected_text, translated_text


def display_results():
    selected_index = listbox_images.curselection()
    if not selected_index:
        return
    image_path = listbox_images.get(selected_index[0])
    original_text_scrolled.delete(1.0, tk.END)
    translated_text_scrolled.delete(1.0, tk.END)
    detected, translated = ocr_and_translate(image_path)
    original_text_scrolled.insert(tk.END, detected)
    translated_text_scrolled.insert(tk.END, translated)
    update_image_display(image_path)


def update_image_display(image_path):
    image = Image.open(image_path)
    image.thumbnail((500, 500))  # Resizing for display
    photo = ImageTk.PhotoImage(image)
    label_image.config(image=photo)
    label_image.image = photo


def load_images():
    image_folder_path = filedialog.askdirectory()
    if not image_folder_path:
        return
    image_list = os.listdir(image_folder_path)
    for image in image_list:
        listbox_images.insert(tk.END, os.path.join(image_folder_path, image))


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
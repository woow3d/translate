import os
import whisper
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tqdm import tqdm
from deep_translator import GoogleTranslator
from threading import Thread


def extract_audio(video_path, audio_path):
    try:
        if not os.path.exists(audio_path):
            ffmpeg.input(video_path).output(audio_path, acodec="mp3", ac=1).run(overwrite_output=True)
    except Exception as e:
        print(f"❌ خطأ أثناء استخراج الصوت من {video_path}: {e}")


def transcribe_and_translate(video_path, model, target_lang):
    srt_path = os.path.splitext(video_path)[0] + ".srt"
    audio_path = os.path.splitext(video_path)[0] + ".mp3"

    if os.path.exists(srt_path):
        progress_list.insert("", "end", values=(os.path.basename(video_path), "✅ مكتمل"))
        return

    item_id = progress_list.insert("", "end", values=(os.path.basename(video_path), "🔄 جاري المعالجة"))
    root.update_idletasks()

    try:
        extract_audio(video_path, audio_path)
        result = model.transcribe(audio_path)
        detected_lang = result["language"]

        source_lang = detected_lang if target_lang == "auto" else target_lang
        translator = GoogleTranslator(source=source_lang, target="ar")

        total_segments = len(result["segments"])
        for i, segment in enumerate(result["segments"]):
            progress = int(((i + 1) / total_segments) * 100)
            progress_list.item(item_id, values=(os.path.basename(video_path), f"⏳ {progress}%"))
            root.update_idletasks()

            start_time = f"{int(segment['start'] // 3600):02}:{int((segment['start'] % 3600) // 60):02}:{int(segment['start'] % 60):02},{int((segment['start'] % 1) * 1000):03}"
            end_time = f"{int(segment['end'] // 3600):02}:{int((segment['end'] % 3600) // 60):02}:{int(segment['end'] % 60):02},{int((segment['end'] % 1) * 1000):03}"

            text = translator.translate(segment['text'])

            with open(srt_path, "a", encoding="utf-8") as srt_file:
                srt_file.write(f"{i + 1}\n{start_time} --> {end_time}\n{text}\n\n")

        progress_list.item(item_id, values=(os.path.basename(video_path), "✅ مكتمل"))
    except Exception as e:
        progress_list.item(item_id, values=(os.path.basename(video_path), f"❌ خطأ: {e}"))
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


def process_videos():
    folder = folder_var.get()
    target_lang = lang_var.get()
    if not folder:
        messagebox.showerror("خطأ", "يرجى اختيار مجلد الفيديوهات")
        return

    model = whisper.load_model("medium")

    video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".flv")
    video_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(video_extensions)]

    if not video_files:
        messagebox.showerror("خطأ", "لم يتم العثور على ملفات فيديو في المجلد المحدد")
        return

    for video_path in video_files:
        transcribe_and_translate(video_path, model, target_lang)

    messagebox.showinfo("تم", "🎉 انتهت العملية بنجاح!")


def select_folder():
    folder = filedialog.askdirectory()
    folder_var.set(folder)


def start_processing():
    Thread(target=process_videos).start()


# إنشاء واجهة المستخدم
root = tk.Tk()
root.title("🎬 مترجم الفيديوهات")
root.geometry("500x400")
root.configure(bg="#f0f0f0")
folder_var = tk.StringVar()
lang_var = tk.StringVar(value="auto")
frame_top = tk.Frame(root, bg="#f0f0f0")
frame_top.pack(pady=10)

tk.Label(frame_top, text="📂 حدد مجلد الفيديوهات:", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, padx=5,
                                                                                          pady=5)
tk.Entry(frame_top, textvariable=folder_var, width=40).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_top, text="اختيار", command=select_folder).grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame_top, text="🌍 اختر لغة التفريغ:", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
tk.OptionMenu(frame_top, lang_var, "auto", "en", "fr", "es", "de", "it", "zh").grid(row=1, column=1, padx=5, pady=5)

tk.Button(frame_top, text="🎬 بدء العملية", command=start_processing, font=("Arial", 12), bg="#4CAF50", fg="white").grid(
    row=2, column=0, columnspan=3, pady=10)

frame_bottom = tk.Frame(root, bg="#ffffff")
frame_bottom.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("اسم الفيديو", "الحالة")
progress_list = ttk.Treeview(frame_bottom, columns=columns, show="headings")
progress_list.heading("اسم الفيديو", text="📄 اسم الفيديو")
progress_list.heading("الحالة", text="⚙️ الحالة")
progress_list.pack(fill="both", expand=True)

root.mainloop()

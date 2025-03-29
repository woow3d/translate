import os
import whisper
import ffmpeg
from tqdm import tqdm
from deep_translator import GoogleTranslator

# تحديد مسار المجلد الذي يحتوي على السكربت
script_dir = os.path.dirname(os.path.abspath(__file__))

def extract_audio(video_path, audio_path):
    """استخراج الصوت من الفيديو باستخدام ffmpeg"""
    if not os.path.exists(audio_path):
        ffmpeg.input(video_path).output(audio_path, acodec="mp3", ac=1).run(overwrite_output=True)

def transcribe_and_translate(video_path, model):
    """تحويل الصوت إلى نص باللغة الإنجليزية ثم ترجمته إلى العربية"""
    srt_path = os.path.splitext(video_path)[0] + ".srt"
    audio_path = os.path.splitext(video_path)[0] + ".mp3"

    if os.path.exists(srt_path):
        print(f"✅ الترجمة موجودة مسبقًا: {srt_path}")
        return

    print(f"🔄 جارِ استخراج النص من {video_path}...")

    try:
        extract_audio(video_path, audio_path)
        result = model.transcribe(audio_path, language="English")

        translator = GoogleTranslator(source="en", target="ar")

        with open(srt_path, "w", encoding="utf-8") as srt_file:
            progress_bar = tqdm(result["segments"], desc=f"📜 معالجة {video_path}", unit="مقطع", ncols=80, ascii=True)
            for i, segment in enumerate(progress_bar):
                start_time = f"{int(segment['start'] // 3600):02}:{int((segment['start'] % 3600) // 60):02}:{int(segment['start'] % 60):02},{int((segment['start'] % 1) * 1000):03}"
                end_time = f"{int(segment['end'] // 3600):02}:{int((segment['end'] % 3600) // 60):02}:{int(segment['end'] % 60):02},{int((segment['end'] % 1) * 1000):03}"
                
                text = translator.translate(segment['text'])  # ترجمة النص
                
                srt_file.write(f"{i+1}\n{start_time} --> {end_time}\n{text}\n\n")

        print(f"✅ تم إنشاء الترجمة: {srt_path}")

    except Exception as e:
        print(f"❌ خطأ أثناء معالجة {video_path}: {e}")

def main():
    print(f"🔄 جارِ تحميل نموذج Whisper...")
    model = whisper.load_model("medium")
    print("✅ تم تحميل النموذج بنجاح!")

    video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".flv")
    video_files = [os.path.join(script_dir, f) for f in os.listdir(script_dir) if f.lower().endswith(video_extensions)]

    if not video_files:
        print("❌ لم يتم العثور على أي ملفات فيديو في نفس مجلد السكربت.")
        return

    for video_path in video_files:
        transcribe_and_translate(video_path, model)

    print("🎉 انتهت العملية بنجاح!")

if __name__ == "__main__":
    main()

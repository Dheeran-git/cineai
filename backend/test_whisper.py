import whisper
import os
import imageio_ffmpeg

def test_whisper():
    print("Testing Whisper...")
    
    # Inject ffmpeg path from imageio-ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    target_ffmpeg = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    if not os.path.exists(target_ffmpeg):
        import shutil
        shutil.copy(ffmpeg_exe, target_ffmpeg)
        print(f"Created ffmpeg.exe at {target_ffmpeg}")
    
    print(f"Adding ffmpeg path: {ffmpeg_dir}")
    os.environ["PATH"] += os.pathsep + ffmpeg_dir
    
    try:
        model = whisper.load_model("tiny") # use tiny for speed in test
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # Check for a sample file in storage
    storage_path = r"C:\Users\Prajw\SampleSmart\backend\storage"
    if os.path.exists(storage_path):
        files = [f for f in os.listdir(storage_path) if f.endswith(('.mp4', '.mp3', '.wav'))]
        if files:
            sample_file = os.path.join(storage_path, files[0])
            print(f"Attempting to transcribe: {sample_file}")
            try:
                result = model.transcribe(sample_file)
                print("Transcription result:", result.get("text"))
            except Exception as e:
                print(f"Transcription failed: {e}")
        else:
            print("No media files found in storage to test.")
    else:
        print(f"Storage path {storage_path} does not exist.")

if __name__ == "__main__":
    test_whisper()

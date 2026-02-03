from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import whisper
import os


VIDEO_PATH = "Beautiful Recitation of Surah Infitar (سورة الانفطار_).mp4"          
LANGUAGE = "en"  
OUTPUT_VIDEO = "output_subtitled-v1.mp4"
OUTPUT_SRT = "subtitles.srt"

# Format time for SRT files
def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

try:
    # Check video file exists
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: '{VIDEO_PATH}' not found!")
        print(f"Make sure the video file is in this folder: {os.getcwd()}")
        input("\nPress Enter to exit...")
        exit()
    
    print(f"Video found: {VIDEO_PATH}")
    
    # Extract audio from video
    print("\nExtracting audio...")
    video = VideoFileClip(VIDEO_PATH)
    audio_file = "temp_audio.wav"
    video.audio.write_audiofile(audio_file, codec='pcm_s16le')
    print("Audio extraction complete!")
    
    # Load Whisper model
    print("\nLoading Whisper AI model...")
    print("   (First time may take a while to download the model)")
    model = whisper.load_model("large-v3")
    print("Model loaded successfully!")
    
    # Transcribe audio
    result = model.transcribe(
    audio_file, 
    language="en",  
    task="translate", 
    initial_prompt="A clear English translation of Surah Al-Muzzammil recitation.",
    no_speech_threshold=0.6, 
    condition_on_previous_text=False 
)    

    subtitles = []
    for segment in result['segments']:
        subtitles.append({
            'text': segment['text'].strip(),
            'start': segment['start'],
            'end': segment['end'],
            'duration': segment['end'] - segment['start']
        })
    
    
    # Print subtitles
    for i, sub in enumerate(subtitles[:5]): 
        print(f"{i+1}. [{sub['start']:.1f}s - {sub['end']:.1f}s]: {sub['text']}")
    if len(subtitles) > 5:
        print(f"... and {len(subtitles) - 5} more")
    
    # Save SRT file
    print(f"\nCreating SRT file: {OUTPUT_SRT}")
    with open(OUTPUT_SRT, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(sub['start'])} --> {format_srt_time(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")
    print(f"SRT file saved successfully!")
    
    # Add subtitles to video
    text_clips = []
    
    for i, sub in enumerate(subtitles):
        print(f"   Adding subtitle {i+1}/{len(subtitles)}...")
        txt_clip = TextClip(
        text=sub['text'],
        font_size=30,             
        color='white',            
        font=r'C:\Windows\Fonts\Arial.ttf',         
        method='caption',
        size=(int(video.w * 0.85), None), 
        # bg_color='black',
        stroke_color='black',
        stroke_width=1,
    )
        
        txt_clip = txt_clip.with_position(('center', video.h - txt_clip.h - 90))
        txt_clip = txt_clip.with_start(sub['start']).with_duration(sub['end'] - sub['start'])
        text_clips.append(txt_clip)
    
    final_video = CompositeVideoClip([video] + text_clips)
    
    # Save final video
    print(f"\nSaving final video: {OUTPUT_VIDEO}")
    print("   (This may take some time...)")
    final_video.write_videofile(
        OUTPUT_VIDEO,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps
    )
    
    # Cleanup
    video.close()
    final_video.close()
    if os.path.exists(audio_file):
        os.remove(audio_file)
    
except Exception as e:
    print(f"\n Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()

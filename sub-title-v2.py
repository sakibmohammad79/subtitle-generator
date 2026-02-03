
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os
import sys
from bidi.algorithm import get_display

VIDEO_PATH = "Beautiful Recitation of Surah Infitar (سورة الانفطار_).mp4"
TEXT_FILE = "subtitles.txt"  
OUTPUT_VIDEO = "output_subtitled_v2.mp4"
OUTPUT_SRT = "from_txt_subtitles.srt"

# Subtitle Styling
FONT_SIZE = 34
FONT_COLOR = 'white'
STROKE_COLOR = 'black'
STROKE_WIDTH = 1.5
SUBTITLE_WIDTH_RATIO = 0.85  
SUBTITLE_POSITION_FROM_BOTTOM = 90  


FONT_PATH = r'C:\Windows\Fonts\Arial.ttf' 


def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def read_subtitles_from_text(text_file):
    
    subtitles = []
    
    if not os.path.exists(text_file):
        print(f" Error: '{text_file}' not found!")
        return subtitles
    
    with open(text_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            try:
                # Split by pipe character
                parts = [p.strip() for p in line.split('|')]
                
                if len(parts) < 3:
                    print(f"Line {line_num}: Not enough parts (need start|end|text)")
                    continue
                
                start_time = float(parts[0])
                end_time = float(parts[1])
                text = parts[2]
                
                # Validation
                if end_time <= start_time:
                    print(f"Line {line_num}: End time must be after start time")
                    continue
                
                subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
                
            except ValueError as e:
                print(f"Line {line_num}: Invalid time format - {e}")
            except Exception as e:
                print(f"Line {line_num}: Error - {e}")
    
    return subtitles


def save_srt_file(subtitles, filename):
    """Save subtitles in SRT format for media player compatibility"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(sub['start'])} --> {format_srt_time(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")
    print(f"SRT file saved: {filename}")


def add_subtitles_to_video(video_path, subtitles, output_path):
    
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found!")
        return False
    
    print(f"\nLoading video: {video_path}")
    video = VideoFileClip(video_path)
    
    print(f"   Video duration: {video.duration:.2f} seconds")
    print(f"   Resolution: {video.w}x{video.h}")
    print(f"   FPS: {video.fps}")
    
    text_clips = []
    
    print(f"\n Creating {len(subtitles)} subtitle clips...")
    for idx, sub in enumerate(subtitles, 1):
        bidi_text = get_display(sub['text'])
        try:
            txt_clip = TextClip(
                text=bidi_text,
                font_size=FONT_SIZE,
                color=FONT_COLOR,
                font=FONT_PATH,
                method='caption',
                size=(int(video.w * SUBTITLE_WIDTH_RATIO), None),
                stroke_color=STROKE_COLOR,
                stroke_width=STROKE_WIDTH,
            )
            
            # Position subtitle at bottom center
            pos = ('center', video.h - txt_clip.h - SUBTITLE_POSITION_FROM_BOTTOM)
            
            txt_clip = (txt_clip.with_start(sub['start'])
                               .with_duration(sub['end'] - sub['start'])
                               .with_position(pos))
            text_clips.append(txt_clip)
            
            if idx % 10 == 0:
                print(f"   Processed {idx}/{len(subtitles)} subtitles...")
                
        except Exception as e:
            print(f"  Error creating subtitle {idx}: {e}")
    
    print(f"\nCompositing video with subtitles...")
    final_video = CompositeVideoClip([video] + text_clips)
    
    print(f"Writing output video: {output_path}")
    print(" This may take several minutes depending on video length...")
    
    final_video.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac', 
        fps=video.fps,
        preset='medium', 
        threads=4
    )
    
    # Cleanup
    video.close()
    final_video.close()
    
    return True


def main():
    """Main execution function"""
    print("=" * 70)
    print("          VIDEO SUBTITLE OVERLAY TOOL")
    print("=" * 70)
    
    # Check if subtitle file exists
    if not os.path.exists(TEXT_FILE):
        print(f"\nError: Subtitle file '{TEXT_FILE}' not found!")
        return

    # Read subtitles
    print(f"\n Reading subtitles from: {TEXT_FILE}")
    subtitles = read_subtitles_from_text(TEXT_FILE)
    
    if not subtitles:
        print("No valid subtitles found!")
        return

    print(f" Found {len(subtitles)} valid subtitles")
    
    # Save SRT file
    print(f"\nSaving SRT file: {OUTPUT_SRT}")
    save_srt_file(subtitles, OUTPUT_SRT)
    
    # Process video
    success = add_subtitles_to_video(VIDEO_PATH, subtitles, OUTPUT_VIDEO)
    
    if success:
        print("\n" + "=" * 70)
        print("SUCCESS! Video created successfully!")
        print("=" * 70)
        print(f"\n Output video: {OUTPUT_VIDEO}")
        print(f"SRT file: {OUTPUT_SRT}")
    else:
        print("\n Failed to create video. Please check the errors above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        sys.exit(1)
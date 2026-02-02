from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os




VIDEO_PATH = "Surah_Muzzammil_Imam_Feysal_Visual_Quran_Recitation_720P.mp4"
TEXT_FILE = "subtitles.txt"  
OUTPUT_VIDEO = "output_txt_subtitled.mp4"
OUTPUT_SRT = "from_txt_subtitles.srt"

# Subtitle styling
FONT_SIZE = 30
FONT_COLOR = 'white'
STROKE_COLOR = 'black'
STROKE_WIDTH = 1
SUBTITLE_WIDTH_RATIO = 0.85
SUBTITLE_POSITION_FROM_BOTTOM = 90




def format_srt_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_sample_text_file():
    """
    Create a sample text file for users to edit
    """
    sample_content = """# SUBTITLE FILE
# Format: start_time | end_time | text
# Time in seconds (decimal allowed)
# Lines starting with # are comments

0 | 3 | In the name of Allah
3.5 | 6 | The Most Gracious, the Most Merciful
6.5 | 9 | Praise be to Allah
9.5 | 12.5 | Lord of all the worlds
13 | 16 | The Most Gracious, the Most Merciful
16.5 | 19 | Master of the Day of Judgment
"""
    
    with open(TEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"✅ Sample text file created: {TEXT_FILE}")
    print("\n📝 Text File Format:")
    print("   start_time | end_time | subtitle text")
    print("   Example: 0 | 3 | In the name of Allah")


def read_subtitles_from_text(text_file):
    """
    Read subtitles from text file
    
    Format:
    start_time | end_time | text
    0 | 3 | In the name of Allah
    3.5 | 6 | The Most Gracious
    """
    subtitles = []
    
    print(f"\n Reading text file: {text_file}")
    
    with open(text_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse line
            try:
                parts = [p.strip() for p in line.split('|')]
                
                if len(parts) != 3:
                    print(f" Warning: Line {line_num} has invalid format, skipping")
                    continue
                
                start = float(parts[0])
                end = float(parts[1])
                text = parts[2]
                
                # Validate
                if not text:
                    print(f" Warning: Line {line_num} has empty text, skipping")
                    continue
                
                if end <= start:
                    print(f" Warning: Line {line_num} has invalid timing, skipping")
                    continue
                
                subtitles.append({
                    'text': text,
                    'start': start,
                    'end': end,
                    'duration': end - start
                })
                
            except ValueError as e:
                print(f"⚠️ Error in line {line_num}: {e}")
                continue
    
    print(f" Loaded {len(subtitles)} subtitles from text file")
    return subtitles


def preview_subtitles(subtitles):
    """Show subtitle preview"""
    print("\n" + "=" * 70)
    print(" SUBTITLE PREVIEW")
    print("=" * 70)
    
    for i, sub in enumerate(subtitles, 1):
        print(f"{i}. [{sub['start']:.1f}s - {sub['end']:.1f}s] {sub['text']}")
    
    print(f"\nTotal: {len(subtitles)} subtitles")
    print("=" * 70)


def save_srt_file(subtitles, filename):
    """Save subtitles as SRT file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(sub['start'])} --> {format_srt_time(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")
    
    print(f" SRT file saved: {filename}")


def add_subtitles_to_video(video_path, subtitles, output_path):
    """Add subtitles to video"""
    
    print(f"\n Loading video: {video_path}")
    video = VideoFileClip(video_path)
    print(f"   Resolution: {video.w}x{video.h}, Duration: {video.duration:.1f}s")
    
    print(f"\n Creating {len(subtitles)} subtitle clips...")
    text_clips = []
    
    for i, sub in enumerate(subtitles):
        print(f"   Creating clip {i+1}/{len(subtitles)}...")
        
        txt_clip = TextClip(
            text=sub['text'],
            font_size=FONT_SIZE,
            color=FONT_COLOR,
            font=r'C:\Windows\Fonts\Arial.ttf',
            method='caption',
            size=(int(video.w * SUBTITLE_WIDTH_RATIO), None),
            stroke_color=STROKE_COLOR,
            stroke_width=STROKE_WIDTH
        )
        
        position = ('center', video.h - txt_clip.h - SUBTITLE_POSITION_FROM_BOTTOM)
        txt_clip = txt_clip.with_position(position)
        txt_clip = txt_clip.with_start(sub['start']).with_duration(sub['duration'])
        text_clips.append(txt_clip)
    
    print("\n Composing final video...")
    final_video = CompositeVideoClip([video] + text_clips)
    
    print(f"\n Saving video: {output_path}")
    print("   (This may take several minutes...)")
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps
    )
    
    video.close()
    final_video.close()
    print("\n✅ Video saved successfully!")



# MAIN PROGRAM


def main():
    try:
        print("=" * 70)
        print("🎬 TEXT FILE MANUAL SUBTITLE CREATOR")
        print("=" * 70)
        
        # Check if text file exists
        if not os.path.exists(TEXT_FILE):
            print(f"\n⚠️ Text file not found: {TEXT_FILE}")
            print("\n💡 Creating sample text file...")
            create_sample_text_file()
            print("\n📝 Steps:")
            print(f"   1. Open '{TEXT_FILE}' in Notepad")
            print("   2. Edit the subtitles using format: start | end | text")
            print("   3. Save the file")
            print("   4. Run this script again")
            input("\nPress Enter to exit...")
            return
        
        # Check if video exists
        if not os.path.exists(VIDEO_PATH):
            print(f"\nError: Video '{VIDEO_PATH}' not found!")
            input("\nPress Enter to exit...")
            return
        
        print(f"📹 Video: {VIDEO_PATH}")
        print(f"📄 Text file: {TEXT_FILE}")
        
        # Read subtitles
        subtitles = read_subtitles_from_text(TEXT_FILE)
        
        if not subtitles:
            print("\nNo valid subtitles found in text file!")
            input("\nPress Enter to exit...")
            return
        
        # Preview
        preview_subtitles(subtitles)
        
        # Confirm
        confirm = input("\n✅ Create video with these subtitles? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled!")
            return
        
        # Save SRT
        save_srt_file(subtitles, OUTPUT_SRT)
        
        # Add to video
        add_subtitles_to_video(VIDEO_PATH, subtitles, OUTPUT_VIDEO)
        
        # Done
        print("\n" + "=" * 70)
        print("🎉 ALL DONE!")
        print("=" * 70)
        print(f"📹 Video: {OUTPUT_VIDEO}")
        print(f"📝 SRT: {OUTPUT_SRT}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\n✅ Press Enter to exit...")


if __name__ == "__main__":
    main()
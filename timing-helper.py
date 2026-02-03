
import subprocess
import json
import time
import sys
import os
from datetime import timedelta

def format_time(seconds):
    td = timedelta(seconds=seconds)
    return str(td)[:-3]

class SimpleTimingTool:
    def __init__(self, video_path):
        self.video_path = video_path
        self.marks = []
        self.current_mark_start = None
        self.start_time = None
        
    def open_video(self):
       
        print(" Video should open in VLC or your default video player")
        
        try:
            if sys.platform == 'win32':
                # Windows
                os.startfile(self.video_path)
            elif sys.platform == 'darwin':
                # macOS
                subprocess.call(['open', self.video_path])
            else:
                # Linux
                subprocess.call(['xdg-open', self.video_path])
            
            print("Video opened!")
            return True
        except Exception as e:
            print(f" Could not open video automatically: {e}")
            print(f"   Please open this file manually: {self.video_path}")
            return False
    
    def run(self):
        
        input("\n Press ENTER to open video and start...")
        
        # Open video
        self.open_video()
        
        
        self.start_time = time.time()
        mark_count = 0
        
        while True:
            try:
                command = input(">> ").strip().lower()
                
                if not command or command == '':  # ENTER pressed
                    current_time = time.time() - self.start_time
                    
                    if self.current_mark_start is None:
                        # Start mark
                        self.current_mark_start = current_time
                        mark_count += 1
                        print(f"\n Mark #{mark_count} START: {format_time(current_time)}")
                  
                    else:
                        # End mark
                        end_time = current_time
                        
                        if end_time > self.current_mark_start:
                            self.marks.append({
                                'start': round(self.current_mark_start, 2),
                                'end': round(end_time, 2),
                                'duration': round(end_time - self.current_mark_start, 2)
                            })
                            print(f" Mark #{mark_count} COMPLETE: {format_time(self.current_mark_start)} → {format_time(end_time)}")
                            print(f"   Duration: {end_time - self.current_mark_start:.2f}s")
                            print(f"   Total marks: {len(self.marks)}\n")
                            self.current_mark_start = None
                        else:
                            print("End time cannot be before start time!")
                            self.current_mark_start = None
                
                elif command == 'u':  # Undo
                    if self.current_mark_start is not None:
                        print("↩️  Reset start mark\n")
                        self.current_mark_start = None
                        mark_count -= 1
                    elif self.marks:
                        removed = self.marks.pop()
                        mark_count -= 1
                        print(f" Removed last mark: {format_time(removed['start'])} → {format_time(removed['end'])}\n")
                    else:
                        print(" No marks to undo!\n")
                
                elif command == 's':  # Save
                    self.save_marks()
                
                elif command == 'q':  # Quit
                    print("\nFinishing session...")
                    break
                
                elif command == 'help' or command == 'h':
                    print("\nCommands:")
                    print("  ENTER - Mark time")
                    print("  u     - Undo last mark")
                    print("  s     - Save progress")
                    print("  q     - Quit\n")
                
                else:
                    print(f" Unknown command: {command}\n")
                    
            except KeyboardInterrupt:
                print("\n\n Interrupted! Saving...")
                break
        
        # Final save
        if self.marks:
            self.save_marks()
            self.generate_subtitle_file()
        else:
            print("\n  No marks were created")
    
    def save_marks(self):
        """Save marks to JSON"""
        if not self.marks:
            print(" No marks to save!\n")
            return
        
        with open("timing_marks.json", 'w', encoding='utf-8') as f:
            json.dump(self.marks, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.marks)} marks to timing_marks.json\n")
    
    def generate_subtitle_file(self):
        """Generate subtitle file"""
        verses = [
            "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            "إِذَا السَّمَاءُ انفَطَرَتْ",
            "وَإِذَا الْكَوَاكِبُ انتَثَرَتْ",
            "وَإِذَا الْبِحَارُ فُجِّرَتْ",
            "وَإِذَا الْقُبُورُ بُعْثِرَتْ",
            "عَلِمَتْ نَفْسٌ مَّا قَدَّمَتْ وَأَخَّرَتْ",
            "يَا أَيُّهَا الْإِنسَانُ مَا غَرَّكَ بِرَبِّكَ الْكَرِيمِ",
            "الَّذِي خَلَقَكَ فَسَوَّاكَ فَعَدَلَكَ",
            "فِي أَيِّ صُورَةٍ مَّا شَاءَ رَكَّبَكَ",
            "كَلَّا بَلْ تُكَذِّبُونَن بِالدِّينِ",
            "وَإِنَّ عَلَيْكُمْ لَحَافِظِينَ",
            "كِرَامًا كَاتِبِينَ",
            "يَعْلَمُونَ مَا تَفْعَلُونَ",
            "إِنَّ الْأَبْرَارَ لَفِي نَعِيمٍ",
            "وَإِنَّ الْفُجَّارَ لَفِي جَحِيمٍ",
            "يَصْلَوْنَهَا يَوْمَ الدِّينِ",
            "وَمَا هُمْ عَنْهَا بِغَائِبِينَ",
            "وَمَا أَدْرَاكَ مَا يَوْمُ الدِّينِ",
            "ثُمَّ مَا أَدْرَاكَ مَا يَوْمُ الدِّينِ",
            "يَوْمَ لَا تَمْلِكُ نَفْسٌ لِّنَفْسٍ شَيْئًا ۖ وَالْأَمْرُ يَوْمَئِذٍ لِّلَّهِ"
        ]
        
        with open("subtitles.txt", 'w', encoding='utf-8') as f:
            f.write("# Surah Al-Infitar Subtitles\n")
            f.write("# Generated using Simple Timing Tool\n")
            f.write("# Format: start_time | end_time | Arabic text\n\n")
            
            for i, mark in enumerate(self.marks):
                if i < len(verses):
                    f.write(f"{mark['start']} | {mark['end']} | {verses[i]}\n")
        
        print("\n" + "="*70)
        print("UBTITLE FILE GENERATED!")
        print("="*70)
        print(f"\n File: subtitles.txt")
        print(f"   Verses completed: {min(len(self.marks), len(verses))}/{len(verses)}")
        
        
        print("\n Summary:")
        for i, mark in enumerate(self.marks[:5]): 
            verse_text = verses[i] if i < len(verses) else f"[Verse {i+1}]"
            print(f"   {i+1}. {format_time(mark['start'])} → {format_time(mark['end'])} | {verse_text[:30]}...")
        
        if len(self.marks) > 5:
            print(f"   ... and {len(self.marks) - 5} more")
        
 

def main():


    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("write video file path: ").strip('"\'')
    
    if not os.path.exists(video_path):
        print(f"\nVideo not found: {video_path}")
        return
    
    tool = SimpleTimingTool(video_path)
    tool.run()

if __name__ == "__main__":
    main()
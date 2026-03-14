import os
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# =========================
# Configurable Parameters
# =========================

slide_duration = 5
video_resolution = (1280, 720)
font_size = 40

# =========================
# Read Input Text File
# =========================

with open("input.txt", "r") as file:
    text = file.read()

# Error handling
if text.strip() == "":
    print("Error: Input file is empty")
    exit()

# Split text into scenes
scenes = text.split("\n")

clips = []

# =========================
# Generate Slides + Audio
# =========================

for i, scene in enumerate(scenes):

    if scene.strip() == "":
        continue

    # Generate Speech
    tts = gTTS(scene)
    audio_file = f"audio_{i}.mp3"
    tts.save(audio_file)

    # Create Slide Image
    img = Image.new("RGB", video_resolution, color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(scene, font=font)

    x = (video_resolution[0] - text_width) / 2
    y = (video_resolution[1] - text_height) / 2

    draw.text((x, y), scene, fill="white", font=font)

    image_file = f"slide_{i}.png"
    img.save(image_file)

    # Create Video Clip
    image_clip = ImageClip(image_file).set_duration(slide_duration)

    audio_clip = AudioFileClip(audio_file)

    video_clip = image_clip.set_audio(audio_clip)

    clips.append(video_clip)

# =========================
# Combine All Clips
# =========================

final_video = concatenate_videoclips(clips)

# Export Video
final_video.write_videofile("generated_video.mp4", fps=24)

print("Video generation completed!")
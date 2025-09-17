import time
import os
from google import genai
from google.genai import types

VIDEO_MODEL = "veo-3.0-fast-generate-001"

# Initialize Gemini client
client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.environ.get("GEMINI_API_KEY"),
)

# Video generation configuration
video_config = types.GenerateVideosConfig(
    aspect_ratio="9:16",
    number_of_videos=1,
    duration_seconds=8,
    person_generation="ALLOW_ALL",
    resolution="720p",
)

def generate_video(prompt: str):
    """
    Generate a video using VEO3 with the given prompt.
    Handles quota errors gracefully.
    """
    if not prompt:
        print("❌ No prompt provided. Please set VIDEO_PROMPT environment variable.")
        return

    try:
        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            prompt=prompt,
            config=video_config,
        )
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            print("❌ Quota exceeded. Please check your Gemini API plan and usage.")
            return
        else:
            raise

    # Wait for video(s) to be generated
    while not operation.done:
        print("🎥 Video is still generating... checking again in 10 seconds...")
        time.sleep(10)
        operation = client.operations.get(operation)

    result = operation.result
    if not result or not result.generated_videos:
        print("❌ No videos were generated.")
        return

    print(f"✅ Generated {len(result.generated_videos)} video(s).")
    for n, generated_video in enumerate(result.generated_videos):
        print(f"⬇️ Downloading video: {generated_video.video.uri}")
        client.files.download(file=generated_video.video)
        generated_video.video.save(f"video_{n}.mp4")
        print(f"💾 Saved: video_{n}.mp4")

def main():
    prompt = os.environ.get("VIDEO_PROMPT")
    generate_video(prompt)

if __name__ == "__main__":
    main()

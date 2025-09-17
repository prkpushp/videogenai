import time
import os
from google import genai
from google.genai import types

# Models
TEXT_MODEL = "gemini-1.5-flash"                # for generating prompt text
VIDEO_MODEL = "veo-3.0-fast-generate-001"      # for generating video

# Initialize Gemini client
client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.environ.get("GEMINI_API_KEY"),
)

# Video generation configuration
video_config = types.GenerateVideosConfig(
    aspect_ratio="9:16",        # Supported: "16:9", "16:10", "9:16"
    number_of_videos=1,         # Supported: 1 - 4
    duration_seconds=8,         # Supported: 5 - 8
    person_generation="ALLOW_ALL",
    resolution="720p",          # Options: "480p", "720p", "1080p"
)

def generate_dynamic_prompt():
    """
    Generate a safe romantic cinematic prompt using Gemini text model.
    """
    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents="""
        Write a JSON-style cinematic video prompt about a couple in their 30s.
        The scene should feel romantic, passionate, and sensual,
        but must avoid explicit sexual or adult content.
        Focus on emotions, atmosphere, closeness, and cinematic style.
        Include keys: title, style, camera, lighting, description.
        """
    )

    prompt = response.text.strip()
    print("🎬 Generated Prompt:\n", prompt)
    return prompt

def generate_video(prompt: str):
    """
    Generate a video using VEO3 with the given prompt.
    """
    operation = client.models.generate_videos(
        model=VIDEO_MODEL,
        prompt=prompt,
        config=video_config,
    )

    # Wait for video(s) to be generated
    while not operation.done:
        print("🎥 Video is still generating... checking again in 10 seconds...")
        time.sleep(10)
        operation = client.operations.get(operation)

    # Get results
    result = operation.result
    if not result:
        print("❌ Error: No result returned.")
        return

    generated_videos = result.generated_videos
    if not generated_videos:
        print("❌ Error: No videos generated.")
        return

    print(f"✅ Generated {len(generated_videos)} video(s).")

    # Save videos locally
    for n, generated_video in enumerate(generated_videos):
        print(f"⬇️ Downloading video: {generated_video.video.uri}")
        client.files.download(file=generated_video.video)
        generated_video.video.save(f"video_{n}.mp4")
        print(f"💾 Saved: video_{n}.mp4")

def main():
    prompt = generate_dynamic_prompt()
    generate_video(prompt)

if __name__ == "__main__":
    main()

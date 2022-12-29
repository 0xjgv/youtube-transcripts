from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from httpx import AsyncClient
from pathlib import Path
import asyncio
import os


load_dotenv()


async def get_channel_video_ids(channel_id: str) -> list[str]:
    # https://stackoverflow.com/questions/18953499/youtube-api-to-fetch-all-videos-on-a-channel
    upload_id = channel_id[:1] + "U" + channel_id[2:]
    print(f"Getting videos for {upload_id=} id from {channel_id=}")
    api_key = os.getenv("API_KEY")

    video_ids = []
    async with AsyncClient(
        base_url="https://www.googleapis.com/", headers={"Accept": "application/json"}
    ) as client:
        page_token = ""
        while 1:
            # https://developers.google.com/youtube/v3/docs/playlistItems/list
            res = await client.get(
                f"/youtube/v3/playlistItems?key={api_key}&playlistId={upload_id}&part=contentDetails&maxResults=50&pageToken={page_token}"
            )

            data = res.json()
            for item in data.get("items", []):
                info = item.get("contentDetails", {})
                video_ids.append(info.get("videoId", False))

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    return video_ids


def get_youtube_transcripts(video_ids: list[str], should_overwrite=False):
    transcripts_dir = Path("transcripts")
    transcripts_dir.mkdir(exist_ok=True)

    for video_id in video_ids:
        transcript_path = Path(transcripts_dir, video_id + ".txt")

        file_size = (transcript_path.exists() and transcript_path.stat().st_size) or 0
        if file_size > 0 and not should_overwrite:
            continue
        transcript_path.touch(exist_ok=True)

        try:
            responses = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US"])
            print(f"Video ID {video_id} proccessed")
            with transcript_path.open("a") as file:
                for response in responses:
                    file.write(response["text"] + "\n")

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # https://www.streamweasels.com/tools/youtube-channel-id-and-user-id-convertor/
    channel_id = "UC2D2CMWXMOVWx7giW1n3LIg"
    video_ids = asyncio.run(get_channel_video_ids(channel_id))

    transcripts = get_youtube_transcripts(video_ids)
    print("Done")

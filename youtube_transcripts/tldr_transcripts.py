from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


def read_transcripts():
    transcripts_dir = Path("./transcripts")

    for file in transcripts_dir.glob("*.txt"):
        print(file)


if __name__ == "__main__":
    read_transcripts()
    print("Done")

import asyncio
import shutil
import os
import re

from .utils import lang_codes

video_reg = re.compile(r"video\[\d+\]\[(?P<quality>\d+)p\]\[(?P<profile>[^\]]+)\]")
audio_subs_reg = re.compile(r"(audio|subtitles)\[\d+\]\[(?P<language>[^\]]+)\]\[(?P<id>[^\]]+)\]")

codecs = {
    "MAIN": "x264",
    "HIGH": "x264",
    "BASELINE": "x264",
    "HEVC": "H265",
    "HDR": "HDR.H265"
}

class Muxer:
    def __init__(self, folder, muxed):
        self.folder = folder
        self.muxed = muxed
        self.command = []

    async def run(self) -> dict:
        files = {
            "video": [],
            "audio": [],
            "subtitles": [],
        }
        data = {}
        for file in os.listdir(self.folder):
            for track in files.keys():
                if track not in file:
                    continue
                files[track].append(f"{self.folder}/{file}")
                
        for k in files.keys():
            if k == "video":
                for v in files[k]:
                    match = video_reg.search(v)
                    data["quality"] = match.group("quality")
                    data["codec"] = codecs.get(match.group("profile"))
                    self.command += [
                        "mkvmerge",
                        "--output",
                        self.muxed,
                        "(",
                        v,
                        ")",
                    ]
            if k == "audio":
                for v in files[k]:
                    match = audio_subs_reg.search(v)
                    language = lang_codes.get(match.group("id"))
                    self.command += [
                        "--language",
                        "0:"+language[1],
                        "--track-name",
                        "0:"+match.group("language"),
                        "--default-track",
                        "0:" + ("no" if "Description" in v else "yes"),
                        "(",
                        v,
                        ")",
                    ]
            if k == "subtitles":
                for v in files[k]:
                    match = audio_subs_reg.search(v)
                    language = lang_codes.get(match.group("id"))
                    self.command += [
                        "--language",
                        "0:"+language[1],
                        "--track-name",
                        "0:"+match.group("language"),
                        "--default-track",
                        "0:" + ("yes" if "Forced" in v else "no"),
                        "(",
                        v,
                        ")",
                    ]

        proc = await asyncio.create_subprocess_exec(
            *self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        shutil.rmtree(self.folder)
        return data

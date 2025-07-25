from __future__ import annotations

import copy
from datetime import datetime, timedelta
import operator
import os
from pathlib import Path
import re
import requests
import subprocess
from typing import Literal
from xml.etree import ElementTree as ET

from classes.tvdb import TVDB
from modules import regex
from modules import xml


class Guide:
    path: str = ""
    _tree: ET.ElementTree[ET.Element] | None = None
    tvdb: TVDB | None = None
    history: list[str] = []

    @property
    def tree(self) -> ET.ElementTree[ET.Element] | None:
        return self._tree

    @tree.setter
    def tree(self, tree: ET.ElementTree[ET.Element]):
        self._tree = tree

    @property
    def dir(self) -> str:
        return os.path.dirname(self.path)
    
    @property
    def filename(self) -> str:
        return Path(self.path).stem
    
    @property
    def channels(self) -> list[ET.Element]:
        if self.tree:
            return self.tree.getroot().findall(".//channel")
        else:
            return []
        
    @property
    def programmes(self) -> list[ET.Element]:
        if self.tree:
            return self.tree.getroot().findall(".//programme")
        else:
            return []

    def __init__(self):
        self.history = ["Created a new guide instance."]

    def of_tree(self, tree: ET.ElementTree[ET.Element]):
        self.history.append("Based on a tree instance.")
        self.path = ""
        self.tree = tree
        return self

    def of_path(self, path: str):
        self.history.append(f"Based on: \"{path}\".")
        self.path = path

        if os.path.isfile(path):
            self.tree = ET.parse(path)
        else:
            self.history.append("File does not exist yet, starting with empty guide.")
            
        return self
    
    def with_tvdb(self, key: str, cache_path: str | None = None):
        self.tvdb = TVDB(key).with_cache(cache_path)
        return self
    
    def exists(self):
        return os.path.isfile(self.path)
    
    def copy(self) -> "Guide":
        copy_guide = Guide()

        copy_guide.path = self.path
        copy_guide._tree = copy.deepcopy(self.tree)
        copy_guide.tvdb = self.tvdb
        copy_guide.history = self.history.copy()

        self.history.append("This guide was copied.")
        copy_guide.history.append("This guide is a copy.")

        return copy_guide
    
    def parse(self) -> "Guide":
        if not self.tree:
            raise Exception("This guide does not have a tree set. Make sure to populate it using one of its methods!")

        root = self.tree.getroot()
        programmes = root.findall(".//programme")
        dates_added = 0
        series_added = 0

        for programme in programmes:
            has_date = bool(programme.findtext("date"))
            start_time = programme.get("start", "")

            if start_time and not has_date:
                new_subtitle_tag = ET.SubElement(programme, "date")
                start_date = start_time[:8]

                new_subtitle_tag.text = start_date

                dates_added += 1

            has_episode = bool(programme.findtext("episode-num"))
            if self.tvdb and not has_episode:
                programme_title = programme.findtext("title")

                if programme_title:
                    show_name = programme_title
                    show_name = re.sub(r"(\s*\[[^\]]+\]\s*)?", "", show_name)
                    show_name = re.sub(r"(\s*т\/с\s*)?", "", show_name)
                    show_name = re.sub(r"(?:\s*[\.\-:]?\s*ep\.?\s*\d+|\s+\d+)?$", "", show_name)

                    episode_number = regex.find_first(r"(?!19[0-9]{2}$|[2-9][0-9]{3}$)[0-9]+$", programme_title)
                    
                    if show_name and episode_number:
                        show = next(iter(self.tvdb.search_series(show_name, country="kor")), None)

                        if show:
                            episodes = self.tvdb.get_episodes(str(show["tvdb_id"])) or []
                            episode = next((ep for ep in episodes if int(ep["number"]) == int(episode_number)), None)

                            if episode:
                                has_subtitle = bool(programme.findtext("sub-title"))

                                if not has_subtitle:
                                    new_subtitle_tag = ET.SubElement(programme, "sub-title")
                                    new_subtitle_tag.text = show_name

                                new_episode_tag = ET.SubElement(programme, "episode-num")
                                new_episode_tag.text = f"S{episode['seasonNumber']}E{episode['number']}"

                                series_added += 1

        self.history.append(f"{dates_added} separate date tags added.")
        self.history.append(f"{series_added} series found and parsed.")

        return self
            
    def write(self, path: str | None = None):
        path = path if path is not None else self.path

        if not path:
            raise Exception("This guide does not have a path set. Make sure to pass a path with the write() function!")

        if not self.tree:
            raise Exception("This guide does not have a tree set. Make sure to populate it using one of its methods!")

        self.parse()

        self.tree.write(path, encoding="utf-8", xml_declaration=True)
        self.history.append(f"Wrote guide file to: \"{path}\".")

        return self
            
    def merge(self, b: "Guide", history_threshold: int | None = None) -> "Guide":
        if self.tree:
            self.merge_channels(b)
            self.merge_programmes(b, history_threshold)
        elif b.tree:
            self.tree = b.tree
            self.history.append("The guide to merge to was empty, data from guide to merge from will be used.")
        else:
            self.history.append("Both guides were empty, nothing was merged.")

        return self

    def merge_channels(self, b: "Guide") -> "Guide":
        if not self.tree:
            raise Exception("The guide to merge to does not have a tree set. Make sure to populate it using one of its methods!")
        if not b.tree:
            raise Exception("The guide to merge from does not have a tree set. Make sure to populate it using one of its methods!")

        a_root = self.tree.getroot()
        b_root = b.tree.getroot()
        merged_root = ET.Element(
            "tv",
            source_info_name="EPGI",
            generator_info_name="kr_tv_grabber",
            generator_info_url="mailto:programmeertol@zomerplaag.nl")
        
        b_channels = b_root.findall(".//channel")
        channels: dict[str | None, ET.Element] = {}

        for el in a_root:
            if el.tag == "channel":
                # Add channel
                channels[el.get("id")] = el
            else:
                # Keep non-channel element
                merged_root.append(el)

        a_count = len(channels)
        self.history.append(f"Extracted {a_count} channels from the guide to merge to.")

        b_count = 0
        duplicate_count = 0
        for channel in b_channels:
            b_count += 1
            if channel.get("id") in channels:
                duplicate_count += 1

            # Add or overwrite channel
            channels[channel.get("id")] = channel

        self.history.append(f"Extracted {b_count} channels from the guide to merge from.")
        self.history.append(f"{duplicate_count} channels were overwritten because they already existed.")

        # Move channels to tree
        for channel in channels.values():
            merged_root.append(channel)

        self.tree = ET.ElementTree(merged_root)

        return self

    def merge_programmes(self, b: "Guide", history_threshold: int | None = None) -> "Guide":
        if not self.tree:
            raise Exception("The guide to merge to does not have a tree set. Make sure to populate it using one of its methods!")
        if not b.tree:
            raise Exception("The guide to merge from does not have a tree set. Make sure to populate it using one of its methods!")

        a_root = self.tree.getroot()
        b_root = b.tree.getroot()
        merged_root = ET.Element(
            "tv",
            source_info_name="EPGI",
            generator_info_name="kr_tv_grabber",
            generator_info_url="mailto:programmeertol@zomerplaag.nl")
        
        b_programmes = b_root.findall(".//programme")
        programmes: list[ET.Element] = []

        for b_programme in b_programmes:
            is_recent = xml.is_recent(b_programme, history_threshold, attribute="start") if history_threshold != None else True

            if is_recent:
                programmes.append(b_programme)

        b_count = len(programmes)
        self.history.append(f"Extracted {b_count} programmes from the guide to be merged from" + (f", at \"{b.path}\"." if b.path else "."))

        duplicate_count = 0
        old_count = 0

        for el in a_root:
            if el.tag == "programme":
                def is_duplicate_programme(element: ET.Element) -> bool:
                    return xml.is_duplicate(element, el, ["start", "stop", "channel"])

                is_recent = xml.is_recent(el, history_threshold, attribute="start") if history_threshold != None else True
                is_duplicate = xml.find_first(programmes, is_duplicate_programme) is not None

                if not is_recent:
                    old_count += 1

                if is_duplicate:
                    duplicate_count += 1
                
                if is_recent and not is_duplicate:
                    # Add programme
                    programmes.append(el)
            else:
                # Keep non-programme element
                merged_root.append(el)

        a_count = len(programmes) - b_count
        self.history.append(f"Extracted {a_count} programmes from the guide to merge to.")
        self.history.append(f"{old_count} programmes were skipped because they exceeded the history threshold of {history_threshold} days.")
        self.history.append(f"{duplicate_count} programmes were skipped because they already existed.")

        # Move programmes to tree
        for programme in programmes:
            merged_root.append(programme)

        self.tree = ET.ElementTree(merged_root)

        return self

    def grab(self, history_threshold: int, future_threshold: int) -> "Guide":
        plugin_guide_path = os.path.join(self.dir, f"{self.filename}.tmp")
        subprocess.run([
            "npx",
            "-y", "tv_grab_kr",
            "--days", f"{future_threshold}",
            "--output", plugin_guide_path
        ], check=True)
        plugin_guide = Guide().of_path(plugin_guide_path)

        self.history.append("Grabbed guides from tv_grab_kr plugin.")

        self.merge(plugin_guide, history_threshold)
        os.remove(plugin_guide_path)

        for day in range(-history_threshold, future_threshold + 1):
            date = datetime.now() + timedelta(days=day)
            date_str = date.strftime("%Y%m%d")

            url = f"https://epg.pw/api/epg.xml?lang=en&date={date_str}&channel_id=6530"
            response = requests.get(url)

            if response.status_code != 200:
                self.history.append(f"Failed to download additional guide from \"{url}\". Status code: {response.status_code}")
            else:
                self.history.append(f"Downloaded additional guide from \"{url}\".")

                additional_guide = Guide().of_tree(ET.ElementTree(ET.fromstring(response.content)))
                additional_guide.timeshift(["start", "stop"], "subtract", timedelta(days=1))

                self.history.append("Timeshifted programmes in additional guide by -1 day.")

                self.merge(additional_guide, history_threshold)

        return self
    
    def timeshift(
            self,
            attributes: list[str],
            operation: Literal["add", "subtract", "multiply", "divide", "mod", "power"],
            difference: timedelta
    ) -> "Guide":
        if not self.tree:
            raise Exception("This guide does not have a tree set. Make sure to populate it using one of its methods!")

        root = self.tree.getroot()

        for programme in root.findall(".//programme"):
            for attr in attributes:
                original_value = programme.get(attr)

                if original_value:
                    operations = {
                        "add": operator.add,
                        "subtract": operator.sub,
                        "multiply": operator.mul,
                        "divide": operator.truediv,
                        "mod": operator.mod,
                        "power": operator.pow
                    }

                    if operation not in operations:
                        raise ValueError(f"Unsupported operation: {operation}")

                    dt = operations[operation](datetime.strptime(original_value[:14], "%Y%m%d%H%M%S"), difference)

                    new_value = dt.strftime("%Y%m%d%H%M%S") + original_value[14:]
                    programme.set(attr, new_value)

        return self
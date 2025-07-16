from datetime import datetime, timedelta
import operator
import os
from pathlib import Path
import shutil
import subprocess
from typing import Literal
from urllib import request
from xml.etree import ElementTree as ET

from app.modules import xml


class Guide:
    path: str
    tree: ET.ElementTree[ET.Element[str]]
    history: list[str]

    @property
    def dir(self) -> str:
        return os.path.dirname(self.path)
    
    @property
    def filename(self) -> str:
        return Path(self.path).stem

    def __init__(self):
        self.history = ["Created a new guide instance."]

    def of(self, tree: ET.ElementTree[ET.Element[str]]):
        self.path = ""
        self.tree = tree
        self.history.append("Based on a tree instance.")
        return self

    def of(self, path: str):
        self.path = path
        self.tree = ET.parse(path)
        self.history.append(f"Based on: \"{self.path}\".")
        return self
    
    def exists(self):
        return os.path.isfile(self.path)
    
    def backup(self, limit: int) -> type["Guide"]:
        if not self.exists():
            raise Exception(f"Cannot backup a guide file that does not exist, at path: \"{self.path}\".")

        for i in range(1, limit + 1):
            max_number_width = len(str(limit))
            backup_file = os.path.join(self.dir, f"{self.filename}.bak{i:0{max_number_width}}")

            if not os.path.exists(backup_file):
                shutil.copyfile(self.path, backup_file)
                
                # Remove the next backup file if it exists
                next_backup = os.path.join(self.dir, f"{self.filename}.bak{(i % limit) + 1:0{max_number_width}}")
                if os.path.isfile(next_backup):
                    os.remove(next_backup)
                    self.history.append(f"The maximum backup count ({limit}) has been reached, \"{next_backup}\" has been removed.")

                return Guide().of(backup_file)
            
    def write(self):
        if not self.exists():
            raise Exception(f"Cannot write to a guide file that does not exist, at path: \"{self.path}\".")
        
        self.tree.write(self.path, encoding="utf-8", xml_declaration=True)
        self.history.append(f"Wrote guide file to: \"{self.path}\".")
        return self
            
    def merge(self, b: type["Guide"], history_threshold: int = None):
        a_root = self.tree.getroot()
        b_root = b.tree.getroot()
        merged_root = ET.Element(
            "tv",
            source_info_name="EPGI",
            generator_info_name="kr_tv_grabber",
            generator_info_url="mailto:programmeertol@zomerplaag.nl")
        
        channels = merge_channels(b_root, a_root)
        programmes = merge_programmes(b_root, a_root, history_threshold)

        for channel in channels:
            merged_root.append(channel)

        for programme in programmes:
            merged_root.append(programme)

        self.tree = ET.ElementTree(merged_root)

        def merge_channels(old_root: ET.Element, new_root: ET.Element) -> list[ET.Element]:
            channels: dict[str | None, ET.Element] = {}

            new_channels = new_root.findall(".//channel")
            old_channels = old_root.findall(".//channel")

            for channel in new_channels:
                channels[channel.get("id")] = channel

            new_channel_count = len(channels)
            self.history.append(f"Extracted {new_channel_count} channels from the new guide")

            for channel in old_channels:
                channels[channel.get("id")] = channel

            old_channel_count = len(channels) - new_channel_count
            self.history.append(f"Extracted {old_channel_count} channels from the old guide")

            return list(channels.values())

        def merge_programmes(old_root: ET.Element, new_root: ET.Element, history_threshold: int = None) -> list[ET.Element]:
            programmes: list[ET.Element] = []

            new_programmes = new_root.findall(".//programme")
            old_programmes = old_root.findall(".//programme")

            for new_programme in new_programmes:
                add_date(new_programme)
                programmes.append(new_programme)

            new_count = len(programmes)
            
            self.history.append(f"Extracted {new_count} programmes from the new guide")

            duplicate_count = 0
            old_count = 0

            for old_programme in old_programmes:
                add_date(old_programme)

                def is_duplicate_programme(element: ET.Element) -> bool:
                    return xml.is_duplicate(element, old_programme, ["start", "stop", "channel"])

                is_recent = xml.is_recent(old_programme, history_threshold, attribute="start") if history_threshold != None else True
                is_duplicate = xml.find_first(programmes, is_duplicate_programme) is not None

                if not is_recent:
                    old_count += 1

                if is_duplicate:
                    duplicate_count += 1
                
                if is_recent and not is_duplicate:
                    programmes.append(old_programme)

            old_programme_count = len(programmes) - new_count

            self.history.append(f"Extracted {old_programme_count} programmes from the old guide")
            self.history.append(f"{old_count} programmes were skipped because they exceeded the history threshold of {history_threshold} days")
            self.history.append(f"{duplicate_count} programmes were skipped because they already existed")

            return programmes
        
        def add_date(programme: ET.Element):
            has_date = bool(programme.findtext("date"))
            start_time = programme.get("start", "")

            if start_time and not has_date:
                new_date_tag = ET.SubElement(programme, "date")
                start_date = start_time[:8]

                new_date_tag.text = start_date

    def grab(self, history_threshold: int, future_threshold: int) -> type["Guide"]:
        plugin_guide_path = os.path.join(self.dir, f"{self.filename}.tmp")
        subprocess.run([
            "npx",
            "-y", "tv_grab_kr",
            "--days", f"{future_threshold}",
            "--output", plugin_guide_path
        ], check=True)
        plugin_guide = Guide().of(plugin_guide_path)

        self.history.append("Grabbed guides from tv_grab_kr plugin.")

        self.merge(plugin_guide, history_threshold)

        for day in range(-history_threshold, future_threshold + 1):
            date = datetime.now() + timedelta(days=day)
            date_str = date.strftime("%Y%m%d")

            url = f"https://epg.pw/api/epg.xml?lang=en&date={date_str}&channel_id=6530"
            response = request.get(url)

            if response.status_code != 200:
                self.history.append(f"Failed to download additional guide from \"{url}\". Status code: {response.status_code}")
            else:
                self.history.append(f"Downloaded additional guide from \"{url}\".")

                additional_guide = Guide().of(ET.fromstring(response.content))
                additional_guide.timeshift(["start", "stop"], "subtract", timedelta(days=1))

                self.history.append("Timeshifted programmes in additional guide by -1 day.")

                self.merge(additional_guide, history_threshold)

        return self
    
    def timeshift(
            self,
            attributes: list[str],
            operation: Literal["add", "subtract", "multiply", "divide", "mod", "power"],
            difference: timedelta
    ) -> type["Guide"]:
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
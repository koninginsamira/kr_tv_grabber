from datetime import datetime, timedelta
import operator
import os
import subprocess
from typing import Literal
from xml.etree import ElementTree as ET

import requests

import modules.xml as xml


def grab(destination_file: str, history_threshold: int = 3, future_threshold: int = 3):
    subprocess.run(["npx", "-y", "tv_grab_kr", "--days", f"{future_threshold}", "--output", destination_file + "1"], check=True)

    print("Grabbed guides from tv_grab_kr plugin.")

    # kbs_world_url = "https://epg.pw/api/epg.xml?lang=en&channel_id=12015" # Philippines
    kbs_world_url = "https://epg.pw/api/epg.xml?lang=en&channel_id=6530" # Russian Federation
    response = requests.get(kbs_world_url)

    if response.status_code != 200:
        print(f"Failed to download additional guide from \"{kbs_world_url}\". Status code: {response.status_code}")
    else:
        print(f"Downloaded additional guide from \"{kbs_world_url}\".")

        kbs_world_guide = ET.fromstring(response.content)

        kbs_world_guide = timeshift(kbs_world_guide, ["start", "stop"], "subtract", timedelta(days=1))
        kbs_world_guide = timeshift(kbs_world_guide, ["start", "stop"], "add", timedelta(hours=2))

        ET.ElementTree(kbs_world_guide).write(destination_file + "2", encoding="utf-8", xml_declaration=True)

        print("Timeshifted programmes in additional guide by -1 day and +2 hours")

    merge(destination_file + "1", destination_file + "2", destination_file, history_threshold)

    print(f"Merged new guides into one file: \"{destination_file}\"")

    os.remove(destination_file + "1")
    os.remove(destination_file + "2")


def timeshift(
    source: ET.Element, attributes: list[str],
    operation: Literal["add", "subtract", "multiply", "divide", "mod", "power"],
    difference: timedelta
) -> ET.Element:
    for programme in source.findall(".//programme"):
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

    return source


def merge(old_guide_file: str, new_guide_file: str, target_file: str = "", history_threshold: int = 3):
    target_file = target_file if target_file else new_guide_file

    print(f"Merging old guide ('{old_guide_file}') with new guide ('{new_guide_file}')...")

    old_tree = ET.parse(old_guide_file)
    old_root = old_tree.getroot()
    new_tree = ET.parse(new_guide_file)
    new_root = new_tree.getroot()
    merged_root = ET.Element(
        "tv",
        source_info_name="EPGI",
        generator_info_name="kr_tv_grabber",
        generator_info_url="mailto:programmeertol@zomerplaag.nl")
    
    channels = merge_channels(old_root, new_root)
    programmes = merge_programmes(old_root, new_root, history_threshold)

    append(merged_root, channels, programmes)
    write(target_file, merged_root)

    print(f"Merged guides to '{target_file}'")


def write(target_file: str, merged_root: ET.Element):
    tree = ET.ElementTree(merged_root)
    tree.write(target_file, encoding='utf-8', xml_declaration=True)


def append(merged_root: ET.Element, channels: list[ET.Element], programmes: list[ET.Element]):
    for channel in channels:
        merged_root.append(channel)

    for programme in programmes:
        merged_root.append(programme)


def merge_channels(old_root: ET.Element, new_root: ET.Element) -> list[ET.Element]:
    channels: dict[str | None, ET.Element] = {}

    new_channels = new_root.findall(".//channel")
    old_channels = old_root.findall(".//channel")

    for channel in new_channels:
        channels[channel.get("id")] = channel

    new_channel_count = len(channels)
    print(f"Extracted {new_channel_count} channels from the new guide")

    for channel in old_channels:
        channels[channel.get("id")] = channel

    old_channel_count = len(channels) - new_channel_count
    print(f"Extracted {old_channel_count} channels from the old guide")

    return list(channels.values())


def merge_programmes(old_root: ET.Element, new_root: ET.Element, history_threshold: int = 3) -> list[ET.Element]:
    programmes: list[ET.Element] = []

    new_programmes = new_root.findall(".//programme")
    old_programmes = old_root.findall(".//programme")

    for new_programme in new_programmes:
        add_date(new_programme)
        programmes.append(new_programme)

    new_count = len(programmes)
    
    print(f"Extracted {new_count} programmes from the new guide")

    duplicate_count = 0
    old_count = 0

    for old_programme in old_programmes:
        add_date(old_programme)

        def is_duplicate_programme(element: ET.Element) -> bool:
            return xml.is_duplicate(element, old_programme, ["start", "stop", "channel"])

        is_recent = xml.is_recent(old_programme, history_threshold, attribute="start")
        is_duplicate = xml.find_first(programmes, is_duplicate_programme) is not None

        if not is_recent:
            old_count += 1

        if is_duplicate:
            duplicate_count += 1
        
        if is_recent and not is_duplicate:
            programmes.append(old_programme)

    old_programme_count = len(programmes) - new_count

    print(f"Extracted {old_programme_count} programmes from the old guide")
    print(f"{old_count} programmes were skipped because they exceeded the history threshold of {history_threshold} days")
    print(f"{duplicate_count} programmes were skipped because they already existed")

    return programmes


def add_date(programme: ET.Element):
    has_date = bool(programme.findtext("date"))
    start_time = programme.get("start", "")

    if start_time and not has_date:
        new_date_tag = ET.SubElement(programme, "date")
        start_date = start_time[:8]

        new_date_tag.text = start_date
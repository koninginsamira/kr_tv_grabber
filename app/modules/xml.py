from datetime import datetime, timezone
from typing import Callable
from xml.etree.ElementTree import Element


def find_first(
        elements: list[Element],
        match: Callable[[Element], bool]) -> Element | None:
    for current_element in elements:
        if match(current_element):
            return current_element
    return None


def find(
        elements: list[Element],
        match: Callable[[Element], bool]) -> list[Element]:
    matches = []

    for current_element in elements:
        if match(current_element):
            matches.append(current_element)
        
    return matches


def is_duplicate(
        element1: Element, element2: Element,
        attributes: list[str] = [], tags: list[str] = []) -> bool:
    for attribute_name in attributes:
        attribute1 = element1.get(attribute_name)
        attribute2 = element2.get(attribute_name)

        if attribute1 != attribute2:
            return False
    
    for tag_name in tags:
        tag1 = element1.findtext(tag_name)
        tag2 = element2.findtext(tag_name)

        if tag1 != tag2:
            return False
    
    return True


def is_recent(
        element: Element, max_age_days: int,
        timestamp_format: str = "%Y%m%d%H%M%S %z",
        attribute: str = "", tag: str = "") -> bool:
    element_time_str = ""

    if attribute:
        element_time_str = element.get(attribute)
    elif tag:
        element_time_str = element.find(tag).text
    else:
        raise Exception(
            "To check if an element is recent, it needs to look for either an attribute or a tag with a date. Neither was given")

    element_time = datetime.strptime(element_time_str, timestamp_format)
    current_time = datetime.now(tz=timezone.utc)

    element_age = current_time - element_time

    result = element_age.days <= max_age_days
    return result
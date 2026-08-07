"""Utilities for navigating the Spanish cadastre ATOM feeds."""

from __future__ import annotations

import unicodedata
import re
from dataclasses import dataclass
from typing import Iterable
from xml.etree import ElementTree as ET

import requests

ATOM_ROOTS = {
    "cp": "https://www.catastro.hacienda.gob.es/INSPIRE/CadastralParcels/ES.SDGC.CP.atom.xml",
    "ad": "https://www.catastro.hacienda.gob.es/INSPIRE/Addresses/ES.SDGC.AD.atom.xml",
    "bu": "https://www.catastro.hacienda.gob.es/INSPIRE/Buildings/ES.SDGC.BU.atom.xml",
}
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass(frozen=True)
class AtomEntry:
    title: str
    href: str


class AtomService:
    """Read and filter ATOM feed entries."""

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    def get_root_feed(self, dataset: str = "cp") -> str:
        root_url = self.get_root_url(dataset)
        response = self.session.get(root_url, timeout=30)
        response.raise_for_status()
        return response.text

    def get_root_url(self, dataset: str = "cp") -> str:
        dataset_key = self.normalize_dataset(dataset)
        if dataset_key not in ATOM_ROOTS:
            raise LookupError(f"Dataset no soportado: {dataset}")
        return ATOM_ROOTS[dataset_key]

    def parse_feed(self, xml: str) -> list[AtomEntry]:
        root = ET.fromstring(xml)
        entries: list[AtomEntry] = []

        for entry in root.findall("atom:entry", ATOM_NS):
            title = entry.findtext("atom:title", default="", namespaces=ATOM_NS)
            link = entry.find("atom:link", ATOM_NS)
            href = link.attrib.get("href", "") if link is not None else ""
            entries.append(AtomEntry(title=title.strip(), href=href.strip()))

        return entries

    def parse_root_feed(self, dataset: str = "cp") -> list[AtomEntry]:
        return self.parse_feed(self.get_root_feed(dataset))

    def list_root(self, dataset: str = "cp") -> list[AtomEntry]:
        return self.parse_root_feed(dataset)

    def normalize_dataset(self, dataset: str) -> str:
        return str(dataset).strip().lower()

    def normalize_region_code(self, region_code: str) -> str:
        return str(region_code).strip().zfill(2)

    def normalize_municipality_code(self, municipality_code: str) -> str:
        return str(municipality_code).strip().zfill(5)

    def normalize_text(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", str(value))
        without_accents = normalized.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"\s+", " ", without_accents).strip().lower()

    def entry_matches_query(self, entry: AtomEntry, query: str) -> bool:
        normalized_query = self.normalize_text(query)
        haystack = self.normalize_text(f"{entry.title} {entry.href}")
        return normalized_query in haystack

    def find_region_entry(self, region_query: str, dataset: str = "cp") -> AtomEntry:
        normalized_region_code = self.normalize_region_code(region_query)
        normalized_region_query = self.normalize_text(region_query)
        root_entries = self.parse_root_feed(dataset)

        for entry in root_entries:
            if normalized_region_code in entry.href:
                return entry
            if normalized_region_code in entry.title:
                return entry
            if self.entry_matches_query(entry, normalized_region_query):
                return entry

        raise LookupError(f"No se encontró la región {region_query} en el feed raíz del dataset {dataset}.")

    def get_region_feed(self, region_query: str, dataset: str = "cp") -> str:
        region_entry = self.find_region_entry(region_query, dataset)
        response = self.session.get(region_entry.href, timeout=30)
        response.raise_for_status()
        return response.text

    def parse_region_feed(self, region_query: str, dataset: str = "cp") -> list[AtomEntry]:
        return self.parse_feed(self.get_region_feed(region_query, dataset))

    def list_region(self, region_query: str, dataset: str = "cp") -> list[AtomEntry]:
        return self.parse_region_feed(region_query, dataset)

    def find_municipality_entry(self, region_query: str, municipality_query: str, dataset: str = "cp") -> AtomEntry:
        normalized_municipality_code = self.normalize_municipality_code(municipality_query)
        normalized_municipality_query = self.normalize_text(municipality_query)
        region_entries = self.parse_region_feed(region_query, dataset)

        for entry in region_entries:
            if normalized_municipality_code in entry.href:
                return entry
            if normalized_municipality_code in entry.title:
                return entry
            if self.entry_matches_query(entry, normalized_municipality_query):
                return entry

        raise LookupError(
            f"No se encontró el municipio {municipality_query} en la región {region_query}."
        )

    def list_municipality(self, region_query: str, municipality_query: str, dataset: str = "cp") -> list[AtomEntry]:
        municipality_entry = self.find_municipality_entry(region_query, municipality_query, dataset)
        return [municipality_entry]

    def get_municipality_download_url(self, region_query: str, municipality_query: str, dataset: str = "cp") -> str:
        municipality_entry = self.find_municipality_entry(region_query, municipality_query, dataset)
        return municipality_entry.href

    def municipality_name_from_entry(self, entry: AtomEntry) -> str:
        title = self.normalize_text(entry.title)
        title = title.replace("addresses ad sdgc", "")
        title = title.replace("buildings bu sdgc", "")
        title = title.replace("cadastral parcels cp sdgc", "")
        title = title.strip()
        if "-" in title:
            title = title.split("-", 1)[1].strip()
        return title.upper()

    def municipality_name_from_query(self, municipality_query: str) -> str:
        normalized = self.normalize_text(municipality_query)
        if normalized.isdigit():
            return normalized
        return normalized.upper()

    def build_download_filename(self, municipality_entry: AtomEntry, dataset: str = "cp") -> str:
        dataset_key = self.normalize_dataset(dataset)
        municipality_name = self.municipality_name_from_entry(municipality_entry)
        municipality_code_match = re.search(r"(\d{5})", municipality_entry.title or municipality_entry.href)
        municipality_code = municipality_code_match.group(1) if municipality_code_match else "00000"
        return f"{municipality_code}-{municipality_name}-{dataset_key}.zip"

    def filter_entries(self, entries: Iterable[AtomEntry], needle: str) -> list[AtomEntry]:
        pattern = re.compile(re.escape(str(needle)), re.IGNORECASE)
        return [entry for entry in entries if pattern.search(entry.title) or pattern.search(entry.href)]

    def find_region(self, region_query: str, dataset: str = "cp") -> list[AtomEntry]:
        return self.list_region(region_query, dataset)

    def find_municipality(self, region_query: str, municipality_query: str, dataset: str = "cp") -> list[AtomEntry]:
        return self.list_municipality(region_query, municipality_query, dataset)

    def find_downloads(self, region_query: str, municipality_query: str, dataset: str = "cp") -> list[AtomEntry]:
        municipality_entry = self.find_municipality_entry(region_query, municipality_query, dataset)
        return [municipality_entry]

    def find_all_downloads(self, region_query: str, municipality_query: str) -> list[tuple[str, AtomEntry]]:
        downloads = []
        for dataset in ("cp", "ad", "bu"):
            downloads.append((dataset, self.find_municipality_entry(region_query, municipality_query, dataset)))
        return downloads

    def as_dicts(self, entries: Iterable[AtomEntry]) -> list[dict[str, str]]:
        return [{"title": entry.title, "href": entry.href} for entry in entries]
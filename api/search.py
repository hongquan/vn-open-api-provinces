import re
from typing import Any, Protocol, cast

from logbook import Logger
from lunr import lunr
from lunr.index import Index
from unidecode import unidecode

from .schema_v1 import DivisionLevel, SearchResult
from .vendor.vietnam_provinces.base import District, Province, Ward
from .vendor.vietnam_provinces.enums.districts import DistrictEnum, ProvinceEnum
from .vendor.vietnam_provinces.enums.wards import WardEnum


logger = Logger(__name__)


class BaseRegion(Protocol):
    code: int
    name: str


def to_search_doc(obj: BaseRegion):
    doc = {'code': obj.code, 'name': obj.name}
    doc['stripped_name'] = unidecode(obj.name)
    return doc


class Searcher:
    ready = False
    province_index: Index | None = None
    district_index: Index | None = None
    ward_index: Index | None = None

    def build_index(self):
        self.province_index = lunr(
            ref='code', fields=('name', 'stripped_name'), documents=tuple(to_search_doc(p.value) for p in ProvinceEnum)
        )
        self.district_index = lunr(
            ref='code', fields=('name', 'stripped_name'), documents=tuple(to_search_doc(p.value) for p in DistrictEnum)
        )
        self.ward_index = lunr(
            ref='code', fields=('name', 'stripped_name'), documents=tuple(to_search_doc(p.value) for p in WardEnum)
        )
        self.ready = True

    def search(
        self,
        query: str,
        level: DivisionLevel = DivisionLevel.P,
        district_code: int | None = None,
        province_code: int | None = None,
    ) -> tuple[SearchResult, ...]:
        if not self.ready:
            logger.warning('Index building does not finished yet!')
            return ()
        if level == DivisionLevel.P:
            lresults: tuple[dict[str, Any], ...] = self.province_index.search(query) if self.province_index else ()
        elif level == DivisionLevel.D:
            lresults = self.district_index.search(query) if self.district_index else ()
        else:
            lresults = self.ward_index.search(query) if self.ward_index else ()
        if not lresults:
            return ()
        # Lunrpy sometimes returns duplicate-like results
        # (same ref but different matches and scores). We will combine those.
        dresults: dict[int, SearchResult] = {}
        for r in lresults:
            code = int(r['ref'])
            for term, fields in r['match_data'].metadata.items():
                if level == DivisionLevel.P:
                    obj: Province | District | Ward = ProvinceEnum[f'P_{code}'].value
                elif level == DivisionLevel.D:
                    obj = DistrictEnum[f'D_{code}'].value
                    if province_code and obj.province_code != province_code:
                        continue
                else:
                    obj = cast(Ward, WardEnum[f'W_{code}'].value)  # type: ignore[misc]
                    if district_code and obj.district_code != district_code:
                        continue
                    elif province_code:
                        dist: District = DistrictEnum[f'D_{obj.district_code}'].value
                        if dist.province_code != province_code:
                            continue
                # Find position of matched keyword, to help highlighting
                matches = {}
                try:
                    matches[term] = locate(obj.name, term)
                except ValueError:
                    # There is a case, where keyword is "lai" but search engine returns "Mường Lay"
                    continue
                try:
                    dresults[code].matches.update(matches)
                except KeyError:
                    dresults[code] = SearchResult(code=code, name=obj.name, matches=matches)
        return tuple(dresults.values())

    def search_province(self, query: str):
        return self.search(query, DivisionLevel.P)

    def search_district(self, query: str, province_code: int | None = None):
        return self.search(query, DivisionLevel.D, province_code=province_code)

    def search_ward(self, query: str, district_code: int | None = None, province_code: int | None = None):
        return self.search(query, DivisionLevel.W, district_code, province_code)


def locate(name: str, term: str):
    name = unidecode(name).lower()
    term = unidecode(term).lower()
    m = re.search(rf'\b{term}\b', name)
    if not m:
        raise ValueError
    return (m.start(0), m.end(0))


repo = Searcher()

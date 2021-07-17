import re
from collections import deque
from typing import Optional, Dict, Union, Tuple, List, Any

from lunr import lunr
from lunr.index import Index
from logbook import Logger
from unidecode import unidecode
from vietnam_provinces import Province, District, Ward
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum
from vietnam_provinces.enums.wards import WardEnum

from .schema import DivisionLevel, SearchResult


logger = Logger(__name__)


def to_search_doc(obj: Union[Province, District, Ward]):
    doc = {
        'code': obj.code,
        'name': obj.name
    }
    doc['stripped_name'] = unidecode(doc['name'])
    return doc


class Searcher:
    ready = False
    province_index: Optional[Index] = None
    district_index: Optional[Index] = None
    ward_index: Optional[Index] = None

    def build_index(self):
        self.province_index = lunr(ref='code', fields=('name', 'stripped_name'),
                                   documents=tuple(to_search_doc(p.value) for p in ProvinceEnum))
        self.district_index = lunr(ref='code', fields=('name', 'stripped_name'),
                                   documents=tuple(to_search_doc(p.value) for p in DistrictEnum))
        self.ward_index = lunr(ref='code', fields=('name', 'stripped_name'),
                               documents=tuple(to_search_doc(p.value) for p in WardEnum))
        self.ready = True

    def search(self, query: str, level: DivisionLevel = DivisionLevel.P,
               district_code: Optional[int] = None,
               province_code: Optional[int] = None) -> Tuple[SearchResult, ...]:
        if not self.ready:
            logger.warning('Index building does not finished yet!')
            return []
        if level == DivisionLevel.P:
            lresults: List[Dict[str, Any]] = self.province_index.search(query)
        elif level == DivisionLevel.D:
            lresults: List[Dict[str, Any]] = self.district_index.search(query)
        else:
            lresults: List[Dict[str, Any]] = self.ward_index.search(query)
        if not lresults:
            return []
        results = deque()
        for r in lresults:
            code = int(r['ref'])
            for term, fields in r['match_data'].metadata.items():
                if level == DivisionLevel.P:
                    obj: Province = ProvinceEnum[f'P_{code}'].value
                elif level == DivisionLevel.D:
                    obj: District = DistrictEnum[f'D_{code}'].value
                    if province_code and obj.province_code != province_code:
                        continue
                else:
                    obj: Ward = WardEnum[f'W_{code}'].value
                    if district_code and obj.district_code != district_code:
                        continue
                    elif province_code:
                        dist: District = DistrictEnum[f'D_{obj.district_code}'].value
                        if dist.province_code != province_code:
                            continue
                # Find position of matched keyword, to help highlighting
                matches = {}
                matches[term] = locate(obj.name, term)
                result = SearchResult(code=code, name=obj.name, matches=matches, score=r['score'])
                results.append(result)

        return tuple(results)

    def search_province(self, query: str):
        return self.search(query, DivisionLevel.P)

    def search_district(self, query: str, province_code: Optional[int] = None):
        return self.search(query, DivisionLevel.D, province_code=province_code)

    def search_ward(self, query: str, district_code: Optional[int] = None, province_code: Optional[int] = None):
        return self.search(query, DivisionLevel.W, district_code, province_code)


def locate(name: str, term: str):
    name = unidecode(name).lower()
    term = unidecode(term).lower()
    m = re.search(rf'\b{term}\b', name)
    if not m:
        raise ValueError
    return (m.start(0), m.end(0))

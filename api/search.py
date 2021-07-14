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

    def search(self, query: str, level: DivisionLevel = DivisionLevel.P) -> Tuple[SearchResult, ...]:
        if not self.ready:
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
                else:
                    obj: Ward = WardEnum[f'W_{code}'].value
                # Find position of matched keyword, to help highlighting
                start = unidecode(obj.name).lower().index(unidecode(term).lower())
                matches = {}
                matches[term] = (start, start + len(term))
                result = SearchResult(code=code, name=obj.name, matches=matches, score=r['score'])
                results.append(result)
        return tuple(results)

    def search_province(self, query: str):
        return self.search(query, DivisionLevel.P)

    def search_district(self, query: str):
        return self.search(query, DivisionLevel.D)

    def search_ward(self, query: str):
        return self.search(query, DivisionLevel.W)

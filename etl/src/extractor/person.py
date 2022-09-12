import dataclasses as dtc
import logging
from typing import Set, Generator, DefaultDict
from collections import defaultdict

from config import CONFIG
from state import PERSON_STATE
from .base import BasePGExtractor


logger = logging.getLogger(__name__)


def get_roles_structure() -> DefaultDict[str, Set]:
    return defaultdict(set)


@dtc.dataclass(init=True)
class PersonRecord:
    person_id: str
    full_name: str

    film_work_id: dtc.InitVar[str]
    role_name: dtc.InitVar[str]

    roles: defaultdict[str, Set[str]] = dtc.field(default_factory=get_roles_structure)

    def __post_init__(
            self,
            film_work_id: str,
            role_name: str,
    ):
        # self.roles = defaultdict(set)
        self.roles[role_name].add(film_work_id)


class PersonExtractor(BasePGExtractor):
    schema = CONFIG.extraction_schema.person
    state = PERSON_STATE
    name = 'person'

    def __init__(self, connection):
        super().__init__(connection, self.schema, self.state)

    @staticmethod
    def group_extracted(queryset: Generator) -> Generator[PersonRecord, None, int]:
        data_dict = {}
        for record in queryset:
            role_name = record.role_name
            if record.person_id in data_dict:
                person_record = data_dict[record.person_id]
                roles = person_record.roles
                roles[role_name].add(record.film_work_id)
            else:
                record_dict = record._asdict()
                data_dict[record.person_id] = PersonRecord(**record_dict)

        for record in data_dict.values():
            yield record

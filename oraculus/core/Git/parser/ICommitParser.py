from abc import ABC, abstractmethod
from typing import List, Any

from oraculus.core.metrics import CommitData

class ICommitParser(ABC):

    @abstractmethod
    def parse_to_commit_data_list(self, raw_data:Any)->List[CommitData]:
        pass
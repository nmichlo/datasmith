from typing import Iterable
from typing import Optional

from datasmith import Annotation
from datasmith import DatasetItem

from datasmith._util import repr_truelike_kwargs_no_uid


# ========================================================================= #
# Bounding Box Object                                                       #
# ========================================================================= #


class DatasetItemPath(DatasetItem):

    def __init__(
        self,
        path: str,
        annotations: Optional[Iterable[Annotation]] = None,
        labels: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        uid: Optional[str] = None,
    ):
        super().__init__(
            annotations=annotations,
            labels=labels,
            tags=tags,
            uid=uid,
        )
        self.path = path

    def __repr__(self):
        return repr_truelike_kwargs_no_uid(self, path=self.path, annotations=list(self.annotations), labels=self.labels, tags=self.tags, uid=self.uid)



# ========================================================================= #
# Bounding Box Object                                                       #
# ========================================================================= #

import uuid
from abc import ABCMeta
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union


from datasmith._util import repr_truelike_kwargs_no_uid


# ========================================================================= #
# Base unique ID object                                                     #
# ========================================================================= #


class _UidObj(object):

    def __init__(
        self,
        labels: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        uid: Optional[str] = None,
    ):
        self._labels: Tuple[str, ...] = ()                if (labels is None) else tuple(set(labels))
        self._tags: Tuple[str, ...]   = ()                if (tags   is None) else tuple(set(tags))
        self._uid: str                = str(uuid.uuid4()) if (uid    is None) else uid
        # validate
        if not isinstance(self._uid, str):
            raise TypeError(f'uid must be of type str, got type: {type(uid)}, for: {repr(uid)}')
        if any(not isinstance(tag, str) for tag in self._tags):
            raise TypeError(f'tags must all be of type str, got: {repr(self._tags)}')
        if any(not isinstance(label, str) for label in self._labels):
            raise TypeError(f'labels must all be of type str, got: {repr(self._labels)}')

    @property
    def uid(self) -> str:
        return self._uid

    # TODO: make these mutable!
    # TODO: make these mutable!
    # TODO: make these mutable!

    @property
    def labels(self) -> Tuple[str, ...]:
        return self._labels

    @property
    def tags(self) -> Tuple[str, ...]:
        return self._tags

    def __repr__(self):
        return repr_truelike_kwargs_no_uid(self, labels=self.labels, tags=self.tags, uid=self.uid)


# ========================================================================= #
# Base Unique ID List                                                       #
# ========================================================================= #


T = TypeVar('T')

# types
UidIdx = Union[int, str, _UidObj]
UidMultiIdx = Union[slice, List[UidIdx]]


class _UidList(Generic[T], metaclass=ABCMeta):

    # must implement these
    ITEM_TYPE: Type[T]
    ITEM_NAME: str
    PARENT_NAME: str

    def __init__(self, items: Optional[Iterable[T]]):
        # storage
        self._item_uids: Dict[str, T] = {}
        self._item_objs: List[T] = []
        # add items
        if items is not None:
            self.extend(items)

    # --- iterators --- #

    def __len__(self):
        return len(self._item_uids)

    def __iter__(self) -> Iterator[T]:
        yield from self._item_objs

    # --- parent / children --- #  TODO: move this logic into its own class so that it can be used for annotations too!

    def append(self, item: T) -> NoReturn:
        # validate the item, making sure the type is correct and UID does not already exist
        if not isinstance(item, self.ITEM_TYPE):
            raise TypeError(f'{self.ITEM_NAME} must be of type: {self.ITEM_TYPE.__name__}, but got type: {type(item)}, for: {repr(item)}')
        if item.uid in self._item_uids:
            raise KeyError(f'{self.ITEM_NAME} with id: {item.uid} already in {self.PARENT_NAME}')
        # add the item to the dataset
        self._item_uids[item.uid] = item
        self._item_objs.append(item)

    def extend(self, items: Iterable[T]) -> NoReturn:
        for item in items:
            self.append(item)

    def _get_single_item(self, uid: UidIdx):
        # support multiple indexing modes, including indexing and unique ids
        if isinstance(uid, int):
            return self._item_objs[uid]
        elif isinstance(uid, str):
            return self._item_uids[uid]
        elif isinstance(uid, self.ITEM_TYPE):
            return self._item_uids[uid.uid]
        else:
            raise TypeError(f'unsupported indexing type: {type(uid)}, for: {repr(uid)}')

    def __getitem__(self, uid: Union[UidIdx, UidMultiIdx]) -> Union[T, List[T]]:
        # support single or multiple indexing modes, including slicing and list indexing
        if isinstance(uid, list):
            return [self._get_single_item(i) for i in uid]
        elif isinstance(uid, slice):
            return self._item_objs[uid]
        else:
            return self._get_single_item(uid)

    def __contains__(self, uid: Union[str, T]) -> bool:
        # support indexing by unique id
        if isinstance(uid, str):
            return (uid in self._item_uids)
        elif isinstance(uid, self.ITEM_TYPE):
            return (uid.uid in self._item_uids)
        else:
            raise TypeError(f'unsupported contains type: {type(uid)}, for: {repr(uid)}')

    def __repr__(self):
        return repr_truelike_kwargs_no_uid(self, items='<hidden>')


# ========================================================================= #
# Dataset Annotation                                                        #
# ========================================================================= #


class AnnotationValue(object, metaclass=ABCMeta):
    pass


class Annotation(Generic[T], _UidObj):

    def __init__(
        self,
        value: T,
        labels: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        uid: Optional[str] = None,
    ):
        if not isinstance(value, AnnotationValue):
            raise TypeError(f'annotation value must be an instance of: {AnnotationValue.__name__}, got type: {type(value)}, for: {repr(value)}')
        # init
        super().__init__(labels=labels, tags=tags, uid=uid)
        # storage
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    def __repr__(self):
        return repr_truelike_kwargs_no_uid(self, value=self.value, labels=self.labels, tags=self.tags, uid=self.uid)



# ========================================================================= #
# Dataset Item                                                              #
# ========================================================================= #


class DatasetItem(_UidObj, metaclass=ABCMeta):

    class _AnnotationList(_UidList[Annotation]):
        ITEM_TYPE = Annotation
        ITEM_NAME = 'annotation'
        PARENT_NAME = 'item'

    def __init__(
        self,
        annotations: Optional[Iterable[Annotation]] = None,
        labels: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        uid: Optional[str] = None,
    ):
        super().__init__(labels=labels, tags=tags, uid=uid)
        # storage
        self._annotations = self._AnnotationList(annotations)

    @property
    def annotations(self) -> _AnnotationList:
        return self._annotations

    def __repr__(self):
        return repr_truelike_kwargs_no_uid(self, annotations=list(self.annotations), labels=self.labels, tags=self.tags, uid=self.uid)


# ========================================================================= #
# Dataset                                                                   #
# ========================================================================= #


class DatasetLabelNotFoundError(Exception):
    pass



class Dataset(_UidObj):

    class _DatasetList(_UidList[DatasetItem]):
        ITEM_TYPE = DatasetItem
        ITEM_NAME = 'item'
        PARENT_NAME = 'dataset'

    def __init__(
        self,
        items: Optional[Iterable[DatasetItem]] = None,
        labels: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        uid: Optional[str] = None,
    ):
        if not isinstance(name, str):
            raise TypeError(f'dataset name must be a str, got type: {type(name)}, for: {repr(name)}')
        # init
        super().__init__(labels=labels, tags=tags, uid=uid)
        # storage
        self._name = name if name else self.uid
        self._items = self._DatasetList(items)

    # --- properties --- #

    @property
    def name(self) -> str:
        return self.name

    def __repr__(self):
        return repr_truelike_kwargs_no_uid(self, items='<hidden>', labels=self.labels, tags=self.tags, uid=self.uid)

    # --- item list --- #

    def __len__(self):
        return len(self._items)

    def __iter__(self) -> Iterator[DatasetItem]:
        yield from self._items

    def append(self, item: DatasetItem) -> NoReturn:
        return self._items.append(item)

    def extend(self, items: Iterable[DatasetItem]) -> NoReturn:
        return self._items.extend(items)

    def __getitem__(self, uid: Union[UidIdx, UidMultiIdx]) -> Union[DatasetItem, List[DatasetItem]]:
        return self._items.__getitem__(uid)

    def __contains__(self, uid: Union[str, DatasetItem]) -> bool:
        return self._items.__contains__(uid)

    # --- validate --- #

    def validate(self) -> 'Dataset':
        # collect all the labels across the dataset
        labels_items = set()
        labels_annos = set()
        for item in self:
            labels_items.update(item.labels)
            for annotation in item.annotations:
                labels_annos.update(annotation.labels)
        # check missing labels obtained from items
        missing_items = set(self._labels) - labels_items
        if missing_items:
            raise DatasetLabelNotFoundError(f'dataset: {self.name} is missing labels contained on items: {missing_items}')
        # check missing labels obtained from items
        missing_annos = set(self._labels) - labels_annos
        if missing_annos:
            raise DatasetLabelNotFoundError(f'dataset: {self.name} is missing labels contained on item annotations: {missing_annos}')
        # done!
        return self

    # --- filter --- #

    def filter_items(
        self,
        item_fn: Optional[Callable[[DatasetItem], bool]] = None,
        item_labels: Optional[Iterable[str]] = None,
        item_tags: Optional[Iterable[str]] = None,
        anno_fn: Optional[Callable[[Annotation], bool]] = None,
        anno_labels: Optional[Iterable[str]] = None,
        anno_tags: Optional[Iterable[str]] = None,
    ):
        def _make_fn_chain(fn, labels, tags):
            chain = []
            if fn:
                chain.append(fn)
            if labels:
                labels = set(labels)
                chain.append(lambda it: labels.issubset(it.labels))
            if tags:
                tags = set(tags)
                chain.append(lambda it: tags.issubset(it.tags))
            return chain
        # keep the specified items
        item_chain = _make_fn_chain(item_fn, item_labels, item_tags)
        anno_chain = _make_fn_chain(anno_fn, anno_labels, anno_tags)
        # filter
        items = []
        for item in self:
            # check the item
            if not all(fn(item) for fn in item_chain):
                continue
            # check the annotations
            if anno_chain:
                keep = True
                for anno in item.annotations:
                    keep = all(fn(anno) for fn in anno_chain)
                    if not keep:
                        break
                # skip the item if an annotation fails
                if not keep:
                    continue
            # keep the item!
            items.append(item)
        # make the new datasets
        # TODO: this should probably not set the tags/labels/name of the dataset
        return Dataset(items, labels=self.labels, tags=self.tags, name=self.name)


# ========================================================================= #
# END                                                                       #
# ========================================================================= #

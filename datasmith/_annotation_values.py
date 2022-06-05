import warnings
from typing import Optional
from typing import Tuple

from datasmith._base import AnnotationValue


# ========================================================================= #
# Bounding Box Object                                                       #
# ========================================================================= #


def _get_scale_wh(image_wh: Optional[Tuple[float, float]] = None):
    return (1, 1) if (image_wh is None) else image_wh


class Bbox(AnnotationValue):

    def __init__(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
    ):
        if not (0 <= x0 <= x1 <= 1): warnings.warn(f'not (0 <= {x0} [x0] <= {x1} [x1] <= 1)')   # usually ratio of original image dimensions
        if not (0 <= y0 <= y1 <= 1): warnings.warn(f'not (0 <= {y0} [y0] <= {y1} [y1] <= 1)')   # usually ratio of original image dimensions
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def __repr__(self):
        return f'{self.__class__.__name__}(x0={repr(self.x0)}, y0={repr(self.y0)}, x1={repr(self.x1)}, y1={repr(self.y1)})'

    # --- from --- #

    @classmethod
    def from_cxywh(
        cls,
        cx: float,
        cy: float,
        w: float,
        h: float,
        image_wh: Optional[Tuple[float, float]] = None,
    ):
        W, H = _get_scale_wh(image_wh)
        return cls(x0=(cx - w/2)/W, y0=(cy - h/2)/H, x1=(cx + w/2)/W, y1=(cy + h/2)/H)

    @classmethod
    def from_xywh(
        cls,
        x0: float,
        y0: float,
        w: float,
        h: float,
        image_wh: Optional[Tuple[float, float]] = None,
    ):
        W, H = _get_scale_wh(image_wh)
        return cls(x0=x0/W, y0=y0/H, x1=(x0 + w)/W, y1=(y0 + h)/H)

    @classmethod
    def from_xyxy(
        cls,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        image_wh: Optional[Tuple[float, float]] = None,
    ):
        W, H = _get_scale_wh(image_wh)
        return cls(x0=x0/W, y0=y0/H, x1=x1/W, y1=y1/H)

    # --- to --- #

    def get_cxywh(self, image_wh: Optional[Tuple[float, float]] = None) -> Tuple[float, float, float, float]:
        W, H = _get_scale_wh(image_wh)
        cx = (self.x1 + self.x0) / 2
        cy = (self.y1 + self.y0) / 2
        w = self.x1 - self.x0
        h = self.y1 - self.y0
        return (cx*W, cy*H, w*W, h*H)

    def get_xywh(self, image_wh: Optional[Tuple[float, float]] = None) -> Tuple[float, float, float, float]:
        W, H = _get_scale_wh(image_wh)
        x0 = self.x0
        y0 = self.y0
        w = self.x1 - self.x0
        h = self.y1 - self.y0
        return (x0*W, y0*H, w*W, h*H)

    def get_xyxy(self, image_wh: Optional[Tuple[float, float]] = None) -> Tuple[float, float, float, float]:
        W, H = _get_scale_wh(image_wh)
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        return (x0*W, y0*H, x1*W, y1*H)


# ========================================================================= #
# Bounding Box Object                                                       #
# ========================================================================= #

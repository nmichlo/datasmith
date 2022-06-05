import json
import os
from collections import defaultdict

from datasmith._base import Annotation
from datasmith._annotations import Bbox
from datasmith._base import Dataset
from datasmith._items import DatasetItemPath


def import_coco(
    root: str,
    rel_instance_file: str ='annotations/instances_default.json',
    rel_images_dir: str = 'images',
):
    with open(os.path.join(root, rel_instance_file), 'r') as fp:
        dat = json.load(fp)
    # checks
    dat_images      = {item['id']: item for item in dat['images']}
    dat_categories  = {item['id']: item for item in dat['categories']}
    dat_annotations = {item['id']: item for item in dat['annotations']}
    image_anno_ids  = defaultdict(list)
    # combine
    for dat_anno in dat['annotations']:
        image_anno_ids[dat_anno['image_id']].append(dat_anno['id'])
    # convert to dataset
    items = []
    for dat_image in dat_images.values():
        # get annotations
        annotations = []
        for anno_id in image_anno_ids[dat_image['id']]:
            dat_anno = dat_annotations[anno_id]
            anno_cat_name = dat_categories[dat_anno['category_id']]['name']
            # append annotation
            annotations.append(Annotation(
                value=Bbox.from_xywh(*dat_anno['bbox'], image_wh=(dat_image['width'], dat_image['height'])),
                labels=[anno_cat_name],
            ))
        # append item
        items.append(DatasetItemPath(
            path=os.path.join(root, rel_images_dir, dat_image['file_name']),
            annotations=annotations,
        ))
    # done
    return Dataset(
        items,
        labels=[item['name'] for item in dat_categories.values()],
        name=os.path.join(root, rel_instance_file)
    )



if __name__ == '__main__':


    def main():

        path = "/Users/nmichlo/Desktop/active_df/df-datasets/data/fire-smoke/cvat-fire-smoke-v3_2022-06-01_14-00_coco/cvat-fire-smoke-v3_2022-06-01_14-00_coco"

        d = Dataset(name='basic_dataset', labels=['fire', 'smoke'])

        dataset = import_coco(path)
        for item in dataset:
            print(item)

    main()

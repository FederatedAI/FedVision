# Copyright (c) 2020 The FedVision Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from fedvision import __basedir__
from fedvision.framework.utils.exception import FedvisionDataNotFoundException
from ppdet.data.reader import Reader
from ppdet.data.source.voc import VOCDataSet
from ppdet.data.transform.batch_operators import PadBatch
from ppdet.data.transform.operators import (
    DecodeImage,
    RandomFlipImage,
    NormalizeImage,
    ResizeImage,
    Permute,
)


class DataReader(object):
    def __init__(self, trainer_id, dataset):
        if not os.path.exists(dataset):
            dataset = os.path.abspath(
                os.path.join(__basedir__, os.path.pardir, "data", dataset)
            )

        if not os.path.exists(dataset):
            raise FedvisionDataNotFoundException(f"dataset {dataset} not found")
        self.root_path = dataset
        self.anno_path = f"{self.root_path}/train{trainer_id}.txt"
        self.image_dir = f"{self.root_path}/JPEGImages"

    def tearDownClass(self):
        """ tearDownClass """
        pass

    def data_loader(self):
        coco_loader = VOCDataSet(
            dataset_dir=self.image_dir,
            image_dir=self.root_path,
            anno_path=self.anno_path,
            sample_num=240,
            use_default_label=False,
            label_list=f"{self.root_path}/label_list.txt",
        )
        sample_trans = [
            DecodeImage(to_rgb=True),
            RandomFlipImage(),
            NormalizeImage(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
                is_scale=True,
                is_channel_first=False,
            ),
            ResizeImage(target_size=800, max_size=1333, interp=1),
            Permute(to_bgr=False),
        ]
        batch_trans = [
            PadBatch(pad_to_stride=32, use_padded_im_info=True),
        ]

        inputs_def = {
            "fields": ["image", "im_info", "im_id", "gt_bbox", "gt_class", "is_crowd"],
        }
        data_loader = Reader(
            coco_loader,
            sample_transforms=sample_trans,
            batch_transforms=batch_trans,
            batch_size=1,
            shuffle=True,
            drop_empty=True,
            inputs_def=inputs_def,
        )()

        return data_loader

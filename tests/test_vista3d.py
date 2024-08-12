# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import unittest

import torch
from parameterized import parameterized

from monai.networks import eval_mode
from monai.networks.nets import VISTA3D, SegResNetDS2
from monai.networks.nets.vista3d import ClassMappingClassify, PointMappingSAM

device = "cuda" if torch.cuda.is_available() else "cpu"

TEST_CASES = [
    [
        {"encoder_embed_dim": 48, "in_channels": 1},
        {},
        (1, 1, 64, 64, 64),
        (1, 1, 64, 64, 64),
    ]
]


class TestVista3d(unittest.TestCase):

    @parameterized.expand(TEST_CASES)
    def test_vista3d_shape(self, args, input_params, input_shape, expected_shape):
        segresnet = SegResNetDS2(
            in_channels=args["in_channels"],
            blocks_down=(1, 2, 2, 4, 4),
            norm="instance",
            out_channels=args["encoder_embed_dim"],
            init_filters=args["encoder_embed_dim"],
            dsdepth=1,
        )
        point_head = PointMappingSAM(feature_size=args["encoder_embed_dim"], n_classes=512, last_supported=132)
        class_head = ClassMappingClassify(n_classes=512, feature_size=args["encoder_embed_dim"], use_mlp=True)
        net = VISTA3D(image_encoder=segresnet, class_head=class_head, point_head=point_head).to(device)
        with eval_mode(net):
            result = net.forward(torch.randn(input_shape).to(device))
            self.assertEqual(result.shape, expected_shape)


if __name__ == "__main__":
    unittest.main()

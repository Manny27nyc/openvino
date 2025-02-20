# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Package: openvino.op
Low level wrappers for the c++ api in ov::op.
"""

# flake8: noqa

import numpy as np

from openvino.pyopenvino.op import Constant

"""Retrieve Constant inner data.

    Internally uses PyBind11 Numpy's buffer protocol.

    :return Numpy array containing internally stored constant data.
"""
Constant.get_data = lambda self: np.array(self, copy=True)

from openvino.pyopenvino.op import Parameter
from openvino.pyopenvino.op import if_op
from openvino.pyopenvino.op import loop
from openvino.pyopenvino.op import tensor_iterator

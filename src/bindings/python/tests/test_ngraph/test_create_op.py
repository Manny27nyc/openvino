# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pytest
from openvino.runtime import PartialShape, Dimension, Model
from openvino.runtime.exceptions import UserInputError

import openvino.runtime.opset8 as ov
import openvino.runtime.opset1 as ov_opset1
import openvino.runtime.opset5 as ov_opset5
from openvino.runtime import Type

np_types = [np.float32, np.int32]
integral_np_types = [
    np.int8,
    np.int16,
    np.int32,
    np.int64,
    np.uint8,
    np.uint16,
    np.uint32,
    np.uint64,
]


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_adaptive_avg_pool(dtype):
    data = ov.parameter([2, 24, 34, 62], name="input", dtype=dtype)
    output_shape = ov.constant(np.array([16, 16], dtype=np.int32))

    node = ov.adaptive_avg_pool(data, output_shape)

    assert node.get_type_name() == "AdaptiveAvgPool"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 24, 16, 16]


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@pytest.mark.parametrize("ind_type", ["i32", "i64"])
def test_adaptive_max_pool(dtype, ind_type):
    data = ov.parameter([2, 24, 34, 62], name="input", dtype=dtype)
    output_shape = ov.constant(np.array([16, 16], dtype=np.int32))

    node = ov.adaptive_max_pool(data, output_shape, ind_type)

    assert node.get_type_name() == "AdaptiveMaxPool"
    assert node.get_output_size() == 2
    assert list(node.get_output_shape(0)) == [2, 24, 16, 16]
    assert list(node.get_output_shape(1)) == [2, 24, 16, 16]
    assert node.get_output_element_type(1) == Type.i32 if ind_type == "i32" else Type.i64


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_binary_convolution(dtype):
    strides = np.array([1, 1])
    pads_begin = np.array([0, 0])
    pads_end = np.array([0, 0])
    dilations = np.array([1, 1])
    mode = "xnor-popcount"
    pad_value = 0.0

    input0_shape = [1, 1, 9, 9]
    input1_shape = [1, 1, 3, 3]
    expected_shape = [1, 1, 7, 7]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)

    node = ov.binary_convolution(
        parameter_input0, parameter_input1, strides, pads_begin, pads_end, dilations, mode, pad_value,
    )

    assert node.get_type_name() == "BinaryConvolution"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_ctc_greedy_decoder(dtype):
    input0_shape = [20, 8, 128]
    input1_shape = [20, 8]
    expected_shape = [8, 20, 1, 1]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)

    node = ov.ctc_greedy_decoder(parameter_input0, parameter_input1)

    assert node.get_type_name() == "CTCGreedyDecoder"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("fp_dtype, int_dtype, int_ci, int_sl, merge_repeated, blank_index",
                         [
                             (np.float32, np.int32, "i32", "i32", True, True),
                             (np.float32, np.int32, "i64", "i32", True, True),
                             (np.float32, np.int32, "i32", "i64", True, True),
                             (np.float32, np.int32, "i64", "i64", True, True),
                             (np.float64, np.int64, "i32", "i32", False, True),
                             (np.float64, np.int64, "i64", "i32", False, True),
                             (np.float64, np.int64, "i32", "i64", False, True),
                             (np.float64, np.int64, "i64", "i64", False, True),
                             (np.float32, np.int32, "i32", "i32", True, False),
                             (np.float32, np.int32, "i64", "i32", True, False),
                             (np.float32, np.int32, "i32", "i64", True, False),
                             (np.float32, np.int32, "i64", "i64", True, False),
                             (np.float64, np.int64, "i32", "i32", False, False),
                             (np.float64, np.int64, "i64", "i32", False, False),
                             (np.float64, np.int64, "i32", "i64", False, False),
                             (np.float64, np.int64, "i64", "i64", False, False)
                         ], )
def test_ctc_greedy_decoder_seq_len(fp_dtype, int_dtype, int_ci, int_sl, merge_repeated, blank_index):
    input0_shape = [8, 20, 128]
    input1_shape = [8]
    input2_shape = [1]
    expected_shape = [8, 20]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=fp_dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=int_dtype)
    parameter_input2 = None
    if blank_index:
        parameter_input2 = ov.parameter(input2_shape, name="Input2", dtype=int_dtype)

    node = ov.ctc_greedy_decoder_seq_len(
        parameter_input0, parameter_input1, parameter_input2, merge_repeated, int_ci, int_sl
    )

    assert node.get_type_name() == "CTCGreedyDecoderSeqLen"
    assert node.get_output_size() == 2
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_deformable_convolution_opset1(dtype):
    strides = np.array([1, 1])
    pads_begin = np.array([0, 0])
    pads_end = np.array([0, 0])
    dilations = np.array([1, 1])

    input0_shape = [1, 1, 9, 9]
    input1_shape = [1, 18, 7, 7]
    input2_shape = [1, 1, 3, 3]
    expected_shape = [1, 1, 7, 7]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)
    parameter_input2 = ov.parameter(input2_shape, name="Input2", dtype=dtype)

    node = ov_opset1.deformable_convolution(
        parameter_input0, parameter_input1, parameter_input2, strides, pads_begin, pads_end, dilations,
    )

    assert node.get_type_name() == "DeformableConvolution"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_deformable_convolution(dtype):
    strides = np.array([1, 1])
    pads_begin = np.array([0, 0])
    pads_end = np.array([0, 0])
    dilations = np.array([1, 1])

    input0_shape = [1, 1, 9, 9]
    input1_shape = [1, 18, 7, 7]
    input2_shape = [1, 1, 3, 3]
    expected_shape = [1, 1, 7, 7]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)
    parameter_input2 = ov.parameter(input2_shape, name="Input2", dtype=dtype)

    node = ov.deformable_convolution(
        parameter_input0, parameter_input1, parameter_input2, strides, pads_begin, pads_end, dilations,
    )

    assert node.get_type_name() == "DeformableConvolution"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_deformable_convolution_mask(dtype):
    strides = np.array([1, 1])
    pads_begin = np.array([0, 0])
    pads_end = np.array([0, 0])
    dilations = np.array([1, 1])

    input0_shape = [1, 1, 9, 9]
    input1_shape = [1, 18, 7, 7]
    input2_shape = [1, 1, 3, 3]
    input3_shape = [1, 9, 7, 7]
    expected_shape = [1, 1, 7, 7]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)
    parameter_input2 = ov.parameter(input2_shape, name="Input2", dtype=dtype)
    parameter_input3 = ov.parameter(input3_shape, name="Input3", dtype=dtype)

    node = ov.deformable_convolution(
        parameter_input0, parameter_input1, parameter_input2, strides,
        pads_begin, pads_end, dilations, parameter_input3
    )

    assert node.get_type_name() == "DeformableConvolution"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_deformable_psroi_pooling(dtype):
    output_dim = 8
    spatial_scale = 0.0625
    group_size = 7
    mode = "bilinear_deformable"
    spatial_bins_x = 4
    spatial_bins_y = 4
    trans_std = 0.1
    part_size = 7

    input0_shape = [1, 392, 38, 63]
    input1_shape = [300, 5]
    input2_shape = [300, 2, 7, 7]
    expected_shape = [300, 8, 7, 7]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)
    parameter_input2 = ov.parameter(input2_shape, name="Input2", dtype=dtype)

    node = ov.deformable_psroi_pooling(
        parameter_input0,
        parameter_input1,
        output_dim,
        spatial_scale,
        group_size,
        mode,
        spatial_bins_x,
        spatial_bins_y,
        trans_std,
        part_size,
        offsets=parameter_input2,
    )

    assert node.get_type_name() == "DeformablePSROIPooling"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_floor_mod(dtype):
    input0_shape = [8, 1, 6, 1]
    input1_shape = [7, 1, 5]
    expected_shape = [8, 7, 6, 5]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)

    node = ov.floor_mod(parameter_input0, parameter_input1)

    assert node.get_type_name() == "FloorMod"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", np_types)
def test_gather_tree(dtype):
    input0_shape = [100, 1, 10]
    input1_shape = [100, 1, 10]
    input2_shape = [1]
    input3_shape = []
    expected_shape = [100, 1, 10]

    parameter_input0 = ov.parameter(input0_shape, name="Input0", dtype=dtype)
    parameter_input1 = ov.parameter(input1_shape, name="Input1", dtype=dtype)
    parameter_input2 = ov.parameter(input2_shape, name="Input2", dtype=dtype)
    parameter_input3 = ov.parameter(input3_shape, name="Input3", dtype=dtype)

    node = ov.gather_tree(parameter_input0, parameter_input1, parameter_input2, parameter_input3)

    assert node.get_type_name() == "GatherTree"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_cell_operator(dtype):
    batch_size = 1
    input_size = 16
    hidden_size = 128

    X_shape = [batch_size, input_size]
    H_t_shape = [batch_size, hidden_size]
    C_t_shape = [batch_size, hidden_size]
    W_shape = [4 * hidden_size, input_size]
    R_shape = [4 * hidden_size, hidden_size]
    B_shape = [4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    expected_shape = [1, 128]

    node_default = ov.lstm_cell(
        parameter_X, parameter_H_t, parameter_C_t, parameter_W, parameter_R, parameter_B, hidden_size,
    )

    assert node_default.get_type_name() == "LSTMCell"
    assert node_default.get_output_size() == 2
    assert list(node_default.get_output_shape(0)) == expected_shape
    assert list(node_default.get_output_shape(1)) == expected_shape

    activations = ["tanh", "Sigmoid", "RELU"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 0.5

    node_param = ov.lstm_cell(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "LSTMCell"
    assert node_param.get_output_size() == 2
    assert list(node_param.get_output_shape(0)) == expected_shape
    assert list(node_param.get_output_shape(1)) == expected_shape


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_cell_operator_opset1(dtype):
    batch_size = 1
    input_size = 16
    hidden_size = 128

    X_shape = [batch_size, input_size]
    H_t_shape = [batch_size, hidden_size]
    C_t_shape = [batch_size, hidden_size]
    W_shape = [4 * hidden_size, input_size]
    R_shape = [4 * hidden_size, hidden_size]
    B_shape = [4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    expected_shape = [1, 128]

    node_default = ov_opset1.lstm_cell(
        parameter_X, parameter_H_t, parameter_C_t, parameter_W, parameter_R, parameter_B, hidden_size,
    )

    assert node_default.get_type_name() == "LSTMCell"
    assert node_default.get_output_size() == 2
    assert list(node_default.get_output_shape(0)) == expected_shape
    assert list(node_default.get_output_shape(1)) == expected_shape

    activations = ["tanh", "Sigmoid", "RELU"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 0.5

    node_param = ov_opset1.lstm_cell(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "LSTMCell"
    assert node_param.get_output_size() == 2
    assert list(node_param.get_output_shape(0)) == expected_shape
    assert list(node_param.get_output_shape(1)) == expected_shape


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_sequence_operator_bidirectional_opset1(dtype):
    batch_size = 1
    input_size = 16
    hidden_size = 128
    num_directions = 2
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    C_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 4 * hidden_size, input_size]
    R_shape = [num_directions, 4 * hidden_size, hidden_size]
    B_shape = [num_directions, 4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "BIDIRECTIONAL"
    node = ov_opset1.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node.get_type_name() == "LSTMSequence"
    assert node.get_output_size() == 3

    activations = ["RELU", "tanh", "Sigmoid"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22

    node_param = ov_opset1.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "LSTMSequence"
    assert node_param.get_output_size() == 3


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_sequence_operator_reverse_opset1(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    C_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 4 * hidden_size, input_size]
    R_shape = [num_directions, 4 * hidden_size, hidden_size]
    B_shape = [num_directions, 4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "REVERSE"

    node_default = ov_opset1.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "LSTMSequence"
    assert node_default.get_output_size() == 3

    activations = ["RELU", "tanh", "Sigmoid"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22

    node_param = ov_opset1.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "LSTMSequence"
    assert node_param.get_output_size() == 3


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_sequence_operator_forward_opset1(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    C_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 4 * hidden_size, input_size]
    R_shape = [num_directions, 4 * hidden_size, hidden_size]
    B_shape = [num_directions, 4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "forward"

    node_default = ov_opset1.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "LSTMSequence"
    assert node_default.get_output_size() == 3

    activations = ["RELU", "tanh", "Sigmoid"]
    activation_alpha = [2.0]
    activation_beta = [1.0]
    clip = 0.5

    node = ov_opset1.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node.get_type_name() == "LSTMSequence"
    assert node.get_output_size() == 3


def test_gru_cell_operator():
    batch_size = 1
    input_size = 16
    hidden_size = 128

    X_shape = [batch_size, input_size]
    H_t_shape = [batch_size, hidden_size]
    W_shape = [3 * hidden_size, input_size]
    R_shape = [3 * hidden_size, hidden_size]
    B_shape = [3 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=np.float32)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=np.float32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=np.float32)
    parameter_R = ov.parameter(R_shape, name="R", dtype=np.float32)
    parameter_B = ov.parameter(B_shape, name="B", dtype=np.float32)

    expected_shape = [1, 128]

    node_default = ov.gru_cell(parameter_X, parameter_H_t, parameter_W, parameter_R, parameter_B, hidden_size)

    assert node_default.get_type_name() == "GRUCell"
    assert node_default.get_output_size() == 1
    assert list(node_default.get_output_shape(0)) == expected_shape

    activations = ["tanh", "relu"]
    activations_alpha = [1.0, 2.0]
    activations_beta = [1.0, 2.0]
    clip = 0.5
    linear_before_reset = True

    # If *linear_before_reset* is set True, then B tensor shape must be [4 * hidden_size]
    B_shape = [4 * hidden_size]
    parameter_B = ov.parameter(B_shape, name="B", dtype=np.float32)

    node_param = ov.gru_cell(
        parameter_X,
        parameter_H_t,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        activations,
        activations_alpha,
        activations_beta,
        clip,
        linear_before_reset,
    )

    assert node_param.get_type_name() == "GRUCell"
    assert node_param.get_output_size() == 1
    assert list(node_param.get_output_shape(0)) == expected_shape


def test_gru_sequence():
    batch_size = 2
    input_size = 16
    hidden_size = 32
    seq_len = 8
    seq_lengths = [seq_len] * batch_size
    num_directions = 1
    direction = "FORWARD"

    X_shape = [batch_size, seq_len, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    W_shape = [num_directions, 3 * hidden_size, input_size]
    R_shape = [num_directions, 3 * hidden_size, hidden_size]
    B_shape = [num_directions, 3 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=np.float32)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=np.float32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=np.float32)
    parameter_R = ov.parameter(R_shape, name="R", dtype=np.float32)
    parameter_B = ov.parameter(B_shape, name="B", dtype=np.float32)

    expected_shape_y = [batch_size, num_directions, seq_len, hidden_size]
    expected_shape_h = [batch_size, num_directions, hidden_size]

    node_default = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        seq_lengths,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "GRUSequence"
    assert node_default.get_output_size() == 2
    assert list(node_default.get_output_shape(0)) == expected_shape_y
    assert list(node_default.get_output_shape(1)) == expected_shape_h

    activations = ["tanh", "relu"]
    activations_alpha = [1.0, 2.0]
    activations_beta = [1.0, 2.0]
    clip = 0.5
    linear_before_reset = True

    # If *linear_before_reset* is set True, then B tensor shape must be [4 * hidden_size]
    B_shape = [num_directions, 4 * hidden_size]
    parameter_B = ov.parameter(B_shape, name="B", dtype=np.float32)

    node_param = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        seq_lengths,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activations_alpha,
        activations_beta,
        clip,
        linear_before_reset,
    )

    assert node_param.get_type_name() == "GRUSequence"
    assert node_param.get_output_size() == 2
    assert list(node_param.get_output_shape(0)) == expected_shape_y
    assert list(node_param.get_output_shape(1)) == expected_shape_h


def test_rnn_sequence():
    batch_size = 2
    input_size = 16
    hidden_size = 32
    seq_len = 8
    seq_lengths = [seq_len] * batch_size
    num_directions = 1
    direction = "FORWARD"

    X_shape = [batch_size, seq_len, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    W_shape = [num_directions, hidden_size, input_size]
    R_shape = [num_directions, hidden_size, hidden_size]
    B_shape = [num_directions, hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=np.float32)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=np.float32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=np.float32)
    parameter_R = ov.parameter(R_shape, name="R", dtype=np.float32)
    parameter_B = ov.parameter(B_shape, name="B", dtype=np.float32)

    expected_shape_y = [batch_size, num_directions, seq_len, hidden_size]
    expected_shape_h = [batch_size, num_directions, hidden_size]

    node_default = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        seq_lengths,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "RNNSequence"
    assert node_default.get_output_size() == 2
    assert list(node_default.get_output_shape(0)) == expected_shape_y
    assert list(node_default.get_output_shape(1)) == expected_shape_h

    activations = ["relu"]
    activations_alpha = [2.0]
    activations_beta = [1.0]
    clip = 0.5

    node_param = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        seq_lengths,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activations_alpha,
        activations_beta,
        clip,
    )

    assert node_param.get_type_name() == "RNNSequence"
    assert node_param.get_output_size() == 2
    assert list(node_param.get_output_shape(0)) == expected_shape_y
    assert list(node_param.get_output_shape(1)) == expected_shape_h


def test_loop():
    bool_val = [True]  # np.array([1], dtype=np.bool)
    condition = ov.constant(bool_val)
    trip_count = ov.constant(16, dtype=np.int32)
    #  Body parameters
    body_timestep = ov.parameter([], np.int32, "timestep")
    body_data_in = ov.parameter([1, 2, 2], np.float32, "body_in")
    body_prev_cma = ov.parameter([2, 2], np.float32, "body_prev_cma")
    body_const_one = ov.parameter([], np.int32, "body_const_one")

    # CMA = cumulative moving average
    prev_cum_sum = ov.multiply(ov.convert(body_timestep, "f32"), body_prev_cma)
    curr_cum_sum = ov.add(prev_cum_sum, ov.squeeze(body_data_in, [0]))
    elem_cnt = ov.add(body_const_one, body_timestep)
    curr_cma = ov.divide(curr_cum_sum, ov.convert(elem_cnt, "f32"))
    cma_hist = ov.unsqueeze(curr_cma, [0])

    # TI inputs
    data = ov.parameter([16, 2, 2], np.float32, "data")
    # Iterations count
    zero = ov.constant(0, dtype=np.int32)
    one = ov.constant(1, dtype=np.int32)
    initial_cma = ov.constant(np.zeros([2, 2], dtype=np.float32), dtype=np.float32)
    iter_cnt = ov.range(zero, np.int32(16), np.int32(1))
    body_const_condition = ov.constant(bool_val)

    graph_body = Model([curr_cma, cma_hist, body_const_condition], [body_timestep,
                       body_data_in, body_prev_cma, body_const_one], "body_function")

    node = ov.loop(trip_count, condition)
    node.set_function(graph_body)
    node.set_special_body_ports([-1, 2])
    node.set_sliced_input(body_timestep, iter_cnt.output(0), 0, 1, 1, -1, 0)
    node.set_sliced_input(body_data_in, data.output(0), 0, 1, 1, -1, 0)
    node.set_merged_input(body_prev_cma, initial_cma.output(0), curr_cma.output(0))
    node.set_invariant_input(body_const_one, one.output(0))

    out0 = node.get_iter_value(curr_cma.output(0), -1)
    out1 = node.get_concatenated_slices(cma_hist.output(0), 0, 1, 1, -1, 0)

    result0 = ov.result(out0)
    result1 = ov.result(out1)

    assert node.get_type_name() == "Loop"
    assert node.get_output_size() == 2
    # final average
    assert list(result0.get_output_shape(0)) == [2, 2]
    assert list(node.get_output_shape(0)) == [2, 2]
    # cma history
    assert list(result1.get_output_shape(0)) == [16, 2, 2]
    assert list(node.get_output_shape(1)) == [16, 2, 2]


def test_roi_pooling():
    inputs = ov.parameter([2, 3, 4, 5], dtype=np.float32)
    coords = ov.parameter([150, 5], dtype=np.float32)
    node = ov.roi_pooling(inputs, coords, [6, 6], 0.0625, "Max")

    assert node.get_type_name() == "ROIPooling"
    assert node.get_output_size() == [6, 6]
    assert list(node.get_output_shape(0)) == [150, 3, 6, 6]
    assert node.get_output_element_type(0) == Type.f32


def test_psroi_pooling():
    inputs = ov.parameter([1, 72, 4, 5], dtype=np.float32)
    coords = ov.parameter([150, 5], dtype=np.float32)
    node = ov.psroi_pooling(inputs, coords, 2, 6, 0.0625, 0, 0, "average")

    assert node.get_type_name() == "PSROIPooling"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [150, 2, 6, 6]
    assert node.get_output_element_type(0) == Type.f32


def test_convert_like():
    parameter_data = ov.parameter([1, 2, 3, 4], name="data", dtype=np.float32)
    like = ov.constant(1, dtype=np.int8)

    node = ov.convert_like(parameter_data, like)

    assert node.get_type_name() == "ConvertLike"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [1, 2, 3, 4]
    assert node.get_output_element_type(0) == Type.i8


def test_bucketize():
    data = ov.parameter([4, 3, 2, 1], name="data", dtype=np.float32)
    buckets = ov.parameter([5], name="buckets", dtype=np.int64)

    node = ov.bucketize(data, buckets, "i32")

    assert node.get_type_name() == "Bucketize"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [4, 3, 2, 1]
    assert node.get_output_element_type(0) == Type.i32


def test_region_yolo():
    data = ov.parameter([1, 125, 13, 13], name="input", dtype=np.float32)
    num_coords = 4
    num_classes = 80
    num_regions = 1
    mask = [6, 7, 8]
    axis = 0
    end_axis = 3
    do_softmax = False

    node = ov.region_yolo(data, num_coords, num_classes, num_regions, do_softmax, mask, axis, end_axis)

    assert node.get_type_name() == "RegionYolo"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [1, (80 + 4 + 1) * 3, 13, 13]
    assert node.get_output_element_type(0) == Type.f32


def test_reorg_yolo():
    data = ov.parameter([2, 24, 34, 62], name="input", dtype=np.int32)
    stride = [2]

    node = ov.reorg_yolo(data, stride)

    assert node.get_type_name() == "ReorgYolo"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 96, 17, 31]
    assert node.get_output_element_type(0) == Type.i32


def test_embedding_bag_offsets_sum_1():
    emb_table = ov.parameter([5, 2], name="emb_table", dtype=np.float32)
    indices = ov.parameter([4], name="indices", dtype=np.int64)
    offsets = ov.parameter([3], name="offsets", dtype=np.int64)
    default_index = ov.parameter([], name="default_index", dtype=np.int64)

    node = ov.embedding_bag_offsets_sum(emb_table, indices, offsets, default_index)

    assert node.get_type_name() == "EmbeddingBagOffsetsSum"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [3, 2]
    assert node.get_output_element_type(0) == Type.f32


def test_embedding_segments_sum_all_inputs():
    emb_table = ov.parameter([5, 2], name="emb_table", dtype=np.float32)
    indices = ov.parameter([4], name="indices", dtype=np.int64)
    segment_ids = ov.parameter([4], name="segment_ids", dtype=np.int64)
    num_segments = ov.parameter([], name="num_segments", dtype=np.int64)
    default_index = ov.parameter([], name="default_index", dtype=np.int64)
    per_sample_weights = ov.parameter([4], name="per_sample_weights", dtype=np.float32)

    node = ov.embedding_segments_sum(
        emb_table, indices, segment_ids, num_segments, default_index, per_sample_weights
    )

    assert node.get_type_name() == "EmbeddingSegmentsSum"
    assert node.get_output_size() == 1
    assert node.get_output_partial_shape(0).same_scheme(PartialShape([-1, 2]))
    assert node.get_output_element_type(0) == Type.f32


def test_embedding_segments_sum_with_some_opt_inputs():
    emb_table = ov.parameter([5, 2], name="emb_table", dtype=np.float32)
    indices = ov.parameter([4], name="indices", dtype=np.int64)
    segment_ids = ov.parameter([4], name="segment_ids", dtype=np.int64)
    num_segments = ov.parameter([], name="num_segments", dtype=np.int64)

    # only 1 out of 3 optional inputs
    node = ov.embedding_segments_sum(emb_table, indices, segment_ids, num_segments)

    assert node.get_type_name() == "EmbeddingSegmentsSum"
    assert node.get_output_size() == 1
    assert node.get_output_partial_shape(0).same_scheme(PartialShape([-1, 2]))
    assert node.get_output_element_type(0) == Type.f32


def test_embedding_bag_packed_sum():
    emb_table = ov.parameter([5, 2], name="emb_table", dtype=np.float32)
    indices = ov.parameter([3, 3], name="indices", dtype=np.int64)
    per_sample_weights = ov.parameter([3, 3], name="per_sample_weights", dtype=np.float32)

    # only 1 out of 3 optional inputs
    node = ov.embedding_bag_packed_sum(emb_table, indices, per_sample_weights)

    assert node.get_type_name() == "EmbeddingBagPackedSum"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [3, 2]
    assert node.get_output_element_type(0) == Type.f32


@pytest.mark.parametrize("dtype", integral_np_types)
def test_interpolate(dtype):
    image_shape = [1, 3, 1024, 1024]
    output_shape = [64, 64]
    attributes = {
        "axes": [2, 3],
        "mode": "cubic",
        "pads_begin": np.array([2, 2], dtype=dtype),
    }

    image_node = ov.parameter(image_shape, dtype, name="Image")

    node = ov.interpolate(image_node, output_shape, attributes)
    expected_shape = [1, 3, 64, 64]

    assert node.get_type_name() == "Interpolate"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize(
    "int_dtype, fp_dtype",
    [
        (np.int8, np.float32),
        (np.int16, np.float32),
        (np.int32, np.float32),
        (np.int64, np.float32),
        (np.uint8, np.float32),
        (np.uint16, np.float32),
        (np.uint32, np.float32),
        (np.uint64, np.float32),
        (np.int32, np.float16),
        (np.int32, np.float64),
    ],
)
def test_prior_box(int_dtype, fp_dtype):
    image_shape = np.array([64, 64], dtype=int_dtype)
    attributes = {
        "offset": fp_dtype(0),
        "min_size": np.array([2, 3], dtype=fp_dtype),
        "aspect_ratio": np.array([1.5, 2.0, 2.5], dtype=fp_dtype),
        "scale_all_sizes": False
    }

    layer_shape = ov.constant(np.array([32, 32], dtype=int_dtype), int_dtype)

    node = ov.prior_box(layer_shape, image_shape, attributes)

    assert node.get_type_name() == "PriorBox"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 20480]


@pytest.mark.parametrize(
    "int_dtype, fp_dtype",
    [
        (np.int8, np.float32),
        (np.int16, np.float32),
        (np.int32, np.float32),
        (np.int64, np.float32),
        (np.uint8, np.float32),
        (np.uint16, np.float32),
        (np.uint32, np.float32),
        (np.uint64, np.float32),
        (np.int32, np.float16),
        (np.int32, np.float64),
    ],
)
def test_prior_box_clustered(int_dtype, fp_dtype):
    image_size = np.array([64, 64], dtype=int_dtype)
    attributes = {
        "offset": fp_dtype(0.5),
        "width": np.array([4.0, 2.0, 3.2], dtype=fp_dtype),
        "height": np.array([1.0, 2.0, 1.0], dtype=fp_dtype),
    }

    output_size = ov.constant(np.array([19, 19], dtype=int_dtype), int_dtype)

    node = ov.prior_box_clustered(output_size, image_size, attributes)

    assert node.get_type_name() == "PriorBoxClustered"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 4332]


@pytest.mark.parametrize(
    "int_dtype, fp_dtype",
    [
        (np.uint8, np.float32),
        (np.uint16, np.float32),
        (np.uint32, np.float32),
        (np.uint64, np.float32),
        (np.uint32, np.float16),
        (np.uint32, np.float64),
    ],
)
def test_proposal(int_dtype, fp_dtype):
    attributes = {
        "base_size": int_dtype(1),
        "pre_nms_topn": int_dtype(20),
        "post_nms_topn": int_dtype(64),
        "nms_thresh": fp_dtype(0.34),
        "feat_stride": int_dtype(16),
        "min_size": int_dtype(32),
        "ratio": np.array([0.1, 1.5, 2.0, 2.5], dtype=fp_dtype),
        "scale": np.array([2, 3, 3, 4], dtype=fp_dtype),
    }
    batch_size = 7

    class_probs = ov.parameter([batch_size, 12, 34, 62], fp_dtype, "class_probs")
    bbox_deltas = ov.parameter([batch_size, 24, 34, 62], fp_dtype, "bbox_deltas")
    image_shape = ov.parameter([3], fp_dtype, "image_shape")
    node = ov.proposal(class_probs, bbox_deltas, image_shape, attributes)

    assert node.get_type_name() == "Proposal"
    assert node.get_output_size() == 2
    assert list(node.get_output_shape(0)) == [batch_size * attributes["post_nms_topn"], 5]


def test_tensor_iterator():
    #  Body parameters
    body_timestep = ov.parameter([], np.int32, "timestep")
    body_data_in = ov.parameter([1, 2, 2], np.float32, "body_in")
    body_prev_cma = ov.parameter([2, 2], np.float32, "body_prev_cma")
    body_const_one = ov.parameter([], np.int32, "body_const_one")

    # CMA = cumulative moving average
    prev_cum_sum = ov.multiply(ov.convert(body_timestep, "f32"), body_prev_cma)
    curr_cum_sum = ov.add(prev_cum_sum, ov.squeeze(body_data_in, [0]))
    elem_cnt = ov.add(body_const_one, body_timestep)
    curr_cma = ov.divide(curr_cum_sum, ov.convert(elem_cnt, "f32"))
    cma_hist = ov.unsqueeze(curr_cma, [0])

    # TI inputs
    data = ov.parameter([16, 2, 2], np.float32, "data")
    # Iterations count
    zero = ov.constant(0, dtype=np.int32)
    one = ov.constant(1, dtype=np.int32)
    initial_cma = ov.constant(np.zeros([2, 2], dtype=np.float32), dtype=np.float32)
    iter_cnt = ov.range(zero, np.int32(16), np.int32(1))

    graph_body = Model([curr_cma, cma_hist], [body_timestep, body_data_in,
                                              body_prev_cma, body_const_one], "body_function")

    node = ov.tensor_iterator()
    node.set_function(graph_body)
    node.set_sliced_input(body_timestep, iter_cnt.output(0), 0, 1, 1, -1, 0)
    node.set_sliced_input(body_data_in, data.output(0), 0, 1, 1, -1, 0)
    node.set_merged_input(body_prev_cma, initial_cma.output(0), curr_cma.output(0))
    node.set_invariant_input(body_const_one, one.output(0))

    node.get_iter_value(curr_cma.output(0), -1)
    node.get_concatenated_slices(cma_hist.output(0), 0, 1, 1, -1, 0)

    assert node.get_type_name() == "TensorIterator"
    assert node.get_output_size() == 2
    # final average
    assert list(node.get_output_shape(0)) == [2, 2]
    # cma history
    assert list(node.get_output_shape(1)) == [16, 2, 2]


def test_read_value_opset5():
    init_value = ov_opset5.parameter([2, 2], name="init_value", dtype=np.int32)

    node = ov_opset5.read_value(init_value, "var_id_667")

    assert node.get_type_name() == "ReadValue"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 2]
    assert node.get_output_element_type(0) == Type.i32


def test_assign_opset5():
    input_data = ov_opset5.parameter([5, 7], name="input_data", dtype=np.int32)
    rv = ov_opset5.read_value(input_data, "var_id_667")
    node = ov_opset5.assign(rv, "var_id_667")

    assert node.get_type_name() == "Assign"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [5, 7]
    assert node.get_output_element_type(0) == Type.i32


def test_read_value():
    init_value = ov.parameter([2, 2], name="init_value", dtype=np.int32)

    node = ov.read_value(init_value, "var_id_667")

    assert node.get_type_name() == "ReadValue"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 2]
    assert node.get_output_element_type(0) == Type.i32


def test_assign():
    input_data = ov.parameter([5, 7], name="input_data", dtype=np.int32)
    rv = ov.read_value(input_data, "var_id_667")
    node = ov.assign(rv, "var_id_667")

    assert node.get_type_name() == "Assign"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [5, 7]
    assert node.get_output_element_type(0) == Type.i32


def test_extract_image_patches():
    image = ov.parameter([64, 3, 10, 10], name="image", dtype=np.int32)
    sizes = [3, 3]
    strides = [5, 5]
    rates = [1, 1]
    padding = "VALID"
    node = ov.extract_image_patches(image, sizes, strides, rates, padding)

    assert node.get_type_name() == "ExtractImagePatches"
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [64, 27, 2, 2]
    assert node.get_output_element_type(0) == Type.i32


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_sequence_operator_bidirectional(dtype):
    batch_size = 1
    input_size = 16
    hidden_size = 128
    num_directions = 2
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    C_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 4 * hidden_size, input_size]
    R_shape = [num_directions, 4 * hidden_size, hidden_size]
    B_shape = [num_directions, 4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "BIDIRECTIONAL"
    node = ov.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node.get_type_name() == "LSTMSequence"
    assert node.get_output_size() == 3

    activations = ["RELU", "tanh", "Sigmoid"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22

    node_param = ov.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "LSTMSequence"
    assert node_param.get_output_size() == 3


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_sequence_operator_reverse(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    C_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 4 * hidden_size, input_size]
    R_shape = [num_directions, 4 * hidden_size, hidden_size]
    B_shape = [num_directions, 4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "REVERSE"

    node_default = ov.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "LSTMSequence"
    assert node_default.get_output_size() == 3

    activations = ["RELU", "tanh", "Sigmoid"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22

    node_param = ov.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "LSTMSequence"
    assert node_param.get_output_size() == 3


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_lstm_sequence_operator_forward(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    C_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 4 * hidden_size, input_size]
    R_shape = [num_directions, 4 * hidden_size, hidden_size]
    B_shape = [num_directions, 4 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_C_t = ov.parameter(C_t_shape, name="C_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "forward"

    node_default = ov.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "LSTMSequence"
    assert node_default.get_output_size() == 3

    activations = ["RELU", "tanh", "Sigmoid"]
    activation_alpha = [2.0]
    activation_beta = [1.0]
    clip = 0.5

    node = ov.lstm_sequence(
        parameter_X,
        parameter_H_t,
        parameter_C_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node.get_type_name() == "LSTMSequence"
    assert node.get_output_size() == 3


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_gru_sequence_operator_bidirectional(dtype):
    batch_size = 1
    input_size = 16
    hidden_size = 128
    num_directions = 2
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 3 * hidden_size, input_size]
    R_shape = [num_directions, 3 * hidden_size, hidden_size]
    B_shape = [num_directions, 3 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "BIDIRECTIONAL"
    node = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node.get_type_name() == "GRUSequence"
    assert node.get_output_size() == 2

    activations = ["RELU", "tanh"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22
    linear_before_reset = True
    B_shape = [num_directions, 4 * hidden_size]
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    node_param = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
        linear_before_reset
    )

    assert node_param.get_type_name() == "GRUSequence"
    assert node_param.get_output_size() == 2


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_gru_sequence_operator_reverse(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 3 * hidden_size, input_size]
    R_shape = [num_directions, 3 * hidden_size, hidden_size]
    B_shape = [num_directions, 3 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "REVERSE"

    node_default = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "GRUSequence"
    assert node_default.get_output_size() == 2

    activations = ["RELU", "tanh"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22
    linear_before_reset = True
    B_shape = [num_directions, 4 * hidden_size]
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    node_param = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
        linear_before_reset
    )

    assert node_param.get_type_name() == "GRUSequence"
    assert node_param.get_output_size() == 2


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_gru_sequence_operator_forward(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, 3 * hidden_size, input_size]
    R_shape = [num_directions, 3 * hidden_size, hidden_size]
    B_shape = [num_directions, 3 * hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "forward"

    node_default = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "GRUSequence"
    assert node_default.get_output_size() == 2

    activations = ["RELU", "tanh"]
    activation_alpha = [2.0]
    activation_beta = [1.0]
    clip = 0.5
    linear_before_reset = True
    B_shape = [num_directions, 4 * hidden_size]
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    node = ov.gru_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
        linear_before_reset
    )

    assert node.get_type_name() == "GRUSequence"
    assert node.get_output_size() == 2


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_rnn_sequence_operator_bidirectional(dtype):
    batch_size = 1
    input_size = 16
    hidden_size = 128
    num_directions = 2
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, hidden_size, input_size]
    R_shape = [num_directions, hidden_size, hidden_size]
    B_shape = [num_directions, hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "BIDIRECTIONAL"
    node = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node.get_type_name() == "RNNSequence"
    assert node.get_output_size() == 2

    activations = ["RELU", "tanh"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22

    node_param = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "RNNSequence"
    assert node_param.get_output_size() == 2


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_rnn_sequence_operator_reverse(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, hidden_size, input_size]
    R_shape = [num_directions, hidden_size, hidden_size]
    B_shape = [num_directions, hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "REVERSE"

    node_default = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "RNNSequence"
    assert node_default.get_output_size() == 2

    activations = ["RELU", "tanh"]
    activation_alpha = [1.0, 2.0, 3.0]
    activation_beta = [3.0, 2.0, 1.0]
    clip = 1.22

    node_param = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node_param.get_type_name() == "RNNSequence"
    assert node_param.get_output_size() == 2


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_rnn_sequence_operator_forward(dtype):
    batch_size = 2
    input_size = 4
    hidden_size = 3
    num_directions = 1
    seq_length = 2

    X_shape = [batch_size, seq_length, input_size]
    H_t_shape = [batch_size, num_directions, hidden_size]
    seq_len_shape = [batch_size]
    W_shape = [num_directions, hidden_size, input_size]
    R_shape = [num_directions, hidden_size, hidden_size]
    B_shape = [num_directions, hidden_size]

    parameter_X = ov.parameter(X_shape, name="X", dtype=dtype)
    parameter_H_t = ov.parameter(H_t_shape, name="H_t", dtype=dtype)
    parameter_seq_len = ov.parameter(seq_len_shape, name="seq_len", dtype=np.int32)
    parameter_W = ov.parameter(W_shape, name="W", dtype=dtype)
    parameter_R = ov.parameter(R_shape, name="R", dtype=dtype)
    parameter_B = ov.parameter(B_shape, name="B", dtype=dtype)

    direction = "forward"

    node_default = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
    )

    assert node_default.get_type_name() == "RNNSequence"
    assert node_default.get_output_size() == 2

    activations = ["RELU", "tanh"]
    activation_alpha = [2.0]
    activation_beta = [1.0]
    clip = 0.5

    node = ov.rnn_sequence(
        parameter_X,
        parameter_H_t,
        parameter_seq_len,
        parameter_W,
        parameter_R,
        parameter_B,
        hidden_size,
        direction,
        activations,
        activation_alpha,
        activation_beta,
        clip,
    )

    assert node.get_type_name() == "RNNSequence"
    assert node.get_output_size() == 2


def test_multiclass_nms():
    boxes_data = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.1, 1.0, 1.1,
                           0.0, -0.1, 1.0, 0.9, 0.0, 10.0, 1.0, 11.0,
                           0.0, 10.1, 1.0, 11.1, 0.0, 100.0, 1.0, 101.0], dtype="float32")
    boxes_data = boxes_data.reshape([1, 6, 4])
    box = ov.constant(boxes_data, dtype=np.float)
    scores_data = np.array([0.9, 0.75, 0.6, 0.95, 0.5, 0.3,
                            0.95, 0.75, 0.6, 0.80, 0.5, 0.3], dtype="float32")
    scores_data = scores_data.reshape([1, 2, 6])
    score = ov.constant(scores_data, dtype=np.float)

    nms_node = ov.multiclass_nms(box, score, output_type="i32", nms_top_k=3,
                                 iou_threshold=0.5, score_threshold=0.0, sort_result_type="classid",
                                 nms_eta=1.0)

    assert nms_node.get_type_name() == "MulticlassNms"
    assert nms_node.get_output_size() == 3
    assert nms_node.outputs()[0].get_partial_shape() == PartialShape([Dimension(0, 6), Dimension(6)])
    assert nms_node.outputs()[1].get_partial_shape() == PartialShape([Dimension(0, 6), Dimension(1)])
    assert list(nms_node.outputs()[2].get_shape()) == [1, ]
    assert nms_node.get_output_element_type(0) == Type.f32
    assert nms_node.get_output_element_type(1) == Type.i32
    assert nms_node.get_output_element_type(2) == Type.i32


def test_matrix_nms():
    boxes_data = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.1, 1.0, 1.1,
                           0.0, -0.1, 1.0, 0.9, 0.0, 10.0, 1.0, 11.0,
                           0.0, 10.1, 1.0, 11.1, 0.0, 100.0, 1.0, 101.0], dtype="float32")
    boxes_data = boxes_data.reshape([1, 6, 4])
    box = ov.constant(boxes_data, dtype=np.float)
    scores_data = np.array([0.9, 0.75, 0.6, 0.95, 0.5, 0.3,
                            0.95, 0.75, 0.6, 0.80, 0.5, 0.3], dtype="float32")
    scores_data = scores_data.reshape([1, 2, 6])
    score = ov.constant(scores_data, dtype=np.float)

    nms_node = ov.matrix_nms(box, score, output_type="i32", nms_top_k=3,
                             score_threshold=0.0, sort_result_type="score", background_class=0,
                             decay_function="linear", gaussian_sigma=2.0, post_threshold=0.0)

    assert nms_node.get_type_name() == "MatrixNms"
    assert nms_node.get_output_size() == 3
    assert nms_node.outputs()[0].get_partial_shape() == PartialShape([Dimension(0, 6), Dimension(6)])
    assert nms_node.outputs()[1].get_partial_shape() == PartialShape([Dimension(0, 6), Dimension(1)])
    assert list(nms_node.outputs()[2].get_shape()) == [1, ]
    assert nms_node.get_output_element_type(0) == Type.f32
    assert nms_node.get_output_element_type(1) == Type.i32
    assert nms_node.get_output_element_type(2) == Type.i32


def test_slice():
    data_shape = [10, 7, 2, 13]
    data = ov.parameter(data_shape, name="input", dtype=np.float32)

    start = ov.constant(np.array([2, 0, 0], dtype=np.int32))
    stop = ov.constant(np.array([9, 7, 2], dtype=np.int32))
    step = ov.constant(np.array([2, 1, 1], dtype=np.int32))

    node_default_axes = ov.slice(data, start, stop, step)

    assert node_default_axes.get_type_name() == "Slice"
    assert node_default_axes.get_output_size() == 1
    assert node_default_axes.get_output_element_type(0) == Type.f32
    assert tuple(node_default_axes.get_output_shape(0)) == np.zeros(data_shape)[2:9:2, ::, 0:2:1].shape

    start = ov.constant(np.array([0, 2], dtype=np.int32))
    stop = ov.constant(np.array([2, 9], dtype=np.int32))
    step = ov.constant(np.array([1, 2], dtype=np.int32))
    axes = ov.constant(np.array([-2, 0], dtype=np.int32))

    node = ov.slice(data, start, stop, step, axes)

    assert node.get_type_name() == "Slice"
    assert node.get_output_size() == 1
    assert node.get_output_element_type(0) == Type.f32
    assert tuple(node.get_output_shape(0)) == np.zeros(data_shape)[2:9:2, ::, 0:2:1].shape


def test_i420_to_bgr():
    expected_output_shape = [1, 480, 640, 3]

    # # Single plane (one arg)
    arg_single_plane = ov.parameter([1, 720, 640, 1], name="input", dtype=np.float32)
    node_single_plane = ov.i420_to_bgr(arg_single_plane)

    assert node_single_plane.get_type_name() == "I420toBGR"
    assert node_single_plane.get_output_size() == 1
    assert node_single_plane.get_output_element_type(0) == Type.f32
    assert list(node_single_plane.get_output_shape(0)) == expected_output_shape

    # Separate planes (three args)
    arg_y = ov.parameter([1, 480, 640, 1], name="input_y", dtype=np.float32)
    arg_u = ov.parameter([1, 240, 320, 1], name="input_u", dtype=np.float32)
    arg_v = ov.parameter([1, 240, 320, 1], name="input_v", dtype=np.float32)

    node_separate_planes = ov.i420_to_bgr(arg_y, arg_u, arg_v)

    assert node_separate_planes.get_type_name() == "I420toBGR"
    assert node_separate_planes.get_output_size() == 1
    assert node_separate_planes.get_output_element_type(0) == Type.f32
    assert list(node_separate_planes.get_output_shape(0)) == expected_output_shape

    # Incorrect inputs number
    with pytest.raises(UserInputError, match=r".*Operation I420toBGR*."):
        node_separate_planes = ov.i420_to_bgr(arg_y, arg_v)

    with pytest.raises(UserInputError, match=r".*Operation I420toBGR*."):
        node_separate_planes = ov.i420_to_bgr(arg_single_plane, None, arg_v)


def test_i420_to_rgb():
    expected_output_shape = [1, 480, 640, 3]

    # # Single plane (one arg)
    arg_single_plane = ov.parameter([1, 720, 640, 1], name="input", dtype=np.float32)
    node_single_plane = ov.i420_to_rgb(arg_single_plane)

    assert node_single_plane.get_type_name() == "I420toRGB"
    assert node_single_plane.get_output_size() == 1
    assert node_single_plane.get_output_element_type(0) == Type.f32
    assert list(node_single_plane.get_output_shape(0)) == expected_output_shape

    # Separate planes (three args)
    arg_y = ov.parameter([1, 480, 640, 1], name="input_y", dtype=np.float32)
    arg_u = ov.parameter([1, 240, 320, 1], name="input_u", dtype=np.float32)
    arg_v = ov.parameter([1, 240, 320, 1], name="input_v", dtype=np.float32)

    node_separate_planes = ov.i420_to_rgb(arg_y, arg_u, arg_v)

    assert node_separate_planes.get_type_name() == "I420toRGB"
    assert node_separate_planes.get_output_size() == 1
    assert node_separate_planes.get_output_element_type(0) == Type.f32
    assert list(node_separate_planes.get_output_shape(0)) == expected_output_shape

    with pytest.raises(UserInputError, match=r".*Operation I420toRGB*."):
        node_separate_planes = ov.i420_to_rgb(arg_y, arg_v)

    with pytest.raises(UserInputError, match=r".*Operation I420toRGB*."):
        node_separate_planes = ov.i420_to_rgb(arg_single_plane, None, arg_v)


def test_nv12_to_bgr():
    expected_output_shape = [1, 480, 640, 3]

    # # Single plane (one arg)
    arg_single_plane = ov.parameter([1, 720, 640, 1], name="input", dtype=np.float32)
    node_single_plane = ov.nv12_to_bgr(arg_single_plane)

    assert node_single_plane.get_type_name() == "NV12toBGR"
    assert node_single_plane.get_output_size() == 1
    assert node_single_plane.get_output_element_type(0) == Type.f32
    assert list(node_single_plane.get_output_shape(0)) == expected_output_shape

    # Separate planes (two args)
    arg_y = ov.parameter([1, 480, 640, 1], name="input_y", dtype=np.float32)
    arg_uv = ov.parameter([1, 240, 320, 2], name="input_uv", dtype=np.float32)

    node_separate_planes = ov.nv12_to_bgr(arg_y, arg_uv)

    assert node_separate_planes.get_type_name() == "NV12toBGR"
    assert node_separate_planes.get_output_size() == 1
    assert node_separate_planes.get_output_element_type(0) == Type.f32
    assert list(node_separate_planes.get_output_shape(0)) == expected_output_shape


def test_nv12_to_rgb():
    expected_output_shape = [1, 480, 640, 3]

    # # Single plane (one arg)
    arg_single_plane = ov.parameter([1, 720, 640, 1], name="input", dtype=np.float32)
    node_single_plane = ov.nv12_to_rgb(arg_single_plane)

    assert node_single_plane.get_type_name() == "NV12toRGB"
    assert node_single_plane.get_output_size() == 1
    assert node_single_plane.get_output_element_type(0) == Type.f32
    assert list(node_single_plane.get_output_shape(0)) == expected_output_shape

    # Separate planes (two args)
    arg_y = ov.parameter([1, 480, 640, 1], name="input_y", dtype=np.float32)
    arg_uv = ov.parameter([1, 240, 320, 2], name="input_uv", dtype=np.float32)

    node_separate_planes = ov.nv12_to_rgb(arg_y, arg_uv)

    assert node_separate_planes.get_type_name() == "NV12toRGB"
    assert node_separate_planes.get_output_size() == 1
    assert node_separate_planes.get_output_element_type(0) == Type.f32
    assert list(node_separate_planes.get_output_shape(0)) == expected_output_shape

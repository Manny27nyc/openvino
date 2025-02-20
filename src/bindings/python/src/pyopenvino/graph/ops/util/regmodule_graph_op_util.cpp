// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#include "regmodule_graph_op_util.hpp"

#include <pybind11/pybind11.h>

namespace py = pybind11;

void regmodule_graph_op_util(py::module m) {
    py::module m_util = m.def_submodule("util", "module openvino.op.util");
    //    regclass_graph_op_util_RequiresTensorViewArgs(m_util);
    regclass_graph_op_util_ArithmeticReduction(m_util);
    //    regclass_graph_op_util_BinaryElementwise(m_util);
    regclass_graph_op_util_BinaryElementwiseArithmetic(m_util);
    regclass_graph_op_util_BinaryElementwiseComparison(m_util);
    regclass_graph_op_util_BinaryElementwiseLogical(m_util);
    //    regclass_graph_op_util_UnaryElementwise(m_util);
    regclass_graph_op_util_UnaryElementwiseArithmetic(m_util);
    regclass_graph_op_util_IndexReduction(m_util);
    regclass_graph_op_util_Variable(m_util);
    regclass_graph_op_util_MultiSubgraphOp(m_util);
}

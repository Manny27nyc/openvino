// Copyright (C) 2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include <memory>
#include <vector>

#include <ngraph/node.hpp>
#include <ngraph/variant.hpp>
#include "low_precision/lpt_visibility.hpp"
#include "low_precision/rt_info/shared_value_attribute.hpp"

namespace ngraph {
/**
 * @ingroup ie_transformation_common_api
 * @brief PrecisionPreservedAttribute defines the precision preserved operation. If the attribute is absent, then an operation is
 * not precision preserved.
 *
 * For more details about the attribute, refer to
 * [PrecisionPreservedAttribute](@ref openvino_docs_IE_DG_lpt_PrecisionPreserved) page in the Inference Engine Developer Guide.
 */
class LP_TRANSFORMATIONS_API PrecisionPreservedAttribute : public SharedAttribute<bool> {
public:
    OPENVINO_RTTI("LowPrecision::PrecisionPreserved", "", ov::RuntimeAttribute, 0);

    PrecisionPreservedAttribute() = default;
    PrecisionPreservedAttribute(const bool value);

    std::string to_string() const override;
};

} // namespace ngraph

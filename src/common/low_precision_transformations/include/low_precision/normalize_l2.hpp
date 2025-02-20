// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include "layer_transformation.hpp"

namespace ngraph {
namespace pass {
namespace low_precision {

/**
 * @ingroup ie_transformation_common_api
 * @brief NormalizeL2Transformation propagates dequantization operations through NormalizeL2 operation.
 *
 * For more details about the transformation, refer to
 * [NormalizeL2Transformation](@ref openvino_docs_IE_DG_lpt_NormalizeL2Transformation) page
 * in the Inference Engine Developer Guide.
 */
class LP_TRANSFORMATIONS_API NormalizeL2Transformation : public LayerTransformation {
public:
    NGRAPH_RTTI_DECLARATION;
    NormalizeL2Transformation(const Params& params = Params());
    bool transform(TransformationContext &context, ngraph::pattern::Matcher &m) override;
    bool canBeTransformed(const TransformationContext& context, std::shared_ptr<Node> layer) const override;
    bool isPrecisionPreserved(std::shared_ptr<Node> layer) const noexcept override;
};

}  // namespace low_precision
}  // namespace pass
}  // namespace ngraph

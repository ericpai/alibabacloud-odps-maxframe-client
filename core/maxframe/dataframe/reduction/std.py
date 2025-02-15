# Copyright 1999-2025 Alibaba Group Holding Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ...tensor.arithmetic import sqrt
from .var import var_dataframe, var_series


def std_dataframe(
    df,
    axis=None,
    skipna=True,
    level=None,
    ddof=1,
    numeric_only=None,
    method=None,
):
    ret = sqrt(
        var_dataframe(
            df,
            axis=axis,
            skipna=skipna,
            level=level,
            ddof=ddof,
            numeric_only=numeric_only,
            method=method,
        )
    )
    return ret


def std_series(series, axis=None, skipna=True, level=None, ddof=1, method=None):
    ret = sqrt(
        var_series(
            series,
            axis=axis,
            skipna=skipna,
            level=level,
            ddof=ddof,
            method=method,
        )
    )
    return ret

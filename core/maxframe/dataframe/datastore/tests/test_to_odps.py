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

import pytest

from ... import DataFrame
from ..to_odps import to_odps_table


@pytest.fixture
def df():
    return DataFrame({"A": [1, 2], "B": [3, 4]})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"partition_col": ["A", "C"]},
        {"partition_col": "C"},
        {"partition": "a=1,C=2"},
    ],
)
def test_to_odps_table_validation(df, kwargs):
    with pytest.raises(ValueError):
        to_odps_table(df, "test_table", **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"partition_col": ["a", "B"]},
        {"partition_col": "a"},
        {"partition": "C=1,d=2"},
    ],
)
def test_to_odps_table_vaild(df, kwargs):
    to_odps_table(df, "test_table", **kwargs)

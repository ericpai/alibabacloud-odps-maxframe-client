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

import itertools
from typing import List

from ....typing_ import TileableType
from ...mode import enter_mode
from ..entity import EntityGraph, TileableGraph
from .tileable import TileableGraphBuilder


@enter_mode(kernel=True)
def build_graph(
    tileables: List[TileableType],
    tile: bool = False,
    fuse_enabled: bool = True,
    **chunk_graph_build_kwargs
) -> EntityGraph:
    tileables = list(itertools.chain(*(tileable.op.outputs for tileable in tileables)))
    tileable_graph = TileableGraph(tileables)
    tileable_graph_builder = TileableGraphBuilder(tileable_graph)
    tileable_graph = next(tileable_graph_builder.build())
    if not tile:
        return tileable_graph
    raise NotImplementedError

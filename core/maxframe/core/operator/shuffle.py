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

from ... import opcodes
from ...serialization.serializables import (
    FieldTypes,
    Int32Field,
    StringField,
    TupleField,
)
from . import FetchShuffle, ShuffleFetchType
from .base import Operator, OperatorStage, VirtualOperator


class ShuffleProxy(VirtualOperator):
    _op_type_ = opcodes.SHUFFLE_PROXY
    n_mappers = Int32Field("n_mappers", default=0)
    # `n_reducers` will be updated in `MapReduceOperator._new_chunks`
    n_reducers = Int32Field("n_reducers", default=0)


class MapReduceOperator(Operator):
    """
    An operator for shuffle execution which partitions data by the value in each record’s partition key, and
    send the partitioned data from all mappers to all reducers.
    """

    # for reducer
    reducer_index = TupleField("reducer_index", FieldTypes.uint64)
    # Total reducer nums, which also be shuffle blocks for single mapper.
    n_reducers = Int32Field("n_reducers")
    # The reducer ordinal in all reducers. It's different from reducer_index,
    # which might be a tuple.
    # `reducer_ordinal` will be set in `_new_chunks`.
    reducer_ordinal = Int32Field("reducer_ordinal")
    reducer_phase = StringField("reducer_phase", default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.stage == OperatorStage.reduce:
            # for reducer, we assign worker at first
            self.scheduling_hint.reassign_worker = True

    def get_dependent_data_keys(self):
        from .fetch import FetchShuffle

        if self.stage == OperatorStage.reduce:
            inputs = self.inputs or ()
            deps = []
            for inp in inputs:
                if isinstance(inp.op, ShuffleProxy):
                    deps.extend(
                        [(chunk.key, self.reducer_index) for chunk in inp.inputs or ()]
                    )
                elif isinstance(inp.op, FetchShuffle):
                    # fetch shuffle by index doesn't store data keys, so it won't run into this function.
                    assert inp.op.shuffle_fetch_type == ShuffleFetchType.FETCH_BY_KEY
                    deps.extend([(k, self.reducer_index) for k in inp.op.source_keys])
                else:
                    deps.append(inp.key)
            return deps
        return super().get_dependent_data_keys()

    def iter_mapper_keys(self, input_id=0):
        # key is mapper chunk key, index is mapper chunk index.
        input_chunk = self.inputs[input_id]
        if isinstance(input_chunk.op, ShuffleProxy):
            keys = [inp.key for inp in input_chunk.inputs]
        else:
            assert isinstance(input_chunk.op, FetchShuffle), input_chunk.op
            if input_chunk.op.shuffle_fetch_type == ShuffleFetchType.FETCH_BY_INDEX:
                # For fetch shuffle by index, all shuffle block of same reducers are
                # identified by their index. chunk key are not needed any more.
                # so just mock key here.
                # keep this in sync with ray executor `execute_subtask`.
                return list(range(input_chunk.op.n_mappers))
            keys = input_chunk.op.source_keys
        return keys

    def iter_mapper_data(self, ctx, input_id=0, pop=False, skip_none=False):
        for key in self.iter_mapper_keys(input_id):
            try:
                if pop:
                    yield ctx.pop((key, self.reducer_index))
                else:
                    yield ctx[key, self.reducer_index]
            except KeyError:
                if not skip_none:  # pragma: no cover
                    raise
                if not pop:
                    ctx[key, self.reducer_index] = None

    def execute(self, ctx, op):
        """The mapper stage must ensure all mapper blocks are inserted into ctx
        and no blocks for some reducers are missing. This is needed by shuffle
        fetch by index, which shuffle block are identified by the  index instead
        of data keys. For operators implementation simplicity, we can sort the
        `ctx` by key which are (chunk key, reducer index) tuple and relax the
        insert order requirements.
        """

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function

import numpy as np
import unittest
import faiss


class TestFactory(unittest.TestCase):

    def test_factory_1(self):

        index = faiss.index_factory(12, "IVF10,PQ4")
        assert index.do_polysemous_training

        index = faiss.index_factory(12, "IVF10,PQ4np")
        assert not index.do_polysemous_training

        index = faiss.index_factory(12, "PQ4")
        assert index.do_polysemous_training

        index = faiss.index_factory(12, "PQ4np")
        assert not index.do_polysemous_training

        try:
            index = faiss.index_factory(10, "PQ4")
        except RuntimeError:
            pass
        else:
            assert False, "should do a runtime error"

    def test_factory_2(self):

        index = faiss.index_factory(12, "SQ8")
        assert index.code_size == 12

    def test_factory_3(self):

        index = faiss.index_factory(12, "IVF10,PQ4")
        faiss.ParameterSpace().set_index_parameter(index, "nprobe", 3)
        assert index.nprobe == 3

        index = faiss.index_factory(12, "PCAR8,IVF10,PQ4")
        faiss.ParameterSpace().set_index_parameter(index, "nprobe", 3)
        assert faiss.downcast_index(index.index).nprobe == 3

    def test_factory_4(self):
        index = faiss.index_factory(12, "IVF10,FlatDedup")
        assert index.instances is not None

    def test_factory_HNSW(self):
        index = faiss.index_factory(12, "HNSW32")
        assert index.storage.sa_code_size() == 12 * 4
        index = faiss.index_factory(12, "HNSW32_SQ8")
        assert index.storage.sa_code_size() == 12
        index = faiss.index_factory(12, "HNSW32_PQ4")
        assert index.storage.sa_code_size() == 4

    def test_factory_HNSW_newstyle(self):
        index = faiss.index_factory(12, "HNSW32,Flat")
        assert index.storage.sa_code_size() == 12 * 4
        index = faiss.index_factory(12, "HNSW32,SQ8", faiss.METRIC_INNER_PRODUCT)
        assert index.storage.sa_code_size() == 12
        assert index.metric_type == faiss.METRIC_INNER_PRODUCT
        index = faiss.index_factory(12, "HNSW32,PQ4")
        assert index.storage.sa_code_size() == 4
        index = faiss.index_factory(12, "HNSW32,PQ4np")
        indexpq = faiss.downcast_index(index.storage)
        assert not indexpq.do_polysemous_training

    def test_factory_fast_scan(self):
        index = faiss.index_factory(56, "PQ28x4fs")
        self.assertEqual(index.bbs, 32)
        index = faiss.index_factory(56, "PQ28x4fs_64")
        self.assertEqual(index.bbs, 64)
        index = faiss.index_factory(56, "IVF50,PQ28x4fs_64", faiss.METRIC_INNER_PRODUCT)
        self.assertEqual(index.bbs, 64)
        self.assertEqual(index.nlist, 50)
        self.assertTrue(index.cp.spherical)
        index = faiss.index_factory(56, "PQ28x4fs,RFlat")
        self.assertEqual(index.k_factor, 1.0)

    def test_parenthesis(self):
        index = faiss.index_factory(50, "IVF32(PQ25),Flat")
        quantizer = faiss.downcast_index(index.quantizer)
        self.assertEqual(quantizer.pq.M, 25)


class TestCloneSize(unittest.TestCase):

    def test_clone_size(self):
        index = faiss.index_factory(20, 'PCA10,Flat')
        xb = faiss.rand((100, 20))
        index.train(xb)
        index.add(xb)
        index2 = faiss.clone_index(index)
        assert index2.ntotal == 100

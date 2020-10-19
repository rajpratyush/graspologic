# Copyright (c) Microsoft Corporation and contributors.
# Licensed under the MIT License.

import pytest
import unittest
import numpy as np
import networkx as nx
from sklearn.metrics import pairwise_distances

from graspologic.embed import AdjacencySpectralEmbed
from graspologic.inference import ldt_function
from graspologic.simulations import er_np, sbm


def test_bad_kwargs():
    np.random.seed(123456)
    A1 = er_np(20, 0.3)
    A2 = er_np(20, 0.3)

    # check test argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, test=0)
    with pytest.raises(ValueError):
        ldt_function(A1, A2, test="foo")
    # check metric argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, metric=0)
    with pytest.raises(ValueError):
        ldt_function(A1, A2, metric="some_kind_of_kernel")
    # check n_components argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, n_components=0.5)
    with pytest.raises(ValueError):
        ldt_function(A1, A2, n_components=-100)
    # check n_bootstraps argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, n_bootstraps=0.5)
    with pytest.raises(ValueError):
        ldt_function(A1, A2, n_bootstraps=-100)
    # check workers argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, workers=0.5)
    # check size_correction argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, size_correction=0)
    # check pooled argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, pooled=0)
    # check align_type argument
    with pytest.raises(ValueError):
        ldt_function(A1, A2, align_type="foo")
    with pytest.raises(TypeError):
        ldt_function(A1, A2, align_type={"not a": "string"})
    # check align_kws argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, align_kws="foo")
    # check input_graph argument
    with pytest.raises(TypeError):
        ldt_function(A1, A2, input_graph="hello")


def test_n_bootstraps():
    A1 = er_np(20, 0.3)
    A2 = er_np(20, 0.3)

    _, _, null_distribution_ = lpt_function(A1, A2, n_bootstraps=123)
    assert null_distribution_.shape[0] == 123


def test_passing_networkx():
    np.random.seed(123)
    A1 = er_np(20, 0.8)
    A2 = er_np(20, 0.8)
    A1_nx = nx.from_numpy_matrix(A1)
    A2_nx = nx.from_numpy_matrix(A2)
    # check passing nx, when exepect embeddings
    with pytest.raises(TypeError):
        ldt_function(A1_nx, A1, input_graph=False)
    with pytest.raises(TypeError):
        ldt_function(A1, A2_nx, input_graph=False)
    with pytest.raises(TypeError):
        ldt_function(A1_nx, A2_nx, input_graph=False)
    # check that the appropriate input works
    ldt_function(A1_nx, A2_nx, input_graph=True)


def test_passing_embeddings():
    np.random.seed(123)
    A1 = er_np(20, 0.8)
    A2 = er_np(20, 0.8)
    ase_1 = AdjacencySpectralEmbed(n_components=2)
    X1 = ase_1.fit_transform(A1)
    ase_2 = AdjacencySpectralEmbed(n_components=2)
    X2 = ase_2.fit_transform(A2)
    ase_3 = AdjacencySpectralEmbed(n_components=1)
    X3 = ase_3.fit_transform(A2)
    # check embeddings having weird ndim
    with pytest.raises(ValueError):
        ldt_function(X1, X2.reshape(-1, 1, 1), input_graph=False)
    with pytest.raises(ValueError):
        ldt_function(X1.reshape(-1, 1, 1), X2, input_graph=False)
    # check embeddings having mismatching number of components
    with pytest.raises(ValueError):
        ldt_function(X1, X3, input_graph=False)
    with pytest.raises(ValueError):
        ldt_function(X3, X1, input_graph=False)
    # check passing weird stuff as input (caught by us)
    with pytest.raises(TypeError):
        ldt_function("hello there", X1, input_graph=False)
    with pytest.raises(TypeError):
        ldt_function(X1, "hello there", input_graph=False)
    with pytest.raises(TypeError):
        ldt_function({"hello": "there"}, X1, input_graph=False)
    with pytest.raises(TypeError):
        ldt_function(X1, {"hello": "there"}, input_graph=False)
    # check passing infinite in input (caught by check_array)
    with pytest.raises(ValueError):
        X1_w_inf = X1.copy()
        X1_w_inf[1, 1] = np.inf
        ldt_function(X1_w_inf, X2, input_graph=False)
    # check that the appropriate input works
    ldt_function(X1, X2, input_graph=False)


def test_pooled():
    np.random.seed(123)
    A1 = er_np(20, 0.3)
    A2 = er_np(100, 0.3)
    ldt_function(A1, A2, pooled=True)


def test_distances_and_kernels():
    np.random.seed(123)
    A1 = er_np(20, 0.3)
    A2 = er_np(100, 0.3)
    # some valid combinations of test and metric
    # # would love to do this, but currently FutureWarning breaks this
    # with pytest.warns(None) as record:
    #     for test in self.tests.keys():
    #         ldt = LatentDistributionTest(test, self.tests[test])
    #         ldt.fit(A1, A2)
    #     ldt = LatentDistributionTest("hsic", "rbf")
    #     ldt.fit(A1, A2)
    # assert len(record) == 0
    ldt_function(A1, A2, test="hsic", metric="rbf")
    # some invalid combinations of test and metric
    with pytest.warns(UserWarning):
        ldt_function(A1, A2, "hsic", "euclidean")
    with pytest.warns(UserWarning):
        ldt_function(A1, A2, "dcorr", "gaussian")
    with pytest.warns(UserWarning):
        ldt_function(A1, A2, "dcorr", "rbf")


def test_bad_matrix_inputs():
    np.random.seed(1234556)
    A1 = er_np(20, 0.3)
    A2 = er_np(20, 0.3)

    bad_matrix = [[1, 2]]
    with pytest.raises(TypeError):
        ldt_function(bad_matrix, A2, test="dcorr")


def test_directed_inputs(self):
    np.random.seed(2)
    A = er_np(100, 0.3, directed=True)
    B = er_np(100, 0.3, directed=True)
    C = er_np(100, 0.3, directed=False)

    # two directed graphs is okay
    ldt_function(A, B)

    # an undirected and a direced graph is not okay
    with pytest.aises(ValueError):
        ldt_function(A, C)
    with pytest.raises(ValueError):
        ldt_function(C, B)


def test_SBM_dcorr():
    np.random.seed(12345678)
    B1 = np.array([[0.5, 0.2], [0.2, 0.5]])

    B2 = np.array([[0.7, 0.2], [0.2, 0.7]])
    b_size = 200
    A1 = sbm(2 * [b_size], B1)
    A2 = sbm(2 * [b_size], B1)
    A3 = sbm(2 * [b_size], B2)
    p_null = ldt_function(A1, A2)
    p_alt = ldt_funciton(A1, A3)
    assert p_null > 0.05
    assert p_alt <= 0.05


def test_different_sizes_null():
    np.random.seed(314)

    A1 = er_np(100, 0.8)
    A2 = er_np(1000, 0.8)

    ldt_not_corrected = LatentDistributionTest(
        "hsic", "gaussian", n_components=2, n_bootstraps=100, size_correction=False
    )
    ldt_corrected_1 = LatentDistributionTest(
        "hsic", "gaussian", n_components=2, n_bootstraps=100, size_correction=True
    )
    ldt_corrected_2 = LatentDistributionTest(
        "hsic", "gaussian", n_components=2, n_bootstraps=100, size_correction=True
    )

    p_not_corrected = ldt_function(
        A1,
        A2,
        test="hsic",
        metric="gaussian",
        n_components=2,
        n_bootstraps=100,
        size_correction=False,
    )
    p_corrected_1 = ldt_function(
        A1,
        A2,
        test="hsic",
        metric="gaussian",
        n_components=2,
        n_bootstraps=100,
        size_correction=True,
    )
    p_corrected_2 = ldt_function(
        A2,
        A1,
        test="hsic",
        metric="gaussian",
        n_components=2,
        n_bootstraps=100,
        size_correction=True,
    )

    assert p_not_corrected <= 0.05
    assert p_corrected_1 > 0.05
    assert p_corrected_2 > 0.05


def test_different_sizes_null(self):
    np.random.seed(314)

    A1 = er_np(100, 0.8)
    A2 = er_np(1000, 0.7)

    ldt_corrected_1 = LatentDistributionTest(
        "hsic", "gaussian", n_components=2, n_bootstraps=100, size_correction=True
    )
    ldt_corrected_2 = LatentDistributionTest(
        "hsic", "gaussian", n_components=2, n_bootstraps=100, size_correction=True
    )

    p_corrected_1 = ldt_function(
        A1,
        A2,
        test="hsic",
        metric="gaussian",
        n_components=2,
        n_bootstraps=100,
        size_correction=True,
    )
    p_corrected_2 = ldt_function(
        A2,
        A1,
        test="hsic",
        metric="gaussian",
        n_components=2,
        n_bootstraps=100,
        size_correction=True,
    )

    assert p_corrected_1 <= 0.05
    assert p_corrected_2 <= 0.05


def test_different_aligners(self):
    np.random.seed(314)
    A1 = er_np(100, 0.8)
    A2 = er_np(100, 0.8)
    ase_1 = AdjacencySpectralEmbed(n_components=2)
    X1 = ase_1.fit_transform(A1)
    ase_2 = AdjacencySpectralEmbed(n_components=2)
    X2 = ase_2.fit_transform(A2)
    X2 = -X2

    p_val_1, _, _ = ldt_function(A1, A2, input_graph=False, align_type=None)
    assert p_val_1 < 0.05

    p_val_2 = ldt_function(A1, A2, input_graph=False, align_type="sign_flips")
    assert p_val_2 >= 0.05

    # also checking that kws are passed through
    ldt_3 = LatentDistributionTest(
        input_graph=False,
        align_type="seedless_procrustes",
        align_kws={"init": "sign_flips"},
    )
    p_val_3 = ldt_function(
        X1,
        X2,
        input_graph=False,
        align_type="seedless_procrustes",
        align_kws={"init": "sign_flips"},
    )
    assert p_val_3 >= 0.05

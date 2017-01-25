#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    25.01.2017 15:14:49 CET
# File:    analyse.py

from collections import namedtuple

from .expr_utils import expr_to_vector, monomial_basis, matrix_to_expr_operator
from .repr_utils import hermitian_to_vector, hermitian_basis, repr_to_matrix_operator
from .linalg import intersection_basis
from .to_matrix import to_matrix

Representation = namedtuple('Representation', ['matrix', 'complex_conjugate'])
SymmetryOperation = namedtuple('SymmetryOperation', ['kmatrix', 'repr'])

def symmetric_hamiltonian(*symmetry_operations, power):
    expr_basis = monomial_basis(power)
    repr_basis = hermitian_basis(dim=symmetry_operations[0].repr.matrix.shape[0])
    expr_dim = len(expr_basis)
    repr_dim = len(repr_basis)
    full_dim = expr_dim * repr_dim
    full_basis = [
        sp.Matrix(x) for x in 
        np.outer(expr_basis, repr_basis).reshape(full_dim, repr_dim, repr_dim).tolist()
    ]
    
    invariant_bases = []
    for op in symmetry_operations:
        # create the matrix form of the two operators
        expr_mat = to_matrix(
            operator=matrix_to_expr_operator(op.kmatrix),
            basis=expr_basis,
            to_vector_fct=expr_to_vector
        )
        repr_mat = to_matrix(
            operator=repr_to_matrix_operator(*op.repr),
            basis=repr_basis,
            to_vector_fct=hermitian_to_vector
        )
        # outer product
        full_mat = sp.matrix(
            np.einsum('ac,bd->abcd', expr_mat, repr_mat).reshape((full_dim, full_dim))
        )
        # get Eig(F \ocross G, 1) basis
        invariant_bases.append(
            np.array(
                (full_mat - sp.eye(full_dim)).nullspace()
            ).tolist()
        )
    
    basis_vectors = intersection_basis(*invariant_bases)
    basis_vectors_expanded = []
    for vec in basis_vectors:
        basis_vectors_expanded.append(
            sum((v * b for v, b in zip(vec, full_basis)), sp.zeros(repr_dim))
        )
    return basis_vectors, full_basis, basis_vectors_expanded


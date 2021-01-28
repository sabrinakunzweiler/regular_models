r"""
Lattices over discrete valuation rings
======================================

We define a class ``DVR_Lattice``. An object of this class represents a
*lattice* `M`, i.e.\ a free `R`-submodule of a finite-dimensional `K`-vector
space `V`. Here `K` is a field equipped with a discrete valuation `v_K` and
`R` is the valuation ring of `v_K`.

For the moment, the `K`-vector space is always a standard vector space `K^n`.
A lattice `M\subset K^n` is determined by a finite list of generators.

The functionality provided by this class includes

- finding a basis of a lattice given by a list of generators,
- computing intersections and sums of lattices with the same ambient vector space.


AUTHORS:

- Stefan Wewers (2019): initial version


EXAMPLES::

    sage: import regular_models.RR_spaces.lattices
    sage: from regular_models.RR_spaces.lattices import DVR_Lattice

We define a `\mathbb{Z}_2`-lattice of rank `2` inside `\mathbb{Q}^3`. ::

    sage: v_2 = QQ.valuation(2)
    sage: V = QQ^3
    sage: v1 = V([1,-1,-2])
    sage: v2 = V([2, 4, 1])
    sage: M1 = DVR_Lattice(v_2, [v1, v2]); M1
    a lattices of rank 2 over the valuation ring of 2-adic valuation

We compute the intersection with another lattice. ::

    sage: w1 = V([0, 2, 1])
    sage: w2 = V([8, 1, 1])
    sage: M2 = DVR_Lattice(v_2, [w1, w2])
    sage: M3 = M1.intersection(M2); M3
    a lattices of rank 1 over the valuation ring of 2-adic valuation
    sage: M3.basis()
    [(32/61, 118/61, 1)]


"""


# *****************************************************************************
#       Copyright (C) 2019 Stefan Wewers <stefan.wewers@uni-ulm.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# *****************************************************************************


from sage.all import SageObject, copy, matrix


class DVR_Lattice(SageObject):
    r""" Return a lattice over a dvr with given generators.

    INPUT:

    - ``v`` -- a discrete valuation on a field `K`, with dvr `R`
    - ``gens`` -- a list of vectors in `K^n`

    OUTPUT:

    the `R`-lattice `M` generated by the given generators.

    """

    def __init__(self, v, gens):
        K = v.domain()
        assert gens != [], "the list of generators must not be empty"
        assert all([m.base_ring() == K for m in gens]), "the coefficients of the\
            generators must lie in the domain of v"
        n = len(gens[0])
        assert all([len(m) == n for m in gens]), "all generators must lie in the same vector space"
        basis = find_basis(v, gens)
        self._v = v
        self._K = K
        self._n = n
        self._basis = basis
        self._rank = len(basis)

    def __repr__(self):
        return "a lattices of rank {} over the valuation ring of {}".format(self.rank(), self.valuation())

    def valuation(self):
        return self._v

    def base_field(self):
        return self._K

    def rank(self):
        return self._rank

    def basis(self):
        return self._basis

    def basis_matrix(self):
        return matrix(self.basis()).transpose()

    def embedding_dimension(self):
        return self._n

    def intersection(self, other):
        r""" Return the intersection of this lattice with another one.

        INPUT:

        - ``other`` -- a lattices over the same dvr and inside the same vector
          space as ``self``.

        OUTPUT:

        the lattice which is the intersection of ``self`` with ``other``.

        """
        v = self.valuation()
        assert v == other.valuation(), "the two lattices must be defined\
            over the same dvr."
        assert self.embedding_dimension() == other.embedding_dimension(),\
            "the two lattices must lie in the same vector space."
        n1 = self.rank()
        A1 = self.basis_matrix()
        A2 = other.basis_matrix()
        A = A1.augment(A2)
        kern = kernel_basis(v, A)
        return DVR_Lattice(v, [A1*(w[:n1]) for w in kern])


# ---------------------------------------------------------------------------

#                          auxiliary functions


def find_basis(v, gens):
    r""" Return a basis of the dvr-lattice with given generators.

    INPUT:

    - ``v`` -- a discrete valuation on a field `K`
    - ``gens`` -- a nonempty list of vectors in `K^n`

    OUTPUT: a list of vectors in `K^n` which forms an `R`-basis of the
    `R`-submodule of `K^n` generated by ``gens``. Here `R` is the valuation
    ring of `v`.

    """
    # A is the matrix with columns the vectors in `gens`
    A = matrix(gens).transpose()
    D, S, T, rank = smith_normal_form(A, v)
    return (S*D).columns()[:rank]


def smith_normal_form(A, v):
    r""" Return the Smith normal form of the matrix ``A``.

    INPUT:

    - ``A`` -- a matrix over a field `K`
    - ``v`` -- a discrete valuation on `K`

    OUTPUT:

    a tuple`(D, S, T, rank)` `D, S, T` matrices, such that

    .. MATH::

        S\cdot A\codt T = D,

    where `S` and `T` are square invertible matrices over the valuation ring `R`
    of `v`, `D` is the Smith normal form of `A` over `R`, and `rank` is the rank of `D`.

    """
    K = A.base_ring()
    m = A.nrows()
    n = A.ncols()
    # assert all([v(a) >= 0 for a in A.coefficients()]), "A must have integral coefficients"
    D = copy(A)
    S = matrix.identity(K, m)
    T = matrix.identity(K, n)
    k = - 1
    while not D.submatrix(k + 1, k + 1).is_zero():
        # the parameter k indicates that the rows i=0,..,k and columns j=0,..,k
        # are already in the required form
        i, j, e = find_pivot(v, D, k)
        # the entry D[i, j] is the next entry with the smallest valuation e
        switch_rows(D, k + 1, i)
        switch_columns(S, k + 1, i)
        switch_columns(D, k + 1, j)
        switch_rows(T, k + 1, j)
        assert A == S*D*T, "something is wrong!"
        # now D[k + 1, k + 1] is a nonzero entry, with minimal valuation e
        a0 = v.element_with_valuation(e)
        a = a0/D[k + 1, k + 1]
        D.rescale_col(k + 1, a)
        T.rescale_row(k + 1, 1/a)
        assert A == S*D*T, "something is wrong!"
        for j in range(k + 2, n):
            if not D[k + 1, j].is_zero():
                x = - D[k + 1, j]/a0
                D.add_multiple_of_column(j, k + 1, x)
                T.add_multiple_of_row(k + 1, j, -x)
                assert A == S*D*T, "something is wrong!"
        # now we kill the rest of the (k+1)th column
        for i in range(k + 2, m):
            if not D[i, k + 1].is_zero():
                x = -D[i, k + 1]/a0
                D.add_multiple_of_row(i, k + 1, x)
                S.add_multiple_of_column(k + 1, i, -x)
                assert A == S*D*T, "something is wrong!"
        if k < n - 1 and k < m - 1:
            k += 1
    assert v(S.determinant()) == 0, "S is not invertible!"
    assert v(T.determinant()) == 0, "T is not invertible!"
    return D, S, T, k + 1


def find_pivot(v, A, k):
    r""" Return the position of the entry with the smalles valuation.

    INPUT:

    - ``v`` -- a discrete valuation on a field `K`
    - ``A`` -- a matrix with entries in `K`
    - ``k`` -- an integer `\geq -1`

    OUTPUT: a triple `(i, j, e)`, with `i, j > k`, where `(i, j)` indicates the
    entry of `A` with the smallest valuation, which is `e`.

    """
    from sage.all import Infinity
    i = k + 1
    j = k + 1
    minimal_value = Infinity
    for r in range(k + 1, A.nrows()):
        for s in range(k + 1, A.ncols()):
            new_value = v(A[r, s])
            if new_value < minimal_value:
                i = r
                j = s
                minimal_value = new_value
    return i, j, minimal_value


def switch_rows(A, i, j):
    r""" Switch the ith and the jth row of A.
    """
    from sage.all import Permutation
    assert i >= 0 and i < A.nrows(), "i = {}, j = {}".format(i, j)
    assert j >= 0 and j < A.nrows(), "i = {}, j = {}".format(i, j)
    if i != j:
        A.permute_rows(Permutation([(i + 1, j + 1)]))


def switch_columns(A, i, j):
    r""" Switch the ith and the jth column of A.
    """
    from sage.all import Permutation
    if i != j:
        A.permute_columns(Permutation([(i + 1, j + 1)]))


def kernel_basis(v, A):
    r""" Return an R-basis of the kernel of a given matrix.

    INPUT:

    - ``v`` -- a discrete valuation over a field `K`
    - ``A`` -- a matrix over `K`

    OUTPUT:

    an `R`-basis of the kernel of `A`, acting on `R^n`, where `n` is the
    number of columns of `A`.

    """
    D, S, T, r = smith_normal_form(A, v)
    kern = T.inverse().columns()[r:]
    assert all([(A*w).is_zero() for w in kern]), "something is wrong!"
    return kern
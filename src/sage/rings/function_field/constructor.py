r"""
Factories to construct function fields

This module provides factories to construct function fields. These factories
are only for internal use.

EXAMPLES::

    sage: K.<x> = FunctionField(QQ); K
    Rational function field in x over Rational Field
    sage: L.<x> = FunctionField(QQ); L
    Rational function field in x over Rational Field
    sage: K is L
    True

AUTHORS:

- William Stein (2010): initial version

- Maarten Derickx (2011-09-11): added ``FunctionField_polymod_Constructor``,
  use ``@cached_function``

- Julian Rueth (2011-09-14): replaced ``@cached_function`` with
  ``UniqueFactory``

"""
from __future__ import absolute_import
#*****************************************************************************
#       Copyright (C) 2010 William Stein <wstein@gmail.com>
#       Copyright (C) 2011 Maarten Derickx <m.derickx.student@gmail.com>
#       Copyright (C) 2011 Julian Rueth <julian.rueth@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.factory import UniqueFactory

class FunctionFieldFactory(UniqueFactory):
    """
    Return the function field in one variable with constant field ``F``. The
    function field returned is unique in the sense that if you call this
    function twice with the same base field and name then you get the same
    python object back.

    INPUT:

    - ``F`` -- field

    - ``names`` -- name of variable as a string or a tuple containing a string

    EXAMPLES::

        sage: K.<x> = FunctionField(QQ); K
        Rational function field in x over Rational Field
        sage: L.<y> = FunctionField(GF(7)); L
        Rational function field in y over Finite Field of size 7
        sage: R.<z> = L[]
        sage: M.<z> = L.extension(z^7-z-y); M
        Function field in z defined by z^7 + 6*z + 6*y

    TESTS::

        sage: K.<x> = FunctionField(QQ)
        sage: L.<x> = FunctionField(QQ)
        sage: K is L
        True
        sage: M.<x> = FunctionField(GF(7))
        sage: K is M
        False
        sage: N.<y> = FunctionField(QQ)
        sage: K is N
        False
    """
    def create_key(self, F, names):
        """
        Given the arguments and keywords, create a key that uniquely
        determines this object.

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ) # indirect doctest
        """
        if not isinstance(names, tuple):
            names=(names,)
        return (F, names)

    def create_object(self, version, key,**extra_args):
        """
        Create the object from the key and extra arguments. This is only
        called if the object was not found in the cache.

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)  # indirect doctest
            sage: L.<x> = FunctionField(QQ)  # indirect doctest
            sage: K is L
            True
        """
        if key[0].is_finite():
            from .function_field import RationalFunctionField_global
            return RationalFunctionField_global(key[0],names=key[1])
        else:
            from .function_field import RationalFunctionField
            return RationalFunctionField(key[0],names=key[1])

FunctionField=FunctionFieldFactory("sage.rings.function_field.constructor.FunctionField")

class FunctionFieldExtensionFactory(UniqueFactory):
    """
    Create a function field defined as an extension of another
    function field by adjoining a root of a univariate polynomial.
    The returned function field is unique in the sense that if you
    call this function twice with an equal ``polynomial`` and ``names``
    it returns the same python object in both calls.

    INPUT:

    - ``polynomial`` -- univariate polynomial over a function field

    - ``names`` -- variable names (as a tuple of length 1 or string)

    - ``category`` -- category (defaults to category of function fields)

    EXAMPLES::

        sage: K.<x> = FunctionField(QQ)
        sage: R.<y>=K[]
        sage: y2 = y*1
        sage: y2 is y
        False
        sage: L.<w>=K.extension(x-y^2)
        sage: M.<w>=K.extension(x-y2^2)
        sage: L is M
        True
    """
    def create_key(self,polynomial,names):
        """
        Given the arguments and keywords, create a key that uniquely
        determines this object.

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: R.<y>=K[]
            sage: L.<w> = K.extension(x-y^2) # indirect doctest

        TESTS:

        Verify that :trac:`16530` has been resolved::

            sage: K.<x> = FunctionField(QQ)
            sage: R.<y> = K[]
            sage: L.<y> = K.extension(y^2-x)
            sage: R.<z> = L[]
            sage: M.<z> = L.extension(z-1)
            sage: R.<z> = K[]
            sage: N.<z> = K.extension(z-1)
            sage: M is N
            False

        """
        if names is None:
            names=polynomial.variable_name()
        if not isinstance(names,tuple):
            names=(names,)
        return (polynomial,names,polynomial.base_ring())

    def create_object(self,version,key,**extra_args):
        """
        Create the object from the key and extra arguments. This is only
        called if the object was not found in the cache.

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: R.<y>=K[]
            sage: L.<w> = K.extension(x-y^2) # indirect doctest
            sage: y2 = y*1
            sage: M.<w> = K.extension(x-y2^2) # indirect doctest
            sage: L is M
            True
        """
        from . import function_field
        f = key[0]
        names = key[1]
        base_field = f.base_ring()
        if function_field.is_RationalFunctionField(base_field):
            k = base_field.constant_field()
            if k.is_finite(): # then we are in positive characteristic
                # irreducible and separable
                if f.is_irreducible() and not all([e % k.characteristic() == 0 for e in f.exponents()]):
                    # monic and integral
                    if f.is_monic() and all(e in base_field.maximal_order() for e in f.coefficients()):
                        return function_field.FunctionField_global_integral(f, names)
                    else:
                        return function_field.FunctionField_global(f, names)
        return function_field.FunctionField_polymod(f, names)

FunctionFieldExtension=FunctionFieldExtensionFactory(
    "sage.rings.function_field.constructor.FunctionFieldExtension")

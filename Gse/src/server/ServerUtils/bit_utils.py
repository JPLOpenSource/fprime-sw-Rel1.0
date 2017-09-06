#!/usr/bin/env python3
######################################################################
# \file
# \author Thomas A. Werne <thomas.a.werne@jpl.nasa.gov>
# \brief
#
# \copyright
# Copyright 2009-2017, by the California Institute of Technology.
# ALL RIGHTS RESERVED.  United States Government Sponsorship
# acknowledged. Any commercial use must be negotiated with the Office
# of Technology Transfer at the California Institute of Technology.
# \copyright
# This software may be subject to U.S. export control laws and
# regulations.  By accepting this document, the user agrees to comply
# with all U.S. export laws and regulations.  User has the
# responsibility to obtain export licenses, or other export authority
# as may be required before exporting such information to foreign
# countries or providing access to foreign persons.
######################################################################

"""Generic utilities."""

###############################################################################

from collections import deque

###############################################################################

COPYRIGHT = '2009-2017, California Institute of Technology.'

###############################################################################


def int_thru_bool(arg):
    """
    Convert an object to a 0 or a 1.

    Arguments
    ---------
    arg : object
        a value to test for truthiness.

    Returns
    -------
    int
        An integer 1 or 0, depending on the truthiness of the input argument.

    """
    return int(bool(arg))


###############################################################################


def bytes_to_int(src):
    """
    Reinterpret byte array as a big-endian integer.

    Arguments
    ---------
    src : bytes
        Byte array representation of a number.

    Returns
    -------
    int
        The integer value of that number.
    """
    ival = 0
    for bval in src:
        ival <<= 8
        ival |= bval
    return ival


###############################################################################


def int_to_bytes(src, nbytes):
    """
    Convert an integer into a (big-endian) byte string.

    Arguments
    ---------
    src : int
        an integer to convert
    nbytes : int
        the number of bytes used to hold the integer

    Returns
    -------
    bytes
        A byte string of length nbytes, whose big-endian value is src.
    """
    bval = deque()
    for _ in range(nbytes):
        bval.appendleft(0xFf & src)
        src >>= 8

    return bytes(bval)


###############################################################################


def bitfield_property(fieldname, nbits, doc=None):
    """
    Builder for bitfield properties.

    Bitfield properties are normal Python properties that take values of either
    None, or an integer with a certain number of bits.

    Arguments
    ---------
    nbits : int
        The bitfield size.

    Returns
    -------
    property
        A property that does limit checking to ensure the set value is between
        0 and 2**nbits - 1 (or None).  If the set value lies outside that
        range, it raises a ValueError.

    """
    def setter(self, val):
        # This function is used as a property with its docstring explicitly set
        # in its constructor.
        # pylint: disable=missing-docstring
        if val is None:
            setattr(self, fieldname, val)
        else:
            val = int(val)
            ulim = 2**nbits
            if 0 <= val < ulim:
                setattr(self, fieldname, val)
            else:
                raise ValueError('Value must be less than {}'.format(ulim))

    def getter(self):
        # This function is used as a property with its docstring explicitly set
        # in its constructor.
        # pylint: disable=missing-docstring
        return getattr(self, fieldname)

    return property(getter, setter, doc=doc)


###############################################################################


class BitArray():
    """
    An array representation of binary data, accessible at the bit level.

    The indexing convention follows the definition from section 1.6.3 of CCSDS
    732.1:  bit 0 is the MSB of the first byte, bit 8 is the MSB of the second
    byte, with all other bits following the natural interpolation and
    extrapolation.
    """

    ###########################################################################

    def __bytes__(self):
        """
        Generate a byte string version of this bit array.

        Returns
        -------
        bytes
            A byte string, whose individual bytes are made up of 8 consecutive
            bits of this bit array.

        Raises
        ------
        ValueError
            If this bit array's length isn't a multiple of 8.

        """
        nbytes, rem = divmod(len(self), 8)
        if rem % 8 != 0:
            raise ValueError("nbits must be a multiple of 8")

        return int_to_bytes(int(self), nbytes)

    ###########################################################################

    def __eq__(self, rhs):
        """
        Compare two bit arrays for equality.

        Returns
        -------
        bool
            True if equal if they have the same number of bits, all of which
            are equal.  False otherwise.
        """
        # The RHS should be a BitArray object, so it's OK to access its
        # protected members.  Disable the warning.
        # pylint: disable=protected-access
        return self._data == rhs._data

    ###########################################################################

    def __format__(self, format_spec=None):
        """
        Pretty-print a bit array.

        Arguments
        ---------
        format_spec : str
            The format specifier.  Valid settings are: '', '#', 'x', '#x'.

        Returns
        -------
        str
            A string version representation of this bit array.  If format_spec
            is '', the return value is the binary representation.  If it's 'x',
            the return value is the hexadecimal representation.  If it begins
            with a '#', the return string is prepended with a '0b' or '0x'.

        Raises
        ------
        ValueError
            If format_spec has an 'x' in it but bytes(self) raises ValueError.

        """
        ival = int(self)
        leader = ''
        if format_spec and format_spec[0] == '#':
            leader = '#'
            format_spec = format_spec[1:]

        if format_spec == 'x':
            # Check to see if self has a bytes representation
            width = len(bytes(self))
            fmt = 'x'
        else:
            width = len(self)
            fmt = 'b'

        if leader:
            width += 2

        return '{:{leader}0{fwidth}{fmt}}'.format(ival, leader=leader,
                                                  fwidth=width, fmt=fmt)

    ###########################################################################

    def __getitem__(self, key):
        """
        Access a subset of this bit array.

        Arguments
        ---------
        key: int or slice
            The bit or set of bits to access.

        Returns
        -------
        int
            An integer (1 or 0) if key is an int.  Otherwise, a new BitArray
            object containing the bits from self selected by the key slice.

        """
        subdata = list(self._data)[key]

        if isinstance(key, int):
            itemval = subdata
        else:
            itemval = self.__class__(subdata)

        return itemval

    ###########################################################################

    def __index__(self):
        """Perform the same function as __int__."""
        return int(self)

    ###########################################################################

    def __init__(self, dataval=None, datalen=None):
        """
        Construct a BitArray object from a valid input object.

        Arguments
        ---------
        dataval : int, BitArray, byte array, bytes, string, list)
            An object to reinterpret as a BitArray.
        datalen : int
            If dataval is an int, this specifies the number of used to
            construct the BitArray.
        """
        ctrs = {
            int: self._update_from_int,
            self.__class__: self._update_from_bitarray,
            bytearray: self._update_from_bytearray,
            bytes: self._update_from_bytearray,
            str: self._update_from_bytearray,
            list: self._update_from_list
            }

        if dataval is None:
            if datalen is None:
                dataval = []
            else:
                raise ValueError('Null initializer with non-null length')

        self._data = deque()
        for src_type, ctr in ctrs.items():
            if isinstance(dataval, src_type):
                ctr(dataval, datalen)

    ###########################################################################

    def __int__(self):
        """Treat the object as a big-endian integer and return it."""
        ival = 0
        for bval in self._data:
            ival <<= 1
            ival |= bval
        return ival

    ###########################################################################

    def __iter__(self):
        """Return an iterator over the bits in the object."""
        # Just iterate over the underlying deque
        for bval in self._data:
            yield bval

    ###########################################################################

    def __len__(self):
        """Get the number of bits in the object."""
        return len(self._data)

    ###########################################################################

    def __repr__(self):
        """
        Create an unambiguous string representation of the object.

        Returns
        -------
        str
            A string that can be eval()d to create a copy of this object.

        """
        # +2 is to account for initial 0b
        width = len(self)
        return '{}({:#}, {width})'.format(self.__class__.__name__, self,
                                          width=width)

    ###########################################################################

    # The function signature must match this format exactly, even though
    # datalen is unused.  Disable the warning.
    # pylint: disable=unused-argument
    def _update_from_bitarray(self, data, datalen):
        """
        Copy a BitArray's value.

        Arguments
        ---------
        data: BitArray
            BitArray whose value is copied
        datalen:
            ignored

        """
        assert isinstance(data, self.__class__)
        # The RHS should be a BitArray object, so it's OK to access its
        # protected members.  Disable the warning.
        # pylint: disable=protected-access
        self._data = deque(data._data)

    ###########################################################################

    # The function signature must match this format exactly, even though
    # datalen is unused.  Disable the warning.
    # pylint: disable=unused-argument
    def _update_from_bytearray(self, data, datalen):
        """
        Copy a byte array's value.

        Arguments
        ---------
        data: bytes
            Source byte array to copy
        datalen:
            ignored

        """
        self._update_from_int(bytes_to_int(data), 8*len(data))

    ###########################################################################

    def _update_from_int(self, data, datalen):
        """
        Copy an int's value.

        Arguments
        ---------
        data: int
            Source integer to copy
        datalen:
            Number of rightmost bits to copy, or the size of the BitArray in
            which to embed the integer.

        """
        self._data.clear()
        for _ in range(datalen):
            self._data.appendleft(0x01 & data)
            data >>= 1

    ###########################################################################

    # The function signature must match this format exactly, even though
    # datalen is unused.  Disable the warning.
    # pylint: disable=unused-argument
    def _update_from_list(self, data, datalen):
        """
        Copy a list's value.

        Arguments
        ---------
        data: list
            Source list to copy.  The truthiness of the elements are converted
            into 1s and 0s.
        datalen:
            ignored

        """
        self._data = deque(map(int_thru_bool, data))

    ###########################################################################

    def append(self, rhs):
        """
        Append to the BitArray.

        Arguments
        ---------
        rhs: object
            Append the truthiness of this argument.

        """
        self._data.append(int_thru_bool(rhs))

    ###########################################################################

    def extend(self, rhs, nbits=None):
        """
        Extend the BitArray.

        Arguments
        ---------
        rhs: BitArray-compatible type
            Object is converted to a BitArray then appended to self.
        nbits: int
            Number of bits to use when converting rhs to a BitArray.

        """
        rhs = self.__class__(rhs, nbits)
        # The RHS is a BitArray object, so it's OK to access its
        # protected members.  Disable the warning.
        # pylint: disable=protected-access
        self._data.extend(rhs._data)

    ###########################################################################

    def consume_bits(self, nbits):
        """
        Consume and return bits from the left of a BitArray.

        Arguments
        ---------
        nbits: int
            the number of bits to pop.

        Returns
        -------
        BitArray
            A BitArray containing the popped bits.
        """
        rhs = []
        for _ in range(nbits):
            rhs.append(self._data.popleft())

        return self.__class__(rhs)

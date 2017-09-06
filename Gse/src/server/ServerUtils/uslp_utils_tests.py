#!/usr/bin/env python3
######################################################################
# \file
# \author Thomas A. Werne <thomas.a.werne@jpl.nasa.gov>
# \brief
#
# \copyright
# Copyright 2007-2017, by the California Institute of Technology.
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

"""USLP Utilities Unit Test module."""

###############################################################################

import unittest

from math import log2, ceil

import uslp.utils as utils

###############################################################################


class BitArrayTestCase(unittest.TestCase):
    """BitArray Unit test class."""

    ###########################################################################

    def test_consume_bits(self):
        """Make sure bit consumption works."""

        # Arbitrary
        src = b'123abcd'

        arr = utils.BitArray(src)

        first_16 = arr.consume_bits(16)

        with self.subTest('Consumed bits'):
            self.assertEqual(first_16, utils.BitArray(src[0:2]))

        with self.subTest('Leftover bits'):
            self.assertEqual(arr, utils.BitArray(src[2:]))

    ###########################################################################

    def test_format(self):
        """Test all format specifiers."""

        # Arbitrary
        src = utils.BitArray(b'123abcd')

        fmt1 = '{}'.format(src)
        fmt2 = '{:#}'.format(src)
        fmt3 = '{:x}'.format(src)
        fmt4 = '{:#x}'.format(src)

        self.assertEqual(
            '00110001001100100011001101100001011000100110001101100100', fmt1)
        self.assertEqual(
            '0b00110001001100100011001101100001011000100110001101100100', fmt2)
        self.assertEqual('31323361626364', fmt3)
        self.assertEqual('0x31323361626364', fmt4)

    ###########################################################################

    def test_from_bitarray(self):
        """Test copy constructor."""

        # Arbitrary
        src = b'28dj1n8c9w'

        arr_1 = utils.BitArray(src)
        arr_2 = utils.BitArray(arr_1)

        with self.subTest("Compare contents"):
            self.assertEqual(arr_1, arr_2)

        with self.subTest("Ensure a real copy was made"):
            self.assertNotEqual(id(arr_1), id(arr_2))

    ###########################################################################

    def test_getitem(self):
        """Test bit-level access."""

        # Arbitrary
        src = [True, False, True, True, False, True, False, False, False]

        arr = utils.BitArray(src)

        with self.subTest("Single-bit access"):
            for idx, val in enumerate(src):
                self.assertEqual(arr[idx], val)

        with self.subTest("Slice access"):
            slc = slice(3, 7)
            self.assertEqual(arr[slc], utils.BitArray(src[slc]))

    ###########################################################################

    def test_index(self):
        """Test index magic method."""

        # Arbitrary
        src = 28362939840
        nbytes = ceil(log2(src))

        arr = utils.BitArray(src, nbytes)

        # hex() calls arr.__index__, the object of this test
        self.assertEqual(src, int(hex(arr), 16))

    ###########################################################################

    def test_init(self):
        """Test initialization method."""

        with self.subTest("Null init"):
            utils.BitArray()

        with self.subTest("Null init, nonzero length"):
            with self.assertRaises(ValueError):
                utils.BitArray(datalen=1)

        for nbits in range(1, 10):
            with self.subTest("Variable length init", nbits=nbits):
                # Semi-arbitrary, needs to require fewer bits than the lower
                # value for nbits in this loop
                val = 1
                pdu = utils.BitArray(val, nbits)

                self.assertEqual(val, int(pdu))
                self.assertEqual(nbits, len(pdu))

    ###########################################################################

    def test_iter(self):
        """Make sure iteration works."""

        # Arbitrary
        truth = [True, False, True, True, False, True, False, False, False]
        arr = utils.BitArray(truth)

        for idx, bitval in enumerate(arr):
            self.assertEqual(bitval, truth[idx])

    ###########################################################################

    def test_repr(self):
        """Ensure repr conversion doesn't fail."""

        arr_1 = utils.BitArray(b'1234')

        # repr() calls are designed to be eval()'d and produce an equivalent
        # object, so disable warnings when eval() is used.
        # pylint: disable=eval-used
        # Need to prepend the module
        arr_2 = eval('utils.' + repr(arr_1))

        self.assertEqual(arr_1, arr_2)

    ###########################################################################

    def test_to_bytes(self):
        """Make sure byte conversion works."""

        arr = utils.BitArray()
        truth = 0

        for nbits in range(25):
            nbytes, rem = divmod(nbits, 8)
            valid_test = (rem == 0)
            test_str = 'Valid len test' if valid_test else 'Invalid len test'

            with self.subTest(test_str, n=nbits):
                if valid_test:
                    self.assertEqual(bytes(arr),
                                     utils.int_to_bytes(truth, nbytes))
                else:
                    with self.assertRaises(ValueError):
                        bytes(arr)

            new_bit = 1 if (nbits % 3 == 0) else 0
            truth <<= 1
            truth |= new_bit
            arr.append(new_bit)


###############################################################################


class MiscTestCase(unittest.TestCase):
    """Module funciton Unit test class."""

    def test_int_thru_bool(self):
        """Test the integer boolean truthiness test."""

        with self.subTest('True integer'):
            self.assertEqual(1, utils.int_thru_bool(78))

        with self.subTest('False integer'):
            self.assertEqual(0, utils.int_thru_bool(0))

        with self.subTest('True object'):
            self.assertEqual(1, utils.int_thru_bool('abc'))

        with self.subTest('False object'):
            self.assertEqual(0, utils.int_thru_bool(None))


###############################################################################


# This will never be bypassed in any real instance
if __name__ == '__main__':      # pragma: no cover
    unittest.main()

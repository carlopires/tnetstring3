import unittest
import random
import math
import io
import tnetstring
import struct
import sys

MAXINT = 2 ** (struct.Struct('i').size * 8 - 1) - 1

FORMAT_EXAMPLES = {
    b'0:}': {},
    b'0:]': [],
    b'51:5:hello,39:11:12345678901#4:this,4:true!0:~4:\x00\x00\x00\x00,]}':
            {b'hello': [12345678901, b'this', True, None, b'\x00\x00\x00\x00']},
    b'5:12345#': 12345,
    b'12:this is cool,': b'this is cool',
    b'0:,': b'',
    b'0:~': None,
    b'4:true!': True,
    b'5:false!': False,
    b'10:\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    b'24:5:12345#5:67890#5:xxxxx,]': [12345, 67890, b'xxxxx'],
    b'18:3:0.1^3:0.2^3:0.3^]': [0.1, 0.2, 0.3],
    b'243:238:233:228:223:218:213:208:203:198:193:188:183:178:173:168:163:158:153:148:143:138:133:128:123:118:113:108:103:99:95:91:87:83:79:75:71:67:63:59:55:51:47:43:39:35:31:27:23:19:15:11:hello-there,]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]': [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[b'hello-there']]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
}

def get_random_object(random=random, depth=0):
    """Generate a random serializable object."""
    #  The probability of generating a scalar value increases as the depth increase.
    #  This ensures that we bottom out eventually.
    if random.randint(depth,10) <= 4:
        what = random.randint(0,1)
        if what == 0:
            n = random.randint(0,10)
            l = []
            for _ in range(n):
                l.append(get_random_object(random,depth+1))
            return l
        if what == 1:
            n = random.randint(0,10)
            d = {}
            for _ in range(n):
                n = random.randint(0,100)
                k = bytes([random.randint(32,126) for _ in range(n)])
                d[k] = get_random_object(random,depth+1)
            return d
    else:
        what = random.randint(0,4)
        if what == 0:
            return None
        if what == 1:
            return True
        if what == 2:
            return False
        if what == 3:
            if random.randint(0,1) == 0:
                return random.randint(0,MAXINT)
            else:
                return -1 * random.randint(0,MAXINT)
        n = random.randint(0,100)
        return bytes([random.randint(32,126) for _ in range(n)])

class Test_Format(unittest.TestCase):
    def test_roundtrip_format_examples(self):
        for data, expect in FORMAT_EXAMPLES.items():
            self.assertEqual(expect,tnetstring.loads(data))
            self.assertEqual(expect,tnetstring.loads(tnetstring.dumps(expect)))
            self.assertEqual((expect,b''),tnetstring.pop(data))

    def test_roundtrip_format_random(self):
        for _ in range(500):
            v = get_random_object()
            self.assertEqual(v,tnetstring.loads(tnetstring.dumps(v)))
            self.assertEqual((v,b""),tnetstring.pop(tnetstring.dumps(v)))

    def test_unicode_handling(self):
        with self.assertRaises(ValueError):
            tnetstring.dumps("hello")
        self.assertEqual(tnetstring.dumps("hello".encode()),b"5:hello,")
        self.assertEqual(type(tnetstring.loads(b"5:hello,")),bytes)

    def test_roundtrip_format_unicode(self):
        for _ in range(500):
            v = get_random_object()
            self.assertEqual(v,tnetstring.loads(tnetstring.dumps(v)))
            self.assertEqual((v,b''),tnetstring.pop(tnetstring.dumps(v)))

    def test_roundtrip_big_integer(self):
        i1 = math.factorial(1000)
        s = tnetstring.dumps(i1)
        i2 = tnetstring.loads(s)
        self.assertEqual(i1, i2)

    def test_malformed_values_raise_instead_of_reading_outside_input(self):
        malformed = (
            b'',
            b':',
            b'0:#',
            b'1:+#',
            b'1:-#',
            b'0:^',
            b'1: ^',
            b'4: 1.0^',
            b'10:123#',
            b'1000000000:value,',
        )
        for value in malformed:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    tnetstring.loads(value)

    def test_load_does_not_retain_read_results(self):
        class ReusingReader:
            def __init__(self):
                self.parts = [
                    bytes(bytearray(b'1')),
                    bytes(bytearray(b':')),
                    bytes(bytearray(b'x,')),
                ]
                self.offset = 0

            def read(self, _size):
                value = self.parts[self.offset]
                self.offset += 1
                return value

        reader = ReusingReader()
        before = tuple(sys.getrefcount(value) for value in reader.parts)
        self.assertEqual(b'x', tnetstring.load(reader))
        after = tuple(sys.getrefcount(value) for value in reader.parts)
        self.assertEqual(before, after)

    def test_container_insert_error_does_not_corrupt_references(self):
        for _ in range(100):
            with self.assertRaises(TypeError):
                tnetstring.loads(b'6:0:]0:~}')

    def test_recursive_values_have_bounded_nesting(self):
        def nested_value(depth):
            value = None
            for _ in range(depth):
                value = [value]
            return value

        def nested_encoding(depth):
            encoded_length = len(b'0:~')
            encoded_prefixes = []
            for _ in range(depth):
                prefix = str(encoded_length).encode() + b':'
                encoded_prefixes.append(prefix)
                encoded_length += len(prefix) + 1
            return b''.join(reversed(encoded_prefixes)) + b'0:~' + (b']' * depth)

        self.assertIsInstance(tnetstring.loads(nested_encoding(512)), list)
        self.assertIsInstance(tnetstring.dumps(nested_value(512)), bytes)

        with self.assertRaises(RecursionError):
            tnetstring.loads(nested_encoding(513))
        with self.assertRaises(RecursionError):
            tnetstring.dumps(nested_value(513))

    def test_rendering_does_not_retain_temporary_strings(self):
        integer_text = '123'
        float_text = '1.25'

        class CustomInt(int):
            def __str__(self):
                return integer_text

        class CustomFloat(float):
            def __repr__(self):
                return float_text

        before = (sys.getrefcount(integer_text), sys.getrefcount(float_text))
        self.assertEqual(b'3:123#', tnetstring.dumps(CustomInt(123)))
        self.assertEqual(b'4:1.25^', tnetstring.dumps(CustomFloat(1.25)))
        after = (sys.getrefcount(integer_text), sys.getrefcount(float_text))
        self.assertEqual(before, after)

class Test_FileLoading(unittest.TestCase):
    def test_roundtrip_file_examples(self):
        for data, expect in FORMAT_EXAMPLES.items():
            s = io.BytesIO()
            s.write(data)
            s.write(b'OK')
            s.seek(0)
            self.assertEqual(expect,tnetstring.load(s))
            self.assertEqual(b'OK',s.read())
            s = io.BytesIO()
            tnetstring.dump(expect,s)
            s.write(b'OK')
            s.seek(0)
            self.assertEqual(expect,tnetstring.load(s))
            self.assertEqual(b'OK',s.read())

    def test_roundtrip_file_random(self):
        for _ in range(500):
            v = get_random_object()
            s = io.BytesIO()
            tnetstring.dump(v,s)
            s.write(b'OK')
            s.seek(0)
            self.assertEqual(v,tnetstring.load(s))
            self.assertEqual(b'OK',s.read())

    def test_error_on_absurd_lengths(self):
        s = io.BytesIO()
        s.write(b'1000000000:pwned!,')
        s.seek(0)
        with self.assertRaises(ValueError):
            tnetstring.load(s)
        self.assertEqual(s.read(1),b':')

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(Test_Format))
    suite.addTest(loader.loadTestsFromTestCase(Test_FileLoading))
    return suite

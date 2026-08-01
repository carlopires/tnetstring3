import concurrent.futures
import sys
import sysconfig
import threading
import unittest

import tnetstring


FREE_THREADED = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


class TestFreeThreading(unittest.TestCase):
    @unittest.skipUnless(FREE_THREADED, "requires a free-threaded CPython build")
    def test_import_keeps_the_gil_disabled(self):
        self.assertFalse(sys._is_gil_enabled())

    def test_parallel_roundtrips_of_shared_values(self):
        worker_count = 16
        rounds_per_worker = 500
        start = threading.Barrier(worker_count)
        value = {
            b"metadata": [
                {b"name": b"alpha", b"size": 123, b"active": True},
                {b"name": b"beta", b"size": 456, b"active": False},
            ],
            b"chunks": [b"a" * 32, b"b" * 32, b"c" * 32],
        }
        encoded = tnetstring.dumps(value)

        def roundtrip():
            start.wait()
            for _ in range(rounds_per_worker):
                self.assertEqual(encoded, tnetstring.dumps(value))
                self.assertEqual(value, tnetstring.loads(encoded))

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(roundtrip) for _ in range(worker_count)]
            for future in futures:
                future.result()

    def test_encoding_snapshots_concurrently_mutated_containers(self):
        encoder_count = 8
        start = threading.Barrier(encoder_count + 1)
        items = list(range(64))
        value = {b"items": items, b"generation": 0}

        def encode():
            start.wait()
            for _ in range(1_000):
                decoded = tnetstring.loads(tnetstring.dumps(value))
                self.assertIsInstance(decoded, dict)

        def mutate():
            start.wait()
            for generation in range(10_000):
                value[b"generation"] = generation
                items.append(generation)
                if len(items) > 128:
                    items.pop(0)
                if generation % 2:
                    value[b"temporary"] = generation
                else:
                    value.pop(b"temporary", None)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=encoder_count + 1
        ) as executor:
            futures = [executor.submit(encode) for _ in range(encoder_count)]
            futures.append(executor.submit(mutate))
            for future in futures:
                future.result()

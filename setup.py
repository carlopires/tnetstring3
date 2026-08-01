from setuptools import Extension, setup


setup(
    ext_modules=[
        Extension(
            name="tnetstring._tnetstring",
            sources=["tnetstring/_tnetstring.c"],
        )
    ]
)

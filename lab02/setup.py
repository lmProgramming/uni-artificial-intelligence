from setuptools import setup, Extension
from Cython.Build import cythonize  # type: ignore
import os

extensions = [
    Extension(
        "clobber.board",
        [os.path.join("clobber", "board.pyx")],
    ),
]

setup(
    name="ClobberGame",
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': "3"}
    ),
    packages=['clobber'],
    zip_safe=False,
)

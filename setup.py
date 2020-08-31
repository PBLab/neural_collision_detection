# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from glob import glob


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='neural_collision_detection',
    version='0.1.0',
    description='Collide neurons and vasculature',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/taucgl/neural_collision_detection',  # Optional
    author='Yoav Jacobson and Hagai Har-Gil',  # Optional
    author_email=['yoavj1@gmail.com', 'hagaihargil@mail.tau.ac.il'],  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='collisions morphology fcl',  # Optional
    packages=find_packages("src", exclude=['contrib', 'docs', 'src/tests']),  # Required
    package_dir={"": "src"},
    py_modules=[path.splitext(path.basename(p))[0] for p in glob("src/*.py")],
    install_requires=['matplotlib > 3',
                      'numpy > 1.17',
                      'scipy > 1.3',
                      'ipython > 7',
                      'pandas > 0.24',
                      'datajoint',
                      'attrs',
                      'numba',
                      'networkx',
                      'napari',
                      'jupyter',
                      'black',
                      'mypy',
                      'flake8',
                      'dask',
                      ]
)

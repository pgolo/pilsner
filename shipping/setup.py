import sys
from setuptools import setup

ext_modules = None
with open('README.md', mode='r', encoding='utf8') as f:
    long_description = f.read()

# pilsner: cythonize?

setup(
    name='pilsner',
    version='0.0.1',
    description='Utility for dictionary-based named entity recognition',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pgolo/pilsner',
    author='Pavel Golovatenko-Abramov',
    author_email='p.golovatenko@gmail.com',
    packages=['pilsner'],
    ext_modules=ext_modules,
    include_package_data=True,
    license='MIT',
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires='sic>=1.0.4'
)

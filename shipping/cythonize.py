try:
    from Cython.Build import cythonize
    ext_modules = cythonize(['pilsner/model.py', 'pilsner/utility.py'], compiler_directives={'language_level': '3'})
except:
    pass

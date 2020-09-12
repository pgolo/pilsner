import cython

cdef class Model(dict):
    
    @cython.locals(
        normalizers=cython.dict,
        dictionary_number=cython.int
    )
    cpdef bint save(self, str filename)

    @cython.locals(
        normalizers=cython.dict,
        _filename=cython.str,
        dictionary=cython.dict,
        keywords=cython.dict
    )
    cpdef load(self, str filename)

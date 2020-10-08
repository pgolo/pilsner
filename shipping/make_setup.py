import sys

def just_do_it(option):
    cythonize = ''
    if option in ['bdist_wheel']:
        with open('shipping/cythonize.py', mode='r', encoding='utf8') as f:
            cythonize = f.read()
    with open('shipping/setup.py', mode='r', encoding='utf8') as i, open('./setup.py', mode='w', encoding='utf8') as o:
        for line in i:
            if line.strip() != '# pilsner: cythonize?':
                o.write(line)
            else:
                o.write(cythonize)

if __name__ == '__main__':
    just_do_it(sys.argv[1] if len(sys.argv) > 1 else '')

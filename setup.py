from setuptools import setup

with open("README.md", "r", encoding="utf8", errors='ignore') as fh:
    long_description = fh.read()

setup(name='dwsimopt',
      version='0.2.0',
      description='DWSIM automation with python for chemical process simulation optimization',
      url='https://github.com/lf-santos/dwsimopt',
      author='Lucas F. Santos',
      author_email='lfs.francisco.95@gmal.com',
      license='MIT',
      packages=['dwsimopt', 'dwsimopt\\tests'],
      install_requires=['numpy',
                        'scipy',
                        'scikit-opt',
                        'wheel',
                        'pythonnet==2.5.2',
                        'pywin32',
                        'matplotlib',
                        ],
      extras_require = {
          "dev": [
              "ipykernel",
              "build",
              "twine",
              "sphinx",
              "sphinx_rtd_theme",
              "check-manifest",
          ],
      },
    #   cmdclass=CMD_CLASSES,
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
              'Development Status :: 3 - Alpha',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 3 :: Only',
              'Programming Language :: Python :: 3.8',
              'Topic :: Scientific/Engineering',
              'Topic :: Scientific/Engineering :: Mathematics'
          ],
)
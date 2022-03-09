from setuptools import setup

with open("README.md", "r", encoding="utf8", errors='ignore') as fh:
    long_description = fh.read()

setup(name='dwsimopt',
      version='0.1.2',
      description='DWSIM automation with python for chemical process simulation optimization',
      url='http://https://github.com/lf-santos/dwsimopt',
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
)
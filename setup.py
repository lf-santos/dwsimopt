from setuptools import setup

setup(name='dwsimopt',
      version='0.0.1',
      description='DWSIM automation with python for chemical process simulation optimization',
      url='http://https://github.com/lf-santos/pyDWSIMopt',
      author='Lucas F. Santos',
      author_email='lfs.francisco.95@gmal.com',
      license='MIT',
      packages=['pyDWSIMopt', 'pyDWSIMopt\\tests'],
      zip_safe=True,
      install_requires=[
          'pythonnet',
          'pywin32',
          'numpy',
          'scikit-optimize',
          'scipy',
      ],
)
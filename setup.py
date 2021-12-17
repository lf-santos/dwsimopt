from setuptools import setup

# Override standard setuptools commands. 
# Enforce the order of dependency installation.
# Because pywin32 has to be installed after pythonnet==3.0.0a1
#-------------------------------------------------
PREREQS = ['numpy',
          'scipy',
          'wheel',
          'pythonnet==2.5.2',
          'pywin32',
          ]

from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

def requires( packages ): 
    from os import system
    from sys import executable as PYTHON_PATH
    from pkg_resources import require
    require( "pip" )
    CMD_TMPLT = '"' + PYTHON_PATH + '" -m pip install %s'
    for pkg in packages: system( CMD_TMPLT % (pkg,) )       

class OrderedInstall( install ):
    def run( self ):
        requires( PREREQS )
        install.run( self )        

class OrderedDevelop( develop ):
    def run( self ):
        requires( PREREQS )
        develop.run( self )        

class OrderedEggInfo( egg_info ):
    def run( self ):
        requires( PREREQS )
        egg_info.run( self )        

CMD_CLASSES = { 
     "install" : OrderedInstall
   , "develop" : OrderedDevelop
   , "egg_info": OrderedEggInfo 
}        
#-------------------------------------------------

with open("README.md", "r", encoding="utf8", errors='ignore') as fh:
    long_description = fh.read()

setup(name='dwsimopt',
      version='0.0.4',
      description='DWSIM automation with python for chemical process simulation optimization',
      url='http://https://github.com/lf-santos/pyDWSIMopt',
      author='Lucas F. Santos',
      author_email='lfs.francisco.95@gmal.com',
      license='MIT',
      packages=['pyDWSIMopt', 'pyDWSIMopt\\tests'],
      install_requires=PREREQS,
      extras_require = {
          "dev": [
              "build",
              "twine",
              "sphinx",
              "sphinx_rtd_theme",
              "check-manifest",
          ],
      },
      cmdclass=CMD_CLASSES,
      long_description=long_description,
      long_description_content_type="text/markdown",
)
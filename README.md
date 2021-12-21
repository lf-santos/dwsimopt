# dwsimopt: DWSIM simulation optimization with Python!

[![PyPI](https://img.shields.io/pypi/v/dwsimopt)](https://pypi.org/project/dwsimopt/)
<a href='https://pydwsimopt.readthedocs.io/en/latest/?badge=latest' target="blank">
    <img src='https://readthedocs.org/projects/pydwsimopt/badge/?version=latest' alt='Documentation Status' />
</a>
[![License](https://img.shields.io/pypi/l/dwsimopt.svg)](https://github.com/lf-santos/dwsimopt/LICENSE)

The DWSIM Optimization (`dwsimopt`) is a Python library that automates DWSIM simulations for process optimization.
The simulations dlls are embedded in the programming environment so that it can be accessd and modified by the optimization algorithms.

# Mathematical background

Although very efficient to describe in details complex systems that would otherwise have to be simplified or approximated, black-box process simulators lack the symbolic formulation of the process model equations and the analytical derivatives that are useful for optimization, for example. The use of simulation may also introduce noise to the calculations due to convergence and approximations of numerical methods, which can jeopardize the calculation of accurate approximate derivatives and, therefore, the use of gradient-based optimization methods directly <a href="https://doi.org/10.1002/aic.11579">[1]</a>. Also, the lack of analytical formulations of the optimization problem prevents the derivation of rigorous upper and lower bounds of the functions that are used for deterministic global optimization <a href="https://doi.org/10.1007/s11590-016-1028-2">[2]</a>. In that sense, the optimization models that require simulations to calculate the objective function and/or constraints are often referred to as simulation optimization problem <a href="https://doi.org/10.1007/s10479-015-2019-x">[3]</a>. A simplified version of this class of problems can be described as to find an ![equation](https://latex.codecogs.com/svg.latex?%5Cinline%20%7B%5Ccolor%7BMagenta%7D%20%5Ctextbf%7Bx%7D%5E*%5Cin%20%5Cmathbb%7BR%7D%5En%7D) that solves globally the following constrained problem

![equation](https://latex.codecogs.com/svg.latex?%7B%5Ccolor%7BMagenta%7D%20%5Cbegin%7Balign*%7D%20%5Cmin_%7B%5Ctextbf%7Bx%7D%5Cin%20%5Cmathcal%7BD%7D%7D%26%20%5C%20%5C%20f%28%5Ctextbf%7Bx%7D%29%5C%5C%20s.t.%26%20%5C%20%5C%20%5Ctextbf%7Bg%7D%28%5Ctextbf%7Bx%7D%29%5Cle%200%2C%20%5Cend%7Balign%7D%7D)

in which the objective function ![equation](https://latex.codecogs.com/svg.latex?%5Cinline%20%7B%5Ccolor%7BMagenta%7D%20f%3A%5Cmathbb%7BR%7D%5En%5Cmapsto%20%5Cmathbb%7BR%7D%7D) and constraints ![equation](https://latex.codecogs.com/svg.latex?%5Cinline%20%7B%5Ccolor%7BMagenta%7D%20%5Ctextbf%7Bg%7D%3A%5Cmathbb%7BR%7D%5En%5Cmapsto%20%5Cmathbb%7BR%7D%5Eq%7D), being *q* the number of constraints, are somewhat expensive to calculate, slightly noisy, and black-box functions, *i.e.* there is no available mathematical expression for *f* or **g**, but for a given ![equation](https://latex.codecogs.com/svg.latex?%5Cinline%20%7B%5Ccolor%7BMagenta%7D%20%5Ctextbf%7Bx%7D%5Cin%5Cmathcal%7BD%7D%5Csubseteq%5Cmathbb%7BR%7D%5En%7D) the value of *f*(**x**) and **f**(**x**) are calculated in a computer code simulation with some noise.

# Requirements

- Python <= 3.9 (python 3.8 recommended -- using python 3.9 requires installing dwsimopt from ``setup.py``)
- DWSIM v7 (open-source chemical process simulation. <a href="https://dwsim.inforside.com.br/new/">Download here</a>)
- pythonnet <= 2.5.2 (on Python 3.9 you'll need to <a href="https://www.lfd.uci.edu/~gohlke/pythonlibs/#pythonnet">download the pythonnet2.5.2 wheel</a> and ``pip install path\to\wheel``)
- pywin32
- numpy
- scipy
- scikit-opt

Or, start from a fresh environment and let the `dwsimopt` install the dependencies. Except DWSIM that must be downloaded and installed manually.

# Installation

Install the latest version of this repository to your machine

<pre>pip install dwsimopt</pre>
or
<pre>git clone https://github.com/lf-santos/dwsimopt.git
cd dwsimopt
python setup.py install
</pre>

Make sure you have all the required packages and software. Navegate throught the jupyter notebook examples. Use the `SimulationOptimization` class to embed your `DMSWIM` simulation into Python. Add degrees of freedom, objective function and constraints from your simulation optimization problem with the `py2dwim` python-dwsimdata exchange interface. Solve the problem with a suitable optimization solver (surrogate-based optimization or global optimization meta-heuristics recommended).

# Citing us

If you use dwsimopt, plese cite the following paper: <a href="https://doi.org/10.1016/j.ces.2021.116699" title="simulation optimization paper">L. F. Santos, C. B. B. Costa, J. A. Caballero, M. A. Ravagnani, Kriging-assisted constrained optimization of single-mixed refrigerant natural gas liquefaction process, Chemical Engineering Science (2021).
116699doi:https://doi.org/10.1016/j.ces.2021.116699.</a>

<pre>
@article{santos2021kriging,
  title={Kriging-assisted constrained optimization of single-mixed refrigerant natural gas liquefaction process},
  author={Santos, Lucas F and Costa, Caliane BB and Caballero, Jos{\'e} A and Ravagnani, Mauro ASS},
  journal={Chemical Engineering Science},
  volume={241},
  pages={116699},
  year={2021},
  publisher={Elsevier}
}
</pre>

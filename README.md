# pyDWSIMopt: DWSIM simulation optimization with Python!

The Python DWSIM Optimization (`pyDWSIMopt`) is a library that automates DWSIM simulations for process optimization.
The simulations dlls are embedded in the programming environment so that it can be accessd and modified by the optimization algorithms.

# Mathematical background

Although very efficient to describe in details complex systems that would otherwise have to be simplified or approximated, black-box process simulators lack the symbolic formulation of the process model equations and the analytical derivatives that are useful for optimization, for example. The use of simulation may also introduce noise to the calculations due to convergence and approximations of numerical methods, which can jeopardize the calculation of accurate approximate derivatives and, therefore, the use of gradient-based optimization methods directly <a href="https://doi.org/10.1002/aic.11579">[1]</a>. Also, the lack of analytical formulations of the optimization problem prevents the derivation of rigorous upper and lower bounds of the functions that are used for deterministic global optimization <a href="https://doi.org/10.1007/s11590-016-1028-2">[2]</a>. In that sense, the optimization models that require simulations to calculate the objective function and/or constraints are often referred to as simulation optimization problem <a href="https://doi.org/10.1007/s10479-015-2019-x">[3]</a>. A simplified version of this class of problems can be described as to find an $\textbf{x}^*\in \mathbb{R}^n$ that solves globally the following constrained problem

$$
\min_{\textbf{x}\in \mathcal{D}} \ \ f(\textbf{x})
$$

$$
\text{s.t.} \ \ \textbf{g}(\textbf{x})\le 0,
$$

in which the objective function $f:\mathbb{R}^n\mapsto \mathbb{R}$ and constraints $\textbf{g}:\mathbb{R}^n\mapsto \mathbb{R}^q$, being $q$ the number of constraints, are somewhat expensive to calculate, slightly noisy, and black-box functions, \textit{i.e.} there is no available mathematical expression for $f$ or $\textbf{g}$, but for a given $\textbf{x}\in\mathcal{D}\subseteq\mathbb{R}^n$ the value of $f(\textbf{x})$ and $\textbf{g}(\textbf{x})$ are calculated in a computer code simulation with some noise.

# Requirements

- Python 3.9.x (might work on older version, but def. not on 3.10+. Also, may need to install from <a hrel="https://www.lfd.uci.edu/~gohlke/pythonlibs/#pythonnet" title="pythonnet wheel for python3.9">wheel</a> for Python 3.9)
- DWSIM v7 +
- pythonnet 2.5.2 +
- scipy 1.7.x +
- numpy 1.21.x +
- matplotlib 3.5.x +

# Installation

Clone the latest version of this repository to your machine

<pre>git clone https://github.com/lf-santos/pyDWSIMopt.git</pre>

Make sure you have all the required packages and software. Navegate throught the jupyter notebook examples. Use the `Simulation` class to embed your `DMSWIM` simulation into Python. Modify the `fobj.py` to calculate the objective function and constraints of your simulation optimization problem.

# Citing us

If you use pyDWSIMopt, plese cite the following paper: <a href="https://doi.org/10.1016/j.ces.2021.116699" title="simulation optimization paper">L. F. Santos, C. B. B. Costa, J. A. Caballero, M. A. Ravagnani, Kriging-assisted constrained optimization of single-mixed refrigerant natural gas liquefaction process, Chemical Engineering Science (2021).
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

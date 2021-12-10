def fpen_barrier(sim,x):
    f, g = sim.fobj(x)
    return f + 1000*max(0,g)

def fpen_quad(sim, x):
    f, g = sim.fobj(x)
    return f + 1000*max(0,g)**2

def fpen_exp(sim, x):
    f, g = sim.fobj(x)
    return f + 1000*exp(max(0,g))
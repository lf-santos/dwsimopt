def fpen_barrier(sim,x):
    f, g = sim.fobj(sim,x)
    return f + 1000*max(0,3-g)


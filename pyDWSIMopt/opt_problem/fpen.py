def fpen_barrier(sim,x):
    f, g = sim.fobj(x)
    return f + 1000*max(0,g)


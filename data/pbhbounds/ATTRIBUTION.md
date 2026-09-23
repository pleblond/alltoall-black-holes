# Vendored evaporation bound curves (f_PBH upper limit vs M [M_sun]).
Source: Bradley Kavanagh's PBHbounds (https://github.com/bradkav/PBHbounds),
itself digitized from the cited papers (see file headers): EGRB (Carr et al.
0912.5297), Voyager (Boudaud & Cirelli 1807.03075), INTEGRAL (Laha et al.
2004.00627), SuperK (Bernal et al. 1912.01014), CMBevap (Poulin et al.
1612.07738), 511keV (Laha; DeRocco & Graham 1906.09994/1906.07740),
Comptel (Laha et al. 2010.04797). Used under the repo's LICENSE (BSD-style;
see upstream). We convert f_PBH -> beta(M) from first principles in
bh_graph.bounds (stated assumptions: monochromatic, gamma = 0.2,
radiation-dominated formation, Planck15 densities).

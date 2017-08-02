load ../data_oct2010/2010_09_14_0_000_ASDF.mat
TEmatrix = ASDFTEdelay(asdf_raw,1);
fname = 'm150.vti'
TE2vti(fname,TEmatrix);

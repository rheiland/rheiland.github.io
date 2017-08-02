function fid = TE2vti(filename, teMtx)
% retval = TE2vti(filename, teMtx)
%
%    filename - output file (in VTK's .vti (image) format)
%    teMtx - transfer entropy matrix
%
% Returns:
%    fid - file ID
%
% Description :
%    
%
% Example :
%    
% Author   : Randy Heiland
%            Indiana University
%

[mWidth, mHeight] = size(teMtx);

hdr = sprintf('<?xml version="1.0"?>\n<VTKFile type="ImageData" version="0.1" byte_order="LittleEndian">\n<ImageData WholeExtent="0 %d 0 %d 0 0" Origin="0 0 0" Spacing="1 1 1">\n<Piece Extent="0 %d 0 %d 0 0">\n<PointData Scalars="TE">\n<DataArray type="Float64" Name="TE" NumberOfComponents="1" format="ascii">\n', mWidth-1,mHeight-1,mWidth-1,mHeight-1)

footer = '\n</DataArray>\n</PointData>\n<CellData>\n</CellData>\n</Piece>\n</ImageData>\n</VTKFile>\n'

fid =fopen(filename,'w');
fprintf(fid,hdr);
fprintf(fid,'%.12f ',teMtx)
fprintf(fid,footer);
fclose(fid);


 function [M_surf,M_caps,offsetXYZ] = ctp2mesh(filename)
%ctp2mesh - generates tirangular mesh representation of center point list where ctpList is x,y,z,r.
load(filename)

ctpList = [neuron.vectorizedStructure.AllVerts ...
    neuron.vectorizedStructure.AllRadii];

% calculate final mask size
minXYZ = min(ctpList(:,1:3));
maxR = max(ctpList(:,4));
offsetXYZ = maxR-minXYZ;

%apply offset to all list - easier coding
nctps = size(ctpList,1) ;
ctpList = ctpList + repmat([offsetXYZ 0],nctps,1);

%create mask based on new coordinates and maxR
maxXYZ = max(ctpList(:,1:3));
im = zeros(round(maxXYZ+maxR),'uint8');

%precompute balls of differnt radii
minR = min(ctpList(:,4));

balls = struct('box',[],'linIdx',[]); %entry into this structure are the actual radii as they are integers.
for iR = ceil(minR):round(maxR)
    balls(iR).box = uint8(circle3d(iR));

    k = ceil(-iR/2):floor(iR/2);
    if numel(k)>iR;k=k(1:iR);end
     balls(iR). linIdx = k;
     
end
    
%%
for iCTP = 1 : nctps
    thisXYX = ctpList(iCTP,1:3);
    thisR = round(ctpList(iCTP,4));
    if thisR == 0
        thisR = 1;
    end
    %size(balls(thisR).box);
    xCoord = round(thisXYX(1) + balls(thisR).linIdx);
    yCoord = round(thisXYX(2) + balls(thisR).linIdx);
    zCoord = round(thisXYX(3) + balls(thisR).linIdx);
    
    im(xCoord,yCoord,zCoord) = balls(round(thisR)).box;
end
    
 M_surf = isosurface(im);
 M_caps = isocaps(im);


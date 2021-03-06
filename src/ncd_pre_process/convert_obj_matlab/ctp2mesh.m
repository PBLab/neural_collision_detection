 function [M_surf,M_caps,offsetXYZ] = ctp2mesh(filename)
%ctp2mesh - generates tirangular mesh representation of center point list where ctpList is x,y,z,r.
raw_data = load(filename);
if endsWith(filename, '.mat')
    ctpList = [raw_data.neuron.vectorizedStructure.AllVerts ...
        raw_data.neuron.vectorizedStructure.AllRadii];
elseif endsWith(filename, '.csv')
    ctpList = raw_data;
end

% flip y-z coordinates and make the new z point to the white matter
y = ctpList(:, 2) * -1;
ctpList(:, 2) = ctpList(:, 3);
ctpList(:, 3) = y;

% Write as csv to disk
balls_csv_fname = strcat(filename(1:end-4), '_balls_yz_flipped.csv');
dlmwrite(balls_csv_fname, ctpList, 'precision', 7);

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
minR = max(min(ctpList(:,4)), 1);

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
    % Since isosurface() swaps x and y, we swap it here to make it correct
    xCoord = round(thisXYX(2) + balls(thisR).linIdx);
    yCoord = round(thisXYX(1) + balls(thisR).linIdx);
    zCoord = round(thisXYX(3) + balls(thisR).linIdx);
    
    im(xCoord,yCoord,zCoord) = balls(round(thisR)).box;
end
    
 M_surf = isosurface(im);
 M_caps = isocaps(im);


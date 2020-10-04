function mycircle = circle3d(circle_size);
        myhalf = round(circle_size-1)/2;
        [x,y,z] = meshgrid(-myhalf:myhalf,-myhalf:myhalf,-myhalf:myhalf);
        mycircle = sqrt(x.^2 + y.^2 +z.^2);
        mycircle = mycircle<=(circle_size/2);
 return
        
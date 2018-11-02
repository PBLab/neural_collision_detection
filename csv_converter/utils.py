# utils

import os, sys
import numpy

class Utils(object):
    @staticmethod
    def memory_usage():
        print("Memory usage:")
        os.system("ps aux | grep %i | grep -v grep | awk '{sum=sum+$6}; END {print sum/1024 \" MB\"}'" % os.getpid() )

    @staticmethod
    def fix_faces(faces):
        for f in faces:
            a, b, c = f
            yield (a-1, b-1, c-1)

    @staticmethod
    def count_lines(fname):
        cnt = 0
        with open(fname, 'r') as f:
            for l in f:
                cnt += 1
        return cnt

    @staticmethod
    def get_min_max(vertices):
        maxX, maxY, maxZ, minX, minY, minZ = 0, 0, 0, 1000, 1000, 1000

        for v in vertices:
            x, y, z = v
            if x > maxX:
                maxX = x
            if y > maxY:
                maxY = y
            if z > maxZ:
                maxZ = z
            if x < minX:
                minX = x
            if y < minY:
                minY = y
            if z < minZ:
                minZ = z

        print("x: %i - %i" % (minX, maxX))
        print("y: %i - %i" % (minY, maxY))
        print("z: %i - %i" % (minZ, maxZ))

        return maxX, maxY, maxZ, minX, minY, minZ

    @staticmethod
    def read_csv_file(filename, datatype = int):
        return Utils.read_csv_file_gen(filename, datatype), Utils.count_lines(filename)

    @staticmethod
    def read_csv_file_gen(filename, datatype = int):
        with open(filename, 'r') as f:
            for line in f:
                x, y, z = line.strip().split(',')
                #yield [datatype(float(x)), datatype(float(y)), datatype(float(z))]
                yield numpy.array([datatype(float(x)), datatype(float(y)), datatype(float(z))])

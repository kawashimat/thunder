import sys
import os
from numpy import *
from scipy.linalg import *
from scipy.sparse import *
from scipy.io import * 
from pyspark import SparkContext
import logging

if len(sys.argv) < 4:
  print >> sys.stderr, \
  "(sta) usage: ref <master> <inputFile_X> <outputFile>"
  exit(-1)

def parseVector(line):
	vec = [float(x) for x in line.split(' ')]
	ts = array(vec[3:]) # get tseries
	return ((int(vec[0]),int(vec[1]),int(vec[2])),ts) # (x,y,z),(tseries) pair 

# parse inputs
sc = SparkContext(sys.argv[1], "ref")
inputFile_X = str(sys.argv[2])
outputFile = str(sys.argv[3])
logging.basicConfig(filename=outputFile+'/'+'stdout.log',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

# parse data
logging.info("(ref) loading data")
lines_X = sc.textFile(inputFile_X)
X = lines_X.map(parseVector)

# get z ordering
logging.info("(ref) getting z ordering")
zinds = X.filter(lambda (k,x) : (k[0] == 1000) & (k[1] == 1000)).map(lambda (k,x) : k[2]).collect()
savemat(outputFile+"/"+"zinds.mat",mdict={'zinds':zinds},oned_as='column',do_compression='true')

# compute ref
logging.info('(ref) computing reference image')
ref = X.map(lambda (k,x) : median(x)).collect()
logging.info('(ref) saving results...')
savemat(outputFile+"ref.mat",mdict={'ref':ref},oned_as='column',do_compression='true')

# compute projection
#xproj = X.map(lambda (k,x) : (k[0],median(x))).reduceByKey(lambda x,y : x+y, 3000).collect()
#savemat(outputFile+"xproj.mat",mdict={'xproj':xproj},oned_as='column',do_compression='true')

#yproj = X.map(lambda (k,x) : (k[1],median(x))).reduceByKey(lambda x,y : x+y, 3000).collect()
#savemat(outputFile+"yproj.mat",mdict={'yproj':yproj},oned_as='column',do_compression='true')

#zproj = X.map(lambda (k,x) : (k[2],median(x))).reduceByKey(lambda x,y : x+y, 3000).collect()
#savemat(outputFile+"zproj.mat",mdict={'zproj':zproj},oned_as='column',do_compression='true')

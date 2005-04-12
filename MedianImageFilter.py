#!/usr/bin/env python
#
#  Example on the use of the MedianImageFilter
#
# this is a modified version which demonstrate use of itk module

import itk
from sys import argv

# to clearly view that itk module (ie InsightToolkit in it) is really long to import :-(
print 'modules loaded'

# types and dimension "declaration"
#
# Types and dimension can come from command line. It can't be easily done in C++.
# we should just do :
# dim = int(argv[4])
# outPType = inPType = argv[5]
# 
dim = 2
outPType = inPType = 'UC'
inType = (inPType, dim)
outType = (outPType, dim)

# use type to instanciate reader, writer and filter
reader = itk.ImageFileReader[inType].New()
writer = itk.ImageFileWriter[outType].New()
filter  = itk.MedianImageFilter[inType, outType].New()

filter.SetInput( reader.GetOutput() )
writer.SetInput( filter.GetOutput() )

reader.SetFileName( argv[1] )
writer.SetFileName( argv[2] )

# use type declared above to instanciate itk::Size object
sizeRadius = itk.Size[dim]()
sizeRadius.SetElement( 0, eval( argv[3] ) )
sizeRadius.SetElement( 1, eval( argv[3] ) )

filter.SetRadius( sizeRadius )


writer.Update()




#!/usr/bin/env python
import itk
from sys import argv

###########################################################
# this script demonstrates usage of itk module facilities
# see MedianImageFilter.py for an example which only uses
# type an dim declarations.
# see WhiteTopHatFilter2.py for the same pipeline without
# itk module
###########################################################

# to clearly view that itk module (ie InsightToolkit in it) is really long to
# import :-(
# that's the price for python flexibility
print 'modules loaded'

# declares types and dim which will be reused in all the pipeline.
# it allows to to change type (or dim) in a single place
dim = 2
inPType = 'US'
outPType = 'UC'
inType = (inPType, dim)
outType = (outPType, dim)

(inName, outName) = argv[1:]

# set file name on the same line
reader = itk.ImageFileReader[inType].New(FileName=inName)

# Radius=3 parameter allows to easily create a structuring element with a radius
# of 3
kernel = itk.BinaryBallStructuringElement[inType](Radius=3)
# important !
kernel.CreateStructuringElement()
# kernel can be created on a single line, but the result is quite dirty : 
# CreateStructuringElement is not an attribute of the structuring element new
# object, and we have no value to give. It should be impossible in future to
# call this method.
# kernel = itk.BinaryBallStructuringElement[inType](Radius=3, CreateStructuringElement=())


# each argument is given in a single line
erode = itk.GrayscaleErodeImageFilter[inType*2].New(reader, Kernel=kernel)
dilate = itk.GrayscaleDilateImageFilter[inType*2].New(erode, Kernel=kernel)

# this filter take 2 images in input. reader and dilate filters give images, and
# once again, everything is given in one line
sub = itk.SubtractImageFilter[inType*3].New(reader, dilate)

cast = itk.CastImageFilter[inType, outType].New(sub)

# the string in parameter is the filename, and the filter gives the input image
writer = itk.ImageFileWriter[outType].New(cast, FileName=outName)

writer.Update()


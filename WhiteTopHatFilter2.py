#!/usr/bin/env python
from InsightToolkit import *
from sys import argv

print 'modules loaded'



reader = itkImageFileReaderUS2_New()
reader.SetFileName(argv[1])

kernel = itkBinaryBallStructuringElementUS2()
kernel.SetRadius(3)
kernel.CreateStructuringElement()

erode = itkGrayscaleErodeImageFilterUS2US2_New()
erode.SetInput(reader.GetOutput())
erode.SetKernel(kernel)
dilate = itkGrayscaleDilateImageFilterUS2US2_New()
dilate.SetInput(erode.GetOutput())
dilate.SetKernel(kernel)
sub = itkSubtractImageFilterUS2US2US2_New()
sub.SetInput2(reader.GetOutput())
sub.SetInput1(dilate.GetOutput())

cast = itkCastImageFilterUS2UC2_New()
cast.SetInput(sub.GetOutput())

writer = itkImageFileWriterUC2_New()
writer.SetInput(cast.GetOutput())
writer.SetFileName(argv[2])
writer.Update()

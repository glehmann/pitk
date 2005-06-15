#!/usr/bin/env python
#coding: iso-8859-15
#
# refactor InsightToolkit module to be more structured
#
# Copyright (C) 2005  Gaëtan Lehmann <gaetan.lehmann@jouy.inra.fr>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import InsightToolkit, sys

# set this variable to True to automatically add an progress display to the newly created
# filter.
auto_progress = False

def initDict() :
	"""
	select attributes of InsightToolkit an split it in groups :
	+ typeDict : a dict. Key is class name without itk prefix. Values are dict with type as name and array of function name as value.
	+ noTypeDict : a dict. Key is a class name without itk prefix. Values are arrays of function names.
	+ nonItk : everything non prefixed with itk or vnl
	+ vnl : everything which begins with vnl (without vnl prefix)
	"""
	import re
	classes = []	# stores classes with types. Types will be isolated later.
	noType = []
	nonItk = []
	vnl = []
	
	# compile regexp which will be used to find itk classes with types.
	typeRegexp = re.compile(r'^itk([a-zA-Z0-9]+?[a-z])([A-Z]*[0-9][A-Z0-9]*)(_.*$|Ptr)')
	# classes without type
	noTypeRegexp = re.compile(r'^itk([a-zA-Z0-9]+?[a-z])(_.*$|Ptr)')
	
	for f in dir(InsightToolkit) :
		if f.startswith('itk') :
			typeRes = typeRegexp.findall(f)
			noTypeRes = noTypeRegexp.findall(f)
			if typeRes != [] :
				# type found
				c, t, func = typeRes[0]
				# some classes end with a character in uppercase, and those character are
				# used as type... correct the few case where we have this problem
				for ex in ['IO', '2D', '3D'] :
					if t.startswith(ex) :
						c += ex
						t = t[len(ex):] 
				classes.append([c, t, func])
			elif noTypeRes != [] :
				# no type found
				noType.append(noTypeRes[0])
		else :
			if f.startswith("vnl_") :
				# [4:] == [len('vnl_'):]
				vnl.append(f[4:])
			else :
				# attrib don't start with itk or vnl_
				nonItk.append(f)
				
	# now, generate dict which contains classes with types
	typeDict = {}
	for c, t, func in classes :
		if not typeDict.has_key(c) :
			typeDict[c] = {}
		if not typeDict[c].has_key(t) :
			typeDict[c][t] = []
		typeDict[c][t].append(func)
	
	# dict which contains classes without type
	noTypeDict = {}
	for c, func in noType :
		if typeDict.has_key(c) :
			# print "name collision : %s" % c
			pass
		else :
			if not noTypeDict.has_key(c) :
				noTypeDict[c] = []
			noTypeDict[c].append(func)
	
		
	# finally, return values :)
	return (typeDict, noTypeDict, nonItk, vnl)

class ItkClassType :
	"""
	this class gives functions avaible for a given type of a given class
	"""
	def __init__(self, name, t, funcs) :
		self.__name__ = name
		self.__type__ = t
		self.__function__ = getattr(InsightToolkit, 'itk%s%s' % (name, t))		
		for func in funcs :
			# attribute name must not have _ prefix
			if func[0] == '_' :
				attrib = func[1:]
			else :
				attrib = func
				
			# get the function to add as attribute
			function = getattr(InsightToolkit, 'itk%s%s%s' % (name, t, func))
			
			if attrib == 'New' :
				# to make prototyping easier, allow to pass parameter(s) to New function
				# I can't understand why, but it don't work in pure functional style: I can't 
				# use function() in New defined below :-(
				self.__new__ = function
				def New(*args, **kargs) :
					# create a new New function to manage parameters
					ret = self.__new__()
					
					# args without name are filter used to set input image
					#
					# count SetInput calls to call SetInput, SetInput2, SetInput3, ...
					# usefull with filter which take 2 input (or more) like SubstractImageFiler
					# Ex: substract image2.png to image1.png and save the result in result.png
					# r1 = itk.ImageFileReader.US2.New(FileName='image1.png')
					# r2 = itk.ImageFileReader.US2.New(FileName='image2.png')
					# s = itk.SubtractImageFilter.US2US2US2.New(r1, r2)
					# itk.ImageFileWriter.US2.New(s, FileName='result.png').Update()
					try :
						for setInputNb, arg  in enumerate(args) :
							# add filter in the pipeline
							ret.SetInput(setInputNb, arg.GetOutput())
					except TypeError :
						# ret seems to not accept SetInput(int, image)... try with SetInput(image)
						ret.SetInput(args[0].GetOutput())
						if len(args) > 1 :
							raise TypeError('Object accept only 1 input.')
						
					# named args : name is the function name, value is argument(s)
					for attribName, value in kargs.iteritems() :
						# use Set as prefix. It allow to use a shorter and more intuitive
						# call (Ex: itk.ImageFileReader.UC2.New(FileName='image.png')) than with the
						# full name (Ex: itk.ImageFileReader.UC2.New(SetFileName='image.png'))
						attrib = getattr(ret, 'Set' + attribName)
						attrib(value)
					
					# now, try to add observer to display progress
					if auto_progress :
						try :
							import sys
							def progress() :
								clrLine = "\033[2000D\033[K"
								p = ret.GetProgress()
								print >> sys.stderr, clrLine+"%s: %f" % (repr(self), p), 
								if p == 1 :
									print >> sys.stderr, clrLine, 
							
							command = PyCommand.New()
							command.SetCommandCallable(progress)
							ret.AddObserver(ProgressEvent(), command.GetPointer())
						except :
							# it seems that something goes wrong...
							# as this feature is designed for prototyping, it's not really a problem
							# if an abject  don't have progress reporter, so adding reporter can silently fail
							pass
					
					return ret
				
				# finally, set our own New function as self.New
				setattr(self, 'New', New)
			    
			else :
				# add method
				setattr(self, attrib, function)
	
	def __call__(self, *args, **kargs) :
		# delegate to New to be consistent with vtk python API where New is masked
		if hasattr(self, 'New') :
			return self.New(*args, **kargs)
		# some types needs to be callable (types without New() method)
		# as it don't seem to be a problem, make all types callable
		ret = self.__function__(*args)
		# named args : name is the function name, value is argument(s)
		for attribName, value in kargs.iteritems() :
			# use Set as prefix (see above).
			attrib = getattr(ret, 'Set' + attribName)
			attrib(value)
		return ret
	
	def __repr__(self) :
		return '<itk.%s[%s]>' % (self.__name__, self.__type__)

		
class ItkClassNoType :
	"""
	this class manage access to functions of classes without types
	"""
	def __init__(self, name, funcs) :
		self.__name__ = name
		self.__function__ = getattr(InsightToolkit, 'itk%s' % name)
		for func in funcs :
			if func[0] == '_' :
				attrib = func[1:]
			else :
				attrib = func
			function = getattr(InsightToolkit, 'itk%s%s' % (name, func))
			setattr(self, attrib, function)
	
	def __call__(self, *args, **kargs) :
		# delegate to New to be consistent with vtk python API where New is masked
		if hasattr(self, 'New') :
			return self.New(*args, **kargs)
		return self.__function__(*args, **kargs)
			    
	def __repr__(self) :
		return '<itk.%s>' % self.__name__


class ItkClass :
	"""
	This class manage access to avaible types
	"""
	def __init__(self, name, types) :
		# the name of the class
		self.__name__ = name
		# types of the class
		self.__types__ = {}
		
		# add each type in dict and in attribs
		for t, funcs in types.iteritems() :
			attrib = self.__manageDigit__(t)
			classType = ItkClassType(name, t, funcs)
			self.__types__[attrib] = classType
			setattr(self, attrib, classType)
	
	def __getitem__(self, key) :
		return self.__types__[self.__manageDigit__(self.__seq2str__(key))]

	# we don't use staticmethod to be able to mask the method
	def __seq2str__(self, seq) :
		if not isinstance(seq, str) and hasattr(seq, '__getitem__') :
			return "".join([self.__seq2str__(e) for e in seq])
		else :
			return str(seq) 
	
	def __manageDigit__(self, key) :
		# to allow usage of numbers
		key = str(key)
		# number attributes must be avaible without _ prefix
		if key.isdigit() :
			key = '_%s' % key
		return key

	def __repr__(self) :
		return '<itk.%s>' % self.__name__
		
	def keys(self) :
		return self.__types__.keys()

	# second level definitions support higher levels
	def __iter__(self):
			for k in self.keys():
					yield k
	def has_key(self, key):
			try:
					value = self[key]
			except KeyError:
					return False
			return True
	def __contains__(self, key):
			return self.has_key(key)

	# third level takes advantage of second level definitions
	def iteritems(self):
		for k in self:
				yield (k, self[k])
	def iterkeys(self):
		return self.__iter__()
	# fourth level uses definitions from lower levels
	def itervalues(self):
		for _, v in self.iteritems():
				yield v
	def values(self):
		return [v for _, v in self.iteritems()]
	def items(self):
		return list(self.iteritems())
	def get(self, key, default=None):
		try:
				return self[key]
		except KeyError:
				return default
	def __len__(self):
			return len(self.keys())

			
class VnlClass :
	"""
	give accex to vnl_ attributes
	"""
	def __init__(self, names) :
		for name in names :
			function = getattr(InsightToolkit, 'vnl_%s' % name)
			setattr(self, name, function)
							   

(typeDict, noTypeDict, nonItk, vnl) = initDict()

for name, types in typeDict.iteritems() :
	exec '%s = ItkClass(name, types)' % name

for name, funcs in noTypeDict.iteritems() :
	exec '%s = ItkClassNoType(name, funcs)' % name
	
# for name in nonItk :
# 	exec '%s = InsightToolkit.%s' % (name, name)

# everything in nonItk is (should be) from SwigExtras sub module
# make it avaible from itk module
SwigExtras = InsightToolkit.SwigExtras

vnl = VnlClass(vnl)

# a function to print itk object info
def Print(itkObject, f=sys.stderr) :
	ss = StringStream()
	itkObject.Print(ss.GetStream())
	print >> f, ss.GetString()

# remove vars used to create module attribute
del typeDict, noTypeDict, nonItk, name, types, funcs #, vnl
# the same for classes and modules ...
del ItkClass, ItkClassNoType, ItkClassType, InsightToolkit, VnlClass, sys
# and the initDict function :-)
del initDict

	

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

import InsightToolkit as _InsightToolkit


def _initDict() :
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
	
	for f in dir(_InsightToolkit) :
		if f.startswith('itk') :
			typeRes = typeRegexp.findall(f)
			noTypeRes = noTypeRegexp.findall(f)
			if typeRes != [] :
				# type found
				classes.append(typeRes[0])
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

class _ItkClassType :
	"""
	this class gives functions avaible for a given type of a given class
	"""
	def __init__(self, name, t, funcs) :
		self.__name__ = name
		self.__type__ = t
		self.__function__ = getattr(_InsightToolkit, 'itk%s%s' % (name, t))
		for func in funcs :
			# attribute name must not have _ prefix
			if func[0] == '_' :
				attrib = func[1:]
			else :
				attrib = func
			function = getattr(_InsightToolkit, 'itk%s%s%s' % (name, t, func))
			# add method
			setattr(self, attrib, function)
	
	def __call__(self, *args, **kargs) :
		# some types needs to be callable (types without New() method)
		# as it don't seem to be a problem, make all types callable
		return self.__function__(*args, **kargs)
	
	def __repr__(self) :
		return '<itk class type itk.%s<%s>>' % (self.__name__, self.__type__)

		
class _ItkClassNoType :
	"""
	this class manage access to functions of classes without types
	"""
	def __init__(self, name, funcs) :
		self.__name__ = name
		self.__function__ = getattr(_InsightToolkit, 'itk%s' % name)
		for func in funcs :
			if func[0] == '_' :
				attrib = func[1:]
			else :
				attrib = func
			function = getattr(_InsightToolkit, 'itk%s%s' % (name, func))
			setattr(self, attrib, function)
	
	def __call__(self, *args, **kargs) :
		return self.__function__(*args, **kargs)
	
	def __repr__(self) :
		return '<itk class no type itk.%s>' % self.__name__


class _ItkClass :
	"""
	This class manage access to avaible types
	"""
	def __init__(self, name, types) :
		self.__name__ = name
		for t, funcs in types.iteritems() :
			attrib = _manageDigit(t)
			setattr(self, attrib, _ItkClassType(name, t, funcs))
			
	def __getitem__(self, key) :
		return getattr(self, _manageDigit(key))
	
	def __call__(self, *keys) :
		return getattr(self, _manageDigit("".join(map(str,keys))))
	
	def __repr__(self) :
		return '<itk class itk.%s>' % self.__name__


def _manageDigit(key) :
	# to allow usage of numbers
	key = str(key)
	# number attributes must be avaible without _ prefix
	if key.isdigit() :
		key = '_%s' % key
	return key


(_typeDict, _noTypeDict, _nonItk, _vnl) = _initDict()

for _name, _types in _typeDict.iteritems() :
	exec '%s = _ItkClass(_name, _types)' % _name

for _name, _funcs in _noTypeDict.iteritems() :
	exec '%s = _ItkClassNoType(_name, _funcs)' % _name
	
# for _name in _nonItk :
# 	exec '%s = _InsightToolkit.%s' % (_name, _name)

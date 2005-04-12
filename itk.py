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
	+ fDict : a dict. Key is class name without itk prefix. Values are avaible type names for this class.
	+ noType : a list. Each element is a class name without itk prefix. Class in this list don't have (recognized) extra types
	+ nonItk : everything non prefixed with itk or vnl
	+ vnl : everything which begins with vnl
	"""
	import re
	classes = []	# stores classes with types. Types will be isolated later.
	noType = []
	nonItk = []
	vnl = []
	noNew = []
	
	# compile regexp which will be used to find itk classes with types.
	typeRegexp = re.compile(r'^itk([a-zA-Z0-9]+?[a-z])([A-Z]*[0-9][A-Z0-9]*)_New$')
	
	for f in dir(_InsightToolkit) :
		if f.startswith('itk') :
			# we keep only attribute which ends with _New. 
			# we skip superclass attributes. It may be used in the future
			if f.endswith('_New') and '_Superclass' not in f :
				res = typeRegexp.findall(f)
				if res != [] :
					# regexp matched something. Add it to classes
					classes.append(res[0])
				else :
					# regexp don't match, but attribute starts with itk
					# add it to noType
					# [3:-4] == [len('itk'):-len('_New')]
					noType.append(f[3:-4])
			else :
				# [3:] == [len('itk'):]
				noNew.append(f[3:])
		else :
			if f.startswith("vnl") :
				# [3:] == [len('vnl'):]
				vnl.append(f[3:])
			else :
				# attrib don't start with itk or vnl
				nonItk.append(f)
				
	# now, generate dict which contains classes with types
	fDict = {}
	for f, t in classes :
		if not fDict.has_key(f) :
			fDict[f] = []
		fDict[f].append(t)
		
	# finally, return values :)
	return (fDict, noType, nonItk, vnl, noNew)

class _ItkClassType :
	def __init__(self, name, t) :
		self.__name__ = name
		self.__type__ = t
		attribs = [f[3+len(name)+len(t)+1:] for f in _InsightToolkit.__dict__ if f.startswith('itk%s%s_' % (name, t)) and '_Superclass' not in f]
		for attrib in attribs :
			function = getattr(_InsightToolkit, 'itk%s%s_%s' % (name, t, attrib))
			setattr(self, attrib, function)
	
	def __repr__(self) :
		return '<itk class type itk.%s<%s>>' % (self.__name__, self.__type__)

		
class _ItkClassNoType :
	def __init__(self, name) :
		self.__name__ = name
		attribs = [f[3+len(name)+1:] for f in _InsightToolkit.__dict__ if f.startswith('itk%s_' % name) and '_Superclass' not in f]
		for attrib in attribs :
			function = getattr(_InsightToolkit, 'itk%s_%s' % (name, attrib))
			setattr(self, attrib, function)
	
	def __repr__(self) :
		return '<itk class no type itk.%s>' % self.__name__


class _ItkClass :
	"""
	This class manage access to avaible types
	"""
	def __init__(self, name, types) :
		self.__name__ = name
		for t in types :
			attrib = _manageDigit(t)
			setattr(self, attrib, _ItkClassType(name, t))
			
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


(_fDict, _noType, _nonItk, _vnl, _noNew) = _initDict()

for _name, _types in _fDict.iteritems() :
	exec '%s = _ItkClass(_name, _types)' % _name

for _name in _noType :
	exec '%s = _ItkClassNoType(_name)' % _name
	
# for _name in _nonItk :
# 	exec '%s = _InsightToolkit.%s' % (_name, _name)
	

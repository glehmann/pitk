#!/usr/bin/env python


import InsightToolkit as _InsightToolkit
def _initDict() :
	import re
	classes = []
	noType = []
	nonItk = []
	for f in _InsightToolkit.__dict__ :
		if f.startswith('itk') :
			if f.endswith('_New') and '_Superclass' not in f :
				res = re.findall(r'^itk([a-zA-Z0-9]+?[a-z0-9])([A-Z]+[0-9][A-Z0-9]*)_New$', f)
				if res != [] :
					classes.append(res[0])
				else :
					noType.append(f[3:-4])
		elif not f.startswith("vnl") and f :
			nonItk.append(f)
	fDict = {}
	for f, t in classes :
		if not fDict.has_key(f) :
			fDict[f] = []
		fDict[f].append(t)
	return (fDict, noType, nonItk)

class _ItkClassType :
	def __init__(self, name, t) :
		attribs = [f[3+len(name)+len(t)+1:] for f in _InsightToolkit.__dict__ if f.startswith('itk%s%s_' % (name, t)) and '_Superclass' not in f]
		for attrib in attribs :
			exec 'self.%s = _InsightToolkit.itk%s%s_%s' % (attrib, name, t, attrib)

class _ItkClass2 :
	def __init__(self, name) :
		attribs = [f[3+len(name)+1:] for f in _InsightToolkit.__dict__ if f.startswith('itk%s_' % name) and '_Superclass' not in f]
		for attrib in attribs :
			function = _InsightToolkit.__dict__['itk%s_%s' % (name, attrib)]
			exec 'self.%s = function' % attrib

class _ItkClass :
	def __init__(self, name, types) :
		for t in types :
			exec 'self.%s = _ItkClassType(name, t)' % t
	def __getitem__(self, key) :
		return getattr(self, key)

(_fDict, _noType, _nonItk) = _initDict()

for _name, _types in _fDict.iteritems() :
	exec '%s = _ItkClass(_name, _types)' % _name

for _name in _noType :
	exec '%s = _ItkClass2(_name)' % _name
	
# for _name in _nonItk :
# 	exec '%s = _InsightToolkit.%s' % (_name, _name)
	

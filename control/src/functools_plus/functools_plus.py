from types import FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType
from functools import wraps

__all__ = 'annotate', 'getannot', 'setannot', 'hasannot', \
	'decorator', 'decorator_function', 'decorator_class', \
	'FUNC_VARARGS', 'FUNC_KWARGS', 'FUNC_GEN', \
	'inspect_callable', 'args_applyer', 'args_applyer_for', \
	'apply_args', 'apply_args_for'

def annotate(**annots):
	def deco(obj):
		if hasattr(obj,'__annotations__'):
			obj.__annotations__.update(annots)
		else:
			obj.__annotations__ = annots
		return obj
	return deco

_NONE = object()
def getannot(obj, key, default=_NONE):
	if hasattr(obj, '__annotations__'):
		if default is _NONE:
			return obj.__annotations__[key]
		else:
			return obj.__annotations__.get(key, default)
	elif default is _NONE:
		raise KeyError(key)
	else:
		return default

def setannot(obj, key, value):
	if hasattr(obj, '__annotations__'):
		obj.__annotations__[key] = value
	else:
		obj.__annotations__ = {key: value}

def hasannot(obj, key):
	if hasattr(obj, '__annotations__'):
		return key in obj.__annotations__
	else:
		return False

def inspect_callable(func):
	"""-> (arg_names, co_flags, func_defaults, func_name)"""
	return _inspect_callable(func,set())

def _inspect_callable(func,visited):
	if func in visited:
		raise TypeError("'%s' object is not callable/inspectable" % type(func).__name__)
	visited.add(func)
	if isinstance(func, FunctionType):
		co = func.func_code
		func_name = func.__name__
		arg_names = list(co.co_varnames[0:co.co_argcount])
		defaults = func.func_defaults
		flags = co.co_flags
	elif isinstance(func, MethodType):
		func = func.im_func
		co = func.func_code
		func_name = func.__name__
		arg_names = list(co.co_varnames[1:co.co_argcount])
		defaults = func.func_defaults
		flags = co.co_flags
	elif isinstance(func, type):
		func_name = func.__name__
		arg_names, flags, defaults, member_name = _inspect_callable(func.__init__.im_func,visited)
		if arg_names:
			del arg_names[0]
		if defaults and len(defaults) > len(arg_names):
			if not arg_names:
				defaults = None
			else:
				defaults = defaults[-len(arg_names):]
	elif hasattr(func, '__call__') and not isinstance(func, (BuiltinFunctionType, BuiltinMethodType)):
		func_name = '<%s object at 0x%x>' % (type(func).__name__, id(func))
		arg_names, flags, defaults, member_name = _inspect_callable(func.__call__.im_func,visited)
	else:
		raise TypeError("'%s' object is not callable/inspectable" % type(func).__name__)
	return arg_names, flags, defaults, func_name

FUNC_VARARGS = 0x04
FUNC_KWARGS  = 0x08
FUNC_GEN     = 0x20

def args_applyer(arg_names,flags=0,defaults=None,func_name=None):
	"""-> f(args..., [*varargs], [**kwargs]) -> ((args...)+varargs, kwargs)"""
	all_args = list(arg_names)
	if len(arg_names) == 1:
		body = ['(',arg_names[0],',)']
	elif arg_names:
		body = ['(',','.join(arg_names),')']
	else:
		body = []
	if flags & FUNC_VARARGS:
		args_name = '_args'
		i = 0
		while args_name in arg_names:
			args_name = '_args'+i
			i += 1
		all_args.append('*'+args_name)
		if arg_names:
			body.append('+')
		body.append(args_name)
	elif not arg_names:
		body.append('()')
	body.append(',')
	if flags & FUNC_KWARGS:
		kwargs_name = '_kwargs'
		i = 0
		while kwargs_name in arg_names:
			kwargs_name = '_kwargs'+i
			i += 1
		all_args.append('**'+kwargs_name)
		body.append(kwargs_name)
	else:
		body.append('{}')
	if func_name:
		apply_args = named_lambda(func_name,all_args,''.join(body))
	else:
		apply_args = eval('lambda %s: (%s)' % (','.join(all_args), ''.join(body)))
	if defaults:
		apply_args.func_defaults = defaults
	return apply_args

def named_lambda(name,args,body):
	_named_lambda = 'def _named_lambda():\n\tdef %s(%s):\n\t\treturn %s\n\treturn %s' % (
		name, ','.join(args), body, name)
	del name, args, body
	exec(_named_lambda)
	return _named_lambda()

# begin helper functions (not used by decorator.py)
def args_applyer_for(func):
	return args_applyer(*inspect_callable(func))

def apply_args(args,kwargs,arg_names,flags=0,defaults=None,func_name=None):
	return args_applyer(arg_names,flags,defaults,func_name)(*args,**kwargs)

def apply_args_for(func,args,kwargs):
	return args_applyer(*inspect_callable(func))(*args,**kwargs)
# end helper functions

def decorator(deco):
	"""deco(func,func_args,func_kwargs,deco_args...)
	
	@decorator
	def my_deco(func,func_args,func_kwargs,deco_args...):
		pass
	
	@my_deco(*deco_args,**deco_kwargs)
	def func(*func_args,**func_kwargs):
		pass
		
	@decorator
	def my_deco2(func,func_args,func_kwargs):
		pass
		
	@my_deco2
	def func2(*func_args,**func_kwargs):
		pass

	@decorator
	def my_deco3(func,func_args,func_kwargs,x=1):
		pass
		
	@my_deco3()
	def func3(*func_args,**func_kwargs):
		pass
	
	@decorator
	@annotate(apply_func_args=False)
	def my_deco4(func,func_args,func_kwargs):
		pass
	
	@my_deco4
	def func4(*func_args,**func_kwargs):
		pass
	"""
	if isinstance(deco, type):
		return decorator_class(deco)
	else:
		return decorator_function(deco)

def decorator_function(deco):
	arg_names, flags, defaults, deco_name = inspect_callable(deco)
	if flags & FUNC_VARARGS == 0 and len(arg_names) < 3:
		raise TypeError('decorator functions need at least 3 arguments (func, func_args, func_kwargs)')
	del arg_names[0:3]
	if not hasattr(deco, '__annotations__'):
		deco.__annotations__ = {}
	apply_deco_args = args_applyer(arg_names,flags,defaults,deco_name)
	deco_wrapper_wrapper = _decorator_function(deco,apply_deco_args)
	if not arg_names and flags & (FUNC_VARARGS | FUNC_KWARGS) == 0:
		return deco_wrapper_wrapper()
	else:
		return deco_wrapper_wrapper

def _decorator_function(deco,apply_deco_args):
	@wraps(deco)
	def deco_wrapper_wrapper(*deco_args,**deco_kwargs):
		deco_args, deco_kwargs = apply_deco_args(*deco_args,**deco_kwargs)
		def deco_wrapper(func):
			apply_func_args = getannot(deco, 'apply_func_args', True)
			if apply_func_args:
				if not callable(apply_func_args):
					apply_func_args = args_applyer(*inspect_callable(func))
				@wraps(func)
				def wrapper(*func_args,**func_kwargs):
					func_args, func_kwargs = apply_func_args(*func_args,**func_kwargs)
					return deco(func,func_args,func_kwargs,*deco_args,**deco_kwargs)
			else:
				@wraps(func)
				def wrapper(*func_args,**func_kwargs):
					return deco(func,func_args,func_kwargs,*deco_args,**deco_kwargs)
			return wrapper
		deco_wrapper.__annotations__ = deco.__annotations__
		return deco_wrapper
	return deco_wrapper_wrapper

def decorator_class(deco):
	arg_names, flags, defaults, deco_name = inspect_callable(deco)
	if flags & FUNC_VARARGS == 0 and not arg_names:
		raise TypeError('decorator classes need an __init__ method with at least 1 argument (func)')
	del arg_names[0:1]
	if not hasattr(deco, '__annotations__'):
		deco.__annotations__ = {}
	apply_deco_args = args_applyer(arg_names,flags,defaults,deco_name)
	deco_wrapper_wrapper = _decorator_class(deco,apply_deco_args)
	if not arg_names and flags & (FUNC_VARARGS | FUNC_KWARGS) == 0:
		return deco_wrapper_wrapper()
	else:
		return deco_wrapper_wrapper

def _decorator_class(deco,apply_deco_args):
	def deco_wrapper_wrapper(*deco_args,**deco_kwargs):
		deco_args, deco_kwargs = apply_deco_args(*deco_args,**deco_kwargs)
		def deco_wrapper(func):
			apply_func_args = getannot(deco, 'apply_func_args', True)
			deco_obj = deco(func,*deco_args,**deco_kwargs)
			if apply_func_args:
				if not callable(apply_func_args):
					apply_func_args = args_applyer(*inspect_callable(func))
				@wraps(func)
				def wrapper(*func_args,**func_kwargs):
					func_args, func_kwargs = apply_func_args(*func_args,**func_kwargs)
					return deco_obj(*func_args,**func_kwargs)
			else:
				wrapper = wraps(func)(deco_obj.__call__)
			return wrapper
		deco_wrapper.__annotations__ = deco.__annotations__
		return deco_wrapper
	return deco_wrapper_wrapper

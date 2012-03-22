# Functools Plus

This is a Python module that provides some functions for working with
functions.

## Reference

 * `@annotate(***)`
 * `getannot(obj, key, [default])`
 * `setannot(obj, key, value)`
 * `hasannot(obj, key)`
 * `@decorator`

Constants:

 * `FUNC_VARARGS`
 * `FUNC_KWARGS`
 * `FUNC_GEN`

Helper Functions:

 * `inspect_callable(a_callable)`
 * `args_applyer(arg_names, [flags], [defaults], [func_name])`
 * `args_applyer_for(func)`
 * `apply_args(args, kwargs, arg_names, [flags], [defaults], [func_name])`
 * `apply_args_for(func, args, kwargs)`

### `@annotate(***)`

`annotate` is a decorator that allows you to add meta data (annotations)
to a function or class. These annotations can later be read using `getannot`
and changed with `setannot`. The existance of an annotation can be queried
using `hasannot`.

	@annotate(egg='spam', tomato=42)
	def foo():
		pass

The annotations will be storad as an `__annotations__` member of the annotated
object.

### `getannot(obj, key, [default])`

Read an annotation from an object. If `key` does not exist `default` is returned.
If `default` is not given a `KeyError` is raised.

	print getannot(foo, 'tomato')

### `setannot(obj, key, value)`

Set an annotation outside of the declaration of `obj`.

	setannot(foo, 'aubergines', 'lots')

### `hasannot(obj, key)`

Query wether an annotation with `key` exists.

	print hasannot(foo, 'egg')

### `@decorator`

The `decorator` decorator makes declaring simple decorators easy.

	@decorator
	def repeat(func,args,kwargs,times):
		return [func(*args,**kwargs) for i in xrange(times)]
	
	# or if you like it more complex:
	@decorator
	class repeat(object):
		def __init__(self,func,times):
			self.func = func
			self.times = times
	
		def __call__(*args,**kwargs):
			# use this trick to avoid name collisions with `self`:
			self, args = args[0], args[1:]
			func = self.func
			return [func(*args,**kwargs) for i in xrange(self.times)]
	
	@repeat(3)
	def say(what):
		return what
	
`say('hello')` returns:

	['hello', 'hello', 'hello']

If your decorator does not take any arguments the generated decorator may not
be called when used:

	@decorator
	def logged(func,args,kwargs):
		print 'BEGIN %s(*%r, **%r)' % (func.__name__,args,kwargs)
		try:
			return func(*args,**kwargs)
		finally:
			print 'END',func.__name__

	# or again if you like it more complex:
	@decorator
	class logged(object):
		def __init__(self,func):
			self.func = func
		def __call__(*args,**kwargs):
			self, args = args[0], args[1:]
			func = self.func
			print 'BEGIN %s(*%r, **%r)' % (func.__name__,args,kwargs)
			try:
				return func(*args,**kwargs)
			finally:
				print 'END',func.__name__

	@logged
	def say(what):
		return what

`say('hello')` prints:

	BEGIN say(*('hello',), **{})
	hello
	END say

Note that in case your decorator has arguments but declares default values for
them you still need to call your decorator when decorating:

	@decorator
	def repeat(func,args,kwargs,times=3):
		return [func(*args,**kwargs) for i in xrange(times)]

	@repeat()
	def say(what):
		return what

In case your decorator changes the signature of the decorated function you need
to tell the `@decorator` decorator that it should not apply the original
signature:

	@decorator
	@annotate(applay_func_args=False)
	def something(func,args,kwargs,deco_arg1,deco_arg2):
		return func(*args,**kwargs)

Note that you can also write the following, because the original
`__annotations__` object is referenced and not copied:

	@annotate(applay_func_args=False)
	@decorator
	def something(func,args,kwargs,deco_arg1,deco_arg2):
		return func(*args,**kwargs)

You can also define the new signature so you don't have to check it manually and
don't need to manually extract arguments passed as keywords that are actually
explicitly named:

	@annotate(applay_func_args=lambda a,b,c=42: ((a,b,c),{}))
	@decorator
	def something(func,args,kwargs,deco_arg1,deco_arg2):
		return func(*args,**kwargs)

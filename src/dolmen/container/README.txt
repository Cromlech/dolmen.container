dolmen.viewlet
**************

  >>> import dolmen.viewlet
  >>> dolmen.viewlet.testing.grok('dolmen.viewlet.meta')

Test environnment
=================

Let set up some context : a content, a request coming from a browser and a view
inside which viewlets would display ::

  >>> mammoth = object()

  >>> from cromlech.io.testing import TestRequest
  >>> request = TestRequest()
  >>> from cromlech.browser.testing import TestView
  >>> view = TestView()

We also have the simplest possible template ::
  
  >>> class Template(object):
  ...     def render(self, renderer):
  ...         return "A simple template for %r." % renderer

  >>> generic_template = Template()
  
get some tools :

  >>> from zope.interface.verify import verifyClass

Example manager
===============

The manager is a location (a slot) where viewlet will display. 
It manage viewlets in the sense of a conductor asking them to render and
merging outputs ::

  >>> import dolmen.viewlet
  >>> from grokcore.component import testing
  
ViewletManager is our IViewletManager base implementation ::

  >>> verifyClass(dolmen.viewlet.IViewletManager,
  ...               dolmen.viewlet.ViewletManager)
  True

Let's make ours ::

  >>> class LeftColumn(dolmen.viewlet.ViewletManager):
  ...     pass

 
  >>> LeftColumn.__name__
  'LeftColumn'

  >>> testing.grok_component('left', LeftColumn)
  True

  >>> LeftColumn.__name__
  'leftcolumn'

Nothing to display yet since we have no managed viewlet ::

  >>> left = LeftColumn(mammoth, request, view)
  >>> left()
  u''

  >>> left.template = generic_template
  >>> left()
  'A simple template for <leftcolumn object at ...>.'


Exemple component
=================

Viewlet provide a base implementation of IViewlet ::

  >>> verifyClass(dolmen.viewlet.IViewlet, dolmen.viewlet.Viewlet)
  True

Let's make a viewlet ::

  >>> class WeatherBlock(dolmen.viewlet.Viewlet):
  ...     dolmen.viewlet.slot(LeftColumn)
  
  >>> dolmen.viewlet.IViewlet.implementedBy(WeatherBlock)
  True
  
  >>> testing.grok_component('weather', WeatherBlock)
  True

  >>> left.template = None
  >>> left.update()
  >>> print left.viewlets
  [<weatherblock object at ...>]
  
A viewlet shall either have a template or implements its own render ::

  >>> left()
  Traceback (most recent call last):
  ...
  NotImplementedError: <class 'weatherblock'> :
  Provide a template or override the render method

Gimme a template ::

  >>> WeatherBlock.template = generic_template
  >>> left()
  u'A simple template for <weatherblock object at ...>.'

Let's test with more than one viewlet ::

  >>> class AnotherBlock(dolmen.viewlet.Viewlet):
  ...     dolmen.viewlet.slot(LeftColumn)
  ...     template = generic_template

  >>> testing.grok_component('another', AnotherBlock)
  True

  >>> left()
  u'A simple template for <anotherblock object at ...>.\nA simple template for <weatherblock object at ...>.'

  >>> dolmen.viewlet.order.set(AnotherBlock, (10, 10))
  >>> left()
  u'A simple template for <weatherblock object at ...>.\nA simple template for <anotherblock object at ...>.'

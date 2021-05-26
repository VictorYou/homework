This is a modified v'0.4' suds library.
Bug fixing:
	1. suds.xsd.sxbase.SchemaObject.namespace, suds could not mapping object to soap element correctly when definition of the element, in xsd, refers to other element
	2. suds.client.Method.__call__, suds is not compatible with robot framework, when logging level is set lower than info may cause unexpected errors. 
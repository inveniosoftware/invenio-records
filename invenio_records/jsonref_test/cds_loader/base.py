from jsonref import JsonLoader
import urlparse

class CDSResolverException(Exception):
    pass

class CDSResolverProgrammaticException(Exception):
    pass

class CDSResolverMetaclass(type):
    def __init__(cls, name, bases, dct):
        print('registering %s' % (name,))

        for scheme in dct['scheme']:
            if cls.resolvers.get(scheme):
                raise CDSResolverProgrammaticException(
                    "Scheme resolver already defined: %s" % scheme)

            if not dct.get('resolve') or not isinstance(dct['resolve'], staticmethod):
                raise CDSResolverProgrammaticException(
                    "Resolver %s doesn't implement resolve method" % name)

            cls.resolvers[scheme] = cls

        super(CDSResolverMetaclass, cls).__init__(name, bases, dct)
        

class CDSResolver():
    """Base class for CSDResolver

    Used mainly with dojson module in cds
    to translate marc21 documents to json
    ones.

    If you want to add a new class to
    handle new schemas just create class
    like this:

    class CDSNewSchema(CSDResolver):
        schema = [<list_of_string_of_schemas>]
        @staticmethod
        def resolve(reference):
            <dereferencing code>
            <return dereferenced link>
    """

    __metaclass__ = CDSResolverMetaclass
    resolvers = {}
    scheme = []

    @staticmethod
    def dereference(scheme, reference):
        if CDSResolver.resolvers.get(scheme):
            resolver = CDSResolver.resolvers[scheme]
            return resolver.resolve(reference)
        else:
            raise CDSResolverException("No resolver for scheme %s" % scheme)


class CDSJsonLoader(JsonLoader):
    def get_remote_json(self, uri, **kwargs):
        scheme = urlparse.urlsplit(uri).scheme
        try:
            return CDSResolver.dereference(scheme, uri)
        except CDSResolverException, e:
            return super(CDSJsonLoader, self).get_remote_json(uri, **kwargs)


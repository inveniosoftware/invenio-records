from base import CDSResolver
import json
import _mysql

class CDSMongoResolver(CDSResolver):
    scheme = ['mongo']

    @staticmethod
    def resolve(reference):
        return 'mongo'


con = _mysql.connect('localhost', 'root', '<password>', 'invenio_json')

class CDSDatabaseResolver(CDSResolver):
    scheme = ['http', 'cds'] # uncommented => use database
    #scheme = ['foobar']     # uncommented => use file
    @staticmethod
    def resolve(reference):
        
        reference = reference[reference.rfind('/')+1:reference.rfind('.')]
        
        con.query("SELECT json from record_json where id=%s" % reference)
        result = con.use_result().fetch_row()[0][0]
    
        #read_json = open('/home/theer/.virtualenvs/cdsinvenio/src/cds/cds/base/dojson/test_out/%s' % reference, 'r').read()
        #return json.loads(read_json)
        return json.loads(result)



class CDSLocalResolver(CDSResolver):
    #scheme = ['http', 'cds'] # uncommented => use files
    scheme = ['foobar']       # uncommented => use database
    @staticmethod
    def resolve(reference):
        
        reference = reference[reference.rfind('/')+1:reference.rfind('.')]
        
        #con.query("SELECT json from record_json where id=%s" % reference)

        
        read_json = open('./sample_data/%s.json' % reference, 'r').read()
        return json.loads(read_json)
        #return json.loads(result)

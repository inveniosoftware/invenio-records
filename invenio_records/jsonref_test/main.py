import urlparse
import traceback
import time

from jsonref import JsonLoader, JsonRef, JsonRefError, dumps
from pprint import pprint

from cds_loader import CDSJsonLoader

document = {
    'param1': 'ala',
    'param2': {'$ref':'mongo://blabla'},
    'param3': {'$ref':'#/param1'},
    'param4': {'$ref': 'http://127.0.0.1:4001/762638.json'},
   # 'param5': {'$ref': 'http://127.0.0.1:4001/dummy2.json'}
}



#try:
#    JsonRef.replace_refs(document, loader=CDSJsonLoader())
#    pprint(JsonRef.replace_refs(document, loader=CDSJsonLoader()))
#except JsonRefError, e:
#    traceback.print_exc()
#    import pdb
#    pdb.set_trace()
#

def prepare_for_dereference(document):
    return JsonRef.replace_refs(document, loader=CDSJsonLoader())

def dereference(json_ref_document):
    traverse(json_ref_document)
#    pprint(json_ref_document)

def traverse(obj):
    """Visists all nodes in a data structure

    This is just to trigger actual dereference,
    because jsonref creates lazyproxy object for
    every link. The real resource is instantiated
    when accessed.
    """

    if isinstance(obj, dict):
        for key, value in obj.iteritems():
            traverse(value)
            
    if isinstance(obj, list):
        for item in obj:
            traverse(item)

    if isinstance(obj, JsonRef):
        obiekt = obj.__subject__
        traverse(obiekt)

def main():
    start = time.time()
    json_ref_document = prepare_for_dereference(document)
    dereference(json_ref_document)
    end = time.time()
    print 'Time: %s seconds' % (end-start)

if __name__=='__main__':
    try:
        main()
    except Exception, e:
        traceback.print_exc()
        print e.message
        import pdb
        pdb.set_trace()

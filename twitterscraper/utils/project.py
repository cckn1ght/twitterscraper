
from IPython.core.debugger import Tracer


def parse_query(query_str):
    query = {}
    Tracer()()
    for op in query_str.split(','):
        if len(op.split(':')) == 1:
            query['keyword'] = op.split(':')[0]
        else:
            query[op.split(':')[0]] = op.split(':')[1]
    return query
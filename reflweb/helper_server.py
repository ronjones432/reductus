import sys
import time
import BaseHTTPServer, SocketServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
#import multiprocessing
#import webbrowser
import urlparse, os

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
import jsonrpclib.config

try:
    import config
except ImportError:
    import default_config as config

jsonrpclib.config.use_jsonclass = False
HandlerClass = SimpleHTTPRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"
homepage = 'web_reduction_filebrowser.html'
currdir = os.path.dirname( __file__ )


if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
#server_address = ('localhost', 0 ) # get next open socket

#HandlerClass.protocol_version = Protocol
#httpd = ServerClass(server_address, HandlerClass)
#http_port = httpd.socket.getsockname()[1]
#print "http port: ", http_port

#sa = httpd.socket.getsockname()
#print "Serving HTTP on", sa[0], "port", sa[1], "..."
## httpd.serve_forever()
#http_process = multiprocessing.Process(target=httpd.serve_forever)
#http_process.start()

class JSONRPCRequestHandler(SimpleJSONRPCRequestHandler):
    """JSON-RPC and documentation request handler class.

    Handles all HTTP POST requests and attempts to decode them as
    XML-RPC requests.

    Handles all HTTP GET requests and interprets them as requests
    for web pages, js, json or css.
    
    Put all static files to be served in 'static' subdirectory.
    """
    
    #rpc_paths = ('/', '/RPC2')
    rpc_paths = () # accept all
    def __init__(self, request, client_address, server):
        #print "init of request handler", request, time.ctime(), self.timeout
        SimpleJSONRPCRequestHandler.__init__(self, request, client_address, server)
    
    def do_OPTIONS(self):
        print 'sending response', time.ctime()
        self.send_response(200)
        #self.send_header('Access-Control-Allow-Origin', 'http://localhost:8000')
        #self.send_header('Access-Control-Allow-Origin', "http://localhost:%d" % (http_port,))           
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

    # Add these headers to all responses
    def end_headers(self):
        self.send_header("Access-Control-Allow-Headers", 
                          "Origin, X-Requested-With, Content-Type, Accept")
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleJSONRPCRequestHandler.end_headers(self)


if getattr(config, 'serve_staticfiles', True) == True:    
    def do_GET(self):
        """Handles the HTTP GET request.

        Interpret all HTTP GET requests as requests for static content.
        """
        # Check that the path is legal
        #if not self.is_rpc_path_valid():
        #    self.report_404()
        #    return

        # Parse query data & params to find out what was passed
        parsedParams = urlparse.urlparse(self.path)
        ## don't need the parsed GET query, at least not yet.
        #queryParsed = urlparse.parse_qs(parsedParams.query)
        #docname = os.path.basename(parsedParams.path)
        docname = parsedParams.path.lstrip('/')
        print docname
        if (docname == "" or docname == "/"):
            docname = homepage
        docpath = os.path.join(currdir, 'static',  *(docname.split("/")))
        if (os.path.exists(docpath)):
            response = open(docpath, 'r').read()
        else:
            self.report_404()
            return
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        if docname.endswith('.js'):
            self.send_header("Content-type", "text/javascript")
        elif docname.endswith('.css'):
            self.send_header("Content-type", "text/css")
        elif docname.endswith('.json'):
            self.send_header("Content-type", "application/json")
        elif docname.endswith('.gif'):
            self.send_header("Content-type", "image/gif")
        elif docname.endswith('.png'):
            self.send_header("Content-type", "image/png")
        else:
            self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    JSONRPCRequestHandler.do_GET = do_GET

class ThreadedJSONRPCServer(SocketServer.ThreadingMixIn, SimpleJSONRPCServer):
    pass
    
#server = SimpleJSONRPCServer(('localhost', 8001), encoding='utf8', requestHandler=JSONRPCRequestHandler)
server = ThreadedJSONRPCServer((config.jsonrpc_servername, config.jsonrpc_port), encoding='utf8', requestHandler=JSONRPCRequestHandler)
rpc_port = server.socket.getsockname()[1]
#webbrowser.open_new_tab('http://localhost:%d/index.html?rpc_port=%d' % (http_port, rpc_port))

import h5py, os, dataflow
from dataflow.core import Template, sanitizeForJSON, lookup_instrument
from dataflow.cache import use_redis
from dataflow.calc import process_template
import dataflow.core as df

from dataflow.modules.refl import define_instrument, INSTRUMENT

#use_redis()
define_instrument(data_source=config.data_repository)

def get_file_metadata(pathlist=None):
    if pathlist is None: pathlist = []
    print pathlist
    import urllib
    import urllib2
    import json

    url = config.file_helper #'http://ncnr.nist.gov/ipeek/listftpfiles.php'
    values = {'pathlist[]' : pathlist}
    data = urllib.urlencode(values, True)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    fn = response.read()
    # this converts json to python object, then the json-rpc lib converts it 
    # right back, but it is more consistent for the client this way:
    return json.loads(fn)


def get_instrument(instrument_id=INSTRUMENT):
    """
    Make the instrument definition available to clients
    """
    instrument = lookup_instrument(instrument_id)
    return instrument.get_definition()

def refl_load(file_descriptors):
    """ 
    file_descriptors will be a list of dicts like 
    [{"path": "ncnrdata/cgd/201511/21066/data/HMDSO_17nm_dry14.nxz.cgd", "mtime": 1447353278}, ...]
    """
    modules = [{"module": "ncnr.refl.load", "version": "0.1", "config": {}}]
    template = Template("test", "test template", modules, [], "ncnr.magik", version='0.0')
    retval = process_template(template, {0: {"files": file_descriptors}}, target=(0, "output"))
    return sanitizeForJSON(retval.todict())

def find_calculated(template_def, config):
    """
    Returns a vector of true/false for each node in the template indicating
    whether that node value has been calculated yet.
    """
    template = Template(**template_def)
    retval = dataflow.calc.find_calculated(template, config)
    return retval

def calc_terminal(template_def, config, nodenum, terminal_id):
    """ json-rpc wrapper for calc_single
    template_def = 
    {"name": "template_name",
     "description": "template description!",
     "modules": ["list of modules"],
     "wires": ["list of wires"],
     "instrument": "facility.instrument_name",
     "version": "2.7.3"
    }
    
    where modules in list of modules above have structure:
    module = 
    {"module": "facility.instrument_name.module_name",
     "version": "0.3.2"
    }
    
    and wires have structure:
    [["wire_start_module_id:wire_start_terminal_id", "wire_end_module_id:wire_end_terminal_id"],
     ["1:output", "2:input"],
     ["0:xslice", "3:input"]
    ]
    
    config = 
    [{"param": "value"}, ...]
    
    nodenum is the module number from the template for which you wish to get the calculated value
    
    terminal_id is the id of the terminal for that module, that you want to get the value from
    (output terminals only).
    """
    template = Template(**template_def)
    #print "template_def:", template_def, "config:", config, "target:",nodenum,terminal_id
    #print "modules","\n".join(m for m in df._module_registry.keys())
    retval = process_template(template, config, target=(nodenum, terminal_id))
    return sanitizeForJSON(retval.todict())
    
def calc_template(template_def, config):
    """ json-rpc wrapper for process_template """
    template = Template(**template_def)
    #print "template_def:", template_def, "config:", config
    retvals = process_template(template, config, target=(None,None))
    output = {}
    for rkey, rv in retvals.items():
        module_id, terminal_id = rkey
        module_key = str(module_id)
        output.setdefault(module_key, {})
        output[module_key][terminal_id] = sanitizeForJSON(rv.todict())
    return output
        
    
server.register_function(get_file_metadata)
server.register_function(refl_load)
server.register_function(calc_terminal)
server.register_function(calc_template)
server.register_function(get_instrument)
server.register_function(find_calculated)
print "serving on",rpc_port
server.serve_forever()
print "done serving rpc forever"
#httpd_process.terminate()

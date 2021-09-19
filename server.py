import argparse
import cgi
from fake_follower_finder import query
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import logging


class Handler(BaseHTTPRequestHandler):
    def _do_404(self):
        logging.error('404: %s\nHeaders:\n%s', str(
            self.path), str(self.headers))
        self.send_response(404)


    def _do_500(self):
        logging.error('500: %s\nHeaders:\n%s', str(
            self.path), str(self.headers))
        self.send_response(500)


    def _do_query(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        try:
            screen_name = form['screen_name'].value
            logging.info('screen name: %s', screen_name)
            fake_followers = query(screen_name)
        except:
            logging.exception('query failed')
            self._do_500()
            return

        self.send_response(200)
        lines = [
            '<html><body>',
            '  found %d fake followers' % len(fake_followers),
            '  <ul>',
        ]

        lines.extend([
            '    <li><a href="https://twitter.com/%s">%s</a></li>' % (f, f)
            for f in fake_followers
        ])

        lines.extend([
                '  </ul>',
                '</body></html>'
        ])

        self.wfile.writelines([bytes(l) for l in lines])


    def do_GET(self):
        logging.info('GET request,\nPath: %s\nHeaders:\n%s',
                     str(self.path), str(self.headers))
        if str(self.path) == '/':
            self.path = 'index.html'
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            self._do_404()


    def do_POST(self):
        logging.info('POST request,\nPath: %s\nHeaders:\n%s',
                     str(self.path), str(self.headers))
        if str(self.path) == '/query':
            self._do_query()
        else:
            self._do_404()


def _run(port=8000):
    import pdb
    pdb.set_trace()
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    try:
        logging.info('starting httpd on port %d', port)
        httpd = HTTPServer(server_address, Handler)
        logging.info('starting to serve')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('stopping httpd\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Identify fake followers.')
    parser.add_argument('--port', type=int, default=4321,
                        help='the port on which to serve')

    args = parser.parse_args()
    _run(port=args.port)

# Import necessary modules
try:
    import httplib
    from urlparse import urlparse
except ModuleNotFoundError:
    import http.client as httplib
    from urllib.parse import urlparse  # Python 3

import socket
import ssl
import random
from functools import partial
from anytree import ContStyle, RenderTree

try:
    from multiprocessing import Pool, freeze_support
except ImportError:
    Pool = None

from .checkers import HeaderEvaluator, CheckerFactory, Finding, FindingSeverity, FindingType
from .models import ModelFactory
from securityheaders.formatters import FindingFormatterFactory
from .optionparser import OptionParser

# Fix for pickling methods
def _pickle_method(method):
    func_name = method.__func__.__name__
    obj = method.__self__
    cls = method.__self__.__class__
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for base_cls in cls.__mro__:
        if func_name in base_cls.__dict__:
            func = base_cls.__dict__[func_name]
            break
    else:
        raise AttributeError(f"Method {func_name} not found in class hierarchy")
    return func.__get__(obj, cls)

try:
    import copyreg
except ModuleNotFoundError:
    import copyreg as copy_reg

import types
copyreg.pickle(types.MethodType, _pickle_method, _unpickle_method)

class SecurityHeaders:
    def __init__(self):
        self.options = OptionParser()

    def load_options_from_file(self, filepath):
        self.options.parse(filepath)

    def set_option(self, key, value):
        self.options.set(key, value)

    def get_option(self, checker, key):
        return self.options.get(checker, key)

    def get_options(self):
        return self.options.result()

    def get_all_checker_names(self):
        return CheckerFactory().getnames()

    def get_all_header_names(self):
        return sorted(ModelFactory().getheadernames())

    def get_all_formatter_names(self):
        return FindingFormatterFactory().getshortnames()

    def get_formatter(self, formatter_name):
        return FindingFormatterFactory().getformatter(formatter_name)

    def format_findings(self, formatter, findings):
        return self.get_formatter(formatter).format(findings)

    def check_headers_from_string(self, headers, options=None):
        options = options or self.options.result()
        return self.check_headers_with_list(headers.splitlines(), options)

    def check_headers_with_list(self, res_headers, options=None):
        options = options or self.options.result()
        headers = []
        for header in res_headers:
            s = header.split(':', 1)
            if len(s) == 2:
                headers.append((s[0].lower(), s[1]))
            else:
                headers.append((s[0].lower(), ''))
        return self.check_headers_with_map(dict(headers), options)

    def check_headers_with_map(self, header_map, options=None):
        options = options or self.options.result()
        checks = CheckerFactory().getactualcheckers(options.get('checks', []))
        unwanted = CheckerFactory().getactualcheckers(options.get('unwanted', []))
        options['checks'] = [e for e in checks if e not in unwanted]
        return HeaderEvaluator().evaluate(header_map, options)

    def check_headers_parallel(self, urls, options=None, callback=None):
        options = options or self.options.result()

        if Pool:
            results = []
            freeze_support()
            with Pool(processes=100) as pool:
                for url in urls:
                    result = pool.apply_async(self.check_headers, args=(url, options.get('redirects', 3), options), callback=callback)
                    results.append(result)
                pool.close()
                pool.join()
            return [res.get() for res in results]
        else:
            raise NotImplementedError("Parallelism is not supported")

    def check_headers(self, url, follow_redirects=3, options=None):
        options = options or self.options.result()

        if isinstance(url, tuple):
            url_id, url = url
        else:
            url_id = 1

        url = url.strip('"')
        if not urlparse(url).scheme:
            url = f"{options.get('defaultscheme', 'https')}://{url}"

        parsed = urlparse(url)
        hostname = parsed.netloc
        path = parsed.path or "/"
        protocol = parsed.scheme

        headers = self._get_user_agent_header()

        try:
            conn = self._get_connection(hostname, protocol)
            conn.request('GET', path, None, headers)
            res = conn.getresponse()
            response_headers = dict(res.getheaders())

            if res.status in range(300, 400) and follow_redirects > 0:
                return self.check_headers((url_id, response_headers.get('location', '')), follow_redirects - 1, options)

            results = self.check_headers_with_map(response_headers, options)
            for finding in results:
                finding.url = url
                finding.url_id = url_id

            return results

        except (socket.timeout, ssl.SSLError) as e:
            return [Finding(None, FindingType.ERROR, str(e), FindingSeverity.ERROR, None, None, url, url_id)]
        except Exception as e:
            return [Finding(None, FindingType.ERROR, str(e), FindingSeverity.ERROR, None, None, url, url_id)]

    def check_headers_with_timeout(self, url, timeout=10, follow_redirects=3, options=None):
        options = options or self.options.result()

        if isinstance(url, tuple):
            url_id, url = url
        else:
            url_id = 1

        url = url.strip('"')
        if not urlparse(url).scheme:
            url = f"{options.get('defaultscheme', 'https')}://{url}"

        parsed = urlparse(url)
        hostname = parsed.netloc
        path = parsed.path or "/"
        protocol = parsed.scheme

        headers = self._get_user_agent_header()

        try:
            conn = self._get_connection(hostname, protocol, timeout)
            conn.request('GET', path, None, headers)
            res = conn.getresponse()
            response_headers = dict(res.getheaders())

            if res.status in range(300, 400) and follow_redirects > 0:
                return self.check_headers((url_id, response_headers.get('location', '')), follow_redirects - 1, options)

            results = self.check_headers_with_map(response_headers, options)
            for finding in results:
                finding.url = url
                finding.url_id = url_id

            return results

        except socket.timeout:
            return [Finding(None, FindingType.ERROR, "Timeout occurred", FindingSeverity.ERROR, None, None, url, url_id)]
        except Exception as e:
            return [Finding(None, FindingType.ERROR, str(e), FindingSeverity.ERROR, None, None, url, url_id)]

    def _get_connection(self, hostname, protocol, timeout=None):
        if protocol == 'http':
            return httplib.HTTPConnection(hostname, timeout=timeout)
        elif protocol == 'https':
            return httplib.HTTPSConnection(hostname, context=ssl._create_unverified_context(), timeout=timeout)
        else:
            raise ValueError(f"Unknown protocol: {protocol}")

    def _get_user_agent_header(self):
        agents = [
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
            'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'
        ]
        return {"User -Agent": random.choice(agents)}
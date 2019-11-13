
import argparse
import random
import requests
import time

from collections import defaultdict

ROUTES = ('subject', 'predicate', 'object')


def parse_args():
    desc = 'Make random calls to the demo server.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-u', '--url', help='server url',
                        default='http://localhost:5000/')
    return parser.parse_args()


class Reporter():
    def __init__(self):
        self.last_time = time.time()
        self.nchars = self.nrequests = 0
        self.status_codes = defaultdict(int)

    def add(self, response):
        self.nchars += len(response.text)
        self.nrequests += 1
        self.status_codes[response.status_code] += 1
        dt = time.time() - self.last_time
        if dt > 10:
            kb_per_second = self.nchars / (1000 * dt)
            requests_per_second = self.nrequests / dt
            status_codes = {code: count for code, count in self.status_codes.items()}
            print(f'nchars={self.nchars} nrequests={self.nrequests} '
                  f'kbps={kb_per_second:.1f} rps={requests_per_second:.1f} ')
            print(f'... status_codes={status_codes}')
            self.__init__()


def main(args):
    assert args.url.endswith('/'), args.url

    def _max_id(route):
        return int(requests.get(f'{args.url}{route}/').json()[f'nb_{route}s'])

    max_ids = {route: _max_id(route) for route in ROUTES}
    print('max_ids:', max_ids)
    reporter = Reporter()

    while True:
        route = random.choice(ROUTES)
        if random.choice((0, 10)):
            id_ = str(random.randint(-1, int(max_ids[route] * 1.1)))
        else:
            limit = str(random.randint(-1, 1001))
            offset = str(random.randint(-1, int(max_ids[route] * 1.1)))
            id_ = f'?limit={limit}&offset={offset}'

        reporter.add(requests.get(f'{args.url}{route}/{id_}'))


if __name__ == '__main__':
    main(parse_args())

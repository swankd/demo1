
import argparse
import random
import requests

ROUTES = ('subject', 'predicate', 'object')


def parse_args():
    desc = 'Make random calls to the demo server.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-u', '--url', help='server url',
                        default='http://localhost:5000/')
    return parser.parse_args()


def main(args):
    assert args.url.endswith('/'), args.url

    def _max_id(route):
        return int(requests.get(f'{args.url}{route}/').json()[f'nb_{route}s'])

    max_ids = {route: _max_id(route) for route in ROUTES}
    print('max_ids:', max_ids)

    while True:
        route = random.choice(ROUTES)
        if random.choice((0, 10)):
            id_ = str(random.randint(-1, int(max_ids[route] * 1.1)))
        else:
            limit = str(random.randint(-1, 1001))
            offset = str(random.randint(-1, int(max_ids[route] * 1.1)))
            id_ = f'?limit={limit}&offset={offset}'

        requests.get(f'{args.url}{route}/{id_}')


if __name__ == '__main__':
    main(parse_args())

"""Encrypt a K8 stock check list for the count app.

The site is public, so the list (products, batches, K8 page and line) is stored
encrypted. Each count gets its own count code; the app on the handheld asks for
the code once and decrypts the list on the device.

Input: a plain list JSON  {"v":1, "count":{"id","name","groups","list"},
                           "groups":[[code,name],...], "products":{code:[desc,unit]},
                           "lines":[[lid, product code, batch], ...]}
       lid = "<grouping>-<K8 page>-<K8 line>", e.g. "02-05-09".

Usage: python3 make_list.py plain.json [count code]
Writes lists/<count id>.k8list and adds the count to lists/index.json.
Prints the count code (a new random one if none is given). Keep the code out of the repository.
"""
import base64, datetime, gzip, json, os, re, secrets, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ALPHABET = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'  # no 0/O, 1/I/L
ITER = 250000
HERE = os.path.dirname(os.path.abspath(__file__))
LISTS = os.path.join(HERE, '..', 'lists')


def norm_code(code):
    return re.sub(r'[^A-Z0-9]', '', code.upper())


def new_code():
    return '-'.join(''.join(secrets.choice(ALPHABET) for _ in range(5)) for _ in range(2))


def encrypt(plain_bytes, code):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm_code(code).encode())
    data = AESGCM(key).encrypt(iv, gzip.compress(plain_bytes, 9), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {'v': 1, 'kdf': 'PBKDF2-SHA256', 'iter': ITER, 'cipher': 'AES-GCM-256', 'gz': True,
            'salt': b64(salt), 'iv': b64(iv), 'data': b64(data)}


def main():
    src = json.load(open(sys.argv[1], encoding='utf-8'))
    code = sys.argv[2] if len(sys.argv) > 2 else new_code()
    cid = src['count']['id']
    assert re.fullmatch(r'[A-Za-z0-9-]{3,60}', cid), 'count id: letters, digits and dashes only'
    env = encrypt(json.dumps(src, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), code)
    env['id'] = cid
    os.makedirs(LISTS, exist_ok=True)
    with open(os.path.join(LISTS, cid + '.k8list'), 'w') as f:
        json.dump(env, f, separators=(',', ':'))
    idx_path = os.path.join(LISTS, 'index.json')
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {'counts': []}
    idx['counts'] = [c for c in idx['counts'] if c['id'] != cid]
    idx['counts'].insert(0, {'id': cid, 'name': src['count']['name'], 'file': 'lists/' + cid + '.k8list',
                             'added': datetime.date.today().isoformat()})
    with open(idx_path, 'w') as f:
        json.dump(idx, f, indent=1)
    print(code)


if __name__ == '__main__':
    main()

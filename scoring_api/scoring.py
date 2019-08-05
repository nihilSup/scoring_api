import hashlib
import json


def _score_key(phone, email, birthday=None, gender=None, first_name=None,
               last_name=None):
    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        birthday if birthday is not None else "",
    ]
    to_hash = "".join(str(key_parts)).encode('UTF-8')
    return "uid:" + hashlib.md5(to_hash).hexdigest()


def get_score(store, phone, email, birthday=None, gender=None, first_name=None,
              last_name=None):
    key = _score_key(phone, email, birthday, gender, first_name, last_name)
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = float(store.cache_get(key) or 0)
    if score:
        return score
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, cid):
    r = store.get("i:%s" % cid)
    return json.loads(r) if r else []

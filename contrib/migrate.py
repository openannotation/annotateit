from __future__ import print_function

from collections import defaultdict
import email
import json
import sys
import iso8601

import annotateit
from annotateit import db
from annotateit import model

class Migrator(object):

    def __init__(self):
        # Make app and database connection
        self.app = annotateit.create_app()
        self.app.test_request_context().push()

        self.annotations = []
        self.accounts = []
        self.discarded_accounts = []


    def run(self, dumpfile):
        msg = email.message_from_file(dumpfile)

        for part in msg.walk():
            if part.is_multipart():
                continue

            typ, doc = process_part(part)

            if typ:
                getattr(self, typ + 's').append(doc)

        print("%d accounts" % len(self.accounts), file=sys.stderr)
        print("%d annotations" % len(self.annotations), file=sys.stderr)

        self._process_accounts()
        self._process_annotations()

    def _process_accounts(self):
        self.accounts, discarded_email = _filter_duplicates(self.accounts, 'email')
        self.accounts, discarded_username = _filter_duplicates(self.accounts, 'username')

        self.discarded_accounts.extend(discarded_email)
        self.discarded_accounts.extend(discarded_username)

        # For posterity
        json.dump(self.accounts, open('accounts.json', 'w'))
        json.dump(self.discarded_accounts, open('discarded_accounts.json', 'w'))

        for acc in self.accounts:
            u = model.User.query.filter_by(email=acc['email']).first()

            if not u:
                u = model.User(acc['username'], acc['email'])
                u.password_hash = acc['pwdhash']
                u.created_at = iso8601.parse_date(acc['created'])
                db.session.add(u)

            c = model.Consumer.query.filter_by(key=acc['_id']).first()

            if not c:
                c = model.Consumer()
                c.key = acc['_id']
                c.secret = acc['secret']
                c.user = u
                c.created_at = iso8601.parse_date(acc['created'])
                db.session.add(c)

        db.session.commit()

    def _process_annotations(self):
        self.happy_annotations = []
        self.lonely_annotations = []

        # Make a lookup table for reassigning annotations that are associated with
        # accounts we've discarded
        self.discarded_lookup = {}

        for acc in self.discarded_accounts:
            u = model.User.query.filter_by(email=acc['email']).first()
            if not u:
                u = model.User.query.filter_by(username=acc['username']).first()
            if not u:
                raise RuntimeError("Don't know who to give discarded accounts annotations to: %s" % acc)
            self.discarded_lookup[acc['_id']] = u

        annotateit = model.Consumer.query.filter_by(key='annotateit').first()

        for ann in self.annotations:
            self._process_annotation(ann)

        json.dump(self.lonely_annotations, open('lonely_annotations.json', 'w'))
        json.dump(self.happy_annotations, open('happy_annotations.json', 'w'))

    def _process_annotation(self, ann):
        ann['id'] = ann['_id']

        consumer = self._ckey_to_consumer(ann['account_id'])
        # first recourse -- may get changed again later
        ann['consumer'] = ann['account_id']
        del ann['account_id']

        if not consumer and 'accountId' in ann:
            consumer = self._ckey_to_consumer(ann['accountId'])
            ann['consumer'] = ann['accountId']

        if 'accountId' in ann:
            del ann['accountId']

        del ann['_rev']
        del ann['_id']
        del ann['type']

        # Fix up crazy borked ranges:
        if ann['ranges'] and ann['ranges'][0] == '[':
            ann['ranges'] = json.loads(''.join(ann['ranges']))

        if consumer:

            if consumer.user.username == ann['user'].get('name') and ann['permissions']['update'] != ['4']:
                # treat this as an annotateit annotation
                ann['consumer'] = 'annotateit'
                ann['user'] = consumer.user.username

                if 'permissions' in ann:
                    for k in ['read', 'admin', 'update', 'delete']:
                        perms = ann['permissions'].get(k, [])

                        # Deal with crazy shit like {u'read': [u'[', u']']}
                        if perms and perms[0] == '[':
                            ann['permissions'][k] = perms = json.loads(''.join(perms))

                        for ckey in perms:
                            if ckey == consumer.user.username:
                                continue

                            assert self._ckey_to_consumer(ckey).key == consumer.key

                            ann['permissions'][k].remove(ckey)
                            ann['permissions'][k].append(consumer.user.username)

                    if ann['permissions'].get('read', []) == []:
                        ann['permissions']['read'] = ['group:__consumer__']

            else:
                # treat this as a true external consumer annotation and don't
                # futz with the user field
                ann['consumer'] = consumer.key

            ann = model.Annotation(**ann)
            ann.save()

            self.happy_annotations.append(dict(ann.items()))

        else:
            # No known consumer
            self.lonely_annotations.append(ann)

    def _ckey_to_consumer(self, ckey):
        if ckey in self.discarded_lookup:
            ckey = self.discarded_lookup[ckey].consumers[0].key

        c = model.Consumer.fetch(ckey)
        return c

def process_part(part):
    if part.get_content_type() != 'application/json':
        print("WARNING: part is not JSON...", file=sys.stderr)
        print(part.get_payload(decode=False), file=sys.stderr)
        return None, None

    doc = json.loads(part.get_payload(decode=False))
    return process_doc(doc)

def process_doc(doc):
    # All domain objects have 'type' keys, and view documents are Javascript.
    # If we find anything else, throw a hissy fit.
    if 'type' not in doc:
        if 'language' not in doc or doc['language'] != 'javascript':
            print("WARNING: doc doesn't have type", file=sys.stderr)
            print(doc, file=sys.stderr)
        return None, None

    return doc['type'].lower(), doc

def _filter_duplicates(list_of_dicts, key, sortkey='created'):
    by_key = defaultdict(list)

    for d in list_of_dicts:
        by_key[d[key]].append(d)

    discarded = []
    filtered = []

    for _, dicts in by_key.iteritems():
        dicts = sorted(dicts, key=lambda x: x[sortkey])

        discarded.extend(dicts[0:-1])
        filtered.append(dicts[-1])

    return filtered, discarded

def main():
    # Open dump file
    fp = None
    if len(sys.argv) == 2:
        fp = open(sys.argv[1])

    m = Migrator()
    m.run(fp or sys.stdin)

if __name__ == '__main__':
    main()


from google.appengine.ext import ndb
from google.appengine.api import memcache
from flask import Flask, render_template, redirect, request, jsonify

cache = memcache.Client()

class Entry(ndb.Model):
    id = ndb.DateTimeProperty(auto_now_add=True)
    name = ndb.StringProperty(required=True)

def get_entry_key(key_name='default_key'):
    return ndb.Key(Entry, key_name)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        entries = cache.get('entries')
        if not entries:
            entries = Entry.query(ancestor=get_entry_key()).order(-Entry.id).fetch()
            cache.set('entries', entries)
        return render_template('index.html', entries=entries)

    if request.method == 'POST':
        content = request.form.get('content')
        if content.strip():
            entry = Entry(name=content, parent=get_entry_key())
            entry.put()
            cache.delete('entries')
        return redirect('/')

@app.route('/clear')
def clear():
    query_keys = Entry.query(ancestor=get_entry_key()).fetch(keys_only=True)
    ndb.delete_multi(query_keys)
    cache.delete('entries')
    return redirect('/')

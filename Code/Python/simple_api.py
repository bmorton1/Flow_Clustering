from bottle import route, run, template
import bottle
import bottle.ext.sqlite
import sys

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile='test.db')
app.install(plugin)

@app.route('/hello/<name>')
def index(name):
        return template('<b>Hello {{name}}</b>!', name=name)

@app.route('/show/:item')
def show(item, db):
        sys.stderr.write('Querying: %s\n' % (item))
        item += '%'
        rows = db.execute('SELECT * from Songs where Artist Like ?', (item, )).fetchall()
        # id, song, artist, avgSyllPerLine, stddev
        if rows:
            response = []
            for row in rows:
                stats = {}
                stats['id'] = row[0]
                stats['song'] = row[1]
                stats['artist'] = row[2]
                stats['syl'] = row[3]
                stats['std'] = row[4]
                response.append(stats)
            return {'response': response}    
        #return HTTPError(404, "Wiz not found")

app.run(host='localhost', port=8080)

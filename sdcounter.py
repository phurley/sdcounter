import psycopg2
import psycopg2.extras

from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

con = psycopg2.connect(database = "ahurley", user = "ahurley")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Rooms API',
        description='A simple API to track rooms and count',
        )

ns = api.namespace('rooms', description='ROOM operations')

room = api.model('Room', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'name': fields.String(required=True, description='The name of the room'),
    'count': fields.Integer(readonly=True, description='Number of people in the room')
    })


@ns.route('/')
class RoomList(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get room list')
    @ns.marshal_with(room)
    def get(self):
        '''Fetch a list of resources'''
        try:
            cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
                cur.execute("select * from rooms")
                result = cur.fetchall()
        finally:
            cur.close()
        return result

    @ns.doc('create_room')
    @ns.expect(room)
    @ns.marshal_with(room, code=201)
    def post(self):
        '''Create a room '''
        try:
            body = api.payload
                cur = con.cursor()
                cur.execute("insert into rooms (name, count) values (%s, %s)", (body["name"], body.get("count", 0)))
                con.commit()
                if cur.rowcount <= 0:
                    api.abort(401, "Error creating room.")
        finally:
            cur.close()
        return body

@ns.route('/<int:id>')
@ns.param('id', 'The room identifier')
@ns.response(404, 'Room not found')
class Room(Resource):
    '''Show a single room and lets you delete them'''
    @ns.doc('get room')
    @ns.marshal_with(room)
    def get(self, id):
        '''Fetch a given room '''
        try:
            cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
                cur.execute("select * from rooms where id = %s", (id, ))
                result = cur.fetchone()
                if result == None:
                    api.abort(404, "Room {} doesn't exist".format(id))
        finally:
            cur.close()
        return result

    @ns.doc('delete room')
    @ns.response(204, 'Room deleted')
    def delete(self, id):
        '''Delete a room given its identifier'''
        try:
            cur = con.cursor()
                cur.execute("delete from rooms where id = %s", (id, ))
                con.commit()
                if cur.rowcount == 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
        finally:
            cur.close()

    @ns.expect(room)
    @ns.marshal_with(room)
    def put(self, id):
        '''Update a room given its identifier'''
        result = {}
        try:
            updates = api.payload
                cur = con.cursor()
                sql_template = "UPDATE rooms SET ({}) = %s WHERE id = %s"
                sql = sql_template.format(', '.join(updates.keys()))
                params = (tuple(updates.values()))
                # print(cur.mogrify(sql, (params, id)))
                cur.execute(sql, (params, id))
                con.commit()
                result = cur.rowcount
                if result <= 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
                result = self.get(id)
        finally:
            cur.close()
        return result


if __name__ == '__main__':
    app.run(debug=True)


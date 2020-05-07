import psycopg2
import psycopg2.extras

from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

connection = psycopg2.connect(database = "ahurley", user = "ahurley")

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Rooms API',
        description='A simple API to track rooms and count',
        )

ns = api.namespace('rooms', description='ROOMs operations')

room = api.model('Room', {
    'id': fields.Integer(readonly=True, description='The room unique identifier'),
    'name': fields.String(required=True, description='The name of the room'),
    'count': fields.Integer(readonly=True, description='Number of people in the room')
    })


@ns.route('/')
class RoomList(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get room list')
    @ns.marshal_with(room)
    def get(self):
        '''Fetch a list of rooms'''
        with connection:
            with connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from rooms")
                return cur.fetchall()

    @ns.doc('create_room')
    @ns.expect(room)
    @ns.marshal_with(room, code=201)
    def post(self):
        '''Create a room '''
        with connection:
            with connection.cursor() as cur:
                body = api.payload
                cur.execute("insert into rooms (name, count) values (%s, %s)", (body["name"], body.get("count", 0)))
                if cur.rowcount <= 0:
                    api.abort(401, "Error creating room.")
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
        with connection:
            with connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from rooms where id = %s", (id, ))
                result = cur.fetchone()
                if result == None:
                    api.abort(404, "Room {} doesn't exist".format(id))
                return result

    @ns.doc('delete room')
    @ns.response(204, 'Room deleted')
    def delete(self, id):
        '''Delete a room given its identifier'''
        with connection:
            with connection.cursor() as cur:
                cur.execute("delete from rooms where id = %s", (id, ))
                connection.commit()
                if cur.rowcount == 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
                return 'Success', 204

    @ns.expect(room)
    @ns.marshal_with(room)
    def put(self, id):
        '''Update a room given its identifier'''
        with connection:
            with connection.cursor() as cur:
                result = {}
                updates = api.payload
                sql_template = "UPDATE rooms SET ({}) = %s WHERE id = %s"
                sql = sql_template.format(', '.join(updates.keys()))
                params = (tuple(updates.values()))
                # print(cur.mogrify(sql, (params, id)))
                cur.execute(sql, (params, id))
                connection.commit()
                result = cur.rowcount
                if result <= 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
        result = self.get(id)
        return result


@ns.route('/<int:id>/count')
@ns.param('id', 'The room identifier')
@ns.response(404, 'Room not found')
class RoomCount(Resource):
    '''Get a single room's count'''
    @ns.doc("get room's count")
    def get(self, id):
        '''Fetch a given room's count '''
        with connection:
            with connection.cursor() as cur:
                cur.execute("select count from rooms where id = %s", (id, ))
                result = cur.fetchone()
                if result == None:
                    api.abort(404, "Room {} doesn't exist".format(id))
                return result[0]

@ns.route('/<int:id>/count/<int:count>')
@ns.param('id', 'The room identifier')
@ns.param('count', 'The new count for the specified room')
@ns.response(404, 'Room not found')
class RoomUpdateCount(Resource):
    '''Update a single room's count '''
    @ns.doc("update a room's count")
    @ns.response(204, 'Room count updated')
    def put(self, id, count):
        '''Update a given room's count '''
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("update rooms set count = %s where id = %s", (count, id))
                result = cursor.rowcount
                if cursor.rowcount <= 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
                return 'Success', 204

@ns.route('/<int:id>/increment/<int:delta>')
@ns.route('/<int:id>/increment', defaults={ 'delta': 1 })
@ns.param('id', 'The room identifier')
@ns.param('delta', 'The change in count for the specified room')
@ns.response(404, 'Room not found')
class RoomUpdateCount(Resource):
    '''Update a single room's count '''
    @ns.doc("update a room's count")
    @ns.response(204, 'Room count updated')
    def put(self, id, delta):
        '''Update a given room's count '''
        with connection:
            with connection.cursor() as cur:
                cur.execute("update rooms set count = count + %s where id = %s", (delta, id))
                result = cur.rowcount
                connection.commit
                if cur.rowcount <= 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
                return 'Success', 204

@ns.route('/<int:id>/decrement/<int:delta>')
@ns.route('/<int:id>/decrement', defaults={ 'delta': 1 })
@ns.param('id', 'The room identifier')
@ns.param('delta', 'The change in count for the specified room')
@ns.response(404, 'Room not found')
class RoomUpdateCount(Resource):
    '''Update a single room's count '''
    @ns.doc("update a room's count")
    @ns.response(204, 'Room count updated')
    def put(self, id, delta):
        '''Update a given room's count '''
        with connection:
            with connection.cursor() as cur:
                cur.execute("update rooms set count = count - %s where id = %s", (delta, id))
                result = cur.rowcount
                connection.commit
                if cur.rowcount <= 0:
                    api.abort(404, "Room {} doesn't exist".format(id))
                return 'Success', 204

nsj = api.namespace('journal', description='Journal Read')

journal = api.model('Journal', {
    'id': fields.Integer(readonly=True, description='The journal unique identifier'),
    'room_id': fields.Integer(readonly=True, description='The room unique identifier'),
    'previous_count': fields.Integer(readonly=True, description='Number of people that were previously in the room'),
    'count': fields.Integer(readonly=True, description='Number of people in the room'),
    'delta': fields.Integer(readonly=True, description='Change in the number of people in the room'),
    'applied_at': fields.DateTime(readonly=True, description='Number of people in the room'),
    })

@nsj.route('/<int:room_id>')
@nsj.response(404, 'Room not found')
class Journal(Resource):
    ''' Retrieve journal entries for a room '''
    @nsj.marshal_with(journal)
    @nsj.doc("Retrieve all journal entries for a room")
    def get(self, room_id):
        with connection:
            with connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("select * from journal where room_id = %s", (room_id, ))
                return cursor.fetchall()

if __name__ == '__main__':
    app.run(debug=True)


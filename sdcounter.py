import psycopg2
import psycopg2.extras

from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

con = psycopg2.connect(
	database = "ahurley",
	user = "ahurley")

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


@ns.route('/<int:id>')
@ns.param('id', 'The room identifier')
@ns.response(404, 'Room not found')
class Room(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_room')
    @ns.marshal_with(room)
    def get(self, id):
        '''Fetch a given resource'''
        try: 
                cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
                print(f"select * from rooms where id = {id}")
                cur.execute(f"select * from rooms where id = {id}")
                result = cur.fetchone()
                print(result)
        finally:
                cur.close()
        return result

    @ns.doc('delete_room')
    @ns.response(204, 'Room deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        return []

    @ns.doc('create_room')
    @ns.expect(room)
    @ns.marshal_with(room, code=201)
    def post(self):
        '''Create a new task'''
        return []
    
    @ns.expect(room)
    @ns.marshal_with(room)
    def put(self, id):
        '''Update a task given its identifier'''
        return []


if __name__ == '__main__':
    app.run(debug=True)

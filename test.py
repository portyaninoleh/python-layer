from __future__ import unicode_literals

from api import LayerAPI
from api import Sender
from api import MessageParts
from api import Message
from api import Announcements


layer = LayerAPI('0Z3bh2TB9tZFcS8hqzs2ecWOy0KTKEUgSzVwujoaONa1URX8',
                 '082dde36-466f-11e5-b52f-919079016f2f')
c = layer.get_conversation('ebff4b28-d5d1-4846-b8c4-8c70fd6ada72')
sender = Sender(name='test')
part = MessageParts(body='Hello', mime_type='text/plain')
part2 = MessageParts(body='YW55IGNhcm5hbCBwbGVhc3VyZQ==', mime_type='image/jpeg', encoding='base64')
message = Announcements(parts=[part, part2], sender=sender, conversation=c)
message = message.send(everyone=True)

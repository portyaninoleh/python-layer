# python-layer
Python library for Layer.com functionality

Initialize layer object
from api import LayerAPI
layer = LayerAPI(platform_api_token, application_id)

Get conversation:
conversation = layer.get_conversation(conversation_id)


Get or create conversation:
conversation = layer.get_or_create_conversation(['user_a', 'user_b'], {'background_color': '#3c3c3c'}, distinct=True)

More about distinct parameter you can read here:
https://developer.layer.com/docs/platform#distinct-conversations


Add participants to conversation:
conversation.add_participants(['user_a', 'user_b'])


Remove participants from conversation:
conversation.remove_participants(['user_a', 'user_b'])


Replace participants in conversation:
conversation.replace_participants(['user_a', 'user_b'])


Set metadata:
conversation.set_metadata([{'metadata.info.background.color': 'red'}, {'metadata.title': 'Metadata Title'}])


Delete metadata:
conversation.delete_metadata(['metadata.info.background', 'metadata.title'])


Send message:
from api import Sender
from api import MessageParts
from api import Message

sender = Sender(name='test sender')
part = MessageParts(body='Hello', mime_type='text/plain')
part2 = MessageParts(body='YW55IGNhcm5hbCBwbGVhc3VyZQ==', mime_type='image/jpeg', encoding='base64')
message = Message(parts=[part, part2], sender=sender, conversation=conversation)
message.send()

You can also create the sender object with some user. You just need to specify the sender_id parameter.
For example:
sender = Sender(sender_id='user_id')

But you can't specify the 'sender_id' and 'name' parameters simultaneously:
https://developer.layer.com/docs/platform#send-a-message

Send announcement:
from api import Announcement
announcement = Announcement(parts=[part, part2], sender=sender, conversation=conversation)
announcement.send()


Add user to the block list:
layer.block_users('owner_id', 'user_id')

where the first parameter is the identifier of block lists owner and second one is the identifier 
of user which should be added to the block list.


Get block list:
layer.get_block_list('owner_id')


Delete user from the block list:
layer.delete_user_from_block_list('owner_id', 'user_id')


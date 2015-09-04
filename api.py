from __future__ import unicode_literals

import requests
import json
import uuid
import datetime
import copy

from constants import BASE_URL
from utils import set_metadata
from utils import delete_metadata


class LayerBase(object):
    """
    Base class for Layer API
    """
    def __init__(self, platform_api_token, application_id, version=1.0):
        self.platform_api_token = platform_api_token
        self.application_id = application_id
        self.url = '{}{}'.format(BASE_URL, self.application_id)
        self.version = version
        self.headers = {
            'Accept': 'application/vnd.layer+json; version={}'.format(unicode(self.version)),
            'Authorization': 'Bearer {}'.format(self.platform_api_token),
            'Content-Type': 'application/json',
            'If-None-Match': unicode(uuid.uuid4())
        }


class MessageBase(object):
    """
    Base structure for messages and announcements
    """
    def __init__(self, parts,
                 sender,
                 conversation,
                 message_id=None,
                 notification=None,
                 url=None,
                 sent_at=None,
                 recipient_status=None):
        """
        Constructor
        :param parts: list() - list of MessageParts objects
        :param sender: list() - list of Sender objects
        :param conversation: Conversation() - conversation object
        :param message_id: unicode() - message id
        :param notification: Notification() - notification object
        :param url: unicode() - message url
        :param sent_at: datetime() - sent at date
        :param recipient_status: dict() - list of recipients and message status for them
        :return: No results returned
        """
        self.parts = parts
        self.notification = notification
        self.sender = sender
        self.conversation = conversation
        self.message_id = message_id
        self.url = url
        self.sent_at = sent_at
        self.recipient_status = recipient_status


class Notification(object):
    """
    Class for handling notifications
    """
    def __init__(self, text, recipients, sound='chime.aiff'):
        """
        Constructor
        :param text: unicode() - notification body
        :param recipients: list() - list of recipients
        :param sound: unicode() - sound name
        :return:
        """
        self.text = text
        self.sound = sound
        self.recipients = recipients

    def get_entity(self):
        result = {'text': self.text,
                  'sound': self.sound}
        if self.recipients:
            result['recipients'] = self.recipients


class Sender(object):
    """
    Sender handler class
    """
    def __init__(self, name=None, sender_id=None):
        """
        Constructor of Sender class. Only one parameter can be given:
        https://developer.layer.com/docs/platform#send-a-message
        :param name: unicode() - Name of sender in case if the message should be sent from the non human sender
        :param sender_id: unicode() - User identifier
        :return: No results returned
        """
        if name and sender_id:
            raise Exception('Only one parameter can be given: name or sender_id')
        self.name = name
        self.sender_id = sender_id

    def __unicode__(self):
        return self.sender_id if self.sender_id else self.name

    def get_entity(self):
        """
        Get the sender object in the needed for Layer format
        :return: dict() with name or user_id data
        """
        if self.sender_id:
            return {'user_id': self.sender_id}
        return {'name': self.name}


class MessageParts(object):
    """
    Message Parts handler class
    """
    def __init__(self, body, mime_type, encoding=None):
        """
        Constructor of Message Part object
        :param body: unicode() - Plain text or base64 hash.
        :param mime_type: unicode() - Can be 'plain/text' or 'image/[jpeg, png etc..]' depends on body of the message
        :param encoding: unicode() - If body is the base64 hash, then this field mst be set to 'base64'
        :return: No results returned
        """
        self.body = body
        self.mime_type = mime_type
        self.encoding = encoding

    def get_part(self):
        """
        Get part of message in the needed format for layer API
        :return: dict() - Constructed in the needed format message part
        """
        result = {'body': self.body,
                  'mime_type': self.mime_type}
        if self.encoding:
            result['encoding'] = self.encoding
        return result


class Announcements(MessageBase):
    """
    Announcements handler class
    """

    def __init__(self, parts, sender, conversation):
        """
        Constructor of announcement object
        :param parts: list() - List of MessagePart objects
        :param sender: Sender() - Sender object
        :param conversation: Conversation() - Conversation object
        :return: No results returned
        """
        super(Announcements, self).__init__(parts=parts, sender=sender, conversation=conversation)
        self.recipients = list()

    def send(self, recipients=None, everyone=False):
        """
        Send announcement method
        :param recipients: list() - list of recipients ids
        :param everyone: boolean() - If True then announcement is sent to all users in the current application
        :return: Announcement object
        """
        data = {'sender': self.sender.get_entity(),
                'parts': [i.get_part() for i in self.parts]}
        if everyone:
            data['recipients'] = 'everyone'
        else:
            data['recipients'] = recipients
        result = requests.post('{}/announcements'.format(self.conversation.url),
                               data=json.dumps(data),
                               headers=self.conversation.origin_headers)
        if result.status_code == 202:
            r = json.loads(result.text)
            self.message_id = r['id']
            self.url = r['url']
            self.sent_at = datetime.datetime.strptime(r['sent_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.recipients = r['recipients']
            return self
        else:
            raise Exception(result.text)


class Message(MessageBase):
    """
    Message handler class
    """

    def send(self):
        """
        Send message method
        :return: Message object if message is sent successfully. Otherwise raise error
        """
        data = {'sender': self.sender.get_entity(),
                'parts': [i.get_part() for i in self.parts]}
        # TODO: Left for future
        # if self.notification:
        #     data['notification'] = self.notification
        result = requests.post('{}/conversations/{}/messages'.format(self.conversation.url,
                                                                     self.conversation.conversation_id),
                               data=json.dumps(data),
                               headers=self.conversation.origin_headers)
        if result.status_code == 201:
            r = json.loads(result.text)
            self.message_id = r['id']
            self.url = r['url']
            self.sent_at = datetime.datetime.strptime(r['sent_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.recipient_status = r['recipient_status']
            return self
        else:
            raise Exception(result.text)


class Conversation(LayerBase):
    """
    Python wrapper for conversations functionality
    """

    def __init__(self,
                 url,
                 id,
                 participants,
                 distinct,
                 created_at,
                 platform_api_token,
                 application_id,
                 version=1.0,
                 metadata=None):
        """
        Build conversation object
        :param url: String
        :param id: String
        :param participants: List
        :param distinct: Boolean
        :param metadata: Dict
        :param created_at: datetime
        :return:
        """
        super(Conversation, self).__init__(platform_api_token, application_id, version)
        self.conversation_url = url
        self.conversation_id = id.split('/')[-1:][0]
        self.participants = participants
        self.distinct = distinct
        self.metadata = metadata
        self.created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.origin_headers = copy.copy(self.headers)
        self.headers['Content-Type'] = 'application/vnd.layer-patch+json'

    def add_participants(self, participants):
        """
        Add participants to conversation
        :param participants: list() - Users identifiers
        :return: No results returned
        """
        data = requests.patch('{}/conversations/{}'.format(self.url, self.conversation_id),
                              data=json.dumps([{'operation': 'add',
                                                'property': 'participants',
                                                'value': unicode(i)} for i in participants]),
                              headers=self.headers)
        if data.status_code == 204:
            self.participants += [unicode(i) for i in participants]
        else:
            raise Exception(data)

    def remove_participants(self, participants):
        """
        Remove participants from conversation
        :param participants: list() - Users identifiers
        :return: No results returned
        """
        participants = [unicode(i) for i in participants]
        data = requests.patch('{}/conversations/{}'.format(self.url, self.conversation_id),
                              data=json.dumps([{'operation': 'remove',
                                                'property': 'participants',
                                                'value': i} for i in participants]),
                              headers=self.headers)
        if data.status_code == 204:
            self.participants = [i for i in self.participants if i not in participants]
        else:
            raise Exception(data)

    def replace_participants(self, participants):
        """
        Replace participants of conversation
        :param participants: list() - Users identifiers
        :return: No results returned
        """
        participants = [unicode(i) for i in participants]
        data = requests.patch('{}/conversations/{}'.format(self.url, self.conversation_id),
                              data=json.dumps({'operation': 'set',
                                               'property': 'participants',
                                               'value': [i for i in participants]}),
                              headers=self.headers)
        if data.status_code == 204:
            self.participants = participants
        else:
            raise Exception(data)

    def set_metadata(self, values):
        """
        Set Metadata of conversation
        :param values: list() - List of dictionaries with key-values of needed data
        :return: No results returned
        """
        data = requests.patch('{}/conversations/{}'.format(self.url, self.conversation_id),
                              data=json.dumps([{'operation': 'set',
                                                'property': d.keys()[0],
                                                'value': d.values()[0]} for d in values]),
                              headers=self.headers)
        if data.status_code == 204:
            self.metadata = set_metadata(self.metadata, values)
        else:
            raise Exception(data.text)

    def delete_metadata(self, values):
        """
        Delete data from metadata of conversation
        :param values: list() - list of keys, which data should be deleted
        :return: No results returned
        """
        data = requests.patch('{}/conversations/{}'.format(self.url, self.conversation_id),
                              data=json.dumps([{'operation': 'delete',
                                                'property': d} for d in values]),
                              headers=self.headers)
        if data.status_code == 204:
            self.metadata = delete_metadata(self.metadata, values)
        else:
            raise Exception(data.text)


class LayerAPI(LayerBase):
    """
    Main layer API class for handling conversations
    """
    def get_or_create_conversation(self, participants, metadata, distinct=False):
        """
        Get or create conversation
        :param participants: list() - users, which should be added to the conversation
        :param metadata: dict() - metadata for the conversation
        :param distinct: boolean() - set to True if the conversation shouldn't be created in case if it exists already
        :return: Conversation object
        """
        data = requests.post('{}/conversations'.format(self.url),
                             data=json.dumps({'participants': [unicode(i) for i in participants],
                                              'distinct': distinct,
                                              'metadata': metadata}),
                             headers=self.headers)
        if data.status_code in [200, 201]:
            print(data.text)
            return Conversation(platform_api_token=self.platform_api_token,
                                application_id=self.application_id, **json.loads(data.text))
        raise Exception(data.text)

    def get_conversation(self, conversation_id):
        """
        Get conversation by ID
        :param conversation_id: unicode() - conversation ID
        :return: Conversation object
        """
        data = requests.get('{}/conversations/{}'.format(self.url, conversation_id),
                            headers=self.headers)
        if data.status_code == 200:
            return Conversation(platform_api_token=self.platform_api_token,
                                application_id=self.application_id,
                                version=self.version,
                                **json.loads(data.text))
        raise Exception(data.text)

    def block_users(self, owner_id, user_to_block):
        """
        Add user to the block list
        :param owner_id: int() or unicode() - Owner's block list identifier
        :param user_to_block: int() or unicode() - Identifier of user which should be blocked
        :return: No results returned
        """
        result = requests.post('{}/users/{}/blocks'.format(self.url, unicode(owner_id)),
                               data=json.dumps({'user_id': unicode(user_to_block)}),
                               headers=self.headers)
        if result.status_code != 204:
            raise Exception(result.text)

    def get_block_list(self, owner_id):
        """
        Retrieve user's block list
        :param owner_id: int() or unicode() - Identifier of block lists owner
        :return: List of dictionaries with users' ids
        """
        result = requests.get('{}/users/{}/blocks'.format(self.url, unicode(owner_id)),
                              headers=self.headers)
        if result.status_code == 200:
            return json.loads(result.text)
        raise Exception(result.text)

    def delete_user_from_block_list(self, owner_id, user_id):
        """
        Remove user from block list
        :param owner_id: int() or unicode() - Identifier of block lists owner
        :param user_id: int() or unicode() - Identifier of user, which should be unblocked
        :return: No results returned
        """
        result = requests.delete('{}/users/{}/blocks/{}'.format(self.url,
                                                                unicode(owner_id),
                                                                unicode(user_id)),
                                 headers=self.headers)
        if result.status_code != 204:
            raise Exception(result.text)





from __future__ import unicode_literals

import requests
import json
import uuid
import datetime

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


class Conversation(LayerBase):
    """
    Python wrapper for conversations functionality
    """

    def __init__(self,
                 url,
                 id,
                 participants,
                 distinct,
                 metadata,
                 created_at,
                 platform_api_token,
                 application_id,
                 version=1.0):
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
                             data=json.dumps({'participants': participants,
                                              'distinct': distinct,
                                              'metadata': metadata}),
                             headers=self.headers)
        if data.status_code == 201:
            return Conversation(**json.loads(data.text))
        raise Exception(data.text)

    def get_conversation(self, conversation_id):
        """
        Get conversation by ID
        :param conversation_id: unicode() - conversation ID
        :return: Conversation object
        """
        data = requests.get('{}/conversations/{}'.format(self.url, conversation_id), headers=self.headers)
        if data.status_code == 200:
            return Conversation(platform_api_token=self.platform_api_token,
                                application_id=self.application_id,
                                version=self.version,
                                **json.loads(data.text))
        raise Exception(data.text)





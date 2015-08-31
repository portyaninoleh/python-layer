from __future__ import unicode_literals

from api import LayerAPI
from utils import set_metadata

layer = LayerAPI('0Z3bh2TB9tZFcS8hqzs2ecWOy0KTKEUgSzVwujoaONa1URX8',
                 '082dde36-466f-11e5-b52f-919079016f2f')
c = layer.get_conversation('ebff4b28-d5d1-4846-b8c4-8c70fd6ada72')
c.set_metadata([{'metadata.info.title': 'A Conversation about Coffee'}])
# c.delete_metadata(['metadata.title'])
print(c.metadata)

# print(set_metadata({'metadata': {'title': '1'}}, [{'property': 'metadata.stats.counter',
#                                                    'value': '10'},
#                                                   {'property': 'metadata.admin',
#                                                    'value': {'user_id': 'fred',
#                                                              'hours': {'start': '9',
#                                                                        'end': '5'}}}]))
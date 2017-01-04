import settings
import pprint
from database.database import IntentsDatabaseEngine, EntitiesDatabaseEngine
# print('Test getting intent entities')
# intents_engine = IntentsDatabaseEngine()
# pp = pprint.PrettyPrinter(indent=3)
# results = intents_engine.get_intent_entities('search-inventory')
# entities = []
# for result in results:
#     entity = {
#             "entity_name": result[0],
#             "entity_type": result[1],
#             "positive_expressions": result[2],
#             "negative_expressions": result[3],
#             "regular_expressions": result[4],
#             "keywords": result[5]
#         }
#     entities.append(entity)
# pp.pprint(entities)
# print('--------------------------------------')
# print('Test adding an entity to entities table')
# entities_engine = EntitiesDatabaseEngine()
# entities_engine.add_entity("test-entity", "test-type", ['pos1', 'pos2', 'pos3'],
#                            ['neg1', 'neg2', 'neg3'], ['reg1', 'reg2', 'reg3'], ['key1', 'key2'])
# results = entities_engine.get_entities()
# pp.pprint(results)
# print('--------------------------------------')
# print('Test updating entity')
# updates = {'entity_name': 'updated_name', 'entity_type': 'updated_type',
#            'positive_expressions': ['up1', 'up2', 'up3'], 'keywords': ['updatedkey']}
# pp.pprint(entities_engine.update_entity('test-entity', **updates))
# print('--------------------------------------')
# print('Test adding entity to intent')
# intents_engine.add_entities_to_intent('search-inventory', 'updated_name')
# results = intents_engine.get_intent_entities('search-inventory')
# pp.pprint(results)
# print('--------------------------------------')
# print('Test deleting entity from intent')
# pp.pprint(intents_engine.delete_entities_from_intent('search-inventory', 'updated_name'))
# print('--------------------------------------')
# print("Test deleting entity")
# pp.pprint(entities_engine.delete_entity('updated_name'))
# print('--------------------------------------')
# results = intents_engine.get_intent_entities('search-inventory')
# pp.pprint(results)


# entities_engine.release_database_connection()
# intents_engine.release_database_connection()

entities_db_engine = EntitiesDatabaseEngine()
print(entities_db_engine.get_binary_entity_expressions('is_plural'))
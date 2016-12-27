import settings
import pprint
from database.database import IntentsDatabaseEngine, EntitiesDatabaseEngine

intents_engine = IntentsDatabaseEngine()
pp = pprint.PrettyPrinter(indent=3)
results = intents_engine.get_intent_entities('search-inventory')
entities = []
for result in results:
    entity = {
            "entity_name": result[0],
            "entity_type": result[1],
            "positive_expressions": result[2],
            "negative_expressions": result[3],
            "regular_expressions": result[4],
        }
    entities.append(entity)
pp.pprint(entities)
print('--------------------------------------')

entities_engine = EntitiesDatabaseEngine()
entities_engine.add_entity("test-entity","test-type",['pos1','pos2','pos3'],['neg1','neg2','neg3'],['reg1','reg2','reg3'])
results = entities_engine.get_entities()
pp.pprint(results)
print('--------------------------------------')
updates = {'entity_name': 'updated_name', 'entity_type': 'updated_type', 'positive_expressions': ['up1','up2','up3']}
pp.pprint(entities_engine.update_entity('test-entity', **updates))
print('--------------------------------------')
intents_engine.add_entities_to_intent('search-inventory', 'updated_name')
results = intents_engine.get_intent_entities('search-inventory')
pp.pprint(results)
print('--------------------------------------')
pp.pprint(entities_engine.delete_entity('updated_name'))
print('--------------------------------------')
results = intents_engine.get_intent_entities('search-inventory')
pp.pprint(results)


entities_engine.release_database_connection()
intents_engine.release_database_connection()
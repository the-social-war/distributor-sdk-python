# Oct7 Distributor

## Installing

```bash
pip install git+https://github.com/the-social-war/distributor-sdk-python.git
```

## Usage

### Initializing the client

```python
import os
from oct7_distributor import DistributorClient

client = DistributorClient(
    # This is the default and can be ommitted
    api_key=os.environ.get("DISTRIBUTOR_API_KEY"),
    # This is the default and can be ommitted. 
    # The value must match the scope allowed by the API key.
    actor_system=os.environ.get("DISTRIBUTOR_ACTOR_SYSTEM"),
    # This is the default and can be ommitted.
    # Get this value from your contact point at oct7.
    url=os.environ.get("DISTRIBUTOR_ENDPOINT"), 
)
```

### Fetching a task for a worker

```python
task = await client.afetch_task(
    platform="instagram", 
    actor_uid="the actor uid"
)
```

If a task is not available for the worker, `None` is returned.
If a task is fetched, its details can be accessed through a pydantic model `task.blueprint`:
```python
task.blueprint
# => PublishPost(type='publish_post', action_uid='e9a96f41076601f02f2589091015a8f9', content=ContentDefinition(type='prompt', text='hi'))
task.blueprint.content.text
# => 'hi'
task.blueprint.model_dump()
# => {'type': 'publish_post', 'action_uid': 'e9a96f41076601f02f2589091015a8f9', 'content': {'type': 'prompt', 'text': 'hi'}}
```

To persist a task and then build a copy based on those details:
```python
persisted_copy = task.serialize()
# => {'blueprint': 
#        {'type': 'publish_post',
#         'action_uid': 'bc10ce423d6cb38ce565195372362974',
#         'content': {
#            'uid': 'ef5f225c735df57c31cb4167f30fe779',
#            'type': 'prompt',
#            'text': 'hi'}
#        },
#     'actor_system': 'simulator',
#     'actor_uid': 'uid-test1'}

task = client.deserialize_task(persisted_copy)
```

### Completing a task

In general, a task can report completion under 3 statuses - success, error, and dropped. These are invoked through the task object:
```python
await task.asuccess()
await task.aerror(message="Some error message")
await task.adropped()
```

Some tasks require adding the details of the entity created during the completion of the task.
There are two supported content entities: `Post` and `Comment`. The relevant entity that the task expects can be accessed via `task.expected_entity`, which returns a python class. To report completion, instantiate an object from this class, and send it to the `task.asuccess` method:
```python
# Example with a Comment
task.expected_entity
# => Comment
comment = task.expected_entity(
    url="some url",
    text="some text",
    author="the avatar name"
)
await task.asuccess(entity=comment)

# Example with a Post
task.expected_entity
# => Post
post = task.expected_entity(
    url="some url",
    text="some text",
    author="the avatar name"
)
await task.asuccess(entity=post)
```

### Handling errors

The library raises the following errors:
- `ValidationError` - this is a native pydantic exception that may be raised during the process of building pydantic objects
- `DistributorException` - this is the parent of the following exceptions
- `DistributorBlueprintException` - this may occur when deserializing a task with incorrect blueprint format, or when receiving an unsupported format from the server
- `DistributorRequestException` - this may occur if an API call raised an internal server error, unauthorized error, or bad request format
- `DistributorUsageException` - this may occur if the client expected parameters that were not provided, or in task completion if an entity is expected but not provided
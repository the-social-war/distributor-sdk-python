from .blueprints import Blueprint
from .api import InvocationParams
from .content_entities import ContentEntity
from .exceptions import DistributorUsageException
from .api import atask_complete

class Task:
    def __init__(self, *, invocation_params: InvocationParams, actor_system: str, actor_uid: str, blueprint: Blueprint) -> None:
        self.invocation_params = invocation_params
        self.actor_system = actor_system
        self.actor_uid = actor_uid
        self.blueprint = blueprint
        self.expected_entity = blueprint.expected_entity

    def __repr__(self) -> str:
        return f"<Task {self.blueprint.__repr__()}>"

    def _common_params(self):
        return dict(
            actor_system=self.actor_system,
            action_uid=self.blueprint.action_uid,
            actor_uid=self.actor_uid,
        )
    
    def serialize(self):
        return dict(
            blueprint=self.blueprint.model_dump(exclude={'expected_entity'}),
            actor_system=self.actor_system,
            actor_uid=self.actor_uid
        )
    
    async def asuccess(self, entity: ContentEntity | None = None):
        expected_entity_class = self.blueprint.expected_entity
        if expected_entity_class and not entity:
            raise DistributorUsageException(f"Task expects {self.blueprint.expected_entity.__name__} but no entity was given")
        if expected_entity_class and not isinstance(entity, expected_entity_class):
            raise DistributorUsageException(f"Task expects {self.blueprint.expected_entity.__name__} but {entity.__class__.__name__} was given")
        
        content_uid = self.blueprint.content.uid if expected_entity_class else None
        
        return await atask_complete(
            invocation_params=self.invocation_params,
            **self._common_params(),
            status='success',
            content_uid=content_uid,
            entity=entity
        )

    async def aerror(self, message: str):
        if not message or len(message) == 0:
            raise DistributorUsageException(f"Error message must be provided")
        
        return await atask_complete(
            invocation_params=self.invocation_params,
            **self._common_params(),
            status='error',
            error_message=message
        )

    async def adropped(self):
        return await atask_complete(
            invocation_params=self.invocation_params,
            **self._common_params(),
            status='dropped'
        )

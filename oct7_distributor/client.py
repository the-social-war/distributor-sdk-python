import os
from base64 import urlsafe_b64decode
from .defaults import Defaults
from .exceptions import DistributorUsageException
from .api import InvocationParams
from .task import Task
from . import api
from . import blueprints

class DistributorClient:
    def __init__(self, *, api_key: str=None, actor_system: str=None, base_endpoint: str=None) -> None:
        self.actor_system = actor_system or os.environ.get(Defaults.actor_system_env_var)
        full_api_key = api_key or os.environ.get(Defaults.api_key_env_var)
        base_endpoint = base_endpoint or os.environ.get(Defaults.base_endpoint_env_var)

        if not actor_system:
            raise DistributorUsageException(f"actor_system must be provided or {Defaults.actor_system_env_var} env var must be set")
        if not full_api_key:
            raise DistributorUsageException(f"api_key must be provided or {Defaults.api_key_env_var} env var must be set")
        if not base_endpoint:
            raise DistributorUsageException(f"base_endpoint must be provided or {Defaults.base_endpoint_env_var} env var must be set")

        try:
            full_api_key = urlsafe_b64decode(full_api_key).decode()
        except:
            raise DistributorUsageException(f"api_key is in wrong format")
        
        cf_access_client_id, cf_access_client_secret, api_key = full_api_key.split(":")
        self.invocation_params = InvocationParams(
            base_endpoint=base_endpoint,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
            api_key=api_key
        )

    def deserialize_task(self, serialized_task):
        blueprint = blueprints.build_blueprint(serialized_task['blueprint'])

        return Task(
            invocation_params=self.invocation_params, 
            actor_system=serialized_task['actor_system'], 
            actor_uid=serialized_task['actor_uid'], 
            blueprint=blueprint
        )

    async def afetch_task(self, *, platform: str, actor_uid: str):
        if not platform:
            raise DistributorUsageException('platform must be provided')
        if platform not in Defaults.supported_platforms:
            raise DistributorUsageException(f"platform {platform} is not one of supported platforms: {', '.join(Defaults.supported_platforms)}")
        if not actor_uid:
            raise DistributorUsageException('actor_uid must be provided')

        res = await api.afetch_task(
            invocation_params=self.invocation_params,
            actor_system=self.actor_system,
            actor_uid=actor_uid,
            platform=platform
        )

        if not res:
            return None
        
        blueprint = blueprints.build_blueprint(res)

        return Task(
            invocation_params=self.invocation_params, 
            actor_system=self.actor_system, 
            actor_uid=actor_uid, 
            blueprint=blueprint
        )
    
    
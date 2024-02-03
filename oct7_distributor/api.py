import aiohttp
from os import path
from pydantic import BaseModel
from .exceptions import DistributorRequestException
from .defaults import Defaults
from .content_entities import ContentEntity

class InvocationParams(BaseModel):
    base_endpoint: str
    cf_access_client_id: str
    cf_access_client_secret: str
    api_key: str

    def url(self, endpoint):
        return path.join(self.base_endpoint, Defaults.api_version, endpoint)

    def headers(self):
        return {
            "Content-Type": "application/json",
            "CF-Access-Client-Id": self.cf_access_client_id,
            "CF-Access-Client-Secret": self.cf_access_client_secret,
            "Authorization": f"Bearer {self.api_key}"
        }

async def _post_with_redirect(session, *, url, data):
    response = await session.post(url, json=data, allow_redirects=False) 
    if response.status in (301, 302):
        new_url = response.headers['Location']
        response = await session.post(new_url, json=data) 
    return response

    
async def afetch_task(*, invocation_params: InvocationParams, actor_system: str, actor_uid: str, platform: str) -> dict | None:
    url = invocation_params.url("fetch-task")
    headers = invocation_params.headers()

    async with aiohttp.ClientSession(headers=headers) as session:
        data = {
            "actor_system": actor_system,
            "actor_uid": actor_uid,
            "platform": platform
        }

        response = await _post_with_redirect(session, url=url, data=data)

        if response.status == 200:
            return await response.json()
        elif response.status in [400, 500]:
            error = await response.json()
            raise DistributorRequestException(error['error'])
        elif response.status == 403: 
            raise DistributorRequestException('unauthorized')
        elif response.status == 204:
            return None  # not found

async def atask_complete(*, invocation_params: InvocationParams, status, actor_system: str, action_uid: str, actor_uid: str, error_message: str | None = None, content_uid: str | None = None, entity: ContentEntity | None = None) -> True:
    url = invocation_params.url("task-complete")
    headers = invocation_params.headers()

    async with aiohttp.ClientSession(headers=headers) as session:
        new_entity = entity.model_dump() if entity else None
        data = {
            "status": status,
            "actor_system": actor_system,
            "action_uid": action_uid,
            "actor_uid": actor_uid,
            "error_message": error_message,
            "content_uid": content_uid, 
            "new_entity": new_entity
        }

        response = await _post_with_redirect(session, url=url, data=data)
        
        if response.status == 200:
            return True
        elif response.status in [400, 500]:
            error = await response.json()
            raise DistributorRequestException(error['error'])
        elif response.status == 403: 
            raise DistributorRequestException('unauthorized')


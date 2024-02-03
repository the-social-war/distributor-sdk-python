from pydantic import BaseModel, ValidationError, validator
from typing import Literal, TypeAlias, Type
from .exceptions import DistributorBlueprintException
from .content_entities import Post, Comment

class ContentDefinition(BaseModel):
    uid: str
    type: Literal['prompt', 'text']
    text: str

class PublishPost(BaseModel):
    type: Literal['publish_post']
    expected_entity: Type[Post] = Post
    action_uid: str
    content: ContentDefinition

class ReactToPost(BaseModel):
    type: Literal['react_to_post']
    expected_entity: None = None
    action_uid: str
    reaction: Literal['like', 'save']
    post_type: Literal['synth_post', 'organic_post']
    post_id: int
    post_url: str
    post_media_url: str | None = None
    post_avatar_pic_url: str | None = None

class SharePost(BaseModel):
    type: Literal['share_post']
    expected_entity: None = None
    action_uid: str
    post_type: Literal['synth_post', 'organic_post']
    post_id: int
    post_url: str
    post_media_url: str | None = None
    post_avatar_pic_url: str | None = None

class CommentOnPost(BaseModel):
    type: Literal['comment_on_post']
    expected_entity: Type[Comment] = Comment
    action_uid: str
    content: ContentDefinition
    post_type: Literal['synth_post', 'organic_post']
    post_id: int
    post_url: str
    post_media_url: str | None = None
    post_avatar_pic_url: str | None = None

class ReactToComment(BaseModel):
    type: Literal['react_to_comment']
    expected_entity: None = None
    action_uid: str
    reaction: Literal['like', 'save']
    post_type: Literal['synth_post', 'organic_post']
    post_id: int
    post_url: str
    post_media_url: str | None = None
    post_avatar_pic_url: str | None = None
    comment_type: Literal['synth_comment', 'organic_comment']
    comment_url: str | None = None
    comment_author: str
    comment_text: str

class ShareComment(BaseModel):
    type: Literal['share_comment']
    expected_entity: None = None
    action_uid: str
    post_type: Literal['synth_post', 'organic_post']
    post_id: int
    post_url: str
    post_media_url: str | None = None
    post_avatar_pic_url: str | None = None
    comment_type: Literal['synth_comment', 'organic_comment']
    comment_url: str | None = None
    comment_author: str
    comment_text: str

Blueprint: TypeAlias = PublishPost | ReactToPost | CommentOnPost | ReactToComment | ShareComment

mapping = dict[str: Blueprint](
    publish_post=PublishPost,
    react_to_post=ReactToPost,
    share_post=SharePost,
    comment_on_post=CommentOnPost,
    react_to_comment=ReactToComment,
    share_comment=ShareComment
)

def build_blueprint(blueprint: dict):
    type = blueprint['type']
    if not type:
        raise DistributorBlueprintException('type must be provided')
    
    klass: Blueprint = mapping[type]
    if not klass:
        raise DistributorBlueprintException(f"type {type} is not one of valid types: {', '.join(mapping.keys())}")
    
    try:
        return klass.model_validate(blueprint)
    except ValidationError as err:
        raise DistributorBlueprintException(f"Validation error for blueprint type {blueprint.type}: {err}")
    

    

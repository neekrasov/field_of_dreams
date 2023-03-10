from pydantic import BaseModel, Field
from typing import Optional, Any, List


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: str


class Chat(BaseModel):
    id: int
    type: str
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    pinned_message: Optional["Message"]


class MessageEntity(BaseModel):
    type: str
    offset: int
    length: int


class Message(BaseModel):
    message_id: int
    from_user: Optional[User] = Field(alias="from")
    date: int
    chat: Chat
    text: Optional[str] = None
    new_chat_member: Optional[User] = None
    entities: Optional[List[MessageEntity]] = None


class CallbackQuery(BaseModel):
    id: int
    data: str
    from_user: Optional[User] = Field(alias="from")
    message: Optional[Message]
    date: Optional[int]
    chat: Optional[Chat]


class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    state: Optional[Any] = None

    def set_state(self, state: Any):
        self.state = state


class ChatMember(BaseModel):
    status: str
    user: User


Chat.update_forward_refs()

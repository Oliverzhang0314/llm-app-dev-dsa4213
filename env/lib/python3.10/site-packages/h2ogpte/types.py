from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Union, Optional, List


class JobKind(str, Enum):
    NoOpJob = "NoOpJob"
    IngestFromFileSystemJob = "IngestFromFileSystemJob"
    IngestUploadsJob = "IngestUploadsJob"
    IngestWebsiteJob = "IngestWebsiteJob"
    IndexFilesJob = "IndexFilesJob"
    UpdateCollectionStatsJob = "UpdateCollectionStatsJob"
    DeleteCollectionsJob = "DeleteCollectionsJob"
    DeleteDocumentsJob = "DeleteDocumentsJob"
    DeleteDocumentsFromCollectionJob = "DeleteDocumentsFromCollectionJob"
    ImportDocumentIntoCollectionJob = "ImportDocumentIntoCollectionJob"
    ImportCollectionIntoCollectionJob = "ImportCollectionIntoCollectionJob"
    DocumentSummaryJob = "DocumentSummaryJob"


class Status(str, Enum):
    Unknown = "unknown"
    Scheduled = "scheduled"
    Queued = "queued"
    Running = "running"
    Completed = "completed"
    Failed = "failed"
    Canceled = "canceled"


class Answer(BaseModel):
    content: str
    error: str
    prompt_raw: str = ""
    llm: str
    input_tokens: int = 0
    output_tokens: int = 0
    origin: str = "N/A"


class ExtractionAnswer(BaseModel):
    content: List[str]
    error: str
    llm: str
    input_tokens: int = 0
    output_tokens: int = 0


class DocumentSummary(BaseModel):
    id: str
    content: str
    error: str
    document_id: str
    kwargs: str
    created_at: datetime


class SuggestedQuestion(BaseModel):
    question: str


class ChatMessage(BaseModel):
    id: str
    content: str
    reply_to: Optional[str] = None
    votes: int
    created_at: datetime
    type_list: Optional[List[str]] = None
    error: Optional[str] = None


class PartialChatMessage(BaseModel):
    id: str
    content: str
    reply_to: Optional[str] = None


class ChatMessageReference(BaseModel):
    document_id: str
    document_name: str
    chunk_id: int
    pages: str
    score: float


class ChatMessageMeta(BaseModel):
    message_type: str
    content: str


class ChatMessageFull(BaseModel):
    id: str
    username: Optional[str] = None
    content: str
    reply_to: Optional[str] = None
    votes: int
    created_at: datetime
    type_list: Optional[List[ChatMessageMeta]] = []
    error: Optional[str] = None


class ChatSessionCount(BaseModel):
    chat_session_count: int


class ChatSessionForCollection(BaseModel):
    id: str
    latest_message_content: Optional[str] = None
    updated_at: datetime


class ChatSessionInfo(BaseModel):
    id: str
    latest_message_content: Optional[str] = None
    collection_id: Optional[str]
    collection_name: Optional[str]
    prompt_template_id: Optional[str] = None
    updated_at: datetime


class QuestionReplyData(BaseModel):
    question_content: str
    reply_content: str
    question_id: str
    reply_id: str
    llm: Optional[str]
    system_prompt: Optional[str]
    pre_prompt_query: Optional[str]
    prompt_query: Optional[str]
    pre_prompt_summary: Optional[str]
    prompt_summary: Optional[str]
    rag_config: Optional[str]
    collection_documents: Optional[List[str]]
    votes: int
    expected_answer: Optional[str]
    user_comment: Optional[str]
    collection_id: Optional[str]
    collection_name: Optional[str]
    response_created_at_time: str
    prompt_template_id: Optional[str] = None


class QuestionReplyDataCount(BaseModel):
    question_reply_data_count: int


class Chunk(BaseModel):
    text: str


class Chunks(BaseModel):
    result: List[Chunk]


class PromptTemplate(BaseModel):
    is_default: bool
    id: Optional[str]
    name: str
    description: Optional[str]
    lang: Optional[str]
    system_prompt: Optional[str]
    pre_prompt_query: Optional[str]
    prompt_query: Optional[str]
    hyde_no_rag_llm_prompt_extension: Optional[str]
    pre_prompt_summary: Optional[str]
    prompt_summary: Optional[str]
    system_prompt_reflection: Optional[str]
    pre_prompt_reflection: Optional[str]
    prompt_reflection: Optional[str]
    auto_gen_description_prompt: Optional[str]
    auto_gen_document_summary_pre_prompt_summary: Optional[str]
    auto_gen_document_summary_prompt_summary: Optional[str]
    auto_gen_document_sample_questions_prompt: Optional[str]
    default_sample_questions: Optional[List[str]]
    created_at: Optional[datetime]


class PromptTemplateCount(BaseModel):
    prompt_template_count: int


class Collection(BaseModel):
    id: str
    name: str
    description: str
    document_count: int
    document_size: int
    created_at: datetime
    updated_at: datetime
    username: str
    rag_type: Optional[str] = None
    embedding_model: Optional[str] = None
    prompt_template_id: Optional[str] = None
    is_public: bool


class CollectionCount(BaseModel):
    collection_count: int


class CollectionInfo(BaseModel):
    id: str
    name: str
    description: str
    document_count: int
    document_size: int
    updated_at: datetime
    user_count: int
    is_public: bool
    username: str
    sessions_count: int


class Document(BaseModel):
    id: str
    name: str
    type: str
    size: int
    page_count: int
    status: Status
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(use_enum_values=True)


class DocumentCount(BaseModel):
    document_count: int


class DocumentInfo(BaseModel):
    id: str
    username: str
    name: str
    type: str
    size: int
    page_count: int
    status: Status
    updated_at: datetime

    model_config = ConfigDict(use_enum_values=True)


class DocumentInfoSummary(BaseModel):
    id: str
    username: str
    name: str
    type: str
    size: int
    page_count: int
    status: Status
    updated_at: datetime
    summary: Optional[str]
    summary_parameters: Optional[str]

    model_config = ConfigDict(use_enum_values=True)


class ShareResponseStatus(BaseModel):
    status: str


class Permission(BaseModel):
    username: str


class User(BaseModel):
    username: str


class Identifier(BaseModel):
    id: str
    error: Optional[str] = None


class JobStatus(BaseModel):
    id: str
    status: str


class Job(BaseModel):
    id: str
    name: str
    passed: float
    failed: float
    progress: float
    completed: bool
    canceled: bool
    date: datetime
    kind: JobKind
    statuses: List[JobStatus]
    errors: List[str]
    last_update_date: datetime
    duration: str


class ConfigItem(BaseModel):
    key_name: str
    string_value: str
    value_type: str
    can_overwrite: bool


class Meta(BaseModel):
    version: str
    build: str
    username: str
    email: str
    license_expired: bool
    license_expiry_date: str
    global_configs: List[ConfigItem]
    picture: Optional[str]


class ObjectCount(BaseModel):
    chat_session_count: int
    collection_count: int
    document_count: int


class Result(BaseModel):
    status: Status

    model_config = ConfigDict(use_enum_values=True)


class SchedulerStats(BaseModel):
    queue_length: int


class SearchResult(BaseModel):
    id: int
    topic: str
    name: str
    text: str
    size: int
    pages: str
    score: float


class SearchResults(BaseModel):
    result: List[SearchResult]


class SessionError(Exception):
    pass


class LLMUsage(BaseModel):
    # FIXME: add list of origins and percentages - update SQL query
    llm_name: str
    llm_cost: float


class LLMUsageLimit(BaseModel):
    current: float
    max_allowed_24h: float
    cost_unit: str
    interval: Optional[str] = None


@dataclass
class ChatRequest:
    t: str  # cq
    mode: str  # l=lexical, s=semantic, h=hybrid
    session_id: str
    correlation_id: str
    body: str
    system_prompt: Optional[str]
    pre_prompt_query: Optional[str]
    prompt_query: Optional[str]
    pre_prompt_summary: Optional[str]
    prompt_summary: Optional[str]
    llm: Union[str, int, None]
    llm_args: Optional[str]
    self_reflection_config: Optional[str]
    rag_config: Optional[str]


@dataclass
class ChatAcknowledgement:
    t: str  # cx
    session_id: str
    correlation_id: str
    message_id: str


@dataclass
class ChatResponse:
    t: str  # ca | cp | ce
    session_id: str
    message_id: str
    reply_to_id: str
    body: str
    error: str


class ObjectNotFoundError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass


class UnauthorizedError(Exception):
    pass

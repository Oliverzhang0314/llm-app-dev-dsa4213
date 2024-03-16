import asyncio
import json
import uuid
import websockets.client
from dataclasses import asdict
from datetime import datetime
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Union, Dict, Type, Optional
from urllib.parse import urlparse

if TYPE_CHECKING:
    from h2ogpte.h2ogpte_async import H2OGPTEAsync

from h2ogpte.types import (
    ChatAcknowledgement,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    SessionError,
    PromptTemplate,
)


class SessionAsync:
    """Create and participate in a chat session.
    This is a live connection to the h2oGPTe server contained to a specific
    chat session on top of a single collection of documents. Users will find all
    questions and responses in this session in a single chat history in the
    UI.
    See Also:
        H2OGPTE.connect: To initialize a session on an existing connection.
    Args:
        address:
                Full URL of the h2oGPTe server to connect to.
        api_key:
                API key for authentication to the h2oGPTe server. Users can generate
                a key by accessing the UI and navigating to the Settings.
        chat_session_id:
                The ID of the chat session the queries should be sent to.
        verify:
                Whether to verify the server's TLS/SSL certificate.
                Can be a boolean or a path to a CA bundle. Defaults to True.
    Examples::
        async with h2ogpte.connect(_chat_session_id) as session:
            answer1 = await session.query(
                'How many paper clips were shipped to Scranton?'
            )
            answer2 = await session.query(
                'Did David Brent co-sign the contract with Initech?'
            )
    """

    def __init__(
        self,
        chat_session_id: str,
        client: "H2OGPTEAsync",
        prompt_template_id: Optional[str] = None,
    ):
        self._chat_session_id = chat_session_id
        self._client = client
        self._websocket: Optional[websockets.client.WebSocketClientProtocol] = None
        # Keeps track of "in-flight" queries (multiple queries may be fired at the
        # same time):
        self._messages: list["_QueryInfo"] = []
        self._prompt_template_id: Optional[str] = prompt_template_id
        self._prompt_template = None  # created by __enter__

    async def query(
        self,
        message: str,
        *,
        system_prompt: Optional[str] = None,
        pre_prompt_query: Optional[str] = None,
        prompt_query: Optional[str] = None,
        pre_prompt_summary: Optional[str] = None,
        prompt_summary: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        self_reflection_config: Optional[Dict[str, Any]] = None,
        rag_config: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        callback: Optional[Callable[[ChatMessage], None]] = None,
    ) -> ChatMessage:
        """Retrieval-augmented generation for a query on a collection.
        Finds a collection of chunks relevant to the query using similarity scores.
        Sends these and any additional instructions to an LLM.
        Format of questions or imperatives::
            "{pre_prompt_query}
            \"\"\"
            {similar_context_chunks}
            \"\"\"\
            {prompt_query}{message}"
        Args:
            message:
                Query or instruction from the end user to the LLM.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` or None for the model
                default. Defaults to '' for no system prompt.
            pre_prompt_query:
                Text that is prepended before the contextual document chunks. The
                default can be customized per environment, but the standard default is
                :code:`"Pay attention and remember the information below, which will
                help to answer the question or imperative after the context ends.\\\\n"`
            prompt_query:
                Text that is appended to the beginning of the user's message. The
                default can be customized per environment, but the standard default is
                "According to only the information in the document sources provided
                within the context above, "
            pre_prompt_summary:
                Not yet used, use H2OGPTE.summarize_content
            prompt_summary:
                Not yet used, use H2OGPTE.summarize_content
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see
                all available options. Default value is to use the first model (0th
                index).
            llm_args:
                Dictionary of kwargs to pass to the llm.
            self_reflection_config:
                Dictionary of arguments for self-reflection, can contain the following
                string:string mappings:
                    llm_reflection: str
                        :code:`"gpt-4-0613"`  or :code:`""` to disable reflection
                    pre_prompt_reflection: str
                        :code:`"Pay attention to the following context. You will need
                        to evaluate the quality of a response for a given prompt."`
                    prompt_reflection: str
                        'Given the above context, here\'s the prompt and the response:
                        :code:`\"\"\"Prompt:\\\\n%s\\\\n\"\"\"\\\\n\\\\n\"\"\"
                        Response:\\\\n%s\\\\n\"\"\"\\\\n\\\\nWhat is the quality of the
                        response for the given prompt? Respond with a score ranging
                        from Score: 0/10 (worst) to Score: 10/10 (best), and give a
                        brief explanation why.'`
                    system_prompt_reflection: str
                        :code:`""`
                    llm_args_reflection: str
                        :code:`"{}"`
            rag_config:
                Dictionary of arguments to control RAG (retrieval-augmented-generation)
                types. Can contain the following key/value pairs:
                rag_type: str one of
                    :code:`"llm_only"` LLM Only (no RAG) - Generates a response to
                        answer the user's query without any supporting document
                        contexts.
                    :code:`"rag"` RAG (Retrieval Augmented Generation) - RAG with
                        neural/lexical hybrid search using the user's query to find
                        relevant contexts from a collection for generating a response.
                    :code:`"rag+"` "RAG+ (RAG without context limit) - RAG with
                        neural/lexical hybrid search using the user's query to find
                        relevant contexts from a collection for generating a response.
                        Uses recursive summarization to overcome LLM context limits.
                        Can require several LLM calls.",
                    :code:`"hyde1"` HyDE RAG (Hypothetical Document Embedding) - RAG
                        with neural/lexical hybrid search using the user's query and
                        the LLM response to find contexts from a collection for
                        generating a response. Requires 2 LLM calls.
                    :code:`"hyde2"` HyDE RAG+ (Combined HyDE+RAG) - RAG with
                        neural/lexical hybrid search using the user's query and the
                        HyDE RAG response to find contexts from a collection for
                        generating a response. Requires 3 LLM calls.
                hyde_no_rag_llm_prompt_extension: str
                    example: :code:`'\\\\nKeep the answer brief, and list the 5 most
                    relevant key words at the end.'`
            timeout:
                Amount of time in seconds to allow the request to run. The default is
                1000 seconds.
            callback:
                Function for processing partial messages, used for streaming responses
                to an end user.
        Returns:
            ChatMessage: The response text and details about the response from the LLM.
            For example::
                ChatMessage(
                    id='XXX',
                    content='The information provided in the context...',
                    reply_to='YYY',
                    votes=0,
                    created_at=datetime.datetime(2023, 10, 24, 20, 12, 34, 875026)
                    type_list=[],
                )
        Raises:
            TimeoutError: The request did not complete in time.
        """
        correlation_id = str(uuid.uuid4())
        request = ChatRequest(
            t="cq",
            mode="s",
            session_id=self._chat_session_id,
            correlation_id=correlation_id,
            body=message,
            system_prompt=system_prompt,
            pre_prompt_query=pre_prompt_query,
            prompt_query=prompt_query,
            pre_prompt_summary=pre_prompt_summary,
            prompt_summary=prompt_summary,
            llm=llm,
            llm_args=json.dumps(llm_args) if llm_args else None,
            self_reflection_config=json.dumps(self_reflection_config),
            rag_config=json.dumps(rag_config),
        )
        serialized = json.dumps(asdict(request), allow_nan=False, separators=(",", ":"))

        async def send_recv_query() -> ChatMessage:
            await self.websocket.send(serialized)
            info = _QueryInfo(correlation_id=correlation_id, callback=callback)
            self._messages.append(info)
            while not info.done:
                await self._poll()
            del self._messages[self._messages.index(info)]
            assert info.message is not None
            return info.message

        return await asyncio.wait_for(send_recv_query(), timeout=timeout)

    async def _poll(self) -> None:
        data = await self.websocket.recv()
        assert isinstance(data, str)
        for line in data.splitlines():
            raw = json.loads(line)
            if raw["session_id"] != self._chat_session_id:
                raise SessionError(
                    f"Received a response for session {raw['session_id']}, while "
                    f"expecting response for session {self._chat_session_id}"
                )
            t = raw["t"]
            if t == "cx":
                self._process_acknowledgment(ChatAcknowledgement(**raw))
            elif t == "ca" or t == "cp":
                self._process_response_or_partial_response(ChatResponse(**raw))
            elif t == "ce":
                raise SessionError(ChatResponse(**raw).error)
            else:
                raise SessionError(f"Invalid chat response type: {t}")

    def _process_acknowledgment(self, res: ChatAcknowledgement) -> None:
        for msg in self._messages:
            if msg.correlation_id == res.correlation_id:
                msg.query_id = res.message_id
                return
        expected = [msg.correlation_id for msg in self._messages]
        raise SessionError(
            f"Received a response with correlation id `{res.correlation_id}`, "
            f"while expecting any of {expected}"
        )

    def _process_response_or_partial_response(self, res: ChatResponse) -> None:
        info = None
        for msg in self._messages:
            if msg.query_id == res.reply_to_id or msg.message_id == res.message_id:
                info = msg
                break
        if info is None:
            if len(self._messages) == 1:
                info = self._messages[0]
            else:
                raise SessionError(f"Unexpected response {res} without prior ACK")

        info.message_id = res.message_id
        if info.message is None:
            info.message = ChatMessage(
                id=res.message_id,
                content="",
                reply_to=info.query_id,
                votes=0,
                created_at=datetime.now(),
                type_list=[],
            )
        elif not info.message.id:
            info.message.id = info.message_id
        info.message.content = res.body
        if info.callback:
            info.callback(info.message)
        if res.t == "ca":
            info.done = True

    async def __aenter__(self) -> "SessionAsync":
        address = self._client._address  # type: ignore[reportPrivateUsage]
        headers = await self._client._get_auth_header()  # type: ignore[reportPrivateUsage]

        url = urlparse(address)
        scheme = "wss" if url.scheme == "https" else "ws"
        self._websocket = await websockets.client.connect(
            uri=f"{scheme}://{url.netloc}/ws",
            extra_headers=headers,
        )
        if self._client and self._prompt_template_id:
            await self._client.set_chat_session_prompt_template(
                self._chat_session_id,
                self._prompt_template_id,
            )
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.websocket.close()

    @property
    def websocket(self) -> websockets.client.WebSocketClientProtocol:
        assert self._websocket is not None
        return self._websocket


class _QueryInfo:
    def __init__(
        self,
        correlation_id: str,
        callback: Optional[Callable[[ChatMessage], None]] = None,
    ):
        self.correlation_id = correlation_id
        self.callback: Optional[Callable[[ChatMessage], None]] = callback
        self.query_id: Optional[str] = None
        self.message_id: Optional[str] = None
        self.done: bool = False
        self.message: Optional[ChatMessage] = None

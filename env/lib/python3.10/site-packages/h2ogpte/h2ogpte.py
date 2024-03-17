import json
import os.path

import requests
import time
import uuid
from packaging import version
from pathlib import Path
from typing import Iterable, Any, Union, List, Dict, Tuple, Optional, cast
from h2o_authn import TokenProvider

from h2ogpte.errors import (
    ErrorResponse,
    HTTPError,
    InternalServerError,
    InvalidArgumentError,
    ObjectNotFoundError,
    UnauthorizedError,
)
from h2ogpte.session import Session
from h2ogpte.types import (
    Answer,
    ChatMessage,
    ChatMessageFull,
    ChatMessageReference,
    ChatSessionCount,
    ChatSessionForCollection,
    ChatSessionInfo,
    ChatMessageMeta,
    Chunk,
    Chunks,
    Collection,
    CollectionCount,
    CollectionInfo,
    Document,
    DocumentCount,
    DocumentInfo,
    DocumentInfoSummary,
    SuggestedQuestion,
    ExtractionAnswer,
    Identifier,
    User,
    Permission,
    Job,
    JobKind,
    Meta,
    ObjectCount,
    QuestionReplyData,
    QuestionReplyDataCount,
    Result,
    ShareResponseStatus,
    SchedulerStats,
    SearchResult,
    SearchResults,
    SessionError,
    LLMUsage,
    LLMUsageLimit,
    DocumentSummary,
    PromptTemplate,
    PromptTemplateCount,
)


class H2OGPTE:
    """Connect to and interact with an h2oGPTe server."""

    # Timeout for HTTP requests
    TIMEOUT = 3600.0

    INITIAL_WAIT_INTERVAL = 0.1
    MAX_WAIT_INTERVAL = 1.0
    WAIT_BACKOFF_FACTOR = 1.4

    def __init__(
        self,
        address: str,
        api_key: Optional[str] = None,
        token_provider: Optional[TokenProvider] = None,
        verify: Union[bool, str] = True,
        strict_version_check: bool = False,
    ):
        """Create a new H2OGPTE client.

        Args:
            address:
                Full URL of the h2oGPTe server to connect to, e.g. "https://h2ogpte.h2o.ai".
            api_key:
                API key for authentication to the h2oGPTe server. Users can generate
                a key by accessing the UI and navigating to the Settings.
            token_provider:
                User's token provider.
            verify:
                Whether to verify the server's TLS/SSL certificate.
                Can be a boolean or a path to a CA bundle.
                Defaults to True.
            strict_version_check:
                Indicate whether a version check should be enforced.

        Returns:
            A new H2OGPTE client.
        """
        # Remove trailing slash from address, if any
        address = address.rstrip("/ ")

        self._address = address
        self._api_key = api_key
        self._verify = verify
        self._token_provider = token_provider
        self._session_id = str(uuid.uuid4())

        if self._api_key is None and self._token_provider is None:
            raise RuntimeError(
                f"Please use either an API key or a Token provider to authenticate."
            )

        if self._api_key is not None and self._token_provider is not None:
            print(
                "Warning: The token_provider parameter will be ignored in favor of the provided api_key"
            )

        self._check_version(strict_version_check)

    def _get_auth_header(self) -> Dict:
        if self._api_key is not None:
            return {
                "Authorization": f"Bearer {self._api_key}",
            }
        elif self._token_provider is not None:
            token = self._token_provider.token()
            return {
                "Authorization": f"Token-Bearer {token}",
                "Session-Id": self._session_id,
            }
        else:
            raise Exception(
                "Please provide either an api_key or a token_provider to authenticate."
            )

    def _check_version(self, strict_version_check: bool):
        from h2ogpte import __version__ as client_version

        server_version = self.get_meta().version
        if server_version[0] == "v":
            server_version = server_version[1:]

        if server_version != client_version:
            msg = (
                f"Warning: Server version {server_version} doesn't match client "
                f"version {client_version}: unexpected errors may occur.\n"
                f"Please install the correct version of H2OGPTE "
                f"with `pip install h2ogpte=={server_version}`."
            )
            if strict_version_check:
                raise RuntimeError(msg)
            else:
                print(msg)
                print(
                    "You can enable strict version checking by passing strict_version_check=True."
                )

    def _get(self, slug: str):
        res = requests.get(
            f"{self._address}{slug}",
            headers={**self._get_auth_header(), **{"Content-Type": "application/json"}},
            verify=self._verify,
            timeout=H2OGPTE.TIMEOUT,
        )
        self._raise_error_if_any(res)
        return res.json()

    def _post(self, slug: str, data: Any):
        res = requests.post(
            f"{self._address}{slug}",
            data=data,
            headers={**self._get_auth_header(), **{"Content-Type": "application/json"}},
            verify=self._verify,
            timeout=H2OGPTE.TIMEOUT,
        )
        self._raise_error_if_any(res)
        return res.json()

    def _raise_error_if_any(self, res: requests.Response) -> None:
        if res.status_code == 200:
            return
        error: ErrorResponse
        try:
            error = res.json()
        except:
            error = {"error": res.content.decode(errors="replace")}
        if res.status_code == 400:
            raise InvalidArgumentError(error)
        elif res.status_code == 401:
            raise UnauthorizedError(error)
        elif res.status_code == 404:
            raise ObjectNotFoundError(error)
        elif res.status_code == 500:
            raise InternalServerError(error)
        else:
            raise HTTPError(error, res.status_code)

    def _db(self, method: str, *args: Any) -> Any:
        return self._post("/rpc/db", marshal([method, *args]))

    def _job(self, method: str, **kwargs: Any) -> Any:
        request_id = str(uuid.uuid4())
        return self._post("/rpc/job", marshal([method, kwargs, request_id]))

    def _lang(self, method: str, **kwargs: Any) -> Any:
        res = self._post("/rpc/lang", marshal(dict(method=method, params=kwargs)))
        return res["result"]

    def _vex(self, method: str, collection_id: str, **kwargs: Any) -> Any:
        return self._post(
            "/rpc/vex",
            marshal(dict(method=method, collection_id=collection_id, params=kwargs)),
        )

    def _wait(self, d: Dict[str, Any], timeout: Optional[float] = None):
        if timeout is None:
            timeout = 86400
        deadline = time.time() + timeout
        job_id = _to_id(d)
        dt = H2OGPTE.INITIAL_WAIT_INTERVAL
        last_job: Optional[Job] = None
        while True:
            job = self.get_job(job_id)
            if job.completed or job.canceled:
                break
            if last_job is not None and last_job.progress == job.progress:
                if time.time() > deadline:
                    raise TimeoutError(
                        f"Job {job.kind} ({job_id}) timed out after {timeout} seconds"
                    )
            else:
                last_job = job
                deadline = time.time() + timeout
            time.sleep(dt)
            dt = min(H2OGPTE.MAX_WAIT_INTERVAL, dt * H2OGPTE.WAIT_BACKOFF_FACTOR)
        return job

    def answer_question(
        self,
        question: str,
        system_prompt: Union[
            str, None
        ] = "",  # "" to disable, 'auto' to use LLMs default, None for h2oGPTe default
        pre_prompt_query: Union[
            str, None
        ] = None,  # "" to disable, None for h2oGPTe default
        prompt_query: Union[
            str, None
        ] = None,  # "" to disable, None for h2oGPTe default
        text_context_list: Optional[List[str]] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        chat_conversation: Optional[List[Tuple[str, str]]] = None,
        timeout: Union[float, None] = None,
        **kwargs: Any,
    ):
        """Send a message and get a response from an LLM.

        Format of inputs content:

            .. code-block::

                {text_context_list}
                \"\"\"\\n{chat_conversation}{question}

        Args:
            question:
                Text query to send to the LLM.
            text_context_list:
                List of raw text strings to be included.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` for the model default, or None for h2oGPTe default. Defaults
                to '' for no system prompt.
            pre_prompt_query:
                Text that is prepended before the contextual document chunks in text_context_list. Only used if text_context_list is provided.
            prompt_query:
                Text that is appended after the contextual document chunks in text_context_list. Only used if text_context_list is provided.
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see all available options.
                Default value is to use the first model (0th index).
            llm_args:
                Dictionary of kwargs to pass to the llm.
            chat_conversation:
                List of tuples for (human, bot) conversation that will be pre-appended
                to an (question, None) case for a query.
            timeout:
                Timeout in seconds.
            kwargs:
                Dictionary of kwargs to pass to h2oGPT.

        Returns:
            Answer: The response text and any errors.
        Raises:
            TimeoutError: If response isn't completed in timeout seconds.
        """
        init_args = dict(
            prompt=question,
            system_prompt=system_prompt,
            pre_prompt_query=pre_prompt_query,
            prompt_query=prompt_query,
            text_context_list=text_context_list,
            llm=llm,
            llm_args=llm_args,
            chat_conversation=chat_conversation,
            timeout=timeout,
        )
        server_version = self.get_meta().version
        if len(server_version) > 1:
            server_version = server_version.lstrip("v")

            # 'timeout' not used in versions below 1.3.0
            if version.parse(server_version) < version.parse("1.3.0"):
                init_args.pop("timeout", None)

        ret = self._lang(
            "answer_question_using_context",
            **init_args,
            **kwargs,
        )
        assert isinstance(ret, dict)
        ret = cast(Dict[str, Any], ret)
        for key in ret:
            assert key in [
                "content",
                "error",
                "prompt_raw",
                "llm",
                "input_tokens",
                "output_tokens",
                "origin",
            ], key
        if ret["error"]:
            raise SessionError(ret["error"])
        return Answer(**ret)

    def summarize_content(
        self,
        text_context_list: Optional[List[str]] = None,
        system_prompt: str = "",  # '' to disable, 'auto' to use LLMs default
        pre_prompt_summary: Optional[str] = None,
        prompt_summary: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        """Summarize one or more contexts using an LLM.

        Effective prompt created (excluding the system prompt):

        .. code-block::

            "{pre_prompt_summary}
            \"\"\"
            {text_context_list}
            \"\"\"
            {prompt_summary}"

        Args:
            text_context_list:
                List of raw text strings to be summarized.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` for the model default or None for h2oGPTe defaults. Defaults
                to '' for no system prompt.
            pre_prompt_summary:
                Text that is prepended before the list of texts. The default can be
                customized per environment, but the standard default is :code:`"In order to write a concise single-paragraph
                or bulleted list summary, pay attention to the following text:\\\\n"`
            prompt_summary:
                Text that is appended after the list of texts. The default can be customized
                per environment, but the standard default is :code:`"Using only the text above, write a condensed and concise
                summary of key results (preferably as bullet points):\\\\n"`
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see all available options.
                Default value is to use the first model (0th index).
            llm_args:
                Dictionary of kwargs to pass to the llm.
            kwargs:
                Dictionary of kwargs to pass to h2oGPT.

        Returns:
            Answer: The response text and any errors.
        """
        ret = self._lang(
            "create_summary_from_context",
            text_context_list=text_context_list,
            system_prompt=system_prompt,
            pre_prompt_summary=pre_prompt_summary,
            prompt_summary=prompt_summary,
            llm=llm,
            llm_args=llm_args,
            **kwargs,
        )
        assert isinstance(ret, dict)
        ret = cast(Dict[str, Any], ret)
        if ret["error"]:
            raise SessionError(ret["error"])
        return Answer(**ret)

    def extract_data(
        self,
        text_context_list: Optional[List[str]] = None,
        system_prompt: str = "",  # '' to disable, 'auto' to use LLMs default, None for h2oGPTe default
        pre_prompt_extract: Optional[str] = None,
        prompt_extract: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        """Extract information from one or more contexts using an LLM.

        pre_prompt_extract and prompt_extract variables must be used together. If these
        variables are not set, the inputs texts will be summarized into bullet points.

        Format of extract content:

            .. code-block::

                "{pre_prompt_extract}\"\"\"
                {text_context_list}
                \"\"\"\\n{prompt_extract}"

        Examples:

            .. code-block:: python

                extract = h2ogpte.extract_data(
                    text_context_list=chunks,
                    pre_prompt_extract="Pay attention and look at all people. Your job is to collect their names.\\n",
                    prompt_extract="List all people's names as JSON.",
                )

        Args:
            text_context_list:
                List of raw text strings to extract data from.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` or None for the model default. Defaults
                to '' for no system prompt.
            pre_prompt_extract:
                Text that is prepended before the list of texts. If not set,
                the inputs will be summarized.
            prompt_extract:
                Text that is appended after the list of texts. If not set, the inputs will be summarized.
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see all available options.
                Default value is to use the first model (0th index).
            llm_args:
                Dictionary of kwargs to pass to the llm.
            kwargs:
                Dictionary of kwargs to pass to h2oGPT.

        Returns:
            ExtractionAnswer: The list of text responses and any errors.
        """
        ret = self._lang(
            "extract_data_from_context",
            text_context_list=text_context_list,
            system_prompt=system_prompt,
            pre_prompt_extract=pre_prompt_extract,
            prompt_extract=prompt_extract,
            llm=llm,
            llm_args=llm_args,
            **kwargs,
        )
        assert isinstance(ret, dict)
        ret = cast(Dict[str, Any], ret)
        if ret["error"]:
            raise SessionError(ret["error"])
        return ExtractionAnswer(**ret)

    def cancel_job(self, job_id: str) -> Result:
        """Stops a specific job from running on the server.

        Args:
            job_id:
                String id of the job to cancel.

        Returns:
            Result: Status of canceling the job.
        """
        return Result(**self._job(".Cancel", job_id=job_id))

    def count_chat_sessions(self) -> int:
        """Counts number of chat sessions owned by the user.

        Returns:
            int: The count of chat sessions owned by the user.
        """
        return ChatSessionCount(**self._db("count_chat_sessions")).chat_session_count

    def count_chat_sessions_for_collection(self, collection_id: str) -> int:
        """Counts number of chat sessions in a specific collection.

        Args:
            collection_id:
                String id of the collection to count chat sessions for.

        Returns:
            int: The count of chat sessions in that collection.
        """
        return ChatSessionCount(
            **self._db("count_chat_sessions_for_collection", collection_id)
        ).chat_session_count

    def count_collections(self) -> int:
        """Counts number of collections owned by the user.

        Returns:
            int: The count of collections owned by the user.
        """
        return CollectionCount(**self._db("count_collections")).collection_count

    def count_documents(self) -> int:
        """Counts number of documents accessed by the user.

        Returns:
            int: The count of documents accessed by the user.
        """
        return DocumentCount(**self._db("count_documents")).document_count

    def count_documents_owned_by_me(self) -> int:
        """Counts number of documents owned by the user.

        Returns:
            int: The count of documents owned by the user.
        """
        return DocumentCount(**self._db("count_documents_owned_by_me")).document_count

    def count_documents_in_collection(self, collection_id: str) -> int:
        """Counts the number of documents in a specific collection.

        Args:
            collection_id:
                String id of the collection to count documents for.

        Returns:
            int: The number of documents in that collection.
        """
        return DocumentCount(
            **self._db("count_documents_in_collection", collection_id)
        ).document_count

    def count_assets(self) -> ObjectCount:
        """Counts number of objects owned by the user.

        Returns:
            ObjectCount: The count of chat sessions, collections, and documents.
        """
        return ObjectCount(**self._db("count_assets"))

    def create_chat_session(self, collection_id: Optional[str] = None) -> str:
        """Creates a new chat session for asking questions (of documents).

        Args:
            collection_id:
                String id of the collection to chat with.
                If None, chat with LLM directly.

        Returns:
            str: The ID of the newly created chat session.
        """
        return _to_id(self._db("create_chat_session", collection_id))

    def create_chat_session_on_default_collection(self) -> str:
        """Creates a new chat session for asking questions of documents on the default collection.

        Returns:
            str: The ID of the newly created chat session.
        """
        return _to_id(self._db("create_chat_session_on_default_collection"))

    def list_embedding_models(self) -> List[str]:
        return list(self._lang("get_embedding_models_dict").keys())

    def create_collection(
        self,
        name: str,
        description: str,
        embedding_model: Union[str, None] = None,
        prompt_template_id: Union[str, None] = None,
    ) -> str:
        """Creates a new collection.

        Args:
            name:
                Name of the collection.
            description:
                Description of the collection
            embedding_model:
                embedding model to use. call list_embedding_models() to list of options.
            prompt_template_id:
                ID of the prompt template to get the prompts from. None to fall back to system defaults.
        Returns:
            str: The ID of the newly created collection.
        """
        if embedding_model is None:
            embedding_model = self._lang("get_default_embedding_model")
        collection_id = _to_id(
            self._db("create_collection", name, description, embedding_model)
        )
        if prompt_template_id is not None:
            self.set_collection_prompt_template(collection_id, prompt_template_id)
        return collection_id

    def delete_chat_sessions(self, chat_session_ids: Iterable[str]) -> Result:
        """Deletes chat sessions and related messages.

        Args:
            chat_session_ids:
                List of string ids of chat sessions to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        return Result(**self._db("delete_chat_sessions", chat_session_ids))

    def delete_chat_messages(self, chat_message_ids: Iterable[str]) -> Result:
        """Deletes specific chat messages.

        Args:
            chat_message_ids:
                List of string ids of chat messages to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        return Result(**self._db("delete_chat_messages", chat_message_ids))

    def delete_document_summaries(self, summaries_ids: Iterable[str]) -> Result:
        """Deletes document summaries.

        Args:
            summaries_ids:
                List of string ids of a document summary to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        return Result(**self._db("delete_document_summaries", summaries_ids))

    def get_collection_questions(
        self, collection_id: str, limit: int
    ) -> List[SuggestedQuestion]:
        """List suggested questions

        Args:
            collection_id:
                A collection ID of which to return the suggested questions
            limit:
                How many questions to return.

        Returns:
            List: A list of questions.
        """
        return [
            SuggestedQuestion(**d)
            for d in self._db("get_collection_questions", collection_id, limit)
        ]

    def get_chat_session_questions(
        self, chat_session_id: str, limit: int
    ) -> List[SuggestedQuestion]:
        """List suggested questions

        Args:
            chat_session_id:
                A chat session ID of which to return the suggested questions
            limit:
                How many questions to return.

        Returns:
            List: A list of questions.
        """
        return [
            SuggestedQuestion(**d)
            for d in self._db("get_chat_session_questions", chat_session_id, limit)
        ]

    def delete_collections(
        self,
        collection_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ):
        """Deletes collections from the environment.

        Documents in the collection will not be deleted.

        Args:
            collection_ids:
                List of string ids of collections to delete from the system.
            timeout:
                Timeout in seconds.
        """
        return self._wait(
            self._job("crawl.DeleteCollectionsJob", collection_ids=collection_ids),
            timeout=timeout,
        )

    def delete_documents(
        self,
        document_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ):
        """Deletes documents from the system.

        Args:
            document_ids:
                List of string ids to delete from the system and all collections.
            timeout:
                Timeout in seconds.
        """
        return self._wait(
            self._job("crawl.DeleteDocumentsJob", document_ids=document_ids),
            timeout=timeout,
        )

    def delete_documents_from_collection(
        self,
        collection_id: str,
        document_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ):
        """Removes documents from a collection.

        See Also: H2OGPTE.delete_documents for completely removing the document from the environment.

        Args:
            collection_id:
                String of the collection to remove documents from.
            document_ids:
                List of string ids to remove from the collection.
            timeout:
                Timeout in seconds.
        """
        return self._wait(
            self._job(
                "crawl.DeleteDocumentsFromCollectionJob",
                collection_id=collection_id,
                document_ids=document_ids,
            ),
            timeout=timeout,
        )

    def import_collection_into_collection(
        self,
        collection_id: str,
        src_collection_id: str,
        gen_doc_summaries: bool = False,
        gen_doc_questions: bool = False,
        timeout: Union[float, None] = None,
    ):
        """Import all documents from a collection into an existing collection

        Args:
            collection_id:
                Collection ID to add documents to.
            src_collection_id:
                Collection ID to import documents from.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            timeout:
                Timeout in seconds.
        """
        return self._wait(
            self._job(
                "crawl.ImportCollectionIntoCollectionJob",
                collection_id=collection_id,
                src_collection_id=src_collection_id,
                gen_doc_summaries=gen_doc_summaries,
                gen_doc_questions=gen_doc_questions,
            ),
            timeout=timeout,
        )

    def import_document_into_collection(
        self,
        collection_id: str,
        document_id: str,
        gen_doc_summaries: bool = False,
        gen_doc_questions: bool = False,
        timeout: Union[float, None] = None,
    ):
        """Import an already stored document to an existing collection

        Args:
            collection_id:
                Collection ID to add documents to.
            document_id:
                Document ID to add.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            timeout:
                Timeout in seconds.
        """
        return self._wait(
            self._job(
                "crawl.ImportDocumentIntoCollectionJob",
                collection_id=collection_id,
                document_id=document_id,
                gen_doc_summaries=gen_doc_summaries,
                gen_doc_questions=gen_doc_questions,
            ),
            timeout=timeout,
        )

    def summarize_document(
        self,
        document_id: str,
        system_prompt: Union[str, None] = None,
        pre_prompt_summary: Union[str, None] = None,
        prompt_summary: Union[str, None] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        max_num_chunks: Union[int, None] = None,
        sampling_strategy: Union[str, None] = None,
        timeout: Optional[float] = None,
    ) -> DocumentSummary:
        """Creates a summary of a document.

        Effective prompt created (excluding the system prompt):

        .. code-block::

            "{pre_prompt_summary}
            \"\"\"
            {text from document}
            \"\"\"
            {prompt_summary}"

        Args:
            document_id:
                String id of the document to create a summary from.
            system_prompt:
                System Prompt
            pre_prompt_summary:
                Prompt that goes before each large piece of text to summarize
            prompt_summary:
                Prompt that goes after each large piece of of text to summarize
            llm:
                LLM to use
            llm_args:
                Arguments for the LLM
            max_num_chunks:
                Max limit of chunks to send to the summarizer
            sampling_strategy:
                How to sample if the document has more chunks than max_num_chunks.
                Options are "auto", "uniform", "first", "first+last", default is "auto" (a hybrid of them all).
            timeout:
                Amount of time in seconds to allow the request to run. The default is 86400 seconds.

        Returns:
            DocumentSummary: Summary of the document

        Raises:
            TimeoutError: The request did not complete in time.
            SessionError: No summary created. Document wasn't part of a collection, or LLM timed out, etc.
        """
        summary_id = str(uuid.uuid4())
        self._wait(
            self._job(
                "crawl.DocumentSummaryJob",
                summary_id=summary_id,
                document_id=document_id,
                system_prompt=system_prompt,
                pre_prompt_summary=pre_prompt_summary,
                prompt_summary=prompt_summary,
                llm=llm,
                llm_args=llm_args,
                max_num_chunks=max_num_chunks,
                sampling_strategy=sampling_strategy,
                timeout=timeout,
            ),
            timeout=timeout,
        )
        res = self._db("get_document_summary", summary_id)
        summary = DocumentSummary(**res[0])
        if summary.error:
            raise SessionError(summary.error)
        return summary

    def list_recent_document_summaries(
        self, document_id: str, offset: int, limit: int
    ) -> List[DocumentSummary]:
        """Fetches recent document summaries

        Args:
            document_id:
                document ID for which to return summaries
            offset:
                How many summaries to skip before returning summaries.
            limit:
                How many summaries to return.
        """
        return [
            DocumentSummary(**d)
            for d in self._db(
                "list_recent_document_summaries", document_id, offset, limit
            )
        ]

    def encode_for_retrieval(
        self, chunks: List[str], embedding_model: Union[str, None] = None
    ) -> List[List[float]]:
        """Encode texts for semantic searching.

        See Also: H2OGPTE.match for getting a list of chunks that semantically match
        each encoded text.

        Args:
            chunks:
                List of strings of texts to be encoded.
            embedding_model:
                embedding model to use. call list_embedding_models() to list of options.

        Returns:
            List of list of floats: Each list in the list is the encoded original text.
        """
        if embedding_model is None:
            embedding_model = self._lang("get_default_embedding_model")
        return self._lang(
            "encode_for_retrieval", chunks=chunks, embedding_model=embedding_model
        )

    def get_chunks(self, collection_id: str, chunk_ids: Iterable[int]) -> List[Chunk]:
        """Get the text of specific chunks in a collection.

        Args:
            collection_id:
                String id of the collection to search in.
            chunk_ids:
                List of ints for the chunks to return. Chunks are indexed starting at 1.

        Returns:
            Chunk: The text of the chunk.

        Raises:
            Exception: One or more chunks could not be found.
        """
        res = self._vex("get_chunks", collection_id, chunk_ids=list(chunk_ids))
        return Chunks(**res).result

    def get_collection(self, collection_id: str) -> Collection:
        """Get metadata about a collection.

        Args:
            collection_id:
                String id of the collection to search for.

        Returns:
            Collection: Metadata about the collection.

        Raises:
            KeyError: The collection was not found.
        """
        res = self._db("get_collection", collection_id)
        if len(res) == 0:
            raise ObjectNotFoundError(
                {"error": f"Collection {collection_id} not found"}
            )
        return Collection(**res[0])

    def get_collection_for_chat_session(self, chat_session_id: str) -> Collection:
        """Get metadata about the collection of a chat session.

        Args:
            chat_session_id:
                String id of the chat session to search for.

        Returns:
            Collection: Metadata about the collection.
        """
        res = self._db("get_collection_for_chat_session", chat_session_id)
        if len(res) == 0:
            raise ObjectNotFoundError({"error": "Collection not found"})
        return Collection(**res[0])

    def get_document(self, document_id: str) -> Document:
        """Fetches information about a specific document.

        Args:
            document_id:
                String id of the document.

        Returns:
            Document: Metadata about the Document.

        Raises:
            KeyError: The document was not found.
        """
        res = self._db("get_document", document_id)
        if len(res) == 0:
            raise ObjectNotFoundError({"error": f"Document {document_id} not found"})
        return Document(**res[0])

    def get_job(self, job_id: str) -> Job:
        """Fetches information about a specific job.

        Args:
            job_id:
                String id of the job.

        Returns:
            Job: Metadata about the Job.
        """
        res = self._job(".Get", job_id=job_id)
        if len(res) == 0:
            raise ObjectNotFoundError({"error": f"Job {job_id} not found"})
        return Job(**(res[0]))

    def get_meta(self) -> Meta:
        """Returns information about the environment and the user.

        Returns:
            Meta: Details about the version and license of the environment and
            the user's name and email.
        """
        return Meta(**(self._get("/rpc/meta")))

    def get_llm_usage_24h(self) -> float:
        return self._db("get_llm_usage_24h")

    def get_llm_usage_24h_by_llm(self) -> List[LLMUsage]:
        return [LLMUsage(**d) for d in self._db("get_llm_usage_24h_by_llm")]

    def get_llm_usage_24h_with_limits(self) -> LLMUsageLimit:
        return LLMUsageLimit(**self._db("get_llm_usage_24h_with_limits"))

    def get_llm_usage_6h(self) -> float:
        return self._db("get_llm_usage_6h")

    def get_llm_usage_6h_by_llm(self) -> List[LLMUsage]:
        return [LLMUsage(**d) for d in self._db("get_llm_usage_6h_by_llm")]

    def get_llm_usage_with_limits(self, interval: str) -> LLMUsageLimit:
        return LLMUsageLimit(**self._db("get_llm_usage_with_limits", interval))

    def get_llm_usage_by_llm(self, interval: str) -> List[LLMUsage]:
        return [LLMUsage(**d) for d in self._db("get_llm_usage_by_llm", interval)]

    def get_scheduler_stats(self) -> SchedulerStats:
        """Count the number of global, pending jobs on the server.

        Returns:
            SchedulerStats: The queue length for number of jobs.
        """
        return SchedulerStats(**self._job(".Stats"))

    def ingest_from_file_system(
        self,
        collection_id: str,
        root_dir: str,
        glob: str,
        gen_doc_summaries: bool = False,
        gen_doc_questions: bool = False,
        timeout: Union[float, None] = None,
    ):
        """Add files from the local system into a collection.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            root_dir:
                String path of where to look for files.
            glob:
                String of the glob pattern used to match files in the root directory.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            timeout:
                Timeout in seconds
        """
        return self._wait(
            self._job(
                "crawl.IngestFromFileSystemJob",
                collection_id=collection_id,
                root_dir=root_dir,
                glob=glob,
                gen_doc_summaries=gen_doc_summaries,
                gen_doc_questions=gen_doc_questions,
            ),
            timeout=timeout,
        )

    def ingest_uploads(
        self,
        collection_id: str,
        upload_ids: Iterable[str],
        gen_doc_summaries: bool = False,
        gen_doc_questions: bool = False,
        timeout: Union[float, None] = None,
    ):
        """Add uploaded documents into a specific collection.

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            delete_upload: Delete uploaded file

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            upload_ids:
                List of string ids of each uploaded document to add to the collection.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            timeout:
                Timeout in seconds
        """
        return self._wait(
            self._job(
                "crawl.IngestUploadsJob",
                collection_id=collection_id,
                upload_ids=upload_ids,
                gen_doc_summaries=gen_doc_summaries,
                gen_doc_questions=gen_doc_questions,
            ),
            timeout=timeout,
        )

    def ingest_website(
        self,
        collection_id: str,
        url: str,
        gen_doc_summaries: bool = False,
        gen_doc_questions: bool = False,
        timeout: Union[float, None] = None,
    ):
        """Crawl and ingest a website into a collection.

        All web pages linked from this URL will be imported. External links will be ignored. Links to other
        pages on the same domain will be followed as long as they are at the same level or
        below the URL you specify. Each page will be transformed into a PDF document.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            url:
                String of the url to crawl.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            timeout:
                Timeout in seconds
        """
        return self._wait(
            self._job(
                "crawl.IngestWebsiteJob",
                collection_id=collection_id,
                url=url,
                gen_doc_summaries=gen_doc_summaries,
                gen_doc_questions=gen_doc_questions,
            ),
            timeout=timeout,
        )

    def list_chat_messages(
        self, chat_session_id: str, offset: int, limit: int
    ) -> List[ChatMessage]:
        """Fetch chat message and metadata for messages in a chat session.

        Messages without a `reply_to` are from the end user, messages with a `reply_to`
        are from an LLM and a response to a specific user message.

        Args:
            chat_session_id:
                String id of the chat session to filter by.
            offset:
                How many chat messages to skip before returning.
            limit:
                How many chat messages to return.

        Returns:
            list of ChatMessage: Text and metadata for chat messages.
        """
        return [
            ChatMessage(**{k: v for k, v in d.items() if v != [None]})
            for d in self._db("list_chat_messages", chat_session_id, offset, limit)
        ]

    def list_chat_message_references(
        self, message_id: str
    ) -> List[ChatMessageReference]:
        """Fetch metadata for references of a chat message.

        References are only available for messages sent from an LLM, an empty list will be returned
        for messages sent by the user.

        Args:
            message_id:
                String id of the message to get references for.

        Returns:
            list of ChatMessageReference: Metadata including the document name, polygon information,
            and score.
        """
        return [
            ChatMessageReference(**d)
            for d in self._db("list_chat_message_references", message_id)
        ]

    def list_list_chat_message_meta(self, message_id: str) -> List[ChatMessageMeta]:
        """Fetch chat message meta information.

        Args:
            message_id:
                Message id to which the metadata should be pulled.

        Returns:
            list of ChatMessageMeta: Metadata about the chat message.
        """
        return [
            ChatMessageMeta(**d) for d in self._db("list_chat_message_meta", message_id)
        ]

    def list_chat_message_meta_part(
        self, message_id: str, info_type: str
    ) -> ChatMessageMeta:
        """Fetch one chat message meta information.

        Args:
            message_id:
                Message id to which the metadata should be pulled.
            info_type:
                Metadata type to fetch.
                Valid choices are: "self_reflection", "usage_stats", "prompt_raw", "llm_only", "rag", "hyde1", "hyde2"

        Returns:
            ChatMessageMeta: Metadata information about the chat message.
        """
        res = self._db("list_chat_message_meta_part", message_id, info_type)
        if len(res) == 0:
            raise ObjectNotFoundError({"error": f"Chat meta type not found"})
        return ChatMessageMeta(**res[0])

    def list_chat_messages_full(
        self, chat_session_id: str, offset: int, limit: int
    ) -> List[ChatMessageFull]:
        """Fetch chat message and metadata for messages in a chat session.

        Messages without a `reply_to` are from the end user, messages with a `reply_to`
        are from an LLM and a response to a specific user message.

        Args:
            chat_session_id:
                String id of the chat session to filter by.
            offset:
                How many chat messages to skip before returning.
            limit:
                How many chat messages to return.

        Returns:
            list of ChatMessageFull: Text and metadata for chat messages.
        """
        return [
            ChatMessageFull(**{k: v for k, v in d.items() if v != [None]})
            for d in self._db("list_chat_messages_full", chat_session_id, offset, limit)
        ]

    def list_chat_sessions_for_collection(
        self, collection_id: str, offset: int, limit: int
    ) -> List[ChatSessionForCollection]:
        """Fetch chat session metadata for chat sessions in a collection.

        Args:
            collection_id:
                String id of the collection to filter by.
            offset:
                How many chat sessions to skip before returning.
            limit:
                How many chat sessions to return.

        Returns:
            list of ChatSessionForCollection: Metadata about each chat session including the
            latest message.
        """
        return [
            ChatSessionForCollection(**d)
            for d in self._db(
                "list_chat_sessions_for_collection", collection_id, offset, limit
            )
        ]

    def list_collections_for_document(
        self, document_id: str, offset: int, limit: int
    ) -> List[CollectionInfo]:
        """Fetch metadata about each collection the document is a part of.

        At this time, each document will only be available in a single collection.

        Args:
            document_id:
                String id of the document to search for.
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        return [
            CollectionInfo(**d)
            for d in self._db(
                "list_collections_for_document", document_id, offset, limit
            )
        ]

    def get_default_collection(self) -> CollectionInfo:
        """Get the default collection, to be used for collection API-keys.

        Returns:
            CollectionInfo: Default collection info.
        """
        res = self._db("get_default_collection")
        if len(res) == 0:
            raise ObjectNotFoundError(
                {
                    "error": f"Collection not found, "
                    f"or not applicable to non collection API keys"
                }
            )
        return CollectionInfo(**res[0])

    def list_documents_in_collection(
        self, collection_id: str, offset: int, limit: int
    ) -> List[DocumentInfo]:
        """Fetch document metadata for documents in a collection.

        Args:
            collection_id:
                String id of the collection to filter by.
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.

        Returns:
            list of DocumentInfo: Metadata about each document.
        """
        return [
            DocumentInfo(**d)
            for d in self._db(
                "list_documents_in_collection", collection_id, offset, limit
            )
        ]

    def list_jobs(self) -> List[Job]:
        """List the user's jobs.

        Returns:
            list of Job:
        """
        return [
            Job(**d)
            for d in self._job(".List")
            if d.get("kind", None) in JobKind.__members__
        ]

    def list_recent_chat_sessions(
        self, offset: int, limit: int
    ) -> List[ChatSessionInfo]:
        """Fetch user's chat session metadata sorted by last update time.

        Chats across all collections will be accessed.

        Args:
            offset:
                How many chat sessions to skip before returning.
            limit:
                How many chat sessions to return.

        Returns:
            list of ChatSessionInfo: Metadata about each chat session including the
            latest message.
        """
        return [
            ChatSessionInfo(**d)
            for d in self._db("list_recent_chat_sessions", offset, limit)
        ]

    def list_question_reply_feedback_data(
        self, offset: int, limit: int
    ) -> List[QuestionReplyData]:
        """Fetch user's questions and answers that have a feedback.

        Questions and answers with metadata and feedback information.

        Args:
            offset:
                How many conversations to skip before returning.
            limit:
                How many conversations to return.

        Returns:
            list of QuestionReplyData: Metadata about questions and answers.
        """
        return [
            QuestionReplyData(**d)
            for d in self._db("list_question_reply_feedback_data", offset, limit)
        ]

    def count_question_reply_feedback(self) -> int:
        """Fetch user's questions and answers with feedback count.

        Returns:
            int: the count of questions and replies that have a user feedback.
        """
        return QuestionReplyDataCount(
            **self._db("count_question_reply_feedback")
        ).question_reply_data_count

    def list_recent_collections(self, offset: int, limit: int) -> List[CollectionInfo]:
        """Fetch user's collection metadata sorted by last update time.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        return [
            CollectionInfo(**d)
            for d in self._db("list_recent_collections", offset, limit)
        ]

    def list_recent_collections_sort(
        self, offset: int, limit: int, sort_column: str, ascending: bool
    ) -> List[CollectionInfo]:
        """Fetch user's collection metadata sorted by last update time.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        return [
            CollectionInfo(**d)
            for d in self._db(
                "list_recent_collections_sort", offset, limit, sort_column, ascending
            )
        ]

    def list_collection_permissions(self, collection_id: str) -> List[Permission]:
        """Returns a list of access permissions for a given collection.

        The returned list of permissions denotes who has access to
        the collection and their access level.

        Args:
            collection_id:
                ID of the collection to inspect.

        Returns:
            list of Permission: Sharing permissions list for the given collection.
        """
        return [
            Permission(**d)
            for d in self._db("list_collection_permissions", collection_id)
        ]

    def list_users(self, offset: int, limit: int) -> List[User]:
        """List system users.

        Returns a list of all registered users fo the system, a registered user,
        is a users that has logged in at least once.

        Args:
            offset:
                How many users to skip before returning.
            limit:
                How many users to return.

        Returns:
            list of User: Metadata about each user.
        """
        return [User(**d) for d in self._db("list_users", offset, limit)]

    def share_collection(
        self, collection_id: str, permission: Permission
    ) -> ShareResponseStatus:
        """Share a collection to a user.

        The permission attribute defined the level of access,
        and who can access the collection, the collection_id attribute
        denotes the collection to be shared.

        Args:
            collection_id:
                ID of the collection to share.
            permission:
                Defines the rule for sharing, i.e. permission level.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        return ShareResponseStatus(
            **self._db("share_collection", collection_id, permission.username)
        )

    def unshare_collection(
        self, collection_id: str, permission: Permission
    ) -> ShareResponseStatus:
        """Remove sharing of a collection to a user.

        The permission attribute defined the level of access,
        and who can access the collection, the collection_id attribute
        denotes the collection to be shared.
        In case of un-sharing, the Permission's user is sufficient

        Args:
            collection_id:
                ID of the collection to un-share.
            permission:
                Defines the user for which collection access is revoked.

        ShareResponseStatus: Status of share request.
        """
        return ShareResponseStatus(
            **self._db("unshare_collection", collection_id, permission.username)
        )

    def unshare_collection_for_all(self, collection_id: str) -> ShareResponseStatus:
        """Remove sharing of a collection to all other users but the original owner

        Args:
            collection_id:
                ID of the collection to un-share.

        ShareResponseStatus: Status of share request.
        """
        return ShareResponseStatus(
            **self._db("unshare_collection_for_all", collection_id)
        )

    def make_collection_public(self, collection_id: str):
        """Make a collection public

        Once a collection is public, it will be accessible to all
        authenticated users of the system.

        Args:
            collection_id:
                ID of the collection to make public.
        """
        self._db("make_collection_public", collection_id)

    def make_collection_private(self, collection_id: str):
        """Make a collection private

        Once a collection is private, other users will no longer
        be able to access chat history or documents related to
        the collection.

        Args:
            collection_id:
                ID of the collection to make private.
        """
        self._db("make_collection_private", collection_id)

    def list_recent_documents(self, offset: int, limit: int) -> List[DocumentInfo]:
        """Fetch user's document metadata sorted by last update time.

        All documents owned by the user, regardless of collection, are accessed.

        Args:
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.

        Returns:
            list of DocumentInfo: Metadata about each document.
        """
        return [
            DocumentInfo(**d) for d in self._db("list_recent_documents", offset, limit)
        ]

    def list_recent_documents_with_summaries(
        self, offset: int, limit: int
    ) -> List[DocumentInfoSummary]:
        """Fetch user's document metadata sorted by last update time, including the latest document summary.

        All documents owned by the user, regardless of collection, are accessed.

        Args:
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.

        Returns:
            list of DocumentInfoSummary: Metadata about each document.
        """
        return [
            DocumentInfoSummary(**d)
            for d in self._db("list_recent_documents_with_summaries", offset, limit)
        ]

    def list_recent_documents_with_summaries_sort(
        self, offset: int, limit: int, sort_column: str, ascending: bool
    ) -> List[DocumentInfoSummary]:
        """Fetch user's document metadata sorted by last update time, including the latest document summary.

        All documents owned by the user, regardless of collection, are accessed.

        Args:
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.

        Returns:
            list of DocumentInfoSummary: Metadata about each document.
        """
        return [
            DocumentInfoSummary(**d)
            for d in self._db(
                "list_recent_documents_with_summaries_sort",
                offset,
                limit,
                sort_column,
                ascending,
            )
        ]

    def match_chunks(
        self,
        collection_id: str,
        vectors: List[List[float]],
        topics: List[str],
        offset: int,
        limit: int,
        cut_off: float = 0,
        width: int = 0,
    ) -> List[SearchResult]:
        """Find chunks related to a message using semantic search.

        Chunks are sorted by relevance and similarity score to the message.

        See Also: H2OGPTE.encode_for_retrieval to create vectors from messages.

        Args:
            collection_id:
                ID of the collection to search within.
            vectors:
                A list of vectorized message for running semantic search.
            topics:
                A list of document_ids used to filter which documents in the collection to search.
            offset:
                How many chunks to skip before returning chunks.
            limit:
                How many chunks to return.
            cut_off:
                Exclude matches with distances higher than this cut off.
            width:
                How many chunks before and after a match to return - not implemented.

        Returns:
            list of SearchResult: The document, text, score and related information of the chunk.
        """
        res = self._vex(
            "match_chunks",
            collection_id,
            vectors=vectors,
            topics=topics,
            offset=offset,
            limit=limit,
            cut_off=cut_off,
            width=width,
        )
        return SearchResults(**res).result

    def search_chunks(
        self, collection_id: str, query: str, topics: List[str], offset: int, limit: int
    ) -> List[SearchResult]:
        """Find chunks related to a message using lexical search.

        Chunks are sorted by relevance and similarity score to the message.

        Args:
            collection_id:
                ID of the collection to search within.
            query:
                Question or imperative from the end user to search a collection for.
            topics:
                A list of document_ids used to filter which documents in the collection to search.
            offset:
                How many chunks to skip before returning chunks.
            limit:
                How many chunks to return.

        Returns:
            list of SearchResult: The document, text, score and related information of the chunk.
        """
        res = self._vex(
            "search_chunks",
            collection_id,
            query=query,
            topics=topics,
            offset=offset,
            limit=limit,
        )
        return SearchResults(**res).result

    def set_chat_message_votes(self, chat_message_id: str, votes: int) -> Result:
        """Change the vote value of a chat message.

        Set the exact value of a vote for a chat message. Any message type can
        be updated, but only LLM response votes will be visible in the UI.
        The expectation is 0: unvoted, -1: dislike, 1 like. Values outside of this will
        not be viewable in the UI.

        Args:
            chat_message_id:
                ID of a chat message, any message can be used but only
                LLM responses will be visible in the UI.
            votes:
                Integer value for the message. Only -1 and 1 will be visible in the
                UI as dislike and like respectively.

        Returns:
            Result: The status of the update.

        Raises:
            Exception: The upload request was unsuccessful.
        """
        return Result(**self._db("set_chat_message_votes", chat_message_id, votes))

    def update_collection(self, collection_id: str, name: str, description: str) -> str:
        """Update the metadata for a given collection.

        All variables are required. You can use `h2ogpte.get_collection(<id>).name` or
        description to get the existing values if you only want to change one or the other.

        Args:
            collection_id:
                ID of the collection to update.
            name:
                New name of the collection, this is required.
            description:
                New description of the collection, this is required.

        Returns:
            str: ID of the updated collection.
        """
        return _to_id(self._db("update_collection", collection_id, name, description))

    def update_collection_rag_type(
        self, collection_id: str, name: str, description: str, rag_type: str
    ) -> str:
        """Update the metadata for a given collection.

        All variables are required. You can use `h2ogpte.get_collection(<id>).name` or
        description to get the existing values if you only want to change one or the other.

        Args:
            collection_id:
                ID of the collection to update.
            name:
                New name of the collection, this is required.
            description:
                New description of the collection, this is required.
            rag_type: str one of

                    :code:`"llm_only"` LLM Only (no RAG) - Generates a response to answer the user's query without any supporting document contexts.

                    :code:`"rag"` RAG (Retrieval Augmented Generation) - RAG with neural/lexical hybrid search using the user's query to find contexts from a collection for generating a response.

                    :code:`"hyde1"` HyDE RAG (Hypothetical Document Embedding) - RAG with neural/lexical hybrid search using the user's query and the LLM response to find contexts from a collection for generating a response. Requires 2 LLM calls.

                    :code:`"hyde2"` HyDE RAG+ (Combined HyDE+RAG) - RAG with neural/lexical hybrid search using the user's query and the HyDE RAG response to find contexts from a collection for generating a response. Requires 3 LLM calls.

        Returns:
            str: ID of the updated collection.
        """
        return _to_id(
            self._db(
                "update_collection_rag_type", collection_id, name, description, rag_type
            )
        )

    def reset_collection_prompt_settings(
        self,
        collection_id: str,
    ) -> str:
        """Reset the prompt settings for a given collection.

        Args:
            collection_id:
                ID of the collection to update.

        Returns:
            str: ID of the updated collection.
        """
        return _to_id(
            self._db(
                "reset_collection_prompt_settings",
                collection_id,
            )
        )

    def upload(self, file_name: str, file: Any) -> str:
        """Upload a file to the H2OGPTE backend.

        Uploaded files are not yet accessible and need to be ingested into a collection.

        See Also:
            ingest_uploads: Add the uploaded files to a collection.
            delete_upload: Delete uploaded file

        Args:
            file_name:
                What to name the file on the server, must include file extension.
            file:
                File object to upload, often an opened file from `with open(...) as f`.

        Returns:
            str: The upload id to be used in ingest jobs.

        Raises:
            Exception: The upload request was unsuccessful.
        """
        res = requests.put(
            f"{self._address}/rpc/fs",
            headers=self._get_auth_header(),
            files=dict(file=(file_name, file)),
            verify=self._verify,
        )
        if res.status_code != 200:
            raise Exception(f"HTTP error: {res.status_code} {res.reason}")
        return _to_id(unmarshal(res.text))

    def list_upload(self) -> List[str]:
        """List pending file uploads to the H2OGPTE backend.

        Uploaded files are not yet accessible and need to be ingested into a collection.

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            ingest_uploads: Add the uploaded files to a collection.
            delete_upload: Delete uploaded file

        Returns:
            List[str]: The pending upload ids to be used in ingest jobs.

        Raises:
            Exception: The upload list request was unsuccessful.
        """
        res = requests.get(
            f"{self._address}/rpc/fs",
            headers=self._get_auth_header(),
            verify=self._verify,
        )
        if res.status_code != 200:
            raise Exception(f"HTTP error: {res.status_code} {res.reason}")
        return unmarshal(res.text)

    def delete_upload(self, upload_id: str) -> str:
        """Delete a file previously uploaded with the "upload" method.

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            ingest_uploads: Add the uploaded files to a collection.

        Args:
            upload_id:
                ID of a file to remove

        Returns:
            upload_id: The upload id of the removed.

        Raises:
            Exception: The delete upload request was unsuccessful.
        """
        res = requests.delete(
            f"{self._address}/rpc/fs?id={upload_id}",
            headers=self._get_auth_header(),
            verify=self._verify,
        )
        if res.status_code != 200:
            raise Exception(f"HTTP error: {res.status_code} {res.reason}")
        return _to_id(unmarshal(res.text))

    def connect(self, chat_session_id: str) -> Session:
        """Create and participate in a chat session.

        This is a live connection to the H2OGPTE server contained to a specific
        chat session on top of a single collection of documents. Users will find all
        questions and responses in this session in a single chat history in the
        UI.

        Args:
            chat_session_id:
                ID of the chat session to connect to.

        Returns:
            Session: Live chat session connection with an LLM.

        """
        return Session(
            self._address,
            client=self,
            chat_session_id=chat_session_id,
        )

    def get_llms(self) -> List[dict]:
        """Lists metadata information about available LLMs in the environment.

        Returns:
            list of dict (string, ANY): Name and details about each available model.

        """
        return self._lang("get_llms")

    def get_llm_names(self) -> List[str]:
        """Lists names of available LLMs in the environment.

        Returns:
            list of string: Name of each available model.

        """
        return self._lang("get_llm_names")

    def download_document(
        self, destination_directory: str, destination_file_name: str, document_id: str
    ) -> Path:
        """Downloads a document to a local system directory.

        Args:
            destination_directory:
                Destination directory to save file into.
            destination_file_name:
                Destination file name.
            document_id:
                Document ID.

        Returns:
            Path: Path of downloaded document

        """
        if not os.path.exists(destination_directory) or not os.path.isdir(
            destination_directory
        ):
            raise FileNotFoundError("Destination directory does not exist")

        destination_directory = Path(destination_directory)
        destination_file = destination_directory / destination_file_name
        if os.path.exists(destination_file) and os.path.isfile(destination_file):
            raise FileExistsError(f"File {destination_file} already exists")

        res = requests.get(
            f"{self._address}/file?id={document_id}&name={destination_file_name}",
            headers=self._get_auth_header(),
            verify=self._verify,
        )
        if res.status_code != requests.codes.ok:
            raise FileNotFoundError(
                f"Failed to download the document, error: {res.status_code}"
            )

        with open(destination_file, "wb") as f:
            f.write(res.content)

        return destination_file

    def list_recent_prompt_templates(
        self, offset: int, limit: int
    ) -> List[PromptTemplate]:
        """Fetch user's prompt templates sorted by last update time.

        Args:
            offset:
                How many prompt templates to skip before returning.
            limit:
                How many prompt templates to return.

        Returns:
            list of PromptTemplate: set of prompts
        """
        return [
            PromptTemplate(**d)
            for d in self._db("list_recent_prompt_templates", offset, limit)
        ]

    def list_recent_prompt_templates_sort(
        self, offset: int, limit: int, sort_column: str, ascending: bool
    ) -> List[PromptTemplate]:
        """Fetch user's prompt templates sorted by last update time.

        Args:
            offset:
                How many prompt templates to skip before returning.
            limit:
                How many prompt templates to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.

        Returns:
            list of PromptTemplate: set of prompts
        """
        return [
            PromptTemplate(**d)
            for d in self._db(
                "list_recent_prompt_templates_sort",
                offset,
                limit,
                sort_column,
                ascending,
            )
        ]

    def get_prompt_template(self, id: Optional[str] = None) -> PromptTemplate:
        """Get a prompt template

        Args:
            id:
                String id of the prompt template to retrieve or None for default

        Returns:
            PromptTemplate: prompts

        Raises:
            KeyError: The prompt template was not found.
        """
        if id is None:
            return PromptTemplate(**self._lang("get_default_prompt_template"))
        res = self._db("get_prompt_template", id)
        if len(res) == 0:
            raise ObjectNotFoundError({"error": f"Prompt Template {id} not found"})
        return PromptTemplate(**res[0])

    def delete_prompt_templates(self, ids: Iterable[str]) -> Result:
        """Deletes prompt templates

        Args:
            ids:
                List of string ids of prompte templates to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        res = self._db("delete_prompt_templates", ids)
        return Result(**res)

    def update_prompt_template(
        self,
        id: str,
        name: str,
        description: Union[str, None] = None,
        lang: Union[str, None] = None,
        system_prompt: Union[str, None] = None,
        pre_prompt_query: Union[str, None] = None,
        prompt_query: Union[str, None] = None,
        hyde_no_rag_llm_prompt_extension: Union[str, None] = None,
        pre_prompt_summary: Union[str, None] = None,
        prompt_summary: Union[str, None] = None,
        system_prompt_reflection: Union[str, None] = None,
        pre_prompt_reflection: Union[str, None] = None,
        prompt_reflection: Union[str, None] = None,
        auto_gen_description_prompt: Union[str, None] = None,
        auto_gen_document_summary_pre_prompt_summary: Union[str, None] = None,
        auto_gen_document_summary_prompt_summary: Union[str, None] = None,
        auto_gen_document_sample_questions_prompt: Union[str, None] = None,
        default_sample_questions: Union[List[str], None] = None,
    ) -> str:
        """
        Update a prompt template

        Args:
            id:
                String ID of the prompt template to update
            name:
                Name of the prompt template
            description:
                Description of the prompt template
            lang:
                Language code
            system_prompt:
                System Prompt
            pre_prompt_query:
                Text that is prepended before the contextual document chunks.
            prompt_query:
                Text that is appended to the beginning of the user's message.
            hyde_no_rag_llm_prompt_extension:
                LLM prompt extension.
            pre_prompt_summary:
                Prompt that goes before each large piece of text to summarize
            prompt_summary:
                Prompt that goes after each large piece of of text to summarize
            system_prompt_reflection:
                System Prompt for self-reflection
            pre_prompt_reflection:
                Text that is prepended before the self-reflection context
            prompt_reflection:
                Text that is appended to the self-reflection context
            auto_gen_description_prompt:
                prompt to create a description of the collection.
            auto_gen_document_summary_pre_prompt_summary:
                pre_prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_summary_prompt_summary:
                prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_sample_questions_prompt:
                prompt to create sample questions for a freshly imported document (if enabled).
            default_sample_questions:
                default sample questions in case there are no auto-generated sample questions.

        Returns:
            str: The ID of the updated prompt template.
        """
        if prompt_reflection is not None:
            assert prompt_reflection.count("%s") == 2, (
                "prompt reflection must contain exactly two occurrences of %s "
                "(one for the pre_prompt_query+context+prompt_query+question and one for response)"
            )
        return _to_id(
            self._db(
                "update_prompt_template",
                id,
                name,
                description,
                lang,
                system_prompt,
                pre_prompt_query,
                prompt_query,
                hyde_no_rag_llm_prompt_extension,
                pre_prompt_summary,
                prompt_summary,
                system_prompt_reflection,
                pre_prompt_reflection,
                prompt_reflection,
                auto_gen_description_prompt,
                auto_gen_document_summary_pre_prompt_summary,
                auto_gen_document_summary_prompt_summary,
                auto_gen_document_sample_questions_prompt,
                default_sample_questions,
            )
        )

    def create_prompt_template(
        self,
        name: str,
        description: Union[str, None] = None,
        lang: Union[str, None] = None,
        system_prompt: Union[str, None] = None,
        pre_prompt_query: Union[str, None] = None,
        prompt_query: Union[str, None] = None,
        hyde_no_rag_llm_prompt_extension: Union[str, None] = None,
        pre_prompt_summary: Union[str, None] = None,
        prompt_summary: Union[str, None] = None,
        system_prompt_reflection: Union[str, None] = None,
        pre_prompt_reflection: Union[str, None] = None,
        prompt_reflection: Union[str, None] = None,
        auto_gen_description_prompt: Union[str, None] = None,
        auto_gen_document_summary_pre_prompt_summary: Union[str, None] = None,
        auto_gen_document_summary_prompt_summary: Union[str, None] = None,
        auto_gen_document_sample_questions_prompt: Union[str, None] = None,
        default_sample_questions: Union[List[str], None] = None,
    ) -> str:
        """
        Create a new prompt template

        Args:
            name:
                Name of the prompt template
            description:
                Description of the prompt template
            lang:
                Language code
            system_prompt:
                System Prompt
            pre_prompt_query:
                Text that is prepended before the contextual document chunks.
            prompt_query:
                Text that is appended to the beginning of the user's message.
            hyde_no_rag_llm_prompt_extension:
                LLM prompt extension.
            pre_prompt_summary:
                Prompt that goes before each large piece of text to summarize
            prompt_summary:
                Prompt that goes after each large piece of of text to summarize
            system_prompt_reflection:
                System Prompt for self-reflection
            pre_prompt_reflection:
                Text that is prepended before the self-reflection context
            prompt_reflection:
                Text that is appended to the self-reflection context
            auto_gen_description_prompt:
                prompt to create a description of the collection.
            auto_gen_document_summary_pre_prompt_summary:
                pre_prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_summary_prompt_summary:
                prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_sample_questions_prompt:
                prompt to create sample questions for a freshly imported document (if enabled).
            default_sample_questions:
                default sample questions in case there are no auto-generated sample questions.

        Returns:
            str: The ID of the newly created prompt template.
        """
        if prompt_reflection is not None:
            assert prompt_reflection.count("%s") == 2, (
                "prompt reflection must contain exactly two occurrences of %s "
                "(one for the pre_prompt_query+context+prompt_query+question and one for response)"
            )
        return _to_id(
            self._db(
                "create_prompt_template",
                name,
                description,
                lang,
                system_prompt,
                pre_prompt_query,
                prompt_query,
                hyde_no_rag_llm_prompt_extension,
                pre_prompt_summary,
                prompt_summary,
                system_prompt_reflection,
                pre_prompt_reflection,
                prompt_reflection,
                auto_gen_description_prompt,
                auto_gen_document_summary_pre_prompt_summary,
                auto_gen_document_summary_prompt_summary,
                auto_gen_document_sample_questions_prompt,
                default_sample_questions,
            )
        )

    def count_prompt_templates(self) -> int:
        """Counts number of prompt templates

        Returns:
            int: The count of prompt templates
        """
        return PromptTemplateCount(
            **self._db("count_prompt_templates")
        ).prompt_template_count

    def set_collection_prompt_template(
        self,
        collection_id: str,
        prompt_template_id: Union[str, None],
        strict_check: bool = False,
    ) -> str:
        """Set the prompt template for a collection

        Args:
            collection_id:
                ID of the collection to update.
            prompt_template_id:
                ID of the prompt template to get the prompts from. None to delete and fall back to system defaults.
            strict_check:
                whether to check that the collection's embedding model and the prompt template are optimally compatible

        Returns:
            str: ID of the updated collection.
        """
        if prompt_template_id is None:
            res = self._db("reset_collection_prompt_template", collection_id)
        else:
            prompt_template = self.get_prompt_template(prompt_template_id)
            embedding_model = self.get_collection(collection_id).embedding_model
            if embedding_model:
                emb_dict = self._lang("get_embedding_models_dict")
                if embedding_model in emb_dict:
                    langs = emb_dict[embedding_model]["languages"]
                    if (
                        langs
                        and prompt_template.lang
                        and prompt_template.lang not in langs
                    ):
                        msg = (
                            f"Warning: The embedding model only supports the following languages: {langs}, "
                            f"but the prompt template specifies the following language: {prompt_template.lang}. "
                            f"Retrieval performance may not be ideal."
                        )
                        print(msg)
                        if strict_check:
                            raise RuntimeError(msg)
            res = self._db(
                "set_collection_prompt_template",
                collection_id,
                prompt_template_id,
            )
        return _to_id(res)

    def get_collection_prompt_template(
        self, collection_id: str
    ) -> Union[PromptTemplate, None]:
        """Get the prompt template for a collection

        Args:
            collection_id:
                ID of the collection

        Returns:
            str: ID of the prompt template.
        """
        res = self._db(
            "get_collection_prompt_template",
            collection_id,
        )
        if len(res) == 0:
            raise ObjectNotFoundError(
                {"error": f"Collection {collection_id} not found"}
            )
        prompt_template_id = res[0]["prompt_template_id"]
        if prompt_template_id is None:
            return None
        res = self._db("get_prompt_template", prompt_template_id)
        if len(res) == 0:
            raise ObjectNotFoundError(
                {"error": f"Prompt Template {prompt_template_id} not found"}
            )
        return PromptTemplate(**res[0])

    def set_chat_session_prompt_template(
        self, chat_session_id: str, prompt_template_id: Union[str, None]
    ) -> str:
        """Get the prompt template for a chat_session

        Args:
            chat_session_id:
                ID of the chat session
            prompt_template_id:
                ID of the prompt template to get the prompts from. None to delete and fall back to system defaults.

        Returns:
            str: ID of the updated chat session
        """
        if prompt_template_id is None:
            res = self._db("reset_chat_session_prompt_template", prompt_template_id)
        else:
            res = self._db(
                "set_chat_session_prompt_template",
                chat_session_id,
                prompt_template_id,
            )
        return _to_id(res)

    def get_chat_session_prompt_template(
        self, chat_session_id: str
    ) -> Union[PromptTemplate, None]:
        """Get the prompt template for a chat_session

        Args:
            chat_session_id:
                ID of the chat session

        Returns:
            str: ID of the prompt template.
        """
        res = self._db(
            "get_chat_session_prompt_template",
            chat_session_id,
        )
        if len(res) == 0:
            raise ObjectNotFoundError(
                {"error": f"Chat session {chat_session_id} not found"}
            )
        prompt_template_id = res[0]["prompt_template_id"]
        if prompt_template_id is None:
            return None
        res = self._db("get_prompt_template", prompt_template_id)
        if len(res) == 0:
            raise ObjectNotFoundError(
                {"error": f"Prompt Template {prompt_template_id} not found"}
            )
        return PromptTemplate(**res[0])


def _to_id(data: Dict[str, Any]) -> str:
    if data is not None and isinstance(data, dict) and data.get("error", ""):
        raise ValueError(data.get("error", ""))
    return Identifier(**data).id


def marshal(d):
    return json.dumps(d, allow_nan=False, separators=(",", ":"))


def unmarshal(s: str):
    return json.loads(s)

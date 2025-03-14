import os
import openai
from typing import List, AsyncIterator, Iterator, Optional
from backend.api.chat.chat_model_base import BaseChatModel
from backend.api.chat.models import OpsLoomMessageChunk

class OpenAIChatModel(BaseChatModel):
    def __init__(self, model: str = "gpt-4", temperature: float = 0.7, api_key: Optional[str] = None):
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in the OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key

    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for the given query using OpenAI's API.
        """
        response = openai.embeddings.create(input=query, model="text-embedding-3-large")
     
        return response.data[0].embedding

    def _format_messages(self, messages: List[str]) -> List[dict]:
        """
        Convert a list of raw message strings into the OpenAI ChatCompletion
        expected format. Here we treat every message as a 'user' message.
        Modify as needed if you want system or assistant roles.
        """
        return [{"role": "user", "content": m} for m in messages]

    def invoke(self, messages: List[str]) -> OpsLoomMessageChunk:
        """
        Synchronously send messages to the model and return the entire response.
        """
        formatted_messages = self._format_messages(messages)
        response =  openai.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=self.temperature,
            stream=False
        )
        # The first choice is generally the primary response
        message = response["choices"][0]["message"]
        return OpsLoomMessageChunk(
            content=message.get("content", ""),
            type="text",
            id=response.get("id", ""),
            additional_kwargs={"finish_reason": response["choices"][0].get("finish_reason")},
            response_metadata=response
        )

    def stream(self, messages: List[str]) -> Iterator[OpsLoomMessageChunk]:
        """
        Synchronously stream a response from the model, yielding chunks as they arrive.
        """
        formatted_messages = self._format_messages(messages)
        response =  openai.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=self.temperature,
            stream=True
        )
        # The response is a generator that yields partial chunks.
        for chunk in response:
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            yield OpsLoomMessageChunk(
                content=content,
                type="text",
                id=chunk.get("id", ""),
                additional_kwargs={"finish_reason": chunk["choices"][0].get("finish_reason")},
                response_metadata=chunk
            )

    async def ainvoke(self, messages: List[str]) -> OpsLoomMessageChunk:
        """
        Asynchronously send messages to the model and return the entire response.
        """
        formatted_messages = self._format_messages(messages)
        response = await openai.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=self.temperature,
            stream=False
        )
        message = response["choices"][0]["message"]
        return OpsLoomMessageChunk(
            content=message.get("content", ""),
            type="text",
            id=response.get("id", ""),
            additional_kwargs={"finish_reason": response["choices"][0].get("finish_reason")},
            response_metadata=response
        )

    async def astream(self, messages: List[str]) -> AsyncIterator[OpsLoomMessageChunk]:
        """
        Asynchronously stream the model's response, yielding partial chunks.
        """
        formatted_messages = self._format_messages(messages)
        # Use 'create' with stream=True for async streaming
        response = openai.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=self.temperature,
            stream=True
        )
        for chunk in response:
            # chunk is a ChatCompletionChunk object
            choice = chunk.choices[0]
            delta = choice.delta
            # finish_reason = choice.finish_reason

            if delta and delta.content:
                content = delta.content
            else:
                content = ""

            yield OpsLoomMessageChunk(
                content=content,
                type="text",
                id=chunk.id,  
            )

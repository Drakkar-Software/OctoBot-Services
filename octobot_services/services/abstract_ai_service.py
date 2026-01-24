#  Drakkar-Software OctoBot-Services
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import abc
import typing


class AbstractAIService(abc.ABC):    
    BACKTESTING_ENABLED = True
    DEFAULT_MODEL: typing.Optional[str] = None
    DEFAULT_MAX_TOKENS: int = 10000
    DEFAULT_TEMPERATURE: float = 0.5
    
    def __init__(self):
        self.model = self.DEFAULT_MODEL
        self.models: list[str] = []

    @abc.abstractmethod
    async def get_completion(
        self,
        messages: list,
        model: typing.Optional[str] = None,
        max_tokens: int = 10000,
        n: int = 1,
        stop: typing.Optional[typing.Union[str, list]] = None,
        temperature: float = 0.5,
        json_output: bool = False,
        response_schema: typing.Optional[typing.Any] = None,
    ) -> typing.Optional[str]:
        """
        Get a completion from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model to use (defaults to service's default model).
            max_tokens: Maximum tokens in the response.
            n: Number of completions to generate.
            stop: Stop sequences.
            temperature: Sampling temperature (0-2).
            json_output: Whether to return JSON formatted output.
            response_schema: Optional Pydantic model or JSON schema dict 
                           for structured output validation.
        
        Returns:
            The completion text, or None if an error occurred.
        
        Raises:
            InvalidRequestError: If the request is malformed.
            RateLimitError: If rate limits are exceeded.
        """
        raise NotImplementedError("get_completion not implemented")
    
    @staticmethod
    @abc.abstractmethod
    def create_message(
        role: str, 
        content: str, 
        model: typing.Optional[str] = None
    ) -> dict:
        """
        Create a message dict for the LLM.
        
        Some models don't support certain roles (e.g., 'system'),
        so this method allows implementations to handle that.
        
        Args:
            role: The message role ('system', 'user', 'assistant').
            content: The message content.
            model: Optional model name to handle model-specific restrictions.
        
        Returns:
            A dict with 'role' and 'content' keys.
        """
        raise NotImplementedError("create_message not implemented")
    
    def get_model(self) -> str:
        return self.model
    
    def get_available_models(self) -> list:
        return self.models

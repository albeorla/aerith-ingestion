import json
import os
import random
import re
import time
from typing import Any, Dict, List, Optional

import backoff
import google.generativeai as genai
import requests
from backoff_config import BackoffConfig
from google.api_core import exceptions
from interfaces import EnvironmentConfigProtocol, GeminiServiceProtocol, LoggerProtocol
from monitoring import MonitoringDashboard
from prompt_templates import (
    GTD_LEVEL_DEFINITIONS,
    get_content_processing_prompt,
    get_function_call_prompt,
    get_task_categorization_prompt,
    get_task_organization_prompt,
    get_task_prioritization_prompt,
    parse_gemini_json_response,
)
from request_manager import Request, RequestBatch, RequestManager, RequestPriority

# TODO: Implement request batching and merging
# TODO: Add input validation and sanitization
# TODO: Add token counting and length limits
# TODO: Implement result caching and reuse
# TODO: Add request/response logging


class GeminiService(GeminiServiceProtocol):
    """Service to interact with the Gemini API for advanced GTD processing."""

    def __init__(
        self,
        env_config: EnvironmentConfigProtocol,
        rate_limiter=None,
        error_handler=None,
        request_manager: Optional[RequestManager[Dict[str, Any], str]] = None,
        monitor: MonitoringDashboard = None,
    ):
        """
        Initialize the GeminiService with the provided environment configuration.

        Args:
            env_config: An object implementing the EnvironmentConfigProtocol.
            rate_limiter: An object implementing the RateLimiterProtocol.
            error_handler: An object implementing the ErrorHandlerProtocol.
            request_manager: An object implementing the RequestManagerProtocol.
            monitor: An instance of the MonitoringDashboard for monitoring purposes.
        """
        # TODO: Add configuration for:
        # - Maximum input length
        # - Content type validation rules
        # - Batch size limits
        # - Cache configuration
        # - Logging levels
        self.logger: LoggerProtocol = env_config.get_logger()
        self.api_key = env_config.get_google_api_key()
        if not self.api_key:
            self.logger.error("Google API key is not set in the environment.")
            raise ValueError("Google API key is not set in the environment.")

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Retrieve the model name and generation configuration from the environment config
        self.model_name = env_config.get_gemini_model_name()
        self.generation_config = env_config.get_gemini_generation_config()
        self.safety_settings = env_config.get_gemini_safety_settings()
        self.logger.info(f"GeminiService initialized with model: {self.model_name}")

        # NEW: store the request_manager for concurrency/caching/dedup
        self.request_manager = request_manager
        self.monitor = monitor or MonitoringDashboard()

        # Initialize Gemini configuration and client here in __init__
        self._configure_gemini()  # Call the configuration method here

    def _configure_gemini(self):
        """
        Internal method to configure Gemini API client using environment variables.
        This method is called during initialization to set up the Gemini API client.
        """
        api_key = self.api_key
        if not api_key:
            self.logger.error("Google API key is not set in the environment.")
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")
        genai.configure(api_key=api_key)  # configure at service init

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        )
        self.logger.info(f"Gemini model configured: {self.model_name}")

    def _preprocess_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Preprocesses Gemini's raw text output to ensure it's valid JSON.

        Args:
            response_text: The raw text response from the Gemini API.

        Returns:
            A dictionary parsed from the JSON response, or None if parsing fails.
        """
        # Use the updated parsing function
        return parse_gemini_json_response(response_text)

    @BackoffConfig.exponential_backoff()
    async def _direct_generate_text(
        self, prompt: str, **generation_params
    ) -> Optional[str]:
        """
        Directly calls the Gemini API to generate text. Used when request
        manager is not available, or for bypass operations.
        """
        start_time = time.monotonic()  # Start timing
        try:
            response = self.model.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(**generation_params),
            )
            response.resolve()  # Ensure the response is fully resolved
            latency = time.monotonic() - start_time  # Calculate latency
            if self.monitor:
                self.monitor.update_processing_time(
                    "gemini_service", latency
                )  # Log latency
            return response.text
        except exceptions.GoogleAPIError as e:
            error_message = f"Gemini API error: {e.message}"
            if self.error_handler:
                context = self.error_handler.create_context(
                    service="gemini_service",
                    operation="generate_text",
                    details={"prompt": prompt, "generation_params": generation_params},
                )
                await self.error_handler.handle_api_error(
                    e, context, message=error_message
                )
            self.logger.error(error_message)
            return None
        except Exception as e:
            error_message = f"Unexpected error in Gemini API call: {e}"
            if self.error_handler:
                context = self.error_handler.create_context(
                    service="gemini_service",
                    operation="generate_text",
                    details={"prompt": prompt, "generation_params": generation_params},
                )
                await self.error_handler.handle_exception(
                    e, context, message=error_message
                )
            self.logger.error(error_message)
            return None

    @BackoffConfig.exponential_backoff()
    async def _generate_text_with_backoff(
        self, prompt: str, **generation_params
    ) -> Optional[str]:
        """
        Generates text using Gemini API with exponential backoff for resilience.
        """
        start_time = time.monotonic()  # Start timing
        try:
            response = self.model.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(**generation_params),
            )
            response.resolve()  # Ensure the response is fully resolved
            latency = time.monotonic() - start_time  # Calculate latency
            if self.monitor:
                self.monitor.update_processing_time(
                    "gemini_service", latency
                )  # Log latency
            return response.text
        except exceptions.GoogleAPIError as e:
            error_message = f"Gemini API error with backoff: {e.message}"
            if self.error_handler:
                context = self.error_handler.create_context(
                    service="gemini_service",
                    operation="generate_text_with_backoff",
                    details={"prompt": prompt, "generation_params": generation_params},
                )
                await self.error_handler.handle_api_error(
                    e, context, message=error_message
                )
            self.logger.error(error_message)
            raise  # Re-raise for backoff to handle
        except Exception as e:
            error_message = f"Unexpected error during Gemini API call with backoff: {e}"
            if self.error_handler:
                context = self.error_handler.create_context(
                    service="gemini_service",
                    operation="generate_text_with_backoff",
                    details={"prompt": prompt, "generation_params": generation_params},
                )
                await self.error_handler.handle_exception(
                    e, context, message=error_message
                )
            self.logger.error(error_message)
            return None

    async def generate_text(self, prompt: str, **generation_params) -> Optional[str]:
        """
        Public interface to generate text, using request manager if available,
        otherwise calls _direct_generate_text.
        """
        if not self.request_manager:
            return await self._direct_generate_text(prompt, **generation_params)

        req_payload = {
            "method": "generate_text",
            "prompt": prompt,
            "generation_params": generation_params,
        }
        request = Request(payload=req_payload, priority=RequestPriority.MEDIUM)
        # Assuming request_manager.submit_request is adapted to handle different return types
        raw_result = await self.request_manager.submit_request(request)
        return raw_result or None  # Adjust based on actual return type from manager

    async def _direct_categorize_gtd_level(
        self, task_content: str, temperature: float = 0.2, max_output_tokens: int = 256
    ) -> Optional[str]:
        """
        Directly categorize GTD level using Gemini API. Bypasses request manager.
        """
        prompt = get_task_categorization_prompt(task_content, GTD_LEVEL_DEFINITIONS)
        try:
            response_text = await self._generate_text_with_backoff(
                prompt, temperature=temperature, max_output_tokens=max_output_tokens
            )
            return response_text
        except Exception as e:
            self.logger.error(f"Error in _direct_categorize_gtd_level: {e}")
            return None

    async def categorize_gtd_level(
        self, task_content: str, temperature: float = 0.2, max_output_tokens: int = 256
    ) -> Optional[dict]:
        """
        Public interface for categorizing GTD level. Queues a request to the
        RequestManager. Returns the parsed JSON if successful.
        """
        if not self.request_manager:
            raw_text = await self._direct_categorize_gtd_level(
                task_content, temperature, max_output_tokens
            )
            return parse_gemini_json_response(raw_text) if raw_text else None

        req_payload = {
            "method": "categorize_gtd_level",
            "task_content": task_content,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        request = Request(payload=req_payload, priority=RequestPriority.MEDIUM)
        raw_result = await self.request_manager.submit_request(request)
        if not raw_result:
            return None

        return parse_gemini_json_response(raw_result)

    async def generate_function_call(
        self, contents: str, function_name: str, parameters: dict
    ) -> Optional[Dict[str, Any]]:
        """
        Generates a function call using Gemini API, structured as a JSON object.
        """
        prompt = get_function_call_prompt(contents, function_name, parameters)
        raw_response_text = await self.generate_text(prompt)
        if not raw_response_text:
            return None
        function_call_response = parse_gemini_json_response(raw_response_text)
        return function_call_response

    async def categorize_task(
        self, task_content: str, gtd_definitions: str
    ) -> Optional[Dict[str, Any]]:
        """
        Categorizes a task into GTD levels using Gemini, returns structured JSON.
        """
        prompt = get_task_categorization_prompt(task_content, gtd_definitions)
        raw_response_text = await self.generate_text(prompt)
        if not raw_response_text:
            return None
        categorization_response = parse_gemini_json_response(raw_response_text)
        return categorization_response

    def extract_gtd_level(self, gemini_response: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the GTD level from a Gemini API response.
        """
        if gemini_response and "gtd_level" in gemini_response:
            return gemini_response["gtd_level"]
        return None

    async def send_prompt(
        self, prompt: str, max_retries: int = 5, initial_delay: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a prompt to Gemini and returns a structured JSON response.
        Includes retry logic and error handling.
        """
        for attempt in range(max_retries):
            try:
                raw_response_text = await self.generate_text(prompt)
                if raw_response_text:
                    return parse_gemini_json_response(raw_response_text)
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(
                        initial_delay * (2**attempt)
                    )  # Exponential backoff
        self.logger.error(f"Failed to get valid response after {max_retries} attempts.")
        return None

    def generate_content(self, prompt: str, **generation_params) -> Optional[str]:
        """
        Generate text using the Gemini API.

        Args:
            prompt: The text prompt to send to the Gemini API.
            generation_params: Additional parameters for the generation request.

        Returns:
            The generated text, or None if the request fails.
        """
        try:
            # Create generation config from parameters
            config = genai.types.GenerationConfig(
                temperature=generation_params.get("temperature", 0.5),
                top_p=generation_params.get("top_p", 0.95),
                top_k=generation_params.get("top_k", 64),
                max_output_tokens=generation_params.get("max_output_tokens", 256),
            )

            # Initialize the model with configuration
            model = genai.GenerativeModel(
                model_name=self.model_name, generation_config=config
            )

            # Generate content
            response = model.generate_content(prompt)
            if response and hasattr(response, "candidates") and response.candidates:
                return response.candidates[0].text  # Safely access the first candidate
            else:
                self.logger.warning("No candidates found in the Gemini API response.")
                return None

        except Exception as e:
            self.logger.error(f"Error generating text with Gemini API: {e}")
            return None

    @BackoffConfig.exponential_backoff()
    async def categorize_gtd_level(
        self, task_content: str, temperature: float = 0.2, max_output_tokens: int = 256
    ) -> Optional[dict]:
        """Categorize a task with consistent retry handling."""
        try:
            prompt = get_task_categorization_prompt(task_content, GTD_LEVEL_DEFINITIONS)
            response_text = await self._generate_text_with_backoff(
                prompt, temperature=temperature, max_output_tokens=max_output_tokens
            )

            if not response_text:
                return None

            # Parse and validate response
            parsed = self._preprocess_response(response_text)
            if not parsed:
                return None

            # Validate required fields
            if not isinstance(parsed, dict) or "gtd_level" not in parsed:
                return None

            # Validate GTD level
            valid_levels = {
                "Purpose and Principles",
                "Vision",
                "Goals and Objectives",
                "Areas of Focus",
                "Projects",
                "Next Actions",
                "Unknown",
            }
            if parsed["gtd_level"] not in valid_levels:
                return None

            return parsed

        except Exception as e:
            self.logger.error(f"Error in categorize_gtd_level: {e}")
            raise  # Let backoff handle the retry

    def process_content(
        self, content: str, temperature: float = 0.2, max_output_tokens: int = 256
    ) -> Optional[dict]:
        """Process task content using the Gemini API."""
        try:
            prompt = get_content_processing_prompt(content)

            response_text = self.generate_text(
                prompt, temperature=temperature, max_output_tokens=max_output_tokens
            )

            if not response_text:
                return None

            # Parse and validate response
            parsed = self._preprocess_response(response_text)
            if not parsed:
                return None

            # Validate required fields
            required_fields = {"processed_content", "original_content", "changes"}
            if not isinstance(parsed, dict) or not all(
                field in parsed for field in required_fields
            ):
                return None

            return parsed

        except Exception as e:
            self.logger.error(f"Error in process_content: {e}")
            return None

    def prioritize_task(
        self, task_content: str, gtd_level: str, temperature: float = 0.2
    ) -> Optional[dict]:
        """Prioritize a task using the Gemini API."""
        try:
            prompt = get_task_prioritization_prompt(task_content, gtd_level)

            response_text = self.generate_text(prompt, temperature=temperature)

            if not response_text:
                return None

            parsed = self._preprocess_response(response_text)
            if not parsed:
                return None

            # Validate required fields
            required_fields = {"priority", "timeframe", "reasoning"}
            if not isinstance(parsed, dict) or not all(
                field in parsed for field in required_fields
            ):
                return None

            return parsed

        except Exception as e:
            self.logger.error(f"Error in prioritize_task: {e}")
            return None

    def organize_tasks(
        self, tasks: list[dict], temperature: float = 0.3
    ) -> Optional[dict]:
        """Organize multiple tasks using the Gemini API."""
        try:
            prompt = get_task_organization_prompt(tasks)

            response_text = self.generate_text(prompt, temperature=temperature)

            if not response_text:
                return None

            parsed = self._preprocess_response(response_text)
            if not parsed:
                return None

            # Validate required fields
            required_fields = {"task_groups", "workflow_order"}
            if not isinstance(parsed, dict) or not all(
                field in parsed for field in required_fields
            ):
                return None

            return parsed

        except Exception as e:
            self.logger.error(f"Error in organize_tasks: {e}")
            return None

    # NEW: Add a batch-processing method that the RequestManager will call
    async def process_batch(
        self, batch: RequestBatch[Dict[str, Any]]
    ) -> List[Optional[str]]:
        """
        Process a batch of requests from the RequestManager. This method uses
        the backoff logic for each request so the concurrency & caching are handled
        globally, while retries are done per request. The return list must match
        the order of the batch.requests.
        """
        if self.monitor:
            self.monitor.metrics["gemini_service"].active_requests += 1
            self.monitor.log_request("gemini_service")

        start = time.monotonic()
        results: List[Optional[str]] = []

        for request in batch.requests:
            payload = request.payload
            method_name = payload.get("method")

            # Parameter validation for all methods
            if method_name == "generate_text":
                if "prompt" not in payload:
                    self.logger.error("Missing 'prompt' in generate_text request")
                    results.append(None)
                    continue

            elif method_name == "categorize_gtd_level":
                if "task_content" not in payload:
                    self.logger.error(
                        "Missing 'task_content' in categorize_gtd_level request"
                    )
                    results.append(None)
                    continue

            elif method_name == "prioritize_task":
                required = ["task_content", "gtd_level"]
                if any(p not in payload for p in required):
                    self.logger.error(
                        f"Missing required fields for prioritize_task: {required}"
                    )
                    results.append(None)
                    continue

            else:
                self.logger.error(f"Unsupported method: {method_name}")
                results.append(None)
                continue

            # We'll do backoff at a per-request level (rather than per-batch).
            @BackoffConfig.exponential_backoff()
            async def call_llm() -> Optional[str]:
                if method_name == "generate_text":
                    prompt = payload["prompt"]
                    kw = payload["kwargs"]
                    return await self._direct_generate_text(prompt, **kw)
                elif method_name == "categorize_gtd_level":
                    return await self._direct_categorize_gtd_level(
                        task_content=payload["task_content"],
                        temperature=payload["temperature"],
                        max_output_tokens=payload["max_output_tokens"],
                    )
                else:
                    self.logger.error(f"Unknown method: {method_name}")
                    return None

            try:
                result = await call_llm()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing request {request.request_id}: {e}")
                results.append(None)

        self.monitor.update_processing_time("gemini_service", time.monotonic() - start)
        if self.monitor:
            self.monitor.metrics["gemini_service"].active_requests -= 1
            self.monitor.update_throughput()
        return results

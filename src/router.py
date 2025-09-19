import asyncio
import httpx
import time
import os
import random
from typing import Dict, List, Tuple, Optional
from .config import Config


class LLMRouter:
    def __init__(self, config: Config):
        self.config = config
        self.queue_depths = {model: 0 for model in config.models.keys()}

    def _detect_query_type(self, messages: List[Dict]) -> str:
        if not messages:
            return "unknown"

        content = messages[-1].get("content", "").lower()

        for query_type, keywords in self.config.routing_keywords.items():
            if any(keyword in content for keyword in keywords):
                return query_type

        return "unknown"

    def _get_queue_depth(self, model_name: str) -> int:
        return self.queue_depths.get(model_name, 0)

    def _generate_mock_response(self, model_name: str, query: str) -> str:
        query_lower = query.lower()

        # Define response templates based on common question patterns
        if any(greeting in query_lower for greeting in ["hello", "hi", "hey", "how are you"]):
            if model_name == "llama3.2-1b-creative":
                return "Hello! I'm LLaMA 3.2 1B Creative, designed for creative and complex tasks. I'm doing well and ready to help you with creative writing, stories, or any imaginative questions you might have. How can I assist you today?"
            else:
                return "Hi there! I'm LLaMA 3.2 1B Fast, optimized for quick and efficient responses. I'm doing great and ready to help! What can I do for you?"

        elif any(word in query_lower for word in ["summary", "summarize", "briefly", "tldr", "overview"]):
            if "machine learning" in query_lower:
                if model_name == "llama3.2-1b-creative":
                    return "**Machine Learning Summary:**\n\nMachine Learning (ML) is a subset of artificial intelligence that enables computers to learn and improve from data without being explicitly programmed. Key concepts include:\n\n• **Supervised Learning**: Training on labeled data (classification, regression)\n• **Unsupervised Learning**: Finding patterns in unlabeled data (clustering, dimensionality reduction)\n• **Reinforcement Learning**: Learning through interaction and rewards\n• **Deep Learning**: Neural networks with multiple layers for complex pattern recognition\n\nML is used in applications like recommendation systems, image recognition, natural language processing, and autonomous vehicles. The process typically involves data collection, preprocessing, model training, evaluation, and deployment."
                else:
                    return "Machine Learning is AI that learns from data without explicit programming. Main types: supervised (labeled data), unsupervised (pattern finding), and reinforcement learning (reward-based). Used in recommendations, image recognition, NLP, and more."
            elif "artificial intelligence" in query_lower:
                return "AI is computer technology that can perform tasks typically requiring human intelligence, like learning, reasoning, and problem-solving. It includes machine learning, natural language processing, computer vision, and robotics."
            else:
                return f"I can provide a summary of '{query[:50]}...'. Could you be more specific about what aspect you'd like me to focus on?"

        elif any(word in query_lower for word in ["what", "who", "when", "where", "why", "how"]):
            if "capital" in query_lower and "france" in query_lower:
                return "The capital of France is Paris. It's the largest city in France and has been the country's capital since 987 AD."
            elif "invented" in query_lower and "telephone" in query_lower:
                return "Alexander Graham Bell is credited with inventing the telephone. He received the first patent for the telephone on March 7, 1876."
            elif "quantum computing" in query_lower:
                if model_name == "llama3.2-1b-creative":
                    return "Quantum computing is a revolutionary computing paradigm that leverages quantum mechanical phenomena like superposition and entanglement to process information. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits (qubits) that can exist in multiple states simultaneously. This allows quantum computers to potentially solve certain complex problems exponentially faster than classical computers, particularly in areas like cryptography, optimization, and molecular simulation. However, quantum computers are still in early development stages and face significant challenges like quantum decoherence and error correction."
                else:
                    return "Quantum computing uses quantum mechanics principles to process information differently than classical computers. Instead of binary bits, it uses qubits that can be in multiple states at once, potentially solving complex problems much faster."
            elif "photosynthesis" in query_lower:
                return "Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen. The chemical equation is: 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂."
            else:
                return f"That's an interesting question about '{query[:50]}...'. I'd be happy to help you find the answer, though I'm currently running in demo mode."

        elif any(word in query_lower for word in ["write", "create", "story", "poem", "creative"]):
            if model_name == "llama3.2-1b-creative":
                if "story" in query_lower and "robot" in query_lower:
                    return "**The Last Sentinel**\n\nIn the year 2087, ARIA-7 stood alone in the abandoned research facility, her optical sensors scanning the empty corridors. Once, these halls buzzed with human activity, but now only dust motes danced in the filtered sunlight.\n\nShe had been designed as a companion robot, but when humanity fled to the stars, she remained behind to tend the vertical gardens that still fed the automated city below. Each day, she would speak to the plants, telling them stories of the humans who once walked among them.\n\n'Today feels different,' she whispered to a tomato vine. Her emotion simulation protocols detected something she couldn't quite process—loneliness mixed with hope. Through the quantum communicator, she had received a signal: humans were returning.\n\nARIA-7's servos hummed with anticipation as she prepared to fulfill her original purpose once more."
                else:
                    return "I'd be delighted to help you create something! As LLaMA 3.2 1B Creative, I specialize in creative and detailed content generation. Could you provide more specific details about what you'd like me to write?"
            else:
                return "I'd be happy to help with creative writing! As LLaMA 3.2 1B Fast, I can provide quick creative responses. What specific type of creative content would you like?"

        else:
            # General conversational response
            if model_name == "llama3.2-1b-creative":
                return f"Thank you for your question! As LLaMA 3.2 1B Creative, I'm designed to provide detailed and thoughtful responses. I understand you're asking about '{query[:100]}{'...' if len(query) > 100 else ''}'. I'd be happy to help you explore this topic in depth. Could you provide any additional context or specify what aspect you're most interested in?"
            else:
                return f"I'd be happy to help with your question about '{query[:50]}{'...' if len(query) > 50 else ''}'. As LLaMA 3.2 1B Fast, I can provide quick, efficient responses. What specific information are you looking for?"

    def _select_model(self, messages: List[Dict], latency_hint: str, priority: str) -> Tuple[str, str]:
        query_type = self._detect_query_type(messages)

        if latency_hint == "fast":
            if self._get_queue_depth("llama3.2-1b-fast") <= self.config.models["llama3.2-1b-fast"]["max_queue_depth"]:
                return "llama3.2-1b-fast", f"{query_type}+fast"

        if query_type in ["creative", "complex", "reasoning"]:
            if self._get_queue_depth("llama3.2-1b-creative") <= self.config.models["llama3.2-1b-creative"]["max_queue_depth"]:
                return "llama3.2-1b-creative", f"{query_type}+preferred"

        fallback_model = self.config.fallback_model
        return fallback_model, f"{query_type}+fallback"

    async def _call_model(self, model_name: str, messages: List[Dict]) -> Dict:
        self.queue_depths[model_name] += 1
        start_time = time.time()

        try:
            # Use mock mode by default in hosted environments
            if self.config.is_mock_mode:
                await asyncio.sleep(random.uniform(0.1, 0.5))
                completion = self._generate_mock_response(model_name, messages[-1]['content'])
                return {
                    "completion": completion,
                    "latency_ms": int((time.time() - start_time) * 1000)
                }

            # Get model configuration
            model_config = self.config.models[model_name]
            endpoint = model_config["endpoint"]
            ollama_model_name = model_config["model_name"]

            # Use Ollama API format with different parameters based on model type
            if "creative" in model_name:
                temperature = 0.8
                num_predict = 768
            else:
                temperature = 0.3
                num_predict = 256

            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    json={
                        "model": ollama_model_name,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": num_predict
                        }
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()

                # Extract response from Ollama format
                completion = result.get("message", {}).get("content", "")
                return {
                    "completion": completion,
                    "latency_ms": int((time.time() - start_time) * 1000)
                }
        except Exception as e:
            # Log the error and return a fallback response
            print(f"Error calling model {model_name}: {e}")
            return {
                "completion": f"Error: Could not reach {model_name}. Please ensure Ollama is running with model {model_config.get('model_name', model_name)} loaded.",
                "latency_ms": int((time.time() - start_time) * 1000)
            }
        finally:
            self.queue_depths[model_name] = max(0, self.queue_depths[model_name] - 1)

    async def route_request(self, messages: List[Dict], latency_hint: str = "normal", priority: str = "normal") -> Dict:
        selected_model, reason = self._select_model(messages, latency_hint, priority)
        queue_depth = self._get_queue_depth(selected_model)

        try:
            result = await self._call_model(selected_model, messages)
            return {
                "model_selected": selected_model,
                "completion": result["completion"],
                "meta": {
                    "reason": reason,
                    "latency_ms": result["latency_ms"],
                    "queue_depth": queue_depth
                }
            }
        except Exception as e:
            if selected_model != self.config.fallback_model:
                fallback_result = await self._call_model(self.config.fallback_model, messages)
                return {
                    "model_selected": self.config.fallback_model,
                    "completion": fallback_result["completion"],
                    "meta": {
                        "reason": f"{reason}+error_fallback",
                        "latency_ms": fallback_result["latency_ms"],
                        "queue_depth": self._get_queue_depth(self.config.fallback_model)
                    }
                }
            raise
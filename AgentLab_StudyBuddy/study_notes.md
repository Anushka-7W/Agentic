# AgentLab StudyBuddy: Learning Guide

## 1. What is Generative AI?
Generative AI creates new content, such as text, images, audio, or code, from patterns learned during training. A large language model (LLM) is a model that can process and generate text.

## 2. What makes an AI agent?
An AI agent is a system that uses a model to pursue a goal through a cycle of interpreting a task, deciding what to do, using tools when needed, and checking the result. Not every chatbot is an agent; tool use and goal-directed steps are common agent characteristics.

## 3. Prompt engineering
A prompt describes the task and constraints for a model. Useful prompts often specify the role, objective, relevant context, expected format, and success criteria. Few-shot prompting includes examples; zero-shot prompting asks for a task without examples.

## 4. Tool calling
Tool calling lets a model request a defined function, such as a calculator or search function. The application executes the tool and returns its result to the model. Tool inputs should be validated, and sensitive actions should require appropriate checks.

## 5. Retrieval-Augmented Generation (RAG)
RAG retrieves relevant information from a document collection and supplies it to a model when answering a question. A typical pipeline splits documents into chunks, creates embeddings, retrieves relevant chunks, and generates an answer grounded in the retrieved context.

## 6. Embeddings and vector search
An embedding represents content as a numerical vector. Vector search compares vectors to find semantically similar content. Similarity search can help retrieve relevant passages, but retrieved passages still need to be checked for relevance and quality.

## 7. Multi-agent workflows
A multi-agent system assigns different tasks to multiple agents or components, such as researcher, writer, and reviewer. Clear responsibilities, shared state, limits, and a way to handle conflicting outputs make these workflows easier to evaluate.

## 8. Reliability and responsible use
AI systems can produce incorrect or unsupported claims. Useful safeguards include checking outputs against sources, limiting tool permissions, protecting API keys, recording errors, testing edge cases, and keeping a human involved for high-impact decisions.

## 9. Evaluation
A study assistant can be evaluated with test questions, answer correctness, relevance to notes, response consistency, error handling, and user feedback. A quiz score is a learning signal, not a complete measure of understanding.

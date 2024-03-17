from h2ogpte.session import Session
from h2ogpte.h2ogpte import H2OGPTE
from h2ogpte.h2ogpte_async import H2OGPTEAsync
from h2ogpte.session_async import SessionAsync

__version__ = "1.4.0"

__all__ = [
    "H2OGPTE",
    "H2OGPTEAsync",
    "Session",
    "SessionAsync",
]

__doc__ = """h2oGPTe - AI for documents and more
===========================================================================================

**h2ogpte** is the Python client library for H2O.ai's Enterprise h2oGPTe, a RAG
(Retrieval-Augmented Generation) based platform built on top of many
open-source software components such as h2oGPT, hnswlib, Torch, Transformers, Golang, Python, 
k8s, Docker, PyMuPDF, DocTR, and many more.

h2oGPTe is designed to help organizations improve their business using **generative AI**. 
It focuses on scaling as your organization expands the number of use cases, users, 
and documents and has the goal of being your one stop for integrating any model or 
LLM functionality into your business.

Main Features
-------------
* Contextualize chat with your own data using RAG (Retrieval-Augmented Generation) 
* Scalable backend and frontend, multi-user, high throughput
* Fully containerized with Kubernetes
* Multi-modal support for text, images, and audio
* Highly customizable prompting for:
    * talk to LLM
    * talk to document
    * talk to collection of documents
    * talk to every page of a collection (Map/Reduce), summary, extraction
* LLM agnostic, choose the model you need for your use case
"""

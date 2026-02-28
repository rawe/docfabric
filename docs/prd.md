# Product Requirements Document (PRD)

## DocFabric

### Document Infrastructure Layer for AI-Optimized Access

## 1. Overview

DocFabric is a document infrastructure layer that standardizes access to heterogeneous document sources and guarantees a consistent, AI-optimized textual representation.

It serves as a controlled access layer between document sources (local or external) and AI systems. DocFabric ensures that every managed document has:

- A persistent identity
- An original file (stored or referenced)
- A consistent Markdown representation
- Deterministic REST access
- LLM-compatible read access via MCP

This PRD defines the Phase 1 (MVP) scope. It also outlines future expansion directions, including semantic search and embedding integration.

## 2. Goals

### Phase 1 Goals

- Provide minimal, robust document management
- Automatically generate and persist one Markdown representation per document
- Offer deterministic REST-based CRUD operations
- Enable character-based partial reading optimized for AI usage
- Provide read-only access via HTTP-based MCP

### Non-Goals (Phase 1)

- Versioning
- Status/processing states
- Chunk-based storage
- Metadata search/filtering
- Authentication and authorization
- Multi-tenancy
- External source adapters (e.g., SharePoint)
- Cloud deployment requirements
- Size limits
- Embedding storage
- Semantic search

## 3. System Concept

DocFabric manages documents through a minimal abstraction model:

- One document
- One internal system-generated ID
- One original file
- One Markdown representation
- One metadata object (key-value pairs)

The system focuses on deterministic behavior and future extensibility without introducing premature architectural complexity.

## 4. Document Model

Each document contains:

### 4.1 System Fields

- id (system-generated, unique)
- created_at
- updated_at
- filename
- content_type
- size_bytes
- metadata (free-form key-value object)

### 4.2 Content

- Original file (stored exactly as uploaded)
- Exactly one Markdown representation

### 4.3 Markdown Representation Rules

- Generated during upload or full document update
- Persisted exactly as generated
- No structural transformation
- No internal chunking
- No semantic enrichment
- No post-processing

## 5. Document Lifecycle (Phase 1)

- Documents are mutable
- Updates replace the entire file
- File updates trigger Markdown regeneration
- Metadata updates are not included in Phase 1 (Phase 2 feature)
- No version tracking
- No processing status model

## 6. REST API Requirements (Phase 1)

DocFabric must expose a REST API.

### 6.1 Create Document

- Upload original file
- Optional metadata input
- System generates:
  - Internal id
  - Markdown representation

### 6.2 Update Document

- Replaces the entire original file
- Regenerates Markdown representation
- Updates updated_at

### 6.3 Delete Document

- Removes:
  - Original file
  - Markdown representation
  - Metadata
  - System record

### 6.4 List Documents

- Returns all documents
- Supports pagination
- Deterministic sorting:
  - created_at DESC (newest first)
- No filtering
- No search
- Intended to support future frontend management tools

### 6.5 Get Document Metadata

- Returns only system fields and metadata
- No content returned

### 6.6 Download Original File

- Returns the exact uploaded file
- No transformation

### 6.7 Read Textual Representation

Provides access to the stored Markdown representation.

Parameters (all optional):

- offset (character-based)
- limit (character-based)

Behavior:

- No parameters → full document
- Only limit → read from beginning up to limit
- Only offset → read from offset to end
- Both → read from offset to offset + limit
- Character-based indexing only

This endpoint must behave robustly with partial parameter combinations.

## 7. Persistence Requirements

Phase 1 requires:

- Local storage for original files
- Persistent database for document records and metadata
- Deterministic mapping:
  - document_id → original file
  - document_id → Markdown representation

The architecture must allow future integration of external storage systems, but such integration is not part of Phase 1.

## 8. MCP Server Requirements (Phase 1)

DocFabric must provide a separate HTTP-based MCP server.

### 8.1 Purpose

Enable LLM-compatible access to managed documents.

### 8.2 Scope

Read-only access only.

Supported capabilities:

- List documents
- Retrieve document metadata
- Read textual representation (partial or full)

Not supported:

- Upload
- Update
- Delete

### 8.3 Access Pattern

The read tool must mirror REST behavior:

- Character-based offset
- Character-based limit
- Implicit full read if parameters are absent

Tool naming should reflect semantic document content rather than explicitly referencing Markdown.

## 9. Non-Functional Requirements

- Deterministic pagination behavior
- Stable CRUD operations
- Designed for large numbers of documents (no fixed numeric constraint defined)
- No explicit file size limits defined in Phase 1
- No performance SLA defined
- No authentication model defined

## 10. Future Vision and Expansion

DocFabric is designed to evolve beyond basic document management.

### 10.1 External Source Integration

Future capabilities may include:

- SharePoint adapters
- External storage references
- Event-based update hooks
- Automatic reprocessing on remote updates

### 10.2 Embedding Integration

DocFabric will support embedding-based indexing to enable semantic search across documents.

This includes:

- Chunking strategies for large documents
- Embedding generation per chunk
- Vector index integration
- Similarity-based retrieval
- Semantic filtering

Embedding integration enables:

- Natural language search
- Context-aware retrieval for LLMs
- Topic-based partitioning
- Intelligent classification

Chunking and vector storage are not part of Phase 1 but are foundational to the long-term vision.

### 10.3 Classification and Partitioning

Future extensions may include:

- Thematic categorization
- Metadata enrichment
- AI-driven document classification
- Logical document partitioning (without altering the original file)

## 11. Core Design Principle

DocFabric establishes a minimal yet extensible document infrastructure layer:

- Deterministic document identity
- Guaranteed textual representation
- Uniform API access
- AI-ready read semantics
- Clear separation between current scope and future expansion

The Phase 1 focus is strict minimalism, operational clarity, and architectural extensibility without introducing premature complexity.

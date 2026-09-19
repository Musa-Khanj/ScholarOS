# Knowledge Library & Document Ingestion

The ScholarOS Knowledge Library manages scientific documents, pre-processes academic papers, chunks text, and indexes content for hybrid retrieval and semantic search.

---

## 1. Supported Document Formats

ScholarOS includes built-in adapters for standard document formats:

| Format | Adapter | Capabilities |
|---|---|---|
| **PDF (`.pdf`)** | `PDFAdapter` | Extracts paper text, section headings, metadata, and abstracts. |
| **Markdown (`.md`)** | `MarkdownAdapter` | Parses hierarchical headings, code blocks, and formatted text. |
| **Plain Text (`.txt`)** | `TextAdapter` | Fast character and line-based extraction. |
| **JSON (`.json`)** | `JSONAdapter` | Ingests structured literature catalogs, bibtex conversions, and datasets. |

---

## 2. Document Ingestion Pipeline

When a document is added to the Knowledge Library:
1. **Extraction**: The appropriate adapter reads and extracts textual content and metadata (authors, title, year).
2. **Sanitization**: Paths and content are validated against the Security subsystem to prevent directory traversal or malicious embedded payloads.
3. **Chunking**: Text is segmented into chunks according to `chunk_size` and `chunk_overlap`.
4. **Vector Embedding**: Chunks are passed to the embedding engine to generate semantic vectors.
5. **Storage**: Vectors and chunk texts are committed to the vector store and keyword index.

---

## 3. Importing Documents in Desktop GUI

1. Switch to the **Knowledge Library** workspace from the left navigation.
2. Click **Import Documents** or drag and drop files into the document list.
3. Select an existing collection or click **New Collection** (e.g., `"Machine Learning"`, `"Quantum Physics"`).
4. Ingestion progress is shown live in the status panel.

---

## 4. Chunking Configuration

Configure chunking parameters in `%APPDATA%\ScholarOS\config\config.toml` (Windows) or `~/.config/scholaros/config.toml`:

```toml
[knowledge]
# Target token/character length per chunk
chunk_size = 1000

# Overlap to preserve context boundaries between chunks
chunk_overlap = 200

# Automatically embed and index documents upon import
auto_index = true
```

Next Step: Learn how to configure and tune retrieval strategies in the [RAG Configuration Guide](rag_configuration.md).

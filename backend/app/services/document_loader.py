"""
CRI-RSK Chatbot — Document loader service.
Loads and cleans JSON, Markdown, and PDF documents from knowledge_base/.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

from langchain.docstore.document import Document

logger = logging.getLogger(__name__)


def load_all_documents(knowledge_base_path: str) -> list[Document]:
    """
    Load all documents from the knowledge base directory.
    Supports JSON (FAQs, procedures), Markdown, and PDF files.
    Returns a list of LangChain Documents with metadata.
    """
    base_path = Path(knowledge_base_path)
    if not base_path.exists():
        logger.error(f"Knowledge base path not found: {base_path}")
        return []

    all_docs = []

    for file_path in base_path.rglob("*"):
        if file_path.is_dir():
            continue

        try:
            if file_path.suffix == ".json":
                docs = _load_json_file(file_path, base_path)
            elif file_path.suffix == ".md":
                docs = _load_markdown_file(file_path, base_path)
            elif file_path.suffix == ".pdf":
                docs = _load_pdf_file(file_path, base_path)
            else:
                continue

            all_docs.extend(docs)
            logger.info(
                f"Loaded {len(docs)} document(s) from {file_path.name}"
            )
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")

    logger.info(f"Total documents loaded: {len(all_docs)}")
    return all_docs


def _get_metadata(file_path: Path, base_path: Path) -> dict:
    """Extract metadata from file path structure."""
    relative = file_path.relative_to(base_path)
    parts = relative.parts

    source = parts[0] if len(parts) > 0 else "unknown"
    category = parts[1] if len(parts) > 1 else "general"
    subcategory = parts[2] if len(parts) > 2 else None

    return {
        "source": source,
        "category": category,
        "subcategory": subcategory,
        "filename": file_path.name,
        "file_type": file_path.suffix.lstrip("."),
    }


def _load_json_file(
    file_path: Path, base_path: Path
) -> list[Document]:
    """Load a JSON file. Handles FAQ and procedure formats."""
    if file_path.name == "_all_incitations.json" or file_path.name.startswith("META-"):
        # Skip bulk and meta files to avoid duplicating the individual INC-*.json files in the vectorstore
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = _get_metadata(file_path, base_path)
    docs = []

    # FAQ format: {"items": [{"question": ..., "answer": ...}]}
    if "items" in data:
        faq_category = data.get("category", metadata["category"])
        for item in data["items"]:
            question = item.get("question", "")
            answer = item.get("answer", "")
            tags = item.get("tags", [])
            content = f"Question: {question}\nRéponse: {answer}"
            doc_metadata = {
                **metadata,
                "document_type": "faq",
                "faq_category": faq_category,
                "tags": ", ".join(tags) if tags else "",
            }
            docs.append(Document(page_content=content, metadata=doc_metadata))

    # Procedure format: {"procedure": {"titre": ..., "description": ...}}
    elif "procedure" in data:
        procedure = data["procedure"]
        titre = procedure.get("titre", "")
        description = procedure.get("description", "")

        # Build full procedure text
        sections = [f"Procédure: {titre}", f"Description: {description}"]

        # Add timeline if present
        if "delai_moyen_indicatif_realisation" in data:
            timeline = data["delai_moyen_indicatif_realisation"]
            sections.append("\nDélais indicatifs:")
            for step in timeline:
                note = f" ({step['note']})" if "note" in step else ""
                sections.append(
                    f"  - {step['etape']}: {step['jours']} jours{note}"
                )

        # Add required documents
        # Add required documents
        if "constitution_dossier" in data:
            dossier = data["constitution_dossier"]
            pieces = dossier.get("pieces_requises", [])
            if pieces:
                sections.append("\nDocuments requis:")
                for piece in pieces:
                    # Handle both string and dict formats
                    if isinstance(piece, str):
                        sections.append(f"  - {piece}")
                    else:
                        doc_text = piece.get("document", "")
                        note = (
                            f" ({piece['note']})" if "note" in piece else ""
                        )
                        sections.append(f"  - {doc_text}{note}")
            
            remarque = dossier.get("remarque", "")
            if remarque:
                sections.append(f"\nRemarque: {remarque}")

        # Add how to start
        if "demarrer_procedure" in data:
            start = data["demarrer_procedure"]
            instructions = start.get("instructions", "")
            if instructions:
                sections.append(
                    f"\nComment démarrer: {instructions}"
                )

        content = "\n".join(sections)
        doc_metadata = {
            **metadata,
            "document_type": "procedure",
            "procedure_title": titre,
        }
        docs.append(Document(page_content=content, metadata=doc_metadata))

    # Incitation format (individual files like INC-H074.json)
    elif isinstance(data, dict) and "nom" in data and ("description_complete" in data or "description_courte" in data):
        titre = data.get("nom", "").replace("\n", " ").strip()
        desc = data.get("description_complete") or data.get("description_courte", "")
        montant = data.get("montant_ou_taux", "")
        
        sections = [f"FICHE INCITATION / SUBVENTION : {titre}", f"Description : {desc}"]
        
        if montant:
            sections.append(f"Avantages et Montants / Taux : {montant}")
            
        cibles = data.get("cibles", [])
        if cibles:
            sections.append(f"Cibles : {', '.join(cibles)}")
            
        criteres = data.get("criteres_eligibilite", [])
        if criteres:
            sections.append("Critères d'éligibilité :\n" + "\n".join([f"- {c}" for c in criteres]))
            
        actions = data.get("actions_financables", [])
        if actions:
            sections.append("Actions finançables :\n" + "\n".join([f"- {a}" for a in actions]))
            
        content = "\n\n".join(sections)
        doc_metadata = {**metadata, "document_type": "incitation", "incitation_id": data.get("id", "")}
        docs.append(Document(page_content=content, metadata=doc_metadata))

    else:
        # Generic JSON — serialize to text
        content = json.dumps(data, ensure_ascii=False, indent=2)
        doc_metadata = {**metadata, "document_type": "data"}
        docs.append(Document(page_content=content, metadata=doc_metadata))

    return docs


def _clean_markdown(text: str) -> str:
    """
    Clean scraped markdown by removing navigation boilerplate.
    Strips menus, weather widgets, breadcrumbs, and repeated nav sections.
    """
    lines = text.split("\n")
    cleaned_lines = []
    content_started = False
    skip_until_content = True

    for line in lines:
        stripped = line.strip()

        # Skip empty lines before content starts
        if not content_started and not stripped:
            continue

        # Skip navigation patterns
        if _is_nav_line(stripped):
            continue

        # Content starts at first heading or first substantial paragraph
        if not content_started:
            if stripped.startswith("#") or (
                len(stripped) > 50 and not stripped.startswith("[")
                and not stripped.startswith("!")
            ):
                content_started = True
            else:
                continue

        cleaned_lines.append(line)

    # Remove trailing navigation (footer)
    result = "\n".join(cleaned_lines)

    # Remove image references to site assets
    result = re.sub(
        r"!\[.*?\]\(https?://www\.rabatinvest\.ma/wp-content/.*?\)",
        "",
        result,
    )

    # Remove weather widget lines
    result = re.sub(r".*openweathermap\.org.*\n?", "", result)

    # Collapse multiple blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


def _is_nav_line(line: str) -> bool:
    """Check if a line is part of navigation boilerplate."""
    nav_patterns = [
        r"^\[.*?\]\(https?://.*\)$",  # Standalone links
        r"^- \[.*?\]\(https?://.*\)$",  # Bullet point links
        r"^\s*- \[.*?\]\(https?://.*\)$",  # Indented bullet links
        r"^!\[.*?\]\(https?://.*\.(jpg|png|svg).*\)$",  # Standalone images
        r"^\[Mobile Menu\]",
        r"^Rabat, MA$",
        r".*°C$",
        r"^TypologieChoisir",
        r"^CibleChoisir",
        r"^Secteurs d'activité",
    ]
    return any(re.match(pattern, line) for pattern in nav_patterns)


def _load_markdown_file(
    file_path: Path, base_path: Path
) -> list[Document]:
    """Load and clean a markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = _clean_markdown(raw_text)
    if not cleaned or len(cleaned) < 20:
        logger.warning(f"Markdown file too short after cleaning: {file_path}")
        return []

    metadata = _get_metadata(file_path, base_path)
    metadata["document_type"] = "article"

    return [Document(page_content=cleaned, metadata=metadata)]


def _load_pdf_file(
    file_path: Path, base_path: Path
) -> list[Document]:
    """Load a PDF file and extract text."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        if not text_parts:
            logger.warning(f"No text extracted from PDF: {file_path}")
            return []

        full_text = "\n\n".join(text_parts)
        metadata = _get_metadata(file_path, base_path)
        metadata["document_type"] = "officiel_royal"

        return [Document(page_content=full_text, metadata=metadata)]

    except ImportError:
        logger.error("pypdf not installed. Cannot load PDF files.")
        return []
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return []

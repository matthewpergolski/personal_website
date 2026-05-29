"""
Data ingestion pipeline for RAG system.

Processes resume PDF and GitHub projects into text chunks
suitable for embedding and retrieval.
"""

import json
import os
import re
import tempfile
import httpx
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# Optional PDF processing (installed via uv)
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from src.services.github import fetch_github_projects
from src.config import get_rag_config, RAGConfig, ROOT_DIR, get_config


@dataclass(frozen=True)
class DocumentChunk:
    """Document chunk with metadata for RAG system."""
    text: str
    metadata: dict
    source: str
    section: str = "general"


async def process_resume_pdf() -> List[DocumentChunk]:
    """Download and process resume PDF into chunks ONLY from RESUME_URL."""
    if not HAS_PYMUPDF:
        print("Warning: PyMuPDF not installed. Skipping PDF processing.")
        return []

    config = get_rag_config()
    site_config = get_config()

    # Get resume URL from environment/config - NO fallback to JSON
    resume_url = site_config.resume_url

    if not resume_url:
        print("Error: No RESUME_URL configured. Set RESUME_URL to point to your resume PDF.")
        print("Set this in your environment variables (envs.sh) or data/site.json")
        return []

    try:
        # Download PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            if resume_url.startswith(('http://', 'https://')):
                print(f"Downloading resume from: {resume_url}")
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(resume_url)
                    response.raise_for_status()
                    print(f"Download status: {response.status_code}")
                    temp_pdf.write(response.content)
            else:
                # Local file path
                # Handle both relative paths (from public URL) and absolute paths
                if resume_url.startswith(('http://', 'https://')):
                    local_path = Path(resume_url)
                else:
                    # Handle the /static/ URL by stripping just the leading '/'
                    resume_path = resume_url.lstrip('/')
                    if resume_path.startswith('static/'):
                        resume_path = resume_path[len('static/'):]
                    local_path = ROOT_DIR / "data" / "static" / resume_path

                if local_path.exists():
                    print(f"Using local PDF at: {local_path}")
                    temp_pdf.write(local_path.read_bytes())
                else:
                    print(f"Resume PDF not found at: {local_path}")
                    print(f"Tried path: {resume_url}")
                    return []

            temp_pdf_path = temp_pdf.name

        # Extract text from PDF
        doc = fitz.open(temp_pdf_path)
        full_text = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            # Add page separator for better chunking
            if page_num > 0:
                full_text.append(f"\n--- Page {page_num + 1} ---\n")
            full_text.append(text)

        doc.close()

        # Clean up temp file
        Path(temp_pdf_path).unlink(missing_ok=True)

        combined_text = ''.join(full_text)
        if not combined_text.strip():
            print("No text extracted from resume PDF")
            return []

        print(f"Extracted {len(combined_text)} characters from resume PDF")

        # Split into sections based on common resume structure
        chunks = []
        sections = _split_pdf_into_sections(combined_text)

        for section_name, section_text in sections.items():
            if section_text.strip():
                chunks.extend(_create_pdf_chunks(section_text, section_name, config))

        return chunks

    except Exception as e:
        print(f"Error processing resume PDF: {e}")
        return []


def _split_pdf_into_sections(text: str) -> dict:
    """Split PDF text into logical sections based on headers."""
    sections = {}
    current_section = "general"
    section_text = []

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Look for common section headers (case-insensitive)
        lower_line = line.lower()
        if "summary" in lower_line or any(keyword in lower_line for keyword in ['objective', 'profile']):
            if section_text:
                sections[current_section] = '\n'.join(section_text)
            current_section = "summary"
            section_text = []
        elif any(keyword in lower_line for keyword in ['experience', 'work', 'employment']):
            if section_text:
                sections[current_section] = '\n'.join(section_text)
            current_section = "experience"
            section_text = []
        elif any(keyword in lower_line for keyword in ['education', 'degree', 'university']):
            if section_text:
                sections[current_section] = '\n'.join(section_text)
            current_section = "education"
            section_text = []
        elif any(keyword in lower_line for keyword in ['skill', 'technology', 'tools']):
            if section_text:
                sections[current_section] = '\n'.join(section_text)
            current_section = "skills"
            section_text = []
        elif any(keyword in lower_line for keyword in ['project', 'portfolio']):
            if section_text:
                sections[current_section] = '\n'.join(section_text)
            current_section = "projects"
            section_text = []
        else:
            section_text.append(line)

    # Add the last section
    if section_text:
        sections[current_section] = '\n'.join(section_text)

    return sections


def _create_pdf_chunks(text: str, section: str, config: RAGConfig) -> List[DocumentChunk]:
    """Create chunks from PDF sections with metadata."""
    chunks = []
    chunk_size = config.chunk_size
    overlap = config.chunk_overlap

    # Clean and prepare text
    text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with spaces
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace

    words = text.split()
    if len(words) <= chunk_size:
        chunks.append(DocumentChunk(
            text=text,
            metadata={
                "section": section,
                "length": len(words),
                "type": "pdf_content",
                "source": "pdf"
            },
            source="resume_pdf",
            section=section
        ))
        return chunks

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) >= 20:  # Minimum meaningful chunk
            chunk_text = ' '.join(chunk_words)
            chunks.append(DocumentChunk(
                text=chunk_text,
                metadata={
                    "section": section,
                    "length": len(chunk_words),
                    "position": len(chunks),
                    "start_word": i,
                    "type": "pdf_content"
                },
                source="resume_pdf",
                section=section
            ))

    return chunks


async def process_github_projects() -> List[DocumentChunk]:
    """Process GitHub projects into chunks for RAG system.

    Includes repository metadata, README content, and key project files.
    """
    config = get_rag_config()
    chunks = []

    try:
        projects = await fetch_github_projects()
        if not projects:
            return []

        for project in projects[:15]:  # Limit to 15 most recent projects for depth
            print(f"Processing GitHub project: {project['name']}")

            # Get basic project metadata
            metadata_text = _format_github_project(project)

            # Try to get README content
            readme_text = await _fetch_github_readme(project['full_name'])
            if readme_text:
                readme_text = f"\nREADME Content:\n{readme_text[:1000]}"  # Limit README to 1K chars
            else:
                readme_text = ""

            # Try to get key project files
            project_files_text = await _fetch_github_key_files(project['full_name'])

            # Combine all project information
            project_text = f"{metadata_text}{readme_text}{project_files_text}"
            if project_text.strip():
                chunks.extend(_create_github_chunks(project_text, project['name'], config))

    except Exception as e:
        print(f"Error processing GitHub projects: {e}")

    return chunks


async def _fetch_github_readme(repo_full_name: str) -> str:
    """Fetch README.md content from a GitHub repository via REST API."""
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return ""

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Try different common README filenames
        for readme_filename in ["README.md", "README.rst", "README.txt", "readme.md"]:
            url = f"https://api.github.com/repos/{repo_full_name}/contents/{readme_filename}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("encoding") == "base64":
                        import base64
                        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                        # Extract first meaningful section of README
                        return _extract_readme_summary(content)
                    break

    except Exception as e:
        print(f"Could not fetch README for {repo_full_name}: {str(e)[:50]}...")

    return ""


def _extract_readme_summary(readme_content: str) -> str:
    """Extract meaningful summary section from README content."""
    lines = readme_content.split('\n')
    summary_parts = []
    capture = True
    max_lines = 50  # Limit to first meaningful section

    for i, line in enumerate(lines[:max_lines]):
        line = line.strip()

        # Stop capturing at certain sections or content
        if any(section in line.lower() for section in [
            '# installation', '# install', '# setup', '# getting started'
        ]):
            break

        # Skip heavily formatted lines (tables, code blocks, etc.)
        if line.count('|') > 3 or line.count('```') > 0 or line.startswith('####'):
            continue

        # Keep meaningful content
        if len(line) > 10 and not line.startswith('[') and not line.count(']') > 2:
            summary_parts.append(line)

    return '\n'.join(summary_parts[:20])  # Return first 20 meaningful lines


async def _fetch_github_key_files(repo_full_name: str) -> str:
    """Fetch key project files (package.json, requirements.txt, etc.) for context."""
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return ""

        key_files = [
            "package.json",      # Node.js
            "requirements.txt",  # Python
            "pyproject.toml",    # Python
            "Dockerfile",        # Containerization
            "docker-compose.yml", # Development setup
            ".vscode/launch.json",  # VS Code debug config
        ]

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        file_contents = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for filename in key_files:
                url = f"https://api.github.com/repos/{repo_full_name}/contents/{filename}"
                try:
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("encoding") == "base64":
                            import base64
                            content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")

                            if filename == "package.json":
                                # Extract dependencies for context
                                import json as json_lib
                                try:
                                    pkg_data = json_lib.loads(content)
                                    deps = pkg_data.get("dependencies", {})
                                    dep_list = list(deps.keys())[:10]  # First 10 deps
                                    file_contents.append(f"Package Dependencies: {', '.join(dep_list)}")
                                except:
                                    pass
                            elif "requirements" in filename:
                                # Extract first few requirements
                                lines = content.split('\n')[:10]
                                file_contents.append(f"Python Requirements: {', '.join(lines)}")
                            else:
                                # For other files, just note existence and size
                                file_contents.append(f"Contains {filename} ({len(content)} chars)")

                            if len(file_contents) >= 3:  # Limit to 3 key files per repo
                                break

                except Exception:
                    continue

        if file_contents:
            return f"\nProject Structure:\n" + '\n'.join(file_contents)
        else:
            return ""

    except Exception as e:
        print(f"Could not fetch key files for {repo_full_name}: {str(e)[:50]}...")

    return ""


def _create_github_chunks(text: str, project_name: str, config: RAGConfig) -> List[DocumentChunk]:
    """Create chunks from GitHub project description."""
    chunks = []
    chunk_size = config.chunk_size

    words = text.split()
    if len(words) <= chunk_size:
        chunks.append(DocumentChunk(
            text=text,
            metadata={
                "project": project_name,
                "length": len(words),
                "type": "description"
            },
            source="github",
            section="project_description"
        ))
        return chunks

    # Split long descriptions
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) >= 10:  # Minimum for GitHub
            chunk_text = ' '.join(chunk_words)
            chunks.append(DocumentChunk(
                text=chunk_text,
                metadata={
                    "project": project_name,
                    "length": len(chunk_words),
                    "position": len(chunks),
                    "type": "description"
                },
                source="github",
                section="project_description"
            ))

    return chunks


def _format_github_project(project: dict) -> str:
    """Format GitHub project into searchable text."""
    name = project.get('name', '')
    description = project.get('description', '')
    language = project.get('language', 'Unknown')
    stars = project.get('stars', 0)
    updated = project.get('updated', '')

    text_parts = []
    text_parts.append(f"Project: {name}")

    if description and description != 'No description available':
        text_parts.append(f"Description: {description}")

    text_parts.append(f"Primary Language: {language}")

    if stars > 0:
        text_parts.append(f"Stars: {stars}")

    if updated:
        text_parts.append(f"Last Updated: {updated}")

    # Include topics if available
    if topics := project.get('topics'):
        text_parts.append(f"Topics: {', '.join(topics)}")

    return ". ".join(text_parts)


async def process_all_documents() -> List[DocumentChunk]:
    """Process all available documents (resume PDF + GitHub projects)."""
    resume_chunks = await process_resume_pdf()
    github_chunks = await process_github_projects()

    all_chunks = resume_chunks + github_chunks

    # Add document totals to metadata
    for chunk in all_chunks:
        chunk.metadata['total_chunks'] = len(all_chunks)

    print(f"Processed {len(resume_chunks)} PDF resume chunks and {len(github_chunks)} GitHub chunks")
    return all_chunks


if __name__ == "__main__":
    import asyncio

    # Test the ingestion pipeline
    async def test():
        print("Testing data ingestion...")
        chunks = await process_all_documents()

        # Show sample chunks
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"Source: {chunk.source}")
            print(f"Section: {chunk.section}")
            print(f"Text: {chunk.text[:200]}...")

        print(f"\nTotal chunks: {len(chunks)}")

    asyncio.run(test())

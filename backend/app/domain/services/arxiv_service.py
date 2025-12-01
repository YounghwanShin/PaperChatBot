"""Service for fetching papers from arXiv."""

import arxiv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

from .paper_service import PaperService
from ...core.exceptions import PDFProcessingError, DuplicatePaperError

logger = logging.getLogger(__name__)


class ArxivService:
    """Service for automatic paper collection from arXiv."""

    def __init__(
        self,
        paper_service: PaperService,
        category: str = "cs.CL",
        max_results: int = 100,
        delay_seconds: float = 3.0,
        num_retries: int = 3
    ):
        """Initialize arXiv service.

        Args:
            paper_service: Paper service for processing downloaded papers
            category: arXiv category to search (default: cs.CL for NLP)
            max_results: Maximum number of results per search
            delay_seconds: Delay between API calls (arXiv policy compliance)
            num_retries: Number of retries for failed requests
        """
        self.paper_service = paper_service
        self.category = category
        self.max_results = max_results
        self.delay_seconds = delay_seconds
        self.num_retries = num_retries

        # Create arXiv client with rate limiting
        self.client = arxiv.Client(
            page_size=max_results,
            delay_seconds=delay_seconds,
            num_retries=num_retries
        )

    def search_papers(
        self,
        days_ago: int = 7,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.LastUpdatedDate
    ) -> List[arxiv.Result]:
        """Search for papers in arXiv.

        Args:
            days_ago: Number of days to look back (default: 7)
            sort_by: Sort criterion for results

        Returns:
            List of arXiv search results filtered by update date
        """
        # Query for category only (arXiv API doesn't support date filtering in query)
        query = f"cat:{self.category}"

        logger.info(f"Searching arXiv with query: {query}, looking back {days_ago} days")

        search = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=sort_by
        )

        # Fetch results
        all_results = list(self.client.results(search))
        logger.info(f"Fetched {len(all_results)} recent papers from arXiv")

        # Filter by date in Python (use 'updated' for most recent submissions)
        cutoff_date = datetime.now() - timedelta(days=days_ago)

        filtered_results = []
        for result in all_results:
            # Use 'updated' date which includes new submissions and updates
            result_date = result.updated if result.updated else result.published
            if result_date and result_date.replace(tzinfo=None) >= cutoff_date:
                filtered_results.append(result)
                logger.debug(
                    f"Including paper: {result.title[:50]}... "
                    f"(updated: {result.updated.strftime('%Y-%m-%d') if result.updated else 'N/A'})"
                )

        logger.info(
            f"Filtered to {len(filtered_results)} papers updated in last {days_ago} day(s) "
            f"(since {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})"
        )

        return filtered_results

    def _download_paper(
        self,
        result: arxiv.Result,
        download_dir: str
    ) -> str:
        """Download paper PDF from arXiv.

        Args:
            result: arXiv search result
            download_dir: Directory to save PDF

        Returns:
            Path to downloaded PDF file

        Raises:
            PDFProcessingError: If download fails
        """
        try:
            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)

            # Generate filename from arXiv ID
            arxiv_id = result.entry_id.split('/')[-1]
            safe_filename = f"arxiv_{arxiv_id.replace('.', '_')}.pdf"
            pdf_path = os.path.join(download_dir, safe_filename)

            # Download PDF
            logger.info(f"Downloading {arxiv_id}: {result.title}")
            result.download_pdf(dirpath=download_dir, filename=safe_filename)

            logger.info(f"Successfully downloaded to {pdf_path}")
            return pdf_path

        except Exception as e:
            raise PDFProcessingError(f"Failed to download paper {result.entry_id}: {e}")

    def _extract_paper_info(self, result: arxiv.Result) -> Dict[str, Any]:
        """Extract paper information from arXiv result.

        Args:
            result: arXiv search result

        Returns:
            Dictionary with paper metadata
        """
        # Extract authors
        authors = ", ".join([author.name for author in result.authors])

        # Extract year from published date
        year = result.published.year if result.published else None

        return {
            "title": result.title,
            "abstract": result.summary,
            "authors": authors,
            "year": year,
            "arxiv_id": result.entry_id.split('/')[-1],
            "arxiv_url": result.entry_id,
            "pdf_url": result.pdf_url,
            "published": result.published.isoformat() if result.published else None
        }

    def fetch_and_process_papers(
        self,
        days_ago: int = 7,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """Fetch papers from arXiv and process them.

        Args:
            days_ago: Number of days to look back (default: 7)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks

        Returns:
            Dictionary with processing results
        """
        results_summary = {
            "total_found": 0,
            "successfully_processed": 0,
            "skipped_duplicates": 0,
            "failed": 0,
            "papers": [],
            "errors": []
        }

        try:
            # Search for papers
            search_results = self.search_papers(days_ago=days_ago)
            results_summary["total_found"] = len(search_results)

            if not search_results:
                logger.info("No papers found in arXiv search")
                return results_summary

            # Process each paper
            for result in search_results:
                try:
                    # Extract paper info
                    paper_info = self._extract_paper_info(result)
                    arxiv_id = paper_info["arxiv_id"]

                    logger.info(f"Processing paper: {paper_info['title']}")

                    # Check for duplicate BEFORE downloading PDF
                    existing_papers = self.paper_service.list_papers()
                    is_duplicate = False

                    for paper in existing_papers:
                        # Check by arXiv ID first
                        if paper.get("arxiv_id") == arxiv_id:
                            is_duplicate = True
                            logger.info(f"Skipping duplicate (arXiv ID): {arxiv_id}")
                            break
                        # Fallback to title check
                        if paper.get("title", "").strip().lower() == paper_info["title"].strip().lower():
                            is_duplicate = True
                            logger.info(f"Skipping duplicate (title): {paper_info['title']}")
                            break

                    if is_duplicate:
                        results_summary["skipped_duplicates"] += 1
                        continue

                    # Download PDF (only if not duplicate)
                    pdf_path = self._download_paper(
                        result,
                        self.paper_service.upload_dir
                    )

                    # Process paper using existing PaperService
                    paper_id, chunks_count = self.paper_service.upload_paper(
                        pdf_path=pdf_path,
                        title=paper_info["title"],
                        abstract=paper_info["abstract"],
                        authors=paper_info["authors"],
                        year=paper_info["year"],
                        arxiv_id=arxiv_id,  # Pass arXiv ID
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )

                    # Record success
                    results_summary["successfully_processed"] += 1
                    results_summary["papers"].append({
                        "paper_id": paper_id,
                        "arxiv_id": arxiv_id,
                        "title": paper_info["title"],
                        "chunks_created": chunks_count
                    })

                    logger.info(
                        f"Successfully processed {arxiv_id}: {paper_id} "
                        f"({chunks_count} chunks)"
                    )

                except DuplicatePaperError as e:
                    # Paper already exists, skip
                    results_summary["skipped_duplicates"] += 1
                    logger.warning(f"Skipping duplicate paper: {paper_info['title']}")
                    results_summary["errors"].append({
                        "arxiv_id": arxiv_id,
                        "title": paper_info["title"],
                        "error": "Duplicate paper"
                    })

                except Exception as e:
                    # Log error and continue
                    results_summary["failed"] += 1
                    error_msg = f"Failed to process {result.entry_id}: {str(e)}"
                    logger.error(error_msg)
                    results_summary["errors"].append({
                        "arxiv_id": result.entry_id.split('/')[-1],
                        "title": result.title,
                        "error": str(e)
                    })

            logger.info(
                f"arXiv fetch completed: {results_summary['successfully_processed']} "
                f"processed, {results_summary['skipped_duplicates']} duplicates, "
                f"{results_summary['failed']} failed"
            )

            return results_summary

        except Exception as e:
            logger.error(f"Error in fetch_and_process_papers: {e}")
            results_summary["errors"].append({
                "error": f"General error: {str(e)}"
            })
            return results_summary

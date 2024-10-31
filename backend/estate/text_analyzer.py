from typing import List, Dict, Optional
from collections import defaultdict
import re

from common.utils import first


class TextAnalyzer:
    """
    A class for identifying and extracting word patterns from text.
    Handles case-insensitive matching and word boundary detection.
    Useful for finding frequencies of specific terms, phrases, or names in text.
    """

    @staticmethod
    def _prepare_text(text: str) -> str:
        """
        Prepares text for pattern extraction by converting to lowercase
        and normalizing whitespace.

        Args:
            text: Input text to prepare

        Returns:
            Normalized text string
        """
        if not isinstance(text, str):
            raise ValueError("Input text must be a string")
        return text.lower().strip()

    @staticmethod
    def _prepare_patterns(patterns: List[str]) -> List[str]:
        """
        Validates and prepares search patterns for matching.

        Args:
            patterns: List of terms/phrases to prepare

        Returns:
            List of normalized patterns

        Raises:
            ValueError: If patterns list is empty or contains invalid entries
        """
        if not patterns:
            raise ValueError("Patterns list cannot be empty")

        normalized_patterns = []
        for pattern in patterns:
            if not isinstance(pattern, str) or not pattern.strip():
                raise ValueError("Each pattern must be a non-empty string")
            normalized_patterns.append(pattern.lower().strip())

        return normalized_patterns

    @staticmethod
    def _create_search_pattern(term: str) -> str:
        """
        Creates a regex pattern for matching a term with word boundaries.

        Args:
            term: Term to create pattern for

        Returns:
            Regex pattern string
        """
        # Escape special regex characters in the term
        escaped_term = re.escape(term)
        return fr'\b{escaped_term}\b'

    @classmethod
    def _count_pattern_occurrences(cls, text: str, patterns: List[str]) -> Dict[str, int]:
        """
        Counts occurrences of each pattern in the text.

        Args:
            text: Text to search in
            patterns: List of patterns to search for

        Returns:
            Dictionary mapping patterns to their occurrence counts
        """
        counts = defaultdict(int)

        # Prepare text once for all searches
        prepared_text = cls._prepare_text(text)

        # Count occurrences of each pattern
        for pattern in patterns:
            search_pattern = cls._create_search_pattern(pattern)
            matches = re.finditer(search_pattern, prepared_text)
            counts[pattern] = sum(1 for _ in matches)

        return counts

    @classmethod
    def findMostFrequentPattern(cls, text: str, patterns: List[str]) -> Optional[str]:
        """
        Finds the most frequently occurring pattern in the given text.

        Args:
            text: Text to search for patterns
            patterns: List of patterns to search for

        Returns:
            Most frequent pattern, or None if no patterns are found

        Raises:
            ValueError: If inputs are invalid

        Examples:
            >>> analyzer = TextAnalyzer()
            >>> # Finding most frequent city
            >>> text = "London is amazing! I love London more than Paris."
            >>> cities = ["London", "Paris", "Berlin"]
            >>> analyzer.findMostFrequentPattern(text, cities)
            'London'

            >>> # Finding most frequent color
            >>> text = "The red car passed the blue house and the red barn."
            >>> colors = ["red", "blue", "green"]
            >>> analyzer.findMostFrequentPattern(text, colors)
            'red'

            >>> # Finding most frequent phrase
            >>> text = "The quick brown fox jumps over the lazy dog. The quick brown fox runs away."
            >>> phrases = ["quick brown fox", "lazy dog"]
            >>> analyzer.findMostFrequentPattern(text, phrases)
            'quick brown fox'
        """
        # Validate and prepare inputs
        if not text.strip():
            raise ValueError("Input text cannot be empty")

        normalized_patterns = cls._prepare_patterns(patterns)

        # Count pattern occurrences
        pattern_counts = cls._count_pattern_occurrences(
            text, normalized_patterns)

        # Find pattern with highest count
        if not pattern_counts:
            return None

        max_count = max(pattern_counts.values())
        if max_count == 0:
            return None

        # Return any pattern with the highest count
        # (first one in case of ties)
        for pattern, count in pattern_counts.items():
            if count == max_count:
                # Return original case version from input list
                original_case_pattern = first(
                    patterns, lambda x: x.lower() == pattern)
                return original_case_pattern

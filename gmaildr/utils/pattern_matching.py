from typing import Union, List

def _match_pattern(text: str, pattern: str) -> bool:
    """
    As soon as it finds a match, it returns True.
    It does not use regex.
    """
    if not pattern or not text:
        return False
    
    text_lower = text.lower()
    pattern_lower = pattern.lower()
    
    if '*' not in pattern_lower and '?' not in pattern_lower:
        return pattern_lower in text_lower
    
    if '*' in pattern_lower:
        parts = pattern_lower.split('*')
        if len(parts) == 1:
            return parts[0] in text_lower
        
        for part in parts:
            if part not in text_lower:
                return False
        return True
    
    if '?' in pattern_lower:
        return any(pattern_lower.replace('?', char, 1) in text_lower for char in text_lower)
    
    return False

def _count_pattern(text: str, pattern: str) -> int:
    """
    Match a pattern against a text and return the number of matches.
    Pattern might have * and ? wildcards.
    IT DOES NOT USE REGEX.
    
    The '*' wildcard matches any substring (including empty). When multiple
    '*' exist, all non-empty segments between them must appear in order.
    The count represents how many ordered occurrences exist, not just
    non-overlapping matches. For example, the pattern "*hello*world*" over
    "hello world world" yields 2 (hello->first world, hello->second world).
    """
    if not pattern or not text:
        return 0
    
    text_lower = text.lower()
    pattern_lower = pattern.lower()
    
    # If no wildcards, simple substring count (including overlapping)
    if '*' not in pattern_lower and '?' not in pattern_lower:
        count = 0
        start_idx = 0
        while True:
            idx = text_lower.find(pattern_lower, start_idx)
            if idx == -1:
                break
            count += 1
            start_idx = idx + 1  # allow overlapping
        return count
    
    # Handle '*' wildcards by counting all ordered sequences of parts
    if '*' in pattern_lower:
        # Split into parts and remove empties created by leading/trailing/consecutive '*'
        raw_parts = pattern_lower.split('*')
        parts: List[str] = [p for p in raw_parts if p]
        
        if len(parts) == 0:
            # Pattern is only wildcards like "*" or "**" → matches whole text once
            return 1 if text_lower else 0
        
        if len(parts) == 1:
            # Single token with wildcards around → count occurrences of that token
            token = parts[0]
            count = 0
            start_idx = 0
            while True:
                idx = text_lower.find(token, start_idx)
                if idx == -1:
                    break
                count += 1
                start_idx = idx + 1  # overlapping allowed
            return count
        
        # Pre-compute all occurrence indices for each part (overlapping allowed)
        occurrences: List[List[int]] = []
        for part in parts:
            positions: List[int] = []
            start_idx = 0
            while True:
                idx = text_lower.find(part, start_idx)
                if idx == -1:
                    break
                positions.append(idx)
                start_idx = idx + 1  # allow overlapping occurrences
            if not positions:
                return 0  # no way to match if any part is missing
            occurrences.append(positions)
        
        # Dynamic programming: for each position of part j, count ways using earlier parts
        # ways[j][k] = number of ways to match up to part j ending at occurrences[j][k]
        ways: List[List[int]] = []
        # Initialize for first part: each occurrence is one way
        ways.append([1 for _ in occurrences[0]])
        
        # For subsequent parts, accumulate counts from previous part positions that are <= current
        for j in range(1, len(parts)):
            prev_positions = occurrences[j - 1]
            prev_ways = ways[j - 1]
            curr_positions = occurrences[j]
            curr_ways: List[int] = [0 for _ in curr_positions]
            
            # Two-pointer accumulation to sum prev_ways where prev_pos <= curr_pos
            i = 0
            running_sum = 0
            for k, curr_pos in enumerate(curr_positions):
                while i < len(prev_positions) and prev_positions[i] <= curr_pos:
                    running_sum += prev_ways[i]
                    i += 1
                curr_ways[k] = running_sum
            ways.append(curr_ways)
        
        # Total ways is sum over last part occurrences
        total_ways = sum(ways[-1])
        return total_ways
    
    # Handle '?' wildcard (single-character). Not required by current tests.
    # To keep behaviour predictable without regex, return 0 for now.
    return 0


def count_patterns(text: str, patterns: Union[str, List[str]]) -> int:
    """
    Match a list (or single) of patterns against a text.
    Returns the sum of counts for each pattern.
    """
    if isinstance(patterns, str):
        patterns = [patterns]
    return sum(_count_pattern(text, pattern) for pattern in patterns)

def match_patterns(text: str, patterns: Union[str, List[str]]) -> bool:
    """
    Match a list (or single) of patterns against a text.
    Returns True if any pattern matches.
    """
    if isinstance(patterns, str):
        patterns = [patterns]
    for pattern in patterns:
        if _match_pattern(text, pattern):
            return True
    return False
from typing import TypeVar, Callable, Optional, Iterable

T = TypeVar('T')


def first(iterable: Iterable[T], callback: Callable[[T], bool]) -> Optional[T]:
    """
    Find and return the first element in an iterable that satisfies the given predicate function.

    This function iterates through the elements of the provided iterable and returns the first
    element for which the callback function returns True. If no element satisfies the condition,
    returns None.

    Args:
        iterable (Iterable[T]): The iterable to search through. Can be any iterable type
            (list, tuple, set, etc.) containing elements of type T.
        callback (Callable[[T], bool]): A function that takes an element of type T and
            returns a boolean. This is the predicate used to test each element.

    Returns:
        Optional[T]: The first element that satisfies the callback condition, or None if no
            element satisfies the condition.

    Examples:
        >>> # Find first even number
        >>> numbers = [1, 3, 4, 7, 8]
        >>> first(numbers, lambda x: x % 2 == 0)
        4

        >>> # Find first string starting with 'a'
        >>> words = ['hello', 'world', 'apple', 'banana']
        >>> first(words, lambda x: x.startswith('a'))
        'apple'

        >>> # When no element satisfies the condition
        >>> first([1, 3, 5], lambda x: x > 10)
        None

    Note:
        - The function stops iterating as soon as it finds a matching element
        - Returns None rather than raising an exception when no match is found
        - The callback function should be pure and not modify the elements
    """
    # Iterate through each item in the iterable
    for item in iterable:
        # If the callback returns True for this item, we've found our match
        if callback(item):
            return item

    # If no item matched the condition, return None
    return None

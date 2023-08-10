"""
Test for Gmail trash search query functionality.

This test verifies that the search query for trash emails is built correctly
and returns the expected Gmail search syntax.
"""

from gmailwiz import Gmail


def test_trash_search_query():
    """Test that trash search query is built correctly."""
    gmail = Gmail(enable_cache=False)
    
    # Test trash query
    trash_query = gmail._build_search_query(days=30, in_folder='trash')
    print(f"Trash query: {trash_query}")
    
    # Verify the query contains the expected components
    assert "in:trash" in trash_query, f"Query should contain 'in:trash', got: {trash_query}"
    assert "after:" in trash_query, f"Query should contain date range 'after:', got: {trash_query}"
    assert "before:" in trash_query, f"Query should contain date range 'before:', got: {trash_query}"
    
    # Test that the query is valid Gmail syntax
    assert trash_query.count("in:") == 1, f"Query should have exactly one 'in:' clause, got: {trash_query}"
    
    print(f"✓ Trash query test passed: {trash_query}")


def test_trash_vs_inbox_query_difference():
    """Test that trash and inbox queries are different."""
    gmail = Gmail(enable_cache=False)
    
    trash_query = gmail._build_search_query(days=30, in_folder='trash')
    inbox_query = gmail._build_search_query(days=30, in_folder='inbox')
    
    print(f"Trash query:  {trash_query}")
    print(f"Inbox query:  {inbox_query}")
    
    # Verify they are different
    assert trash_query != inbox_query, "Trash and inbox queries should be different"
    assert "in:trash" in trash_query, f"Trash query should contain 'in:trash', got: {trash_query}"
    assert "in:inbox" in inbox_query, f"Inbox query should contain 'in:inbox', got: {inbox_query}"
    
    print("✓ Trash vs inbox query difference test passed")


def test_trash_query_with_other_filters():
    """Test trash query with additional filters."""
    gmail = Gmail(enable_cache=False)
    
    # Test with unread filter
    trash_unread_query = gmail._build_search_query(
        days=30, 
        in_folder='trash', 
        is_unread=True
    )
    
    print(f"Trash unread query: {trash_unread_query}")
    
    # Verify both filters are present
    assert "in:trash" in trash_unread_query, f"Query should contain 'in:trash', got: {trash_unread_query}"
    assert "is:unread" in trash_unread_query, f"Query should contain 'is:unread', got: {trash_unread_query}"
    
    print("✓ Trash query with filters test passed")

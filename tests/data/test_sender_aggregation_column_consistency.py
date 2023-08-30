"""
Test that sender aggregation column lists match exactly with dictionary keys.
"""

import pytest
from gmaildr.data.sender_aggregation import (
    SENDER_DATA_COLUMNS,
    SENDER_DATA_TEXT_COLUMNS,
    AGG_COLUMNS,
    TEXT_AGG_COLUMNS,
    DERIVED_FROM_AGG_COLUMNS,
    TEXT_DERIVED_FROM_AGG_COLUMNS
)


def test_sender_data_columns_consistency():
    """
    Test that SENDER_DATA_COLUMNS matches exactly with the keys from AGG_COLUMNS and DERIVED_FROM_AGG_COLUMNS.
    """
    # Get all column names from the dictionaries
    agg_columns_keys = set(AGG_COLUMNS.keys())
    derived_columns_keys = set(DERIVED_FROM_AGG_COLUMNS.keys())
    all_dictionary_columns = agg_columns_keys.union(derived_columns_keys)
    
    # Get column names from the list
    list_columns = set(SENDER_DATA_COLUMNS)
    
    # They should be exactly equal
    assert all_dictionary_columns == list_columns, (
        f"SENDER_DATA_COLUMNS list does not match dictionary keys!\n"
        f"Dictionary keys ({len(all_dictionary_columns)}): {sorted(all_dictionary_columns)}\n"
        f"List columns ({len(list_columns)}): {sorted(list_columns)}\n"
        f"Missing from list: {sorted(all_dictionary_columns - list_columns)}\n"
        f"Extra in list: {sorted(list_columns - all_dictionary_columns)}"
    )
    
    print(f"✅ SENDER_DATA_COLUMNS consistency check passed!")
    print(f"   {len(AGG_COLUMNS)} AGG_COLUMNS + {len(DERIVED_FROM_AGG_COLUMNS)} DERIVED_FROM_AGG_COLUMNS = {len(list_columns)} total columns")


def test_sender_data_text_columns_consistency():
    """
    Test that SENDER_DATA_TEXT_COLUMNS matches exactly with the keys from TEXT_AGG_COLUMNS and TEXT_DERIVED_FROM_AGG_COLUMNS.
    """
    # Get all column names from the text dictionaries
    text_agg_columns_keys = set(TEXT_AGG_COLUMNS.keys())
    text_derived_columns_keys = set(TEXT_DERIVED_FROM_AGG_COLUMNS.keys())
    all_text_dictionary_columns = text_agg_columns_keys.union(text_derived_columns_keys)
    
    # Get column names from the text list
    text_list_columns = set(SENDER_DATA_TEXT_COLUMNS)
    
    # They should be exactly equal
    assert all_text_dictionary_columns == text_list_columns, (
        f"SENDER_DATA_TEXT_COLUMNS list does not match dictionary keys!\n"
        f"Dictionary keys ({len(all_text_dictionary_columns)}): {sorted(all_text_dictionary_columns)}\n"
        f"List columns ({len(text_list_columns)}): {sorted(text_list_columns)}\n"
        f"Missing from list: {sorted(all_text_dictionary_columns - text_list_columns)}\n"
        f"Extra in list: {sorted(text_list_columns - all_text_dictionary_columns)}"
    )
    
    print(f"✅ SENDER_DATA_TEXT_COLUMNS consistency check passed!")
    print(f"   {len(TEXT_AGG_COLUMNS)} TEXT_AGG_COLUMNS + {len(TEXT_DERIVED_FROM_AGG_COLUMNS)} TEXT_DERIVED_FROM_AGG_COLUMNS = {len(text_list_columns)} total text columns")


def test_no_overlap_between_base_and_text_columns():
    """
    Test that there's no overlap between SENDER_DATA_COLUMNS and SENDER_DATA_TEXT_COLUMNS.
    """
    base_columns = set(SENDER_DATA_COLUMNS)
    text_columns = set(SENDER_DATA_TEXT_COLUMNS)
    
    overlap = base_columns.intersection(text_columns)
    
    assert len(overlap) == 0, (
        f"Found overlap between base and text columns: {sorted(overlap)}\n"
        f"Base columns should be completely separate from text columns."
    )
    
    print(f"✅ No overlap check passed!")
    print(f"   {len(base_columns)} base columns and {len(text_columns)} text columns are completely separate")


def test_all_columns_accounted_for():
    """
    Test that all dictionary keys are accounted for in the column lists.
    """
    # Get all keys from all dictionaries
    all_agg_keys = set(AGG_COLUMNS.keys())
    all_text_agg_keys = set(TEXT_AGG_COLUMNS.keys())
    all_derived_keys = set(DERIVED_FROM_AGG_COLUMNS.keys())
    all_text_derived_keys = set(TEXT_DERIVED_FROM_AGG_COLUMNS.keys())
    
    all_dictionary_keys = all_agg_keys.union(all_text_agg_keys).union(all_derived_keys).union(all_text_derived_keys)
    
    # Get all columns from lists
    all_list_columns = set(SENDER_DATA_COLUMNS).union(set(SENDER_DATA_TEXT_COLUMNS))
    
    # They should be exactly equal
    assert all_dictionary_keys == all_list_columns, (
        f"Total dictionary keys do not match total list columns!\n"
        f"Dictionary keys ({len(all_dictionary_keys)}): {sorted(all_dictionary_keys)}\n"
        f"List columns ({len(all_list_columns)}): {sorted(all_list_columns)}\n"
        f"Missing from lists: {sorted(all_dictionary_keys - all_list_columns)}\n"
        f"Extra in lists: {sorted(all_list_columns - all_dictionary_keys)}"
    )
    
    print(f"✅ All columns accounted for!")
    print(f"   Total: {len(all_list_columns)} columns ({len(SENDER_DATA_COLUMNS)} base + {len(SENDER_DATA_TEXT_COLUMNS)} text)")

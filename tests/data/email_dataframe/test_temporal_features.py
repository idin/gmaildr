from datetime import datetime, timedelta
import random
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
from gmaildr.data.email_dataframe.temporal_features import add_temporal_features
from gmaildr.data.email_dataframe.time_between_emails import add_time_between_emails_features


def test_time_between_emails_features():
    """Test time between emails features with two senders."""
    # Create test data
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    
    # Sender 1: emails every day
    sender1_emails = [
        {'message_id': f's1_{i}', 'sender_email': 'sender1@test.com', 'sender_local_timestamp': base_time + timedelta(days=i)}
        for i in range(5)
    ]
    
    # Sender 2: emails every month
    sender2_emails = [
        {'message_id': f's2_{i}', 'sender_email': 'sender2@test.com', 'sender_local_timestamp': base_time + timedelta(days=i*30)}
        for i in range(5)
    ]
    
    # Shuffle the data to test that sorting and grouping works correctly
    all_emails = sender1_emails + sender2_emails
    random.shuffle(all_emails)
    
    email_df = EmailDataFrame(all_emails)
    result = add_time_between_emails_features(email_df, in_place=False)
    assert result is not None
    # Check features exist
    assert 'time_since_previous_email_days' in result.columns
    assert 'time_to_next_email_days' in result.columns
    assert 'time_since_first_email_days' in result.columns
    assert 'time_to_last_email_days' in result.columns
    
    # Check sender1 values (daily emails)
    sender1_data = result[result['sender_email'] == 'sender1@test.com']
    assert sender1_data.iloc[0]['time_since_previous_email_days'] == 0  # First email
    assert abs(sender1_data.iloc[1]['time_since_previous_email_days'] - 1.0) < 0.001  # 1 day
    assert sender1_data.iloc[4]['time_to_next_email_days'] == 0  # Last email
    assert abs(sender1_data.iloc[3]['time_to_next_email_days'] - 1.0) < 0.001  # 1 day to next
    
    # Check sender2 values (monthly emails)
    sender2_data = result[result['sender_email'] == 'sender2@test.com']
    assert sender2_data.iloc[0]['time_since_previous_email_days'] == 0  # First email
    assert abs(sender2_data.iloc[1]['time_since_previous_email_days'] - 30.0) < 0.001  # 30 days
    assert sender2_data.iloc[4]['time_to_next_email_days'] == 0  # Last email
    assert abs(sender2_data.iloc[3]['time_to_next_email_days'] - 30.0) < 0.001  # 30 days to next

def test_time_between_emails_features_in_place():
    """Test time between emails features with two senders in place."""
    # Create test data
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    
    # Sender 1: emails every day
    sender1_emails = []
    day_diff = 1
    day = 0
    for i in range(5):
        sender1_emails.append(
            {
                'message_id': f's1_{i}', 
                'sender_email': 'sender1@test.com', 
                'sender_local_timestamp': base_time + timedelta(days=day)}
        )
        day_diff += 1
        day += day_diff

    # Shuffle the data to test that sorting and grouping works correctly
    random.shuffle(sender1_emails)
    
    email_df = EmailDataFrame(sender1_emails)
    result = add_time_between_emails_features(email_df, in_place=True)
    assert result is None
    assert 'time_since_previous_email_days' in email_df.columns
    assert 'time_to_next_email_days' in email_df.columns
    assert 'time_since_first_email_days' in email_df.columns
    assert 'time_to_last_email_days' in email_df.columns

    # Check all 5 data points individually (increasing day differences: 0, 1, 3, 6, 10)
    sender1_data = email_df[email_df['sender_email'] == 'sender1@test.com']

    assert isinstance(sender1_data, EmailDataFrame), "filtering is not working correctly. It should return an EmailDataFrame"
    sender1_data = sender1_data.sort_values('sender_local_timestamp')
    assert isinstance(sender1_data, EmailDataFrame), "sorting is not working correctly. It should return an EmailDataFrame"

    # time_since_previous_email_days: 0, 2, 3, 4, 5 (actual gaps from the day pattern)
    assert sender1_data.iloc[0]['time_since_previous_email_days'] == 0  # First email
    assert abs(sender1_data.iloc[1]['time_since_previous_email_days'] - 2.0) < 0.001  # 2 day gap
    assert abs(sender1_data.iloc[2]['time_since_previous_email_days'] - 3.0) < 0.001  # 3 day gap
    assert abs(sender1_data.iloc[3]['time_since_previous_email_days'] - 4.0) < 0.001  # 4 day gap
    assert abs(sender1_data.iloc[4]['time_since_previous_email_days'] - 5.0) < 0.001  # 5 day gap
    
    # time_to_next_email_days: 2, 3, 4, 5, 0 (actual gaps to next emails)
    assert abs(sender1_data.iloc[0]['time_to_next_email_days'] - 2.0) < 0.001  # 2 days to next
    assert abs(sender1_data.iloc[1]['time_to_next_email_days'] - 3.0) < 0.001  # 3 days to next
    assert abs(sender1_data.iloc[2]['time_to_next_email_days'] - 4.0) < 0.001  # 4 days to next
    assert abs(sender1_data.iloc[3]['time_to_next_email_days'] - 5.0) < 0.001  # 5 days to next
    assert sender1_data.iloc[4]['time_to_next_email_days'] == 0  # Last email
    
    # time_since_first_email_days: 0, 2, 5, 9, 14 (actual days from first email)
    assert sender1_data.iloc[0]['time_since_first_email_days'] == 0  # First email
    assert abs(sender1_data.iloc[1]['time_since_first_email_days'] - 2.0) < 0.001  # Day 2
    assert abs(sender1_data.iloc[2]['time_since_first_email_days'] - 5.0) < 0.001  # Day 5
    assert abs(sender1_data.iloc[3]['time_since_first_email_days'] - 9.0) < 0.001  # Day 9
    assert abs(sender1_data.iloc[4]['time_since_first_email_days'] - 14.0) < 0.001  # Day 14
    
    # time_to_last_email_days: 14, 12, 9, 5, 0 (actual days to last email)
    assert abs(sender1_data.iloc[0]['time_to_last_email_days'] - 14.0) < 0.001  # 14 days to last
    assert abs(sender1_data.iloc[1]['time_to_last_email_days'] - 12.0) < 0.001  # 12 days to last
    assert abs(sender1_data.iloc[2]['time_to_last_email_days'] - 9.0) < 0.001  # 9 days to last
    assert abs(sender1_data.iloc[3]['time_to_last_email_days'] - 5.0) < 0.001  # 5 days to last
    assert sender1_data.iloc[4]['time_to_last_email_days'] == 0  # Last email


def test_add_temporal_features():
    """Test basic temporal features like day_of_week, hour_of_day, etc."""
    # Create test data with specific timestamps
    test_data = [
        {
            'message_id': 'msg1',
            'sender_email': 'test@example.com',
            'timestamp': datetime(2024, 1, 15, 14, 30, 0),  # Monday, 2:30 PM
            'sender_local_timestamp': datetime(2024, 1, 15, 9, 30, 0)  # Monday, 9:30 AM (local)
        },
        {
            'message_id': 'msg2', 
            'sender_email': 'test@example.com',
            'timestamp': datetime(2024, 1, 20, 22, 15, 0),  # Saturday, 10:15 PM
            'sender_local_timestamp': datetime(2024, 1, 20, 19, 15, 0)  # Saturday, 7:15 PM (local)
        }
    ]
    
    email_df = EmailDataFrame(test_data)
    result = add_temporal_features(email_df, in_place=False)
    assert result is not None
    # Check that all temporal features were added
    assert 'day_of_week' in result.columns
    assert 'hour_of_day' in result.columns
    assert 'is_weekend' in result.columns
    assert 'is_business_hour' in result.columns
    assert 'sender_time_difference_hours' in result.columns
    
    # Check day_of_week values (Monday=0, Saturday=5)
    assert result.iloc[0]['day_of_week'] == 0  # Monday
    assert result.iloc[1]['day_of_week'] == 5  # Saturday
    
    # Check hour_of_day values (from sender_local_timestamp)
    assert result.iloc[0]['hour_of_day'] == 9   # 9:30 AM
    assert result.iloc[1]['hour_of_day'] == 19  # 7:15 PM
    
    # Check is_weekend values
    assert result.iloc[0]['is_weekend'] == False  # Monday
    assert result.iloc[1]['is_weekend'] == True   # Saturday
    
    # Check is_business_hour values (9-17)
    assert result.iloc[0]['is_business_hour'] == True   # 9:30 AM
    assert result.iloc[1]['is_business_hour'] == False  # 7:15 PM
    
    # Check sender_time_difference_hours (timestamp - sender_local_timestamp)
    assert abs(result.iloc[0]['sender_time_difference_hours'] - 5.0) < 0.001  # 5 hour difference
    assert abs(result.iloc[1]['sender_time_difference_hours'] - 3.0) < 0.001  # 3 hour difference
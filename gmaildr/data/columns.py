EMAIL_DF_CORE_COLUMNS = [
    # Core required columns (always present)
    'message_id', 'sender_email', 'sender_name', 'recipient_email', 'recipient_name', 
    'subject', 'timestamp', 'sender_local_timestamp',
    
    # Size information
    'size_bytes', 'size_kb',
    
    # Email status
    'has_attachments', 'is_read', 'is_important', 'is_starred', 'is_forwarded', 'in_folder',
    
    # Metadata
    'labels', 'thread_id', 'snippet',
    
    # Date components (auto-generated)
    'year', 'month', 'day', 'hour', 'day_of_week',
    
    # Language detection
    'subject_language', 'subject_language_confidence', 'text_language', 'text_language_confidence',
    
    # Email classification
    'has_role_based_email'
]

EMAIL_DF_OPTIONAL_COLUMNS = [
    # Optional columns (conditional)
    'text_content',  # When include_text=True
    'cluster'        # After running clustering
]

EMAIL_DF_EXTENDED_METRICS_COLUMNS = [
    # Extended schema with metrics (when include_metrics=True and include_text=True)
    # Content analysis metrics
    'word_count', 'sentence_count', 'avg_sentence_length', 'capitalization_ratio',
    'question_count', 'exclamation_count', 'url_count', 'email_count', 'phone_count',
    
    # Sentiment & style metrics
    'sentiment_score', 'formality_score', 'readability_score', 'complexity_score',
    
    # Human detection metrics
    'human_score', 'is_human_sender', 'content_score', 'sender_score', 
    'behavioural_score', 'conversation_score'
]

# Complete list of all possible EmailDataFrame columns
EMAIL_DF_COLUMNS = EMAIL_DF_CORE_COLUMNS + EMAIL_DF_OPTIONAL_COLUMNS + EMAIL_DF_EXTENDED_METRICS_COLUMNS

# Core ML features (always available)
EMAIL_ML_DF_CORE_COLUMNS = [
    # Core numeric features
    'size_bytes', 'size_kb', 'year',
    
    # Periodic features (sin/cos encoded) - CRUCIAL for ML
    'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 
    'day_of_year_sin', 'day_of_year_cos',
    
    # Boolean features (converted to int)
    'has_attachments', 'is_read', 'is_important',
    
    # Language features
    'subject_language_confidence',
    
    # Role-based features
    'has_role_based_email',
    
    # Categorical features (one-hot encoded) - CRUCIAL for ML
    'in_folder_inbox', 'in_folder_archive', 'in_folder_spam', 'in_folder_trash', 
    'in_folder_drafts', 'in_folder_sent', 'in_folder_nan',
    
    # Required identifier
    'message_id'
]

# Optional ML features (only available when text content is available)
EMAIL_ML_DF_OPTIONAL_COLUMNS = [
    # Individual email text analysis features (if they exist in input)
    'word_count', 'sentence_count', 'avg_sentence_length', 'capitalization_ratio',
    'question_count', 'exclamation_count', 'url_count', 'email_count', 'phone_count',
    
    # Individual email analysis metrics (if they exist in input)
    'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
    'has_promotional_content', 'has_tracking_pixels', 'has_bulk_email_indicators',
    'external_link_count', 'image_count', 'caps_word_count',
    'html_to_text_ratio', 'link_to_text_ratio', 'caps_ratio', 'promotional_word_ratio'
]

# Complete list of all possible ML features
EMAIL_ML_DF_COLUMNS = EMAIL_ML_DF_CORE_COLUMNS + EMAIL_ML_DF_OPTIONAL_COLUMNS

EMAIL_ML_SHOULD_NOT_HAVE_COLUMNS = [
    'sender_email', 'timestamp', 'sender_local_timestamp', 'subject', 'text_content', 'thread_id', 'recipient_email', 'labels'
]

SENDER_DF_COLUMNS = [
    # Core aggregation features
    'sender_email', 'total_emails', 'unique_subjects', 'unique_threads',
    'first_email_timestamp', 'last_email_timestamp', 'date_range_days', 'emails_per_day',
    
    # Size metrics
    'total_size_bytes', 'mean_email_size_bytes', 'max_email_size_bytes', 
    'min_email_size_bytes', 'std_email_size_bytes',
    
    # Status ratios
    'read_ratio', 'important_ratio', 'starred_ratio',
    
    # Language metrics
    'subject_primary_language', 'subject_language_diversity', 'english_subject_ratio',
    'mean_subject_language_confidence', 'text_primary_language', 'text_language_diversity',
    'english_text_ratio', 'mean_text_language_confidence',
    
    # Role-based metrics
    'is_role_based_sender', 'role_based_emails_count', 'role_based_emails_ratio',
    
    # Temporal metrics
    'most_active_day', 'weekend_ratio', 'most_active_hour', 'business_hours_ratio',
    
    # Text metrics
    'mean_subject_length_chars', 'std_subject_length_chars', 'mean_text_length_chars',
    'std_text_length_chars',
    
    # Additional metrics
    'inbox_count', 'archive_count', 'trash_count', 'unique_recipients', 'recipient_diversity',
    'most_common_recipient', 'forwarded_emails_count', 'forwarded_emails_ratio',
    'subject_length_variation_coef', 'text_length_variation_coef', 'domain',
    'is_personal_domain', 'name_consistency', 'display_name', 'name_variations',
    'unique_subject_ratio'
]

SENDER_ML_DF_COLUMNS = [
    # Core features (sin/cos encoded)
    'sender_email', 'total_emails', 'unique_subjects', 'mean_email_size_bytes',
    'total_emails_sin', 'total_emails_cos', 'unique_subjects_sin', 'unique_subjects_cos',
    'mean_email_size_sin', 'mean_email_size_cos',
    
    # Temporal entropy features (sin/cos encoded)
    'day_of_week_entropy_sin', 'day_of_week_entropy_cos', 'hour_of_day_entropy_sin', 
    'hour_of_day_entropy_cos',
    
    # Ratio features (sin/cos encoded)
    'weekend_ratio_sin', 'weekend_ratio_cos', 'business_hours_ratio_sin', 
    'business_hours_ratio_cos', 'burst_days_ratio_sin', 'burst_days_ratio_cos',
    
    # Additional numeric features
    'date_range_days', 'emails_per_day', 'total_size_bytes', 'max_email_size_bytes',
    'min_email_size_bytes', 'std_email_size_bytes', 'read_ratio', 'important_ratio',
    'starred_ratio', 'subject_language_diversity', 'english_subject_ratio',
    'mean_subject_language_confidence', 'text_language_diversity', 'english_text_ratio',
    'mean_text_language_confidence', 'mean_subject_length_chars', 'std_subject_length_chars',
    'mean_text_length_chars', 'std_text_length_chars', 'inbox_count', 'archive_count',
    'trash_count', 'role_based_emails_count', 'role_based_emails_ratio',
    'unique_recipients', 'recipient_diversity', 'forwarded_emails_count',
    'forwarded_emails_ratio', 'subject_length_variation_coef', 'text_length_variation_coef',
    'name_variations', 'unique_subject_ratio',
    
    # Boolean features
    'is_role_based_sender', 'is_personal_domain', 'name_consistency',
    
    # Categorical features (one-hot encoded)
    'domain_gmail.com', 'domain_yahoo.com', 'domain_hotmail.com', 'domain_outlook.com',
    'domain_other', 'most_active_day_monday', 'most_active_day_tuesday',
    'most_active_day_wednesday', 'most_active_day_thursday', 'most_active_day_friday',
    'most_active_day_saturday', 'most_active_day_sunday', 'most_active_day_nan',
    'subject_primary_language_en', 'subject_primary_language_other',
    'text_primary_language_en', 'text_primary_language_other'
]

SENDER_ML_SHOULD_NOT_HAVE_COLUMNS = [
    'first_email_timestamp', 'last_email_timestamp', 'display_name', 'most_common_recipient'
]
# youtube_limits.py

# --- YouTube Limits Constants (Defaults) ---
# These act as fallbacks if not provided by the calling script
DEFAULT_YOUTUBE_DESCRIPTION_LIMIT = 4090
DEFAULT_YOUTUBE_TAG_LIMIT = 100
DEFAULT_YOUTUBE_TOTAL_TAGS_LIMIT = 470
DEFAULT_YOUTUBE_MAX_TAGS_COUNT = 40
# --- End Constants ---


def validate_description(
    description: str,
    limit: int = DEFAULT_YOUTUBE_DESCRIPTION_LIMIT # Accept limit as argument
) -> tuple[str, list[str]]:
    """
    Validates and truncates a description to meet YouTube's character limit.

    Args:
        description: The original video description string.
        limit: The character limit to enforce.

    Returns:
        A tuple containing:
            - The validated (potentially truncated) description string.
            - A list of warning messages generated during validation.
    """
    warnings = []
    if not description:
        return "", warnings

    description = str(description) # Ensure string type

    if len(description) > limit: # Use the passed 'limit' argument
        warnings.append(f"Description length ({len(description)}) exceeds limit ({limit}), truncated.")

        truncated = description[:limit]
        last_space = truncated.rfind(' ')

        # Use percentage of the *actual limit* being used
        if last_space > limit * 0.9:
             validated_description = truncated[:last_space].strip()
        else:
             validated_description = truncated.strip()

        return validated_description, warnings

    return description, warnings


def validate_tags(
    tags: list,
    tag_char_limit: int = DEFAULT_YOUTUBE_TAG_LIMIT,        # Accept limits as arguments
    total_char_limit: int = DEFAULT_YOUTUBE_TOTAL_TAGS_LIMIT,
    max_count_limit: int = DEFAULT_YOUTUBE_MAX_TAGS_COUNT
) -> tuple[list[str], list[str]]:
    """
    Validates and optimizes a list of tags to meet YouTube's limits.

    Args:
        tags: A list of tag strings.
        tag_char_limit: Max characters allowed per individual tag.
        total_char_limit: Max total characters allowed for all tags combined.
        max_count_limit: Max number of tags allowed.

    Returns:
        A tuple containing:
            - The validated list of tag strings.
            - A list of warning messages generated during validation.
    """
    warnings = []
    if not tags or not isinstance(tags, list):
        return [], warnings

    # --- Step 1: Clean and Normalize Tags ---
    cleaned_tags = []
    for i, tag in enumerate(tags):
        if not tag or not isinstance(tag, str) or not tag.strip():
            continue
        clean_tag = tag.strip()
        if clean_tag: cleaned_tags.append(clean_tag)
    # --- End Cleaning ---


    # --- Step 2: Apply Limits (using passed arguments) ---
    valid_tags = []
    total_chars = 0
    tag_count = 0
    limits_hit = False

    for tag in cleaned_tags:
        if limits_hit: break

        # 2a. Check Max Tag Count
        if tag_count >= max_count_limit: # Use argument
            if not limits_hit: warnings.append(f"Max tag count ({max_count_limit}) reached. Remaining tags skipped.")
            limits_hit = True
            continue

        # 2b. Check/Truncate Individual Tag Length
        original_tag_repr = f"'{tag[:30]}...'" if len(tag) > 30 else f"'{tag}'"
        if len(tag) > tag_char_limit: # Use argument
            tag = tag[:tag_char_limit].strip()
            warnings.append(f"Tag {original_tag_repr} truncated to '{tag}' (>{tag_char_limit} chars).")

        current_tag_len = len(tag)
        if current_tag_len == 0: continue

        # 2c. Check Total Character Count
        separator_len = 1 if valid_tags else 0
        prospective_total = total_chars + current_tag_len + separator_len

        if prospective_total > total_char_limit: # Use argument
            if not limits_hit: warnings.append(f"Total tag char limit (~{total_char_limit}) reached. Remaining tags skipped.")
            limits_hit = True
            continue

        # --- Add the tag (avoid duplicates) ---
        if tag not in valid_tags:
            valid_tags.append(tag)
            total_chars += current_tag_len + separator_len
            tag_count += 1

    # --- End Applying Limits ---

    return valid_tags, warnings
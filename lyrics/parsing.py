import logging


def lrc_to_dictionary(lrc):
    if not lrc:
        return {}

    lines = lrc.strip().split('\n')
    lrc_dict = {}

    for line in lines:
        # Skip lines that don't have a timestamp or are too short
        if "]" not in line or not line.startswith("["):
            continue

        try:
            timestamp_part, lyric = line.split(']', 1)
            timestamp = timestamp_part[1:]
            lyric = lyric.strip()
            minutes, seconds = timestamp.split(':')
            total_ms = int(minutes) * 60 * 1000 + float(seconds) * 1000
            lrc_dict[int(total_ms)] = lyric
        except (ValueError, IndexError):
            # Edge cases
            logging.warning(f"Skipping malformed LRC line: {line}")
            continue

    return lrc_dict

from flags.state import flag_state


def bitcaster_enabled() -> bool:
    return bool(flag_state("BITCASTER_ENABLED"))

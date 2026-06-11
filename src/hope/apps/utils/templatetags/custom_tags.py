from django import template

register = template.Library()


@register.simple_tag
def greeting(first_name: str | None, last_name: str | None) -> str:
    """Build the email salutation line from a recipient's name.

    Returns ``"Dear First Last,"`` when a name is present and ``"Dear,"`` when both
    parts are empty — avoiding the double/trailing space that a literal template
    space would leave (e.g. ``"Dear ,"``). Used in both HTML and plain-text emails.
    """
    name = " ".join(part for part in (first_name, last_name) if part)
    return f"Dear {name}," if name else "Dear,"

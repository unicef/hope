from django import template

register = template.Library()


@register.inclusion_tag("universal_table.html")
def universal_table(title, page, row_template, headers):
    return {
        "title": title,
        "page": page,
        "row_template": row_template,
        "headers": headers,
    }

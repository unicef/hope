from django import template

register = template.Library()


@register.inclusion_tag("universal_table.html")
def universal_table(title, page, row_template, headers, page_size, page_sizes=[10, 25, 50]):
    return {
        "title": title,
        "page": page,
        "row_template": row_template,
        "headers": headers,
        "page_size": page_size,
        "page_sizes": page_sizes,
    }

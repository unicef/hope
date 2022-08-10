import difflib
import json
from difflib import _mdiff

from django import template
from django.utils.safestring import mark_safe

from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

register = template.Library()


class HtmlDiff(difflib.HtmlDiff):
    def _format_line(self, side, flag, linenum, text):
        try:
            linenum = "{}".format(linenum)
            id = f' id="{self._prefix[side]}{linenum}"'
        except TypeError:
            id = ""
        text = text.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")
        text = text.replace(" ", "&nbsp;").rstrip()

        return f'<td class="diff_header lineno"{id}>{linenum}</td><td class="code" nowrap="nowrap">{text}</td>'

    def make_table(self, fromlines, tolines, fromdesc="", todesc="", context=False, numlines=5):
        """Returns HTML table of side by side comparison with change highlights

        Arguments:
        fromlines -- list of "from" lines
        tolines -- list of "to" lines
        fromdesc -- "from" file column header string
        todesc -- "to" file column header string
        context -- set to True for contextual differences (defaults to False
            which shows full differences).
        numlines -- number of context lines.  When context is set True,
            controls number of lines displayed before and after the change.
            When context is False, controls the number of lines to place
            the "next" link anchors before the next change (so click of
            "next" link jumps to just before the change).
        """

        # make unique anchor prefixes so that multiple tables may exist
        # on the same page without conflict.
        self._make_prefix()

        # change tabs to spaces before it gets more difficult after we insert
        # markup
        fromlines, tolines = self._tab_newline_replace(fromlines, tolines)

        # create diffs iterator which generates side by side from/to data
        if context:
            context_lines = numlines
        else:
            context_lines = None
        diffs = _mdiff(
            fromlines,
            tolines,
            context_lines,
            linejunk=self._linejunk,
            charjunk=self._charjunk,
        )

        # set up iterator to wrap lines that exceed desired width
        if self._wrapcolumn:
            diffs = self._line_wrapper(diffs)

        # collect up from/to lines and flags into lists (also format the lines)
        fromlist, tolist, flaglist = self._collect_lines(diffs)

        # process change flags, generating middle column of next anchors/links
        fromlist, tolist, flaglist, next_href, next_id = self._convert_flags(
            fromlist, tolist, flaglist, context, numlines
        )

        s = []
        fmt = '<tr><td class="diff_next"{}>{}</td>{}<td class="diff_next">{}</td>{}</tr>\n'
        for i in range(len(flaglist)):
            if flaglist[i] is None:
                # mdiff yields None on separator lines skip the bogus ones
                # generated for the first line
                if i > 0:
                    s.append("        </tbody>        \n        <tbody>\n")
            else:
                s.append(fmt.format(next_id[i], next_href[i], fromlist[i], next_href[i], tolist[i]))
        if fromdesc or todesc:
            header_row = "<thead><tr>{}{}{}{}</tr></thead>".format(
                '<th class="diff_next"><br /></th>',
                '<th colspan="2" class="diff_header">{}</th>'.format(fromdesc),
                '<th class="diff_next"><br /></th>',
                '<th colspan="2" class="diff_header">{}</th>'.format(todesc),
            )
        else:
            header_row = ""

        table = self._table_template % dict(data_rows="".join(s), header_row=header_row, prefix=self._prefix[1])

        return (
            table.replace("\0+", '<span class="diff_add">')
            .replace("\0-", '<span class="diff_sub">')
            .replace("\0^", '<span class="diff_chg">')
            .replace("\1", "</span>")
            .replace("\t", "&nbsp;")
        )


@register.filter(name="getattr")
def get_attr(d, v):
    return getattr(d, v)


@register.simple_tag
def define(val=None):
    return val


@register.filter
def adults(hh):
    return hh.members.filter(age__gte=18, age__lte=65, work__in=["fulltime", "seasonal", "parttime"]).count()


@register.filter
def pretty_json(json_object):
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    lex = lexers.get_lexer_by_name("json")
    return mark_safe(highlight(json_str, lex, HtmlFormatter()))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def pygmentize(code):
    formatter = HtmlFormatter(linenos=True)
    lex = lexers.get_lexer_by_name("python")
    formatted_code = highlight(code, lex, formatter)
    return mark_safe(formatted_code)


@register.filter
def diff(commit, panels="before,after"):
    rule = commit.rule
    left_panel, right_panel = [], []
    right_label = "No data"
    if panels == "before,after":
        left_label = "No Data (First Commit"
        if "definition" in commit.before:
            left_label = f"Version before commit ({commit.prev.version})"
            left_panel = commit.before["definition"].split("\n")

        right_label = f"Version after commit ({commit.version})"
        right_panel = commit.after["definition"].split("\n")
    elif panels == "after,current":
        left_label = f"Version commit ({commit.version})"
        left_panel = commit.after["definition"].split("\n")

        right_label = f"Version current ({rule.version})"
        right_panel = rule.definition.split("\n")
    elif panels == "before,current":
        left_label = f"Version  commit ({commit.version})"
        left_panel = commit.after["definition"].split("\n")

        right_label = f"Version current ({rule.version})"
        right_panel = rule.definition.split("\n")
    else:
        raise Exception(f"Invalid value for panels: `{panels}`")
    return mark_safe(HtmlDiff(wrapcolumn=80).make_table(left_panel, right_panel, left_label, right_label))

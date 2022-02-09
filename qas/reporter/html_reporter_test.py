#!/usr/bin/env python3


import unittest
from jinja2 import Environment, BaseLoader


class TestJinja(unittest.TestCase):
    def test_jinja(self):
        tpl = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>My Webpage</title>
        </head>
        <body>
            <ul id="navigation">
            {% for item in navigation %}
                <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
            {% endfor %}
            </ul>

            <h1>My Webpage</h1>
            {{ a_variable }}

            {# a comment #}
        </body>
        </html>
        """

        template = Environment(loader=BaseLoader).from_string(tpl)
        data = template.render(navigation=[{
            "href": "href1",
            "caption": "caption1",
        }, {
            "href": "href2",
            "caption": "caption2",
        }], a_variable="hello world")
        print(data)


tpl = """key: {{ val.key }}
{% for sub in val.subs %}
{% print(render(sub)) %}
{% endfor %}
"""


class TestJinja2(unittest.TestCase):
    def setUp(self) -> None:
        env = Environment(loader=BaseLoader)
        env.globals.update(render=self.render)
        self.template = env.from_string(tpl)

    def render(self, val):
        return "\n".join(["  " + line for line in self.template.render(val=val).split("\n")])

    def test_recursive(self):
        res = self.template.render(val={
            "key": "val1",
            "subs": [{
                "key": "val2",
                "subs": [{
                    "key": "val3",
                }]
            }, {
                "key": "val4",
                "subs": [{
                    "key": "val5"
                }, {
                    "key": "val6"
                }]
            }]
        })
        print(res)


if __name__ == "__main__":
    unittest.main()

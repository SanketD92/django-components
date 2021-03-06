from textwrap import dedent

from django.template import Context, Template
from django.test import SimpleTestCase

from django_components import component

from .django_test_setup import *  # NOQA


class SimpleComponent(component.Component):
    def context(self, variable, variable2="default"):
        return {
            "variable": variable,
            "variable2": variable2,
        }

    def template(self, context):
        return "simple_template.html"

    class Media:
        css = {"all": ["style.css"]}
        js = ["script.js"]

class IffedComponent(SimpleComponent):
    def template(self, context):
        return "iffed_template.html"

class ComponentTemplateTagTest(SimpleTestCase):
    def setUp(self):
        # NOTE: component.registry is global, so need to clear before each test
        component.registry._registry = {}

    def test_single_component_dependencies(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template('{% load component_tags %}{% component_dependencies %}')
        rendered = template.render(Context())
        self.assertHTMLEqual(rendered, dedent("""
            <link href="style.css" type="text/css" media="all" rel="stylesheet">
            <script type="text/javascript" src="script.js"></script>
        """).strip())

    def test_single_component(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template('{% load component_tags %}{% component name="test" variable="variable" %}')
        rendered = template.render(Context({}))
        self.assertHTMLEqual(rendered, "Variable: <strong>variable</strong>\n")

    def test_call_component_with_two_variables(self):
        component.registry.register(name="test", component=IffedComponent)

        template = Template('{% load component_tags %}{% component name="test" variable="variable" variable2="hej" %}')
        rendered = template.render(Context({}))
        self.assertHTMLEqual(rendered, dedent("""
            Variable: <strong>variable</strong>
            Variable2: <strong>hej</strong>
        """))

    def test_component_called_with_positional_name(self):
        component.registry.register(name="test", component=SimpleComponent)

        template = Template('{% load component_tags %}{% component "test" variable="variable" %}')
        rendered = template.render(Context({}))
        self.assertHTMLEqual(rendered, "Variable: <strong>variable</strong>\n")

    def test_multiple_component_dependencies(self):
        component.registry.register(name="test1", component=SimpleComponent)
        component.registry.register(name="test2", component=SimpleComponent)

        template = Template('{% load component_tags %}{% component_dependencies %}')
        rendered = template.render(Context())
        self.assertHTMLEqual(rendered, dedent("""
            <link href="style.css" type="text/css" media="all" rel="stylesheet">
            <script type="text/javascript" src="script.js"></script>
        """).strip())

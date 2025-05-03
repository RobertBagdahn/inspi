from django.forms import TextInput
from django.utils.html import format_html


class HtmxAutocompleteWidget(TextInput):
    """A widget that provides an HTMX-powered autocomplete field."""
    
    template_name = 'autocomplete/widgets/htmx_autocomplete.html'
    
    def __init__(self, url, min_chars=2, *args, **kwargs):
        self.url = url
        self.min_chars = min_chars
        super().__init__(*args, **kwargs)
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # Add HTMX attributes to the widget
        widget_attrs = context['widget']['attrs']
        widget_attrs.update({
            'hx-get': self.url,
            'hx-trigger': f'keyup changed delay:500ms',
            'hx-target': f'#{name}-results',
            'hx-indicator': f'#{name}-indicator',
            'hx-params': '*',
            'name': '' + name + '[]',
            'autocomplete': 'off',
        })
        
        return context
    
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        
        # Create the full widget HTML with results container and loading indicator
        html = format_html(
            """
            <div class="htmx-autocomplete-container relative">
                {}
                <div id="{}-indicator" class="htmx-indicator absolute right-2 top-2 hidden">
                    <svg class="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                </div>
                <div id="{}-results" class="absolute z-10 w-full mt-1 bg-white shadow-lg rounded-md max-h-60 overflow-auto"></div>
            </div>
            """,
            input_html,
            name,
            name
        )
        
        return html

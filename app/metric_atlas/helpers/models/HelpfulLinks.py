from dataclasses import dataclass, field
import streamlit as st


@dataclass
class HelpfulLinks:
    """
    A dataclass for the helpful links block that is used in sidebars and other places.
    """

    links: list = field(default_factory=lambda: [])

    def __post_init__(self):
        self.links = [
            {"label": "Metabase Dashboards", "url": "https://fleetio.metabaseapp.com"},
            {
                "label": "Data Request Form",
                "url": "https://form.asana.com/?k=HR7Xb-fmiP4aaWYs8jG1yw&d=106485643367",
            },
            {
                "label": "Data Team Notion",
                "url": "https://www.notion.so/fleetio/Data-Analytics-Team-3399685778604edbaf3af09b88480964",
            },
        ]

    def render(self):
        """
        A method that returns the st.info() component with helpful links.
        """

        info_body = "### Helpful Links  \n"
        for link in self.links:
            info_body += f"[{link['label']}]({link['url']})  \n"

        return st.info(info_body)

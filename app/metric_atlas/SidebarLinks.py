from dataclasses import dataclass
import streamlit as st


@dataclass
class SidebarLinks:
    """
    A dataclass for the helpful links block that is used in sidebars and other places.
    """

    links: list

    def render(self):
        """
        A method that returns the st.info() component with helpful links.
        """

        info_body = "### Helpful Links  \n"
        for link in self.links:
            info_body += f"[{link['label']}]({link['url']})  \n"

        return st.info(info_body)

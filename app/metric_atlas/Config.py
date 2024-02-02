from dataclasses import dataclass
import yaml


@dataclass
class Config:
    """
    A dataclass for configuration variables.
    """

    # App
    config_file_path: str = "config/config.yml"
    logo_url: str = None
    name: str = None
    sidebar_links: list[dict] = None
    how_to_videos: list[dict] = None
    enable_sample_data_mode: bool = True
    metric_categories: list[dict] = None
    home_page_key_metrics: list[dict] = None

    def __post_init__(self):
        # Load Config
        with open(self.config_file_path, "r") as f:
            config = yaml.safe_load(f)

        self.enable_sample_data_mode = config.get("app").get(
            "enable_sample_data_mode", True
        )
        self.logo_url = config.get("app").get("logo_url", None)
        self.name = config.get("app").get("name", None)
        self.sidebar_links = config.get("app").get("sidebar_links", None)
        self.how_to_videos = config.get("app").get("how_to_videos", None)

        self.metric_categories = config.get("metric_categories", None)

        self.home_page_key_metrics = config.get("home_page").get("key_metrics", None)

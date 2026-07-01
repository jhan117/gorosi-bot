from src.crawlers.seoultech import SeoultechCrawler
from src.crawlers.housing import HousingCrawler
from src.crawlers.internship import InternshipCrawler

def get_crawler(crawler_type: str, url: str):
    """
    Factory function to get the appropriate crawler instance based on type.
    """
    crawlers = {
        "seoultech": SeoultechCrawler,
        "housing": HousingCrawler,
        "internship": InternshipCrawler
    }
    
    crawler_class = crawlers.get(crawler_type)
    if not crawler_class:
        raise ValueError(f"Unknown crawler type: {crawler_type}")
        
    return crawler_class(url)

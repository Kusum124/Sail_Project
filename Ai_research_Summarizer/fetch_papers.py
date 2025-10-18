import arxiv

def fetch_latest_papers(query="machine learning", max_results=5):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title.strip(),
            "summary": result.summary.strip(),
            "link": result.entry_id.strip()
        })
    return papers

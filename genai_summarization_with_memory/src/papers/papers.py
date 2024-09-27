import logging
from bs4 import BeautifulSoup
from src.database.database import insert_paper
from src.llm.llm import generate_llm_response
from src.memory.memory import get_mem0_memory
from src.utils.http_requests import make_http_request

def extract_abstract_from_url(url):
    """
    Retrieve the abstract section from an HTML page.
    """
    response = make_http_request(
        url=url,
        method='GET',
        return_type='html'
    )
    if not response:
        return "Failed to retrieve the page"

    soup = BeautifulSoup(response, 'html.parser')
    abstract_section = soup.find('blockquote', class_='abstract')
    if not abstract_section:
        return "Abstract not found"

    abstract = abstract_section.get_text(separator=' ', strip=True)
    return abstract


def get_papers_from_url(url):
    """Retrieve papers from the specified URL."""
    response = make_http_request(url=url, method="GET", return_type="html")
    if isinstance(response, str) and response.startswith("Error"):
        print(response)
        return []

    soup = BeautifulSoup(response, 'html.parser')
    papers = soup.find_all('article')
    return_list = []

    for paper in papers:
        title_tag = paper.find('h3')
        title = title_tag.text.strip() if title_tag else 'No title'
        link_tag = paper.find('a', href=True)
        link = f"https://huggingface.co{link_tag['href']}" if link_tag else 'No link'
        paper_id = link.split('/')[-1]

        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Id: {paper_id}")
        print("-" * 40)

        return_paper = {
            "title": title,
            "link": link,
            "id": paper_id
        }
        return_list.append(return_paper)

    return return_list


def get_daily_papers(input_data):
    """Retrieve daily papers from the specified input data source."""
    if input_data.startswith('http'):
        return get_papers_from_url(input_data)
    else:
        print("Input data source not supported.")
        return []


def convert_paper_to_diary_entry(paper, config, model_name):
    """
    Convert a paper to a diary entry from the author's perspective using the LLM.
    """
    diary_prompt = f'''Write a diary entry from the perspective of an author who has just completed a research paper. Reflect on the challenges faced during the research, the key discoveries made, and the significance of the findings. Discuss any innovative methods or frameworks introduced and their implications for the field. Conclude with feelings of pride and anticipation for the community's response to the work.

Paper Details:
    ID: {paper['id']}
    Title: {paper['title']}
    Link: {paper['link']}
    Abstract: {paper['abstract']}
    '''

    print(diary_prompt)
    diary_response = generate_llm_response(diary_prompt, model_name, config)
    return diary_response


def process_daily_papers(source_url, config, config_file=None, test=False):
    """Main command to fetch papers and store them."""
    mem0_memory = get_mem0_memory(config, config_file=config_file)

    # Fetch the daily papers from the specified source URL
    daily_papers = get_daily_papers(source_url)

    if not daily_papers:
        print("No papers found or an error occurred.")
        return

    # Iterate over the fetched papers and process them
    paper_count = 0
    for paper in daily_papers:
        paper_id = paper['id']
        arxiv_url = f"https://arxiv.org/abs/{paper_id}"
        
        # Extract the abstract from the corresponding arXiv page
        abstract = extract_abstract_from_url(url=arxiv_url)
        paper['abstract'] = abstract

        # Insert the paper into the SQLite database
        insert_paper(paper)

        # Convert the paper details into a diary entry format and add it to memory
        diary_entry = convert_paper_to_diary_entry(paper, config, 'w1')
        response = mem0_memory.add(diary_entry, "papers_memory")
        print(f"Added memory: {response}")

        paper_count += 1
        if test and paper_count >= 1:
            break

    print(f"Processed {paper_count} paper(s) successfully.")

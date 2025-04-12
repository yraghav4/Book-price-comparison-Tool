import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- Website 1: BooksToScrape ---
def scrape_books_to_scrape(query):
    books = []
    for page in range(1, 4):
        url = f"http://books.toscrape.com/catalogue/page-{page}.html"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.select('article.product_pod')
        for item in items:
            title = item.h3.a['title']
            price = item.select_one('.price_color').text.replace('£', '₹')
            if query.lower() in title.lower():
                books.append({
                    'Title': title,
                    'Author': 'N/A',
                    'Price': price,
                    'Website': 'BooksToScrape'
                })
    return books

# --- Website 2: OpenLibrary ---
def scrape_openlibrary(query):
    books = []
    url = f"https://openlibrary.org/search?q={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.select('.searchResultItem')
    for item in items[:10]:
        title_elem = item.select_one('a')
        author_elem = item.select_one('.bookauthor')
        title = title_elem.text.strip() if title_elem else "Unknown"
        author = author_elem.text.strip() if author_elem else "Unknown"
        books.append({
            'Title': title,
            'Author': author,
            'Price': 'Free',
            'Website': 'OpenLibrary'
        })
    return books

# --- Website 3: Project Gutenberg ---
def scrape_gutenberg(query):
    books = []
    url = f"https://www.gutenberg.org/ebooks/search/?query={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.select('li.booklink')
    for item in items[:10]:
        title_elem = item.select_one('span.title')
        author_elem = item.select_one('span.subtitle')
        title = title_elem.text.strip() if title_elem else "Unknown"
        author = author_elem.text.strip() if author_elem else "Unknown"
        books.append({
            'Title': title,
            'Author': author,
            'Price': 'Free',
            'Website': 'Gutenberg'
        })
    return books

# --- Website 4: BetterWorldBooks ---
def scrape_betterworldbooks(query):
    books = []
    url = f"https://www.betterworldbooks.com/search/results?q={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.select('div.book-item')
    for item in items[:10]:
        title_elem = item.select_one('.book-title')
        author_elem = item.select_one('.book-author')
        price_elem = item.select_one('.item-price')
        if title_elem and price_elem:
            title = title_elem.get_text(strip=True)
            author = author_elem.get_text(strip=True) if author_elem else "Unknown"
            price = price_elem.get_text(strip=True).replace('$', '₹')
            books.append({
                'Title': title,
                'Author': author,
                'Price': price,
                'Website': 'BetterWorldBooks'
            })
    return books

# --- Website 5: AbeBooks ---
def scrape_abebooks(query):
    books = []
    url = f"https://www.abebooks.com/servlet/SearchResults?sts=t&cm_sp=SearchF-_-topnav-_-Results&an=&tn={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.select('.cf.result')
    for item in items[:10]:
        title_elem = item.select_one('.title')
        author_elem = item.select_one('.author')
        price_elem = item.select_one('.item-price')
        if title_elem and price_elem:
            title = title_elem.get_text(strip=True)
            author = author_elem.get_text(strip=True) if author_elem else "Unknown"
            price = price_elem.get_text(strip=True).replace('$', '₹')
            books.append({
                'Title': title,
                'Author': author,
                'Price': price,
                'Website': 'AbeBooks'
            })
    return books

# --- Exporting Utilities ---
def export_to_excel(data, filename='book_results.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"✅ Excel exported to: {filename}")

def generate_graph(counts, filename='graph.png'):
    plt.figure(figsize=(6, 4))
    plt.bar(counts.keys(), counts.values(), color='green')
    plt.title('Books Found per Website')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(filename)
    print(f"📊 Graph saved as: {filename}")

def export_to_pdf(data, counts, graph_file='graph.png', pdf_file='report.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Book Price Comparison Report", ln=True, align='C')

    if os.path.exists(graph_file):
        pdf.image(graph_file, x=30, w=150)

    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for site, count in counts.items():
        pdf.cell(0, 10, f"{site}: {count} books found", ln=True)
    pdf.ln(5)

    for book in data:
        line = f"- {book['Title']} | Author: {book['Author']} | Price: {book['Price']} | {book['Website']}"
        pdf.multi_cell(0, 8, line)

    pdf.output(pdf_file)
    print(f"📄 PDF saved as: {pdf_file}")
    try:
        os.system(f'start {pdf_file}' if os.name == 'nt' else f'open {pdf_file}')
    except:
        pass

# --- Main Program ---
def main():
    query = input("🔍 Enter book title or keyword: ").strip()
    print("Searching...")

    all_books = []
    site_counts = {}

    sources = {
        "BooksToScrape": scrape_books_to_scrape,
        "OpenLibrary": scrape_openlibrary,
        "Gutenberg": scrape_gutenberg,
        "BetterWorldBooks": scrape_betterworldbooks,
        "AbeBooks": scrape_abebooks
    }

    for name, func in sources.items():
        try:
            result = func(query)
            all_books.extend(result)
            site_counts[name] = len(result)
        except Exception as e:
            print(f"⚠️ Error scraping {name}: {e}")
            site_counts[name] = 0

    if all_books:
        export_to_excel(all_books)
        generate_graph(site_counts)
        export_to_pdf(all_books, site_counts)
    else:
        print("❌ No books found for your query. Try another title.")

if __name__ == '__main__':
    main()

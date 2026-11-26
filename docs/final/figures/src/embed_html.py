"""Update inline figure images and downloadable assets while preserving the HTML body."""
import base64
import mimetypes
import re
from pathlib import Path

from bs4 import BeautifulSoup


def embed(html_path, figure_dir):
    soup = BeautifulSoup(html_path.read_bytes(), 'html.parser')
    markdown = html_path.with_suffix('.md').read_text()
    pairs = re.findall(r'!\[([^\]]*)\]\(figures/([^/)]+\.png)\)', markdown)
    if len(pairs) != 8 or len(set(name for _, name in pairs)) != 8:
        raise ValueError('Expected eight distinct figures in the Markdown')
    images = soup.find_all('img')
    if len(images) != len(pairs):
        raise ValueError('HTML and Markdown figure counts differ')

    def data_uri(name):
        path = figure_dir / name
        mime = mimetypes.guess_type(name)[0]
        encoded = base64.b64encode(path.read_bytes()).decode('ascii')
        return f'data:{mime};base64,{encoded}'

    for (alt, name), tag in zip(pairs, images):
        if tag.get('alt') != alt:
            raise ValueError(f'Figure order or caption differs near {name}')
        tag['data-filename'] = name
        tag['src'] = data_uri(name)
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if href.startswith('figures/'):
            name = Path(href).name
        elif href.startswith('data:') and tag.get('download'):
            name = tag['download']
        else:
            continue
        tag['href'] = data_uri(name)
        tag['download'] = name
    html_path.write_text(str(soup))


if __name__ == '__main__':
    directory = Path(__file__).resolve().parents[1]
    embed(directory.parent / '07_research_design.html', directory)

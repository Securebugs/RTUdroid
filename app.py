from flask import Flask, render_template_string
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import schedule
import time
import threading
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Fallback JSON data (from your provided output)
fallback_news = [
    {"title": "List of Boys Hostel Allotment to B.Tech First Year Students (2025 )", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/14082025061809-media.pdf"},
    {"title": "Girls Hostel Allotment List Office Order-2025-26", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/13082025085730-media.pdf"},
    {"title": "Important information of exam section", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/12082025111406-media.pdf"},
    {"title": "Fee Structure for Session 2025-26", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/05082025075518-media.pdf"},
    {"title": "Format of Medical Certificate", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/05082025065320-media.pdf"},
    {"title": "Format of Income Certificate", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/05082025065338-media.pdf"},
    {"title": "CBCS Guideline of BCA for student admitted from session 2024-25", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/16072025125423-media.pdf"},
    {"title": "Office order", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/10072025055900-media.jpeg"},
    {"title": "Hostel Fee Details", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/10072025053158-media.jpeg"},
    {"title": "Circular", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/18062025035534-media.pdf"},
    {"title": "Regarding Schedule of form filling Even Sem (Main & Back/ Mercy Back) Exam 2024-25 (Phase-III)", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/03052025125733-media.pdf"},
    {"title": "regarding schedule of filling up online examination forms for Even Sem (Main/Back/Mercy Back) exams, 2024-25", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/08042025124503-media.pdf"},
    {"title": "Circular for opening of affiliation portal for starting of new college/program for 2025-26", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/08042025121303-media.pdf"},
    {"title": "Regarding form filling schedule for online examination forms for B.Tech. VI & VIII sem and B.Arch. VI & X sem (Main, Back, Mercy Back) exam, 2024-25", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/10032025031242-media.pdf"},
    {"title": "Office order of Warning to faculty examiners", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/15022025124607-media.jpeg"},
    {"title": "Circular Regarding Exam Form filling for Mercy Exam 2020-21", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/23122021124426-media.pdf"},
    {"title": "Notice Regarding Final Semester Special Exam and I & III semester Exam 2020-21", "link": "https://www.rtu.ac.in/index/Adminpanel/Images/Media/23122021124421-media.pdf"}
]

# Initialize SQLite database and populate with fallback data if empty
def init_db():
    try:
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        link TEXT NOT NULL,
                        fetch_time TIMESTAMP NOT NULL
                    )''')
        
        # Check if database is empty
        c.execute("SELECT COUNT(*) FROM news")
        count = c.fetchone()[0]
        logging.debug(f"Database contains {count} news items")
        if count == 0:
            current_time = datetime.now()
            for item in fallback_news:
                c.execute("INSERT INTO news (title, link, fetch_time) VALUES (?, ?, ?)",
                         (item["title"], item["link"], current_time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            logging.info(f"Initialized database with {len(fallback_news)} fallback news items")
        else:
            logging.info("Database already contains news items")
        conn.commit()
    except Exception as e:
        logging.error(f"Database initialization error: {e}")
    finally:
        conn.close()

# Function to fetch and parse news using requests-html
def fetch_news():
    url = "https://www.rtu.ac.in/index/"
    conn = None
    session = None
    try:
        session = HTMLSession()
        response = session.get(url, timeout=20)
        logging.debug("Fetched page, attempting to render JavaScript")
        response.html.render(timeout=30, sleep=2)
        soup = BeautifulSoup(response.html.html, 'html.parser')
        news_container = soup.select_one('div[id^="news-container_"]')

        if not news_container:
            logging.warning("News container not found, using fallback data")
            news_items = fallback_news
        else:
            news_items = []
            for item in news_container.find_all('li'):
                title_div = item.find('div', class_='newsscroller_title')
                if title_div and title_div.a:
                    title = title_div.a.text.strip().replace('\n', '').replace('\t', '')
                    if '<img' in title:
                        title = title.split('<img')[0].strip()
                    link = title_div.a['href']
                    if not link.startswith('http'):
                        link = f"https://www.rtu.ac.in{link}"
                    news_items.append({"title": title, "link": link})
            logging.debug(f"Found {len(news_items)} news items from website")

        if not news_items:
            logging.warning("No news items found, using fallback data")
            news_items = fallback_news

        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute("SELECT MAX(fetch_time) FROM news")
        last_fetch = c.fetchone()[0]
        last_fetch_time = datetime.strptime(last_fetch, '%Y-%m-%d %H:%M:%S') if last_fetch else datetime.min

        current_time = datetime.now()
        new_items = 0
        for item in news_items:
            c.execute("SELECT COUNT(*) FROM news WHERE link = ?", (item["link"],))
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO news (title, link, fetch_time) VALUES (?, ?, ?)",
                         (item["title"], item["link"], current_time.strftime('%Y-%m-%d %H:%M:%S')))
                new_items += 1
        
        conn.commit()
        logging.info(f"Fetched {new_items} new news items at {current_time}")
        return True
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute("SELECT MAX(fetch_time) FROM news")
        last_fetch = c.fetchone()[0]
        last_fetch_time = datetime.strptime(last_fetch, '%Y-%m-%d %H:%M:%S') if last_fetch else datetime.min
        current_time = datetime.now()
        new_items = 0
        for item in fallback_news:
            c.execute("SELECT COUNT(*) FROM news WHERE link = ?", (item["link"],))
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO news (title, link, fetch_time) VALUES (?, ?, ?)",
                         (item["title"], item["link"], current_time.strftime('%Y-%m-%d %H:%M:%S')))
                new_items += 1
        conn.commit()
        logging.info(f"Fallback: Inserted {new_items} news items at {current_time}")
        return True
    finally:
        if conn:
            conn.close()
        if session:
            session.close()

# Schedule news fetching every 4 hours
def run_scheduler():
    schedule.every(4).hours.do(fetch_news)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in a separate thread
def start_background_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

# Route to display news table
@app.route('/')
def index():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT title, link, fetch_time FROM news ORDER BY fetch_time DESC")
    news_items = c.fetchall()
    conn.close()
    logging.debug(f"Retrieved {len(news_items)} news items from database for display")

    status_message = ""
    if not news_items:
        status_message = "No news available. Using fallback data or the RTU website may be unreachable."
    else:
        try:
            latest_fetch = max(datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S') for item in news_items)
            if datetime.now() - latest_fetch > timedelta(hours=4):
                status_message = ""
        except Exception as e:
            logging.error(f"Error checking fetch time: {e}")

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
        <title>RTU News</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                overflow: hidden;
            }
            .container {
                width: 100%;
                height: 100vh;
                display: flex;
                flex-direction: column;
                padding: 5px;
            }
            .news-card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 5px 2px;
                width: calc(100% - 4px);
                height: calc(100% - 10px);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            .table-wrapper {
                flex-grow: 1;
                overflow-y: auto;
            }
            .status {
                color: #dc3545;
                margin-bottom: 10px;
                text-align: center;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 0;
            }
            thead {
                position: sticky;
                top: 0;
                background-color: #f7bd3d;
                z-index: 2;
            }
            th {
                padding: 8px;
                text-align: center;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 5px;
            }
            th img {
                width: auto;
                height: auto;
                max-width: 16px;
                max-height: 16px;
            }
            tbody {
                z-index: 1;
            }
            tr {
                cursor: pointer;
            }
            td {
                border: 1px solid #dee2e6;
                padding: 8px;
                text-align: left;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #e9ecef;
            }
            .modal-full {
                max-width: 100%;
                margin: 0;
                width: 100vw;
            }
            .modal-full .modal-content {
                height: 100vh;
                border-radius: 0;
                display: flex;
                flex-direction: column;
                background-color: #313131;
                color: white;
            }
            .modal-header {
                flex-shrink: 0;
                padding: 10px 15px;
                background-color: #313131;
                border-bottom: none;
            }
            .modal-title {
                font-size: 1rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: calc(100% - 40px);
                color: white;
            }
            .modal-body {
                padding: 0;
                flex-grow: 1;
                overflow-y: auto;
                overflow-x: hidden;
                position: relative;
                background-color: transparent;
            }
            .modal-footer {
                flex-shrink: 0;
                justify-content: center;
                padding: 10px;
                background-color: #313131;
                border-top: none;
            }
           .btn-close {
    background: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23ffffff'%3E%3Cpath d='M.293.293a1 1 0 011.414 0L8 6.586 14.293.293a1 1 0 111.414 1.414L9.414 8l6.293 6.293a1 1 0 01-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 01-1.414-1.414L6.586 8 .293 1.707A1 1 0 01.293.293z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 16px 16px;
    width: 24px;
    height: 24px;
    border: none;
    opacity: 1;
    cursor: pointer;
}

            .btn-secondary {
                color: white;
                background-color: transparent;
                border-color: white;
                padding: 2px 8px;
                font-size: 0.875rem;
                border: 1px solid white;
            }
            .btn-secondary:hover {
                background-color: #4a4a4a;
            }
            #modalContent {
                width: 100%;
                height: 100%;
                min-height: 100%;
                position: relative;
            }
            .modal-body iframe, .modal-body img {
                width: 100%;
                height: 100%;
                min-height: 100%;
                border: none;
                display: block;
                object-fit: contain;
                background-color: transparent;
            }
            .loader {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: rgba(128, 128, 128, 0.8);
                border-radius: 50%;
                width: 60px;
                height: 60px;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 3;
            }
            .loader .material-icons {
                font-size: 36px;
                color: white;
                animation: heartbeat 1.5s ease-in-out infinite;
            }
            .error-message {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #dc3545;
                font-size: 1rem;
                text-align: center;
                z-index: 3;
            }
            @keyframes heartbeat {
                0% { transform: scale(1); }
                20% { transform: scale(1.3); }
                40% { transform: scale(1); }
                60% { transform: scale(1.3); }
                80% { transform: scale(1); }
                100% { transform: scale(1); }
            }
            @media (min-width: 768px) {
                body.modal-open {
                    overflow: hidden;
                    position: fixed;
                    width: 100%;
                    height: 100%;
                }
                .modal-backdrop {
                    background-color: rgba(0,0,0,0.5) !important;
                }
                .modal:not(.show) {
                    display: none !important;
                }
            }
            @media (max-width: 576px) {
                .container {
                    padding: 5px;
                }
                .news-card {
                    margin: 5px 10px;
                    width: calc(100% - 20px);
                }
                .modal-header, .modal-footer {
                    padding: 8px 10px;
                }
                .modal-title {
                    font-size: 0.9rem;
                }
                .btn-secondary {
                    font-size: 0.75rem;
                    padding: 2px 6px;
                }
                .modal-body iframe, .modal-body img {
                    height: 100%;
                    min-height: 100%;
                }
                .loader {
                    width: 50px;
                    height: 50px;
                }
                .loader .material-icons {
                    font-size: 30px;
                }
                .error-message {
                    font-size: 0.9rem;
                    padding: 0 10px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            {% if status_message %}
            <p class="status">{{ status_message }}</p>
            {% endif %}
            <div class="news-card">
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th><img src="https://www.rtu.ac.in/index/Adminpanel/Images/newicon1.gif" alt="Icon"> Recent News from RTU</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in news %}
                            <tr data-bs-toggle="modal" data-bs-target="#contentModal" data-url="{{ item[1] }}" data-title="{{ item[0] }}">
                                <td>{{ item[0] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="modal fade" id="contentModal" tabindex="-1" aria-labelledby="contentModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-full">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="contentModalLabel"></h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div id="modalContent"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function () {
                const modal = document.getElementById('contentModal');
                modal.addEventListener('show.bs.modal', async function (event) {
                    const row = event.relatedTarget;
                    const url = row.getAttribute('data-url');
                    const title = row.getAttribute('data-title');
                    const modalTitle = document.getElementById('contentModalLabel');
                    const modalContent = document.getElementById('modalContent');
                    
                    modalTitle.textContent = title;
                    modalContent.innerHTML = `
                        <div class="loader" id="loader">
                            <span class="material-icons">picture_as_pdf</span>
                        </div>
                    `;
                    
                    const docExtensions = ['.pdf', '.docx', '.xls', '.xlsx'];
                    if (docExtensions.some(ext => url.toLowerCase().endsWith(ext))) {
                        try {
                            const response = await fetch(url, { 
                                method: 'HEAD',
                                signal: AbortSignal.timeout(5000)
                            });
                            if (response.ok) {
                                modalContent.innerHTML = `
                                    <div class="loader" id="loader">
                                        <span class="material-icons">picture_as_pdf</span>
                                    </div>
                                    <iframe src="https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true" frameborder="0" style="width:100%;height:100%;min-height:100%;" onload="document.getElementById('loader').style.display='none';"></iframe>
                                `;
                            } else {
                                console.error(`Fetch failed with status ${response.status} for ${url}`);
                                modalContent.innerHTML = `<div class="error-message">File moved or removed</div>`;
                            }
                        } catch (error) {
                            console.error(`Fetch error for ${url}: ${error.message}`);
                            modalContent.innerHTML = `
                                <div class="loader" id="loader">
                                    <span class="material-icons">picture_as_pdf</span>
                                </div>
                                <iframe src="https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true" frameborder="0" style="width:100%;height:100%;min-height:100%;" onload="document.getElementById('loader').style.display='none';" onerror="document.getElementById('loader').style.display='none'; this.parentElement.innerHTML='<div class=\\'error-message\\'>File moved or removed</div>';"></iframe>
                            `;
                        }
                    } else {
                        modalContent.innerHTML = `
                            <div class="loader" id="loader">
                                <span class="material-icons">picture_as_pdf</span>
                            </div>
                            <img src="${url}" alt="News Image" style="width:100%;height:100%;min-height:100%;object-fit:contain;" onload="document.getElementById('loader').style.display='none';" onerror="document.getElementById('loader').style.display='none'; this.parentElement.innerHTML='<div class=\\'error-message\\'>File moved or removed</div>';">
                        `;
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, news=news_items, status_message=status_message)

if __name__ == '__main__':
    init_db()
    fetch_news()
    start_background_scheduler()
    app.run(debug=True)

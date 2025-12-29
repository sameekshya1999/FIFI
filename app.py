"""
FIFI Web Application - Flask Backend
IU South Bend Information Chatbot
"""

from flask import Flask, render_template, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Import API configuration
from api_config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE

# Import static knowledge base
from knowledge_base import get_static_answer

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Store conversation history (in production, use sessions or database)
conversation_histories = {}


def load_urls(filepath="iu_southbend_urls.txt"):
    """Load scraped URLs from file"""
    urls = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    return urls


def fetch_page_content(url, timeout=10):
    """Fetch and extract text content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]
    except Exception:
        return None


def find_relevant_urls(urls, query):
    """Find URLs that might be relevant to the query"""
    keywords = query.lower().split()
    relevant = []

    keyword_patterns = {
        'admission': ['admission', 'apply', 'enroll'],
        'tuition': ['tuition', 'cost', 'fee', 'bursar', 'financial'],
        'financial': ['financial', 'aid', 'scholarship', 'bursar'],
        'program': ['program', 'academic', 'degree', 'major'],
        'course': ['course', 'class', 'schedule', 'registrar'],
        'housing': ['housing', 'residence', 'dorm'],
        'parking': ['parking', 'transportation'],
        'library': ['library', 'libguide', 'libguides', 'circulation', 'reserves', 'reserve', 'book', 'borrow', 'checkout', 'printing', 'print', '3d', 'werc', 'policy', 'librarian', 'research', 'hours', 'schurz', 'subject-librarian', 'research-support', 'wideformat', 'room', 'study', 'room-reservation'],
        'career': ['career', 'job', 'internship', 'handshake'],
        'transfer': ['transfer'],
        'graduate': ['graduate', 'grad', 'master'],
        'international': ['international', 'oiss', 'visa'],
        'calendar': ['calendar', 'schedule', 'date'],
        'contact': ['contact', 'phone', 'email'],
        'visit': ['visit', 'tour', 'campus'],
        'student': ['student', 'service'],
        'orientation': ['orientation', 'new-student'],
        'faculty': ['faculty', 'professor', 'staff', 'directory', 'people', 'dr', 'doctor'],
        'computer': ['computer', 'computer-science', 'computer-science-informatics', 'cs', 'computing', 'informatics', 'clas'],
        'math': ['math', 'mathematics', 'applied'],
        'business': ['business', 'mba', 'accounting', 'management'],
        'nursing': ['nursing', 'health', 'nurse'],
        'education': ['education', 'teaching', 'teacher'],
        'arts': ['arts', 'music', 'theatre', 'art', 'performance'],
    }

    matched_patterns = set()
    for keyword in keywords:
        for pattern, url_keywords in keyword_patterns.items():
            if keyword in url_keywords or any(k in keyword for k in url_keywords):
                matched_patterns.update(url_keywords)

    if not matched_patterns:
        matched_patterns = set(keywords)

    # Prioritize URLs with more pattern matches and faculty/people pages
    scored_urls = []
    for url in urls:
        url_lower = url.lower()
        score = 0
        for pattern in matched_patterns:
            if pattern in url_lower:
                score += 1
        # Boost faculty/people pages
        if 'faculty' in url_lower or 'people' in url_lower or 'staff' in url_lower:
            score += 2
        if score > 0:
            scored_urls.append((url, score))

    # Sort by score descending and return top 8
    scored_urls.sort(key=lambda x: x[1], reverse=True)
    return [url for url, score in scored_urls[:8]]


def get_context_from_urls(urls, query):
    """Fetch content from relevant URLs to use as context"""
    relevant_urls = find_relevant_urls(urls, query)
    context_parts = []

    for url in relevant_urls[:3]:
        content = fetch_page_content(url)
        if content:
            context_parts.append(f"Source: {url}\n{content[:1500]}")

    return "\n\n---\n\n".join(context_parts) if context_parts else ""


def chat_with_fifi(query, urls, conversation_history):
    """Send query to OpenAI with context from IU South Bend URLs"""

    # First, check static knowledge base for instant answers
    static_answer = get_static_answer(query)
    if static_answer:
        # Use static knowledge as primary context
        context = f"VERIFIED INFORMATION:\n{static_answer}"
    else:
        # Fall back to fetching from URLs
        context = get_context_from_urls(urls, query)

    system_message = """You are FIFI, a friendly and helpful chatbot assistant for IU South Bend (Indiana University South Bend).
Your purpose is to help students, prospective students, and visitors find information about IU South Bend.

Guidelines:
- Be friendly, helpful, and professional
- Use the provided context from IU South Bend web pages to answer questions
- If you don't have specific information, suggest relevant resources or direct users to contact the appropriate office
- Always mention relevant URLs from the context when applicable
- If a question is not related to IU South Bend, politely redirect to IU South Bend topics
- Keep responses concise but informative
- Format your responses nicely with line breaks where appropriate"""

    messages = [{"role": "system", "content": system_message}]

    for msg in conversation_history[-6:]:
        messages.append(msg)

    user_message = query
    if context:
        user_message = f"""Question: {query}

Here is relevant information from IU South Bend website:

{context}

Please answer the question based on this information."""

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}"


# Load URLs at startup
urls = load_urls()


@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get or create conversation history for this session
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []

    history = conversation_histories[session_id]

    # Get response from FIFI
    response = chat_with_fifi(user_message, urls, history)

    # Update conversation history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})

    # Keep only last 10 messages
    if len(history) > 10:
        conversation_histories[session_id] = history[-10:]

    return jsonify({'response': response})


@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    data = request.json
    session_id = data.get('session_id', 'default')

    if session_id in conversation_histories:
        conversation_histories[session_id] = []

    return jsonify({'status': 'cleared'})


if __name__ == '__main__':
    print(f"FIFI Web App starting...")
    print(f"Loaded {len(urls)} IU South Bend URLs")
    app.run(debug=True, port=5000)

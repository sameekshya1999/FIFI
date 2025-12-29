"""
FIFI - IU South Bend Information Chatbot
A chatbot that answers questions about IU South Bend using scraped URL data
"""

import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Import API configuration
from api_config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


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

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Get text content
        text = soup.get_text(separator=' ', strip=True)

        # Limit text length
        return text[:3000]
    except Exception as e:
        return None


def find_relevant_urls(urls, query):
    """Find URLs that might be relevant to the query"""
    keywords = query.lower().split()
    relevant = []

    # Map keywords to URL patterns
    keyword_patterns = {
        'admission': ['admission', 'apply', 'enroll'],
        'tuition': ['tuition', 'cost', 'fee', 'bursar', 'financial'],
        'financial': ['financial', 'aid', 'scholarship', 'bursar'],
        'program': ['program', 'academic', 'degree', 'major'],
        'course': ['course', 'class', 'schedule', 'registrar'],
        'housing': ['housing', 'residence', 'dorm'],
        'parking': ['parking', 'transportation'],
        'library': ['library', 'libguide'],
        'career': ['career', 'job', 'internship', 'handshake'],
        'transfer': ['transfer'],
        'graduate': ['graduate', 'grad', 'master'],
        'international': ['international', 'oiss', 'visa'],
        'calendar': ['calendar', 'schedule', 'date'],
        'contact': ['contact', 'phone', 'email'],
        'visit': ['visit', 'tour', 'campus'],
        'student': ['student', 'service'],
        'orientation': ['orientation', 'new-student'],
    }

    # Find matching patterns
    matched_patterns = set()
    for keyword in keywords:
        for pattern, url_keywords in keyword_patterns.items():
            if keyword in url_keywords or any(k in keyword for k in url_keywords):
                matched_patterns.update(url_keywords)

    # If no patterns matched, use original keywords
    if not matched_patterns:
        matched_patterns = set(keywords)

    # Find relevant URLs
    for url in urls:
        url_lower = url.lower()
        for pattern in matched_patterns:
            if pattern in url_lower:
                relevant.append(url)
                break

    # Return top 5 most relevant URLs
    return relevant[:5]


def get_context_from_urls(urls, query):
    """Fetch content from relevant URLs to use as context"""
    relevant_urls = find_relevant_urls(urls, query)
    context_parts = []

    print(f"\n[FIFI is searching {len(relevant_urls)} relevant pages...]")

    for url in relevant_urls[:3]:  # Limit to 3 pages to avoid token limits
        content = fetch_page_content(url)
        if content:
            context_parts.append(f"Source: {url}\n{content[:1500]}")

    return "\n\n---\n\n".join(context_parts) if context_parts else ""


def chat_with_fifi(query, urls, conversation_history):
    """Send query to OpenAI with context from IU South Bend URLs"""

    # Get relevant context from URLs
    context = get_context_from_urls(urls, query)

    # System message for FIFI
    system_message = """You are FIFI, a friendly and helpful chatbot assistant for IU South Bend (Indiana University South Bend).
Your purpose is to help students, prospective students, and visitors find information about IU South Bend.

Guidelines:
- Be friendly, helpful, and professional
- Use the provided context from IU South Bend web pages to answer questions
- If you don't have specific information, suggest relevant resources or direct users to contact the appropriate office
- Always mention relevant URLs from the context when applicable
- If a question is not related to IU South Bend, politely redirect to IU South Bend topics
- Keep responses concise but informative"""

    # Build messages
    messages = [{"role": "system", "content": system_message}]

    # Add conversation history
    for msg in conversation_history[-6:]:  # Keep last 6 messages for context
        messages.append(msg)

    # Add current query with context
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
        return f"I'm sorry, I encountered an error: {str(e)}\nPlease check your API key in api_config.py"


def display_banner():
    """Display FIFI chatbot banner"""
    banner = """
    ============================================================
    |                                                          |
    |      FFFFF  III  FFFFF  III                              |
    |      F       I   F       I                               |
    |      FFFF    I   FFFF    I                               |
    |      F       I   F       I                               |
    |      F      III  F      III                              |
    |                                                          |
    |         IU South Bend Information Assistant              |
    |                                                          |
    ============================================================
    """
    print(banner)


def main():
    """Main function to run FIFI chatbot"""
    display_banner()

    # Load URLs
    urls = load_urls()
    print(f"    Loaded {len(urls)} IU South Bend URLs as knowledge base\n")
    print("    Type 'quit' or 'exit' to end the conversation")
    print("    Type 'help' for assistance")
    print("=" * 60)

    conversation_history = []

    while True:
        print()
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nFIFI: Goodbye! Good luck with your IU South Bend journey! Go Titans!")
            break

        if user_input.lower() == 'help':
            print("\nFIFI: I can help you with information about:")
            print("  - Admissions and applications")
            print("  - Academic programs and courses")
            print("  - Tuition and financial aid")
            print("  - Student services and resources")
            print("  - Campus facilities and parking")
            print("  - Career services and internships")
            print("  - And much more about IU South Bend!")
            print("\nJust ask me a question!")
            continue

        # Get response from FIFI
        response = chat_with_fifi(user_input, urls, conversation_history)

        # Update conversation history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})

        print(f"\nFIFI: {response}")


if __name__ == "__main__":
    main()

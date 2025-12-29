# FIFI - Fast Information Finder Intelligence

A chatbot assistant for IU South Bend (Indiana University South Bend) that helps students find information about library services, admissions, programs, and more.

![FIFI Chatbot](https://img.shields.io/badge/FIFI-IU%20South%20Bend-cc0000)

## Features

- Library hours, room reservations, and borrowing information
- Printing and scanning services
- Subject librarians contact info
- Admissions requirements
- Tuition and financial aid info
- Campus facilities and parking
- Real-time web scraping for up-to-date information

## Requirements

- Python 3.8 or higher
- OpenAI API key

## Quick Start

### 1. Clone or Download the Project

Download all files to a folder on your computer.

### 2. Install Dependencies

Open terminal/command prompt in the project folder and run:

```bash
pip install flask openai requests beautifulsoup4
```

### 3. Add Your OpenAI API Key

Open `api_key.txt` and replace the placeholder with your actual OpenAI API key:

```
sk-your-openai-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Go to: **http://127.0.0.1:5000**

## Project Files

```
FIFI/
├── app.py                 # Main Flask web application
├── api_config.py          # API configuration loader
├── api_key.txt            # Your OpenAI API key (add your key here)
├── knowledge_base.py      # Pre-loaded FAQ answers
├── iu_southbend_urls.txt  # Curated URLs for web scraping
├── fifi_chatbot.py        # Command-line chatbot (optional)
├── scrape_iu_southbend.py # URL scraper (optional)
├── templates/
│   └── index.html         # Web interface
└── README.md              # This file
```

## Usage

### Web Interface
1. Run `python app.py`
2. Open http://127.0.0.1:5000 in your browser
3. Click on FAQ buttons or type your question
4. Get instant answers about IU South Bend

### Command Line (Optional)
```bash
python fifi_chatbot.py
```

## Sample Questions

- "What are the library hours?"
- "How do I reserve a study room?"
- "How do I borrow a book?"


## Customization

### Add More URLs
Edit `iu_southbend_urls.txt` to add more IU South Bend URLs for the chatbot to reference.

### Add More FAQ Answers
Edit `knowledge_base.py` to add pre-loaded answers for common questions.

### Change Model
Edit `api_config.py` to change the OpenAI model:
```python
MODEL_NAME = "gpt-4"  # or "gpt-3.5-turbo"
```

## Troubleshooting

### "Module not found" error
Run: `pip install flask openai requests beautifulsoup4`

### "Invalid API key" error
Make sure your OpenAI API key in `api_key.txt` is correct and has credits.

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

## Credits

Built for IU South Bend Library Services.

**FIFI** = Fast Information Finder Intelligence

## License

This project is for educational purposes.

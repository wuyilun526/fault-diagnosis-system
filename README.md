# Intelligent Fault Diagnosis System

An AI-powered intelligent fault diagnosis system that automatically analyzes system alerts, metrics, and log information to provide accurate fault diagnosis and solutions.

## ✨ Features

- 🔍 **Intelligent Diagnosis**: AI-powered fault analysis based on large language models
- 📚 **Knowledge Base Management**: Support for fault classification and solution knowledge base
- 🔄 **RAG Retrieval**: Similar case retrieval based on vector database
- 📊 **Visualization**: Intuitive fault diagnosis result display
- 🔐 **Security**: API key configuration and error handling

## 🛠️ Tech Stack

- **Backend Framework**: Django
- **Frontend Technology**: HTML, CSS, JavaScript, jQuery
- **AI Model**: Qwen (Tongyi Qianwen)
- **Vector Database**: Chroma
- **Text Vectorization**: sentence-transformers

## 📋 System Requirements

- Python 3.8+
- Django 4.2+
- Qwen API Key

## 🚀 Quick Start

1. **Clone the project**
```bash
git clone https://github.com/wuyilun526/fault-diagnosis-system.git
cd fault-diagnosis-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Configure in .env file
DASHSCOPE_API_KEY=your_api_key_here
```

4. **Initialize database**
```bash
python manage.py migrate
python manage.py sync_vector_db
```

5. **Start the service**
```bash
python manage.py runserver
```

## 📝 Usage Guide

1. **Access the System**
   - Open your browser and visit `http://localhost:8000`

2. **Fault Diagnosis**
   - Enter alert information
   - Optional: Add metrics and log information
   - Click the "Start Diagnosis" button

3. **Knowledge Base Management**
   - Add fault categories
   - Manage fault knowledge entries
   - View historical diagnosis records

## 🔧 Configuration

### Environment Variables
- `DASHSCOPE_API_KEY`: Qwen API key
- `DEBUG`: Debug mode switch
- `SECRET_KEY`: Django secret key

### Vector Database
- Default storage in `./chroma_db` directory
- Text vectorization using sentence-transformers model
- Customizable similarity threshold

## 📚 Project Structure

```
fault-diagnosis-system/
├── diagnosis/              # Main application directory
│   ├── models.py          # Data models
│   ├── views.py           # View functions
│   ├── services.py        # Business logic
│   └── management/        # Management commands
├── static/                # Static files
│   ├── css/              # Style files
│   └── js/               # JavaScript files
├── templates/            # Template files
├── manage.py            # Django management script
└── requirements.txt     # Project dependencies
```

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License

## 👥 Authors

- wuyilun526@163.com

## 🙏 Acknowledgments

- [Qwen](https://dashscope.aliyun.com/) - AI model support
- [Django](https://www.djangoproject.com/) - Web framework
- [Chroma](https://www.trychroma.com/) - Vector database
- [sentence-transformers](https://www.sbert.net/) - Text vectorization 
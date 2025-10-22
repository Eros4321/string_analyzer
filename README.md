# String Analyzer API

A Django REST Framework API that allows users to **store, analyze, and filter strings** based on specific criteria such as palindrome status, word count, character length, and more.

---

## 🚀 Features

- Store and retrieve analyzed strings.
- Automatically detect whether a string is a **palindrome**.
- Filter strings using query parameters such as:
  ```
  GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
  ```
- Filter strings using **natural language**, e.g.:
  ```
  GET /strings/filter-by-natural-language?query=strings that contain letter a and are palindromes
  ```
- Whitespace is **ignored** when counting characters or checking for palindromes.

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Django 5+**
- **Django REST Framework**
- **SQLite3 (default database)**

---

## 📦 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Eros4321/string_analyzer.git
   cd <your-repo-name>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate     # On Windows
   # OR
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Test the endpoints**
   - Create or analyze a string: `POST /strings`
   - Get all strings with filters:  
     ```
     GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
     ```
   - Get a specific string: `GET /strings/<string_value>`
   - Delete a string: `DELETE /strings/<string_value>`

---

## 🧪 Example JSON Response

```json
{
  "id": 1,
  "original_string": "level",
  "is_palindrome": true,
  "length": 5,
  "word_count": 1,
  "created_at": "2025-10-22T18:00:00Z"
}
```

---

## 🧰 Project Structure

```
string_analyzer/
│
├── analyzer/
│   ├── views.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🧑‍💻 Author

**Eros4321**  
Built with ❤️ using Django REST Framework.

---

## 🪄 License

This project is licensed under the **MIT License**.

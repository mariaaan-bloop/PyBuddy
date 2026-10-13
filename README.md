# 🐍 PyBuddy — Teman Belajar Python

**PyBuddy** is an AI-powered chatbot designed to help Indonesian students and beginners learn Python programming in a simple, interactive, and beginner-friendly way.

🚀 **Try PyBuddy:** [https://appbuddyapp.streamlit.app/](https://appbuddyapp.streamlit.app/)

## 📖 About the Project

Learning programming can be challenging for beginners, especially when they encounter unfamiliar concepts, confusing code, or error messages.

PyBuddy aims to make learning Python easier by providing explanations in Bahasa Indonesia, practical code examples, and interactive exercises. Users can ask questions and learn at their own pace.

## ✨ Features

- **AI-Powered Learning Assistant** — Ask Python-related questions and receive explanations in Bahasa Indonesia.
- **Beginner-Friendly Explanations** — Understand programming concepts through simple language and everyday analogies.
- **Python Code Examples** — Explore short code examples to understand how Python works.
- **Error Assistance** — Learn to understand common Python errors and how to fix them.
- **Interactive Learning Topics** — Explore different Python topics through the navigation menu.
- **Practice Exercises** — Practice programming concepts with beginner-level questions.
- **XP and Level Progression** — Track learning activity through experience points and levels.
- **Customizable Themes** — Choose Light, Dark, or Sunset mode.
- **Chat Interface** — Ask questions and review responses in one conversation.

## 📚 Learning Topics

PyBuddy provides learning support for the following topics:

| Topic | Description |
|---|---|
| 🐣 Basic Python | Variables, data types, and basic output |
| 📦 List, Tuple & Dictionary | Understanding Python collection data types |
| 🔁 Loops & Conditions | Learning `if-else`, `for`, and `while` |
| 🧩 Functions & Modules | Creating functions and using modules |
| 🐞 Debugging Errors | Understanding and troubleshooting Python errors |
| 📝 Practice Exercises | Practicing Python fundamentals |

## 🛠️ Tech Stack

- **Python** — Main programming language
- **Streamlit** — Web application framework and user interface
- **Groq API** — AI inference and chatbot responses
- **GitHub** — Source code management
- **Streamlit Community Cloud** — Application deployment

## 🚀 Getting Started

### Prerequisites

Make sure you have Python installed and a Groq API key.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

Replace the placeholders with your actual GitHub repository URL and folder name.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API Key

Create a `.streamlit/secrets.toml` file and add your Groq API key:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

**Important:** Never upload your API key or `secrets.toml` file to a public repository.

### 4. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to use PyBuddy.

## 🎯 Target Users

PyBuddy is designed for:

- Students learning Python for the first time.
- University students studying introductory programming.
- Beginners who need help understanding Python concepts and errors.
- Independent learners who prefer explanations in Bahasa Indonesia.

## 🌱 Project Goals

PyBuddy aims to make programming education more accessible by helping beginners understand Python concepts, practice problem-solving, and develop confidence in coding.

## 🔮 Future Improvements

Potential improvements include:

- More structured learning paths.
- Additional interactive coding exercises.
- Progress tracking across learning sessions.
- More personalized learning recommendations.
- Improved chat interface and accessibility.

## 👩‍💻 Live Application

Try the application here:

**[Open PyBuddy](https://appbuddyapp.streamlit.app/)**

---

Made with 💚 for Indonesian Python learners.

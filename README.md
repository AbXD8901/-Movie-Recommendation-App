# 🎬 Movie Recommendation System  

A **Streamlit-based Movie Recommendation App** powered by **MySQL** and **Machine Learning**. This app provides **personalized movie recommendations** using **genre-based filtering, content-based filtering (plot & crew analysis), and general recommendations**.  

🚀 **Features:**  
✅ User registration & login system 📌  
✅ Track watched movies 🎥  
✅ Get movie recommendations based on **favorite genres** 🎭  
✅ AI-powered **plot & crew-based** recommendations 🧠  
✅ Dynamic **general recommendations** (highest budget, revenue, and ratings) 💰  

---

## 📌 How It Works  

### 🔹 1. **Favourite Genre Based Movies**  
✔ Every user selects **favorite genres** at registration.  
✔ The system **filters movies** from the database matching those genres.  
✔ **No watch history required**—this works for new users too!  

### 🔹 2. **Based on Movies You Watched…**  
💡 If the user has watched **at least 2 movies**, AI-based recommendations are generated:  

1️⃣ **Crew-Based Recommendations:**  
   - The system scans the **entire watch history** of the user.  
   - It identifies the **top 2 most frequently appearing crew members** (directors, actors, etc.).  
   - Recommends **2 movies** where those crew members are involved.  

2️⃣ **Plot-Based Recommendations (TF-IDF & Cosine Similarity):**  
   - Extracts the **overview** (plot description) of the **2 most recently watched movies**.  
   - Generates a **theme vector** using **TF-IDF** (Term Frequency-Inverse Document Frequency).  
   - **Instead of comparing with all movies**, the system only considers movies with at least **one matching genre** from the 2 watched movies.  
   - The 2 most similar movies are recommended.  

👉 **Total: 4 AI-powered recommendations (2 Crew-based + 2 Plot-based)**  

### 🔹 3. **General Recommendations**  
For all users, the system recommends **4 movies** based on:  
✔ **Highest budget**  
✔ **Highest revenue**  
✔ **2 highest-rated movies**  

🎯 If a user watches a movie from this list, it **automatically updates** with a new movie matching the same condition.  

---

## 💻 Tech Stack  

| Component            | Technology Used  |  
|----------------------|-----------------|  
| Frontend UI         | **Streamlit** 🖥️ |  
| Backend Database    | **MySQL** 🗄️ |  
| Database Connector  | **pymysql** 🔗 |  
| Machine Learning    | **Scikit-learn (TF-IDF, KNN)** 🤖 |  
| Programming Language | **Python** 🐍 |  

---

## 📂 Database Schema  

**1️⃣ `user_info`** → Stores user details  
```sql
CREATE TABLE user_info (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    favorite_genre VARCHAR(255) NOT NULL
);
```

**2️⃣ `movies`** → Stores movie details  
```sql
CREATE TABLE movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    movie VARCHAR(255) NOT NULL,
    release_date DATE,
    rating FLOAT,
    genre VARCHAR(255),
    overview TEXT,
    crew TEXT,
    budget BIGINT,
    revenue BIGINT,
    country VARCHAR(50)
);
```

**3️⃣ `watched`** → Tracks movies watched by users  
```sql
CREATE TABLE watched (
    watched_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_info(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
```

**4️⃣ `recommendations`** → Stores recommended movies  
```sql
CREATE TABLE recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    reason VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user_info(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
```
---

## 📜 License  
This project is licensed under the **MIT License**. Feel free to use and modify it!  

---

This README covers **everything** about your project in a professional way. 🚀 Let me know if you want to add anything else!

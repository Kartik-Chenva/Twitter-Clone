🐦 Twitter Clone (Django Project)
A social media web application inspired by Twitter, built using Django.
Users can sign up, log in, create tweets, follow other users, and view a personalized feed showing posts only from people they follow.

✨ Main Features (Updated)

👤 User Authentication – Sign up, log in, and log out securely.
📝 Tweet Management – Create, view, and delete tweets easily.
🔄 Follow/Unfollow System – Connect with other users.
🏠 Home Feed – View all posts from all users on the platform.
🖼️ Profile Pages – View your tweets and followers in one place.

🛠️ Technologies Used

Backend: Python, Django
Frontend: HTML, CSS, Bootstrap, JavaScript
Database: MySQL

🚀 How to Run the Project
1️⃣ Clone this repository:
git clone https://github.com/Kartik-Chenva/Twitter-Clone.git

2️⃣ Go to the project folder:
cd Twitter-Clone

3️⃣ Create and activate a virtual environment:
python -m venv venv

On Windows:
venv\Scripts\activate

4️⃣ Install all dependencies:
pip install -r requirements.txt

5️⃣ Apply database migrations:
python manage.py makemigrations
python manage.py migrate

6️⃣ Start the development server:
python manage.py runserver

7️⃣ Open your browser:

Visit → http://127.0.0.1:8000/

📸 Screenshots

Add 2–3 screenshots of your project here.
Upload images to your GitHub repository and include their links below:

Example:

🏠 Home Feed Page:


👤 User Profile Page:


💡 Additional Notes
     Make sure to create a superuser for admin access:
      python manage.py createsuperuser

Keep your .env file secure and never push it to GitHub.

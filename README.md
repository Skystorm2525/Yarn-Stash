Yarn Stash

Yarn Stash is a full-stack Flask web application that helps knitters and crocheters manage yarn inventory, organize patterns, and track project allocations.

This project was built from scratch using Python, Flask, SQLite, HTML, CSS, and Git.

⸻

Features

• Add, edit, and delete yarn with image upload
• Track skeins owned, allocated, and available
• Create projects and assign yarn with validation
• Prevent over-allocation of yarn
• Upload and preview pattern files (PDF and images)
• Organize patterns into folders
• Fully styled custom UI with responsive grid layouts
• Database migrations handled manually
• Git version control and clean repository structure

⸻

Tech Stack

Backend:
	•	Python
	•	Flask
	•	SQLite

Frontend:
	•	HTML
	•	CSS (custom responsive grid system)
	•	Jinja2 templating

Other:
	•	Git and GitHub
	•	File uploads
	•	Relational database design

⸻

Database Design

Tables include:
	•	yarn
	•	projects
	•	project_yarn
	•	patterns
	•	folders

Relationships enforce:
	•	Yarn allocation limits
	•	Folder-pattern associations
	•	Project-yarn joins

⸻

Installation
	1.	Clone the repository:

git clone https://github.com/Skystorm2525/Yarn-Stash.git
	2.	Navigate into the folder:

cd Yarn-Stash
	3.	Create a virtual environment:

python3 -m venv venv
source venv/bin/activate
	4.	Install dependencies:

pip install flask
	5.	Initialize the database:

python init_db.py
	6.	Run the app:

python app.py

Visit:
http://127.0.0.1:5000

⸻

Why I Built This

I wanted a structured way to manage yarn inventory and project planning. Instead of using spreadsheets, I designed and implemented a full database-driven application with custom UI styling and allocation logic.

This project demonstrates:
	•	Backend logic design
	•	Database schema management
	•	Form validation
	•	File handling
	•	UI layout systems
	•	Git version control

⸻

Future Improvements
	•	User authentication
	•	Deployment to a cloud platform
	•	Search and filtering
	•	Performance optimization
	•	API endpoints

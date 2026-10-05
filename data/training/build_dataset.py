"""
@file build_dataset.py
@description Generates realistic academic training dataset and unseen test cases for resume section classification
@module data.training.build_dataset
"""

import csv
import json
import os
from collections import Counter
from typing import Dict, List, Tuple

VALID_LABELS = [
    "SUMMARY",
    "CONTACT",
    "EDUCATION",
    "EXPERIENCE",
    "PROJECTS",
    "SKILLS",
    "CERTIFICATIONS",
    "ACHIEVEMENTS",
    "OTHER",
]

# 45 realistic examples per class = 405 training examples
TRAINING_EXAMPLES: List[Tuple[str, str]] = [
    # --- SUMMARY ---
    ("Dedicated computer science student with strong foundations in algorithms and web development.", "SUMMARY"),
    ("Results-driven software engineer with 2+ years of hands-on experience building scalable microservices.", "SUMMARY"),
    ("Proactive data analyst passionate about uncovering actionable insights through statistical modeling and visualization.", "SUMMARY"),
    ("Motivated fresher seeking an entry-level software developer role to apply modern programming skills.", "SUMMARY"),
    ("Passionate machine learning enthusiast with academic experience in NLP, deep learning, and predictive analytics.", "SUMMARY"),
    ("Full stack developer skilled in TypeScript, React, and Python backend microservices architectures.", "SUMMARY"),
    ("Detail-oriented technical lead with a proven track record in Agile project delivery and clean code practices.", "SUMMARY"),
    ("Undergraduate senior looking to leverage problem-solving skills in high-impact cloud engineering projects.", "SUMMARY"),
    ("Resourceful backend developer experienced in distributed systems, REST API design, and SQL query tuning.", "SUMMARY"),
    ("Enthusiastic AI researcher with strong background in computer vision, mathematics, and PyTorch experimentation.", "SUMMARY"),
    ("Professional Summary: Experienced in architecting robust cloud pipelines and containerized deployments.", "SUMMARY"),
    ("Career Objective: To secure a challenging position where I can contribute to core backend systems.", "SUMMARY"),
    ("Analytical problem solver eager to contribute to forward-thinking software development teams.", "SUMMARY"),
    ("Self-taught developer with deep interest in open source contributions and test-driven development.", "SUMMARY"),
    ("Disciplined software developer adept at translating complex user requirements into performant features.", "SUMMARY"),
    ("Goal-oriented graduate with hands-on proficiency in Python, PostgreSQL, and modern frontend frameworks.", "SUMMARY"),
    ("Software engineer committed to writing maintainable, well-documented, and production-ready code.", "SUMMARY"),
    ("Tech-savvy professional with solid grounding in data structures, algorithms, and object-oriented design.", "SUMMARY"),
    ("Recent graduate with first-class honors in Computer Engineering, seeking junior DevOps opportunities.", "SUMMARY"),
    ("Passionate full stack developer with experience in end-to-end development of data-intensive web apps.", "SUMMARY"),
    ("Summary of Qualifications: Demonstrated expertise in automated testing, CI/CD, and system architecture.", "SUMMARY"),
    ("Forward-thinking developer with strong collaborative instincts and quick technical adaptability.", "SUMMARY"),
    ("Dynamic software engineering graduate with hands-on internship experience in cloud computing.", "SUMMARY"),
    ("Aspiring data scientist eager to build machine learning solutions for complex real-world problems.", "SUMMARY"),
    ("Professional Overview: Proven background in API engineering, performance optimization, and clean code.", "SUMMARY"),
    ("Innovative thinker with a knack for rapid prototyping and modern reactive frontend user interfaces.", "SUMMARY"),
    ("Junior developer with extensive experience building academic capstone projects in full stack ecosystems.", "SUMMARY"),
    ("Software engineer with experience delivering high-availability RESTful web services in startup settings.", "SUMMARY"),
    ("Hardworking graduate student specializing in distributed data systems and natural language processing.", "SUMMARY"),
    ("Creative problem solver who thrives in fast-paced software development and agile sprint environments.", "SUMMARY"),
    ("Profile: Committed to writing secure, modular, and performant code across the entire technology stack.", "SUMMARY"),
    ("Enthusiastic programmer with comprehensive understanding of MVC patterns, Git, and relational databases.", "SUMMARY"),
    ("Career Summary: Proven track record of developing scalable applications and integrating third-party APIs.", "SUMMARY"),
    ("Adaptable software engineer with a strong background in automated testing and continuous deployment.", "SUMMARY"),
    ("Fresh graduate with strong academic performance in data analytics, database management, and Python.", "SUMMARY"),
    ("Solution-driven software engineer who enjoys solving algorithmic challenges and architecting databases.", "SUMMARY"),
    ("Passionate coder with experience in microservices, event-driven architectures, and Docker containers.", "SUMMARY"),
    ("Skilled programmer looking for opportunities to contribute to enterprise-grade web development.", "SUMMARY"),
    ("Versatile engineer with cross-functional background in data science, backend APIs, and modern UI design.", "SUMMARY"),
    ("Dedicated technologist eager to apply knowledge of cloud architecture and software design patterns.", "SUMMARY"),
    ("Summary: Experienced in building robust data pipelines, schema design, and unit testing pipelines.", "SUMMARY"),
    ("High-performing student with keen interest in distributed systems, asynchronous programming, and Linux.", "SUMMARY"),
    ("Software developer seeking a junior engineering role with focus on backend services and cloud deployment.", "SUMMARY"),
    ("Motivated engineer with academic background in artificial intelligence, neural networks, and statistics.", "SUMMARY"),
    ("Passionate web developer with practical exposure to React, Node.js, and relational database management.", "SUMMARY"),

    # --- CONTACT ---
    ("Email: alex.morgan@testdomain.edu | Phone: +1-555-0144 | LinkedIn: linkedin.com/in/alexmorgan", "CONTACT"),
    ("johndoe@email.com | +1 (555) 234-5678 | San Francisco, CA | github.com/johndoe", "CONTACT"),
    ("Contact: dev.candidate@testmail.com, Tel: 555-0199, Portfolio: devcandidate.me", "CONTACT"),
    ("linkedin.com/in/sarah-connor | github.com/sarahconnor | sarah.c@domain.org", "CONTACT"),
    ("Mobile: +44 20 7946 0912 | Email: applicant@academictest.co.uk", "CONTACT"),
    ("alex.smith.dev@gmail.com | github.com/alexsmithdev | linkedin.com/in/alexsmithdev", "CONTACT"),
    ("Email: emily.watson@university.edu | Phone: 555-345-6789 | Chicago, Illinois", "CONTACT"),
    ("David Miller | Seattle, WA | david.miller@techtest.com | (555) 987-6543", "CONTACT"),
    ("Address: 123 University Ave, Boston, MA | Phone: 555-432-1098 | Email: student@mit.edu", "CONTACT"),
    ("github.com/developer-profile | linkedin.com/in/devprofile | dev@profiledomain.com", "CONTACT"),
    ("Phone: +1 555 789 0123 | Email: contact.me@engineer.io | Austin, Texas", "CONTACT"),
    ("portfolio.janesmith.dev | jane.smith@mailbox.net | +1 (555) 654-3210", "CONTACT"),
    ("Michael Chang | Tel: 555-222-3333 | mchang@cs.state.edu | New York, NY", "CONTACT"),
    ("Contact Information: Email: rahul.patel@univ.ac.in | Mobile: +91 98765 43210", "CONTACT"),
    ("Email: clark.kent@dailyplanet.org | Cell: 555-0100 | Metropolis, NY", "CONTACT"),
    ("lucas.silva@techmail.br | +55 11 91234-5678 | São Paulo, Brazil", "CONTACT"),
    ("priya.sharma@testdomain.com | Phone: +91 91234 56789 | Bengaluru, India", "CONTACT"),
    ("Personal details: Email: candidate.user@sample.net, Phone: 555-876-5432", "CONTACT"),
    ("github.com/cloud-architect-2024 | linkedin.com/in/cloud-architect | architect@cloud.dev", "CONTACT"),
    ("Email: kevin.bacon@connect.org | Mobile: +1 (555) 321-7654 | Denver, CO", "CONTACT"),
    ("Address: 456 College Road, Atlanta, GA | Telephone: 555-901-2345 | applicant@gatech.edu", "CONTACT"),
    ("dev.contact@domain.co | +1 555 890 1234 | San Jose, California", "CONTACT"),
    ("LinkedIn: linkedin.com/in/robert-chen | GitHub: github.com/rchen-dev | Email: rchen@dev.io", "CONTACT"),
    ("Telephone: 555-555-0188 | Electronic Mail: info.candidate@techmail.com", "CONTACT"),
    ("Hannah Abbott | hannah.abbott@oxford.ac.uk | +44 1865 270000 | Oxford, UK", "CONTACT"),
    ("Liam O'Connor | liam.oconnor@dublin.ie | +353 1 496 0000 | Dublin, Ireland", "CONTACT"),
    ("Email: test.engineer@domain.com | Phone: 555-123-9876 | Los Angeles, CA", "CONTACT"),
    ("github.com/datascience-student | student@ds.university.edu | +1-555-456-7890", "CONTACT"),
    ("Contact: (555) 765-4321 | applicant.tech@inbox.com | linkedin.com/in/applicant-tech", "CONTACT"),
    ("Email: carlos.rodriguez@madrid.es | Movil: +34 600 123 456 | Madrid, Spain", "CONTACT"),
    ("portfolio: candidate-showcase.vercel.app | email: hello@showcase.dev | phone: 555-888-9999", "CONTACT"),
    ("Chloe Martin | chloe.martin@paris.fr | +33 1 42 68 55 00 | Paris, France", "CONTACT"),
    ("Phone: 555-234-8765 | Mail: candidate.qa@tester.org | Dallas, TX", "CONTACT"),
    ("github.com/fullstack-coder | linkedin.com/in/fullstack-coder | coder@fullstack.org", "CONTACT"),
    ("Email: aaron.judge@yankees.org | Phone: 555-999-0000 | Bronx, NY", "CONTACT"),
    ("Contact Info: Phone: +1 (555) 678-9012 | Email: junior.dev@sampledomain.com", "CONTACT"),
    ("natalia.ivanova@tech.ru | +7 495 123-45-67 | Moscow, Russia", "CONTACT"),
    ("Website: myportfolio.io | Email: me@myportfolio.io | Cell: 555-333-4444", "CONTACT"),
    ("Email: devon.miles@flag.org | Tel: 555-246-8102 | Washington, DC", "CONTACT"),
    ("LinkedIn: linkedin.com/in/steve-rogers | Email: cap@avengers.org | Brooklyn, NY", "CONTACT"),
    ("Phone: +1 555 432 9870 | Email: code.enthusiast@domain.edu | Toronto, ON", "CONTACT"),
    ("Contact details: email: amir.khan@delhi.ac.in, mobile: +91 98111 22233", "CONTACT"),
    ("Email: simon.baker@sydney.edu.au | Mobile: +61 2 9351 2222 | Sydney, Australia", "CONTACT"),
    ("dev.lead@coders.net | Phone: 555-890-5678 | Miami, FL | github.com/devlead", "CONTACT"),
    ("Direct Line: 555-014-9988 | Email: student.cv@campus.edu | Pittsburgh, PA", "CONTACT"),

    # --- EDUCATION ---
    ("Bachelor of Science in Computer Science, State University, GPA: 3.8/4.0, 2020 - 2024", "EDUCATION"),
    ("B.Tech in Computer Science and Engineering, National Institute of Technology, 2019 - 2023", "EDUCATION"),
    ("Master of Science in Artificial Intelligence, Carnegie Mellon University, 2022 - 2024", "EDUCATION"),
    ("B.S. in Software Engineering, University of California Berkeley, Expected Graduation: May 2025", "EDUCATION"),
    ("Bachelor of Engineering in Information Technology, Mumbai University, First Class with Distinction", "EDUCATION"),
    ("Associate Degree in Web Development, Community College of Denver, GPA 3.9, 2021", "EDUCATION"),
    ("Master of Science in Data Science, University of Washington, Coursework in Machine Learning & Big Data", "EDUCATION"),
    ("Ph.D. in Computer Science, Stanford University, Dissertation on Distributed Optimization", "EDUCATION"),
    ("B.S. in Electrical and Computer Engineering, Georgia Institute of Technology, 2018 - 2022", "EDUCATION"),
    ("Relevant Coursework: Data Structures, Algorithms, Operating Systems, Database Systems, Computer Networks", "EDUCATION"),
    ("Education: Bachelor of Science in Mathematics and Computing, State College, Magna Cum Laude", "EDUCATION"),
    ("B.A. in Computer Science with Minor in Statistics, Boston University, 2020 - 2024", "EDUCATION"),
    ("Diploma in Full Stack Software Development, Code Academy Institute, 2022", "EDUCATION"),
    ("Bachelor of Science in Information Systems, University of Texas at Austin, Dean's List (all semesters)", "EDUCATION"),
    ("M.S. in Computer Science, University of Illinois Urbana-Champaign, Specialization in Cloud Computing", "EDUCATION"),
    ("B.Tech in Electronics and Communication Engineering, Anna University, CGPA: 8.9/10.0", "EDUCATION"),
    ("Secondary School Certificate (Class XII), Central Board of Secondary Education, 94.2%", "EDUCATION"),
    ("Academic Credentials: Bachelor of Science in Cybersecurity, Purdue University, 2021 - 2025", "EDUCATION"),
    ("Coursework: Object-Oriented Programming, Discrete Mathematics, Software Engineering Principles, AI", "EDUCATION"),
    ("Undergraduate Degree: B.S. in Computer Science, University of Michigan Ann Arbor, GPA: 3.7", "EDUCATION"),
    ("Master of Science in Software Engineering, San Jose State University, GPA 3.85, 2023", "EDUCATION"),
    ("Bachelor of Science in Computer Information Systems, Arizona State University, 2019 - 2023", "EDUCATION"),
    ("B.Sc. in Computer Science, University of Toronto, Faculty of Arts & Science, 2020 - 2024", "EDUCATION"),
    ("Dual Degree: B.S. in Computer Science & B.A. in Economics, Cornell University, 2019 - 2023", "EDUCATION"),
    ("High School Diploma, St. Xavier's High School, Physics, Chemistry, and Mathematics Stream", "EDUCATION"),
    ("University Education: Master of Science in Informatics, University of Edinburgh, 2022", "EDUCATION"),
    ("Bachelor of Technology in Data Science, Indian Institute of Information Technology, 2020 - 2024", "EDUCATION"),
    ("Academic Background: B.S. in Applied Computing, Oregon State University, 2021 - 2024", "EDUCATION"),
    ("B.Eng. in Software Engineering, McGill University, Montreal, QC, Canada, 2018 - 2022", "EDUCATION"),
    ("Postgraduate Diploma in Cloud Computing and DevOps, Lambton College, 2023", "EDUCATION"),
    ("Education & Academics: B.S. in Computational Data Analytics, Ohio State University, GPA: 3.75", "EDUCATION"),
    ("Relevant Studies: Distributed Systems, Compiler Design, Cloud Architecture, Linear Algebra", "EDUCATION"),
    ("Bachelor of Science, Computer Science Major, University of Maryland College Park, 2024", "EDUCATION"),
    ("Master of Information Technology, University of Melbourne, Melbourne, Australia, 2023", "EDUCATION"),
    ("Bachelor of Science in Software Development, Western Governors University, 2022", "EDUCATION"),
    ("B.Tech in Artificial Intelligence and Machine Learning, SRM University, 2021 - 2025", "EDUCATION"),
    ("Academic History: Bachelor of Science in Information Technology, Penn State University", "EDUCATION"),
    ("Coursework completed: Deep Learning, Probabilistic Graphical Models, Advanced NLP, Computer Vision", "EDUCATION"),
    ("Bachelor of Science in Computer Science, Rutgers University, Summa Cum Laude, 2020 - 2024", "EDUCATION"),
    ("Master of Science in Computing and Information Systems, Queen Mary University of London", "EDUCATION"),
    ("B.S. in Applied Mathematics and Statistics, Stony Brook University, Minor in CS, 2023", "EDUCATION"),
    ("Bachelor of Engineering in Computer Technology, Delhi Technological University, 2019 - 2023", "EDUCATION"),
    ("Education: B.S. in Computer Science and Engineering, University of California San Diego", "EDUCATION"),
    ("Associate of Applied Science in Software Engineering, Northern Virginia Community College", "EDUCATION"),
    ("B.Tech, Computer Science, Vellore Institute of Technology, Graduated July 2024, GPA: 8.8", "EDUCATION"),

    # --- EXPERIENCE ---
    ("Software Engineer Intern at TechCorp Labs (June 2023 - Aug 2023): Developed REST APIs using FastAPI.", "EXPERIENCE"),
    ("Junior Backend Developer at Acme Software Solutions, responsible for PostgreSQL query tuning.", "EXPERIENCE"),
    ("Software Development Engineer Intern at CloudTech: Containerized legacy microservices using Docker.", "EXPERIENCE"),
    ("Data Analyst Intern at Insight Analytics: Built automated dashboard pipelines in Python and Tableau.", "EXPERIENCE"),
    ("Frontend Developer at WebCrafters Inc (2022 - 2024): Built responsive UI components using React and Tailwind.", "EXPERIENCE"),
    ("Graduate Teaching Assistant for CS 101, grading assignments and conducting weekly algorithm lab sessions.", "EXPERIENCE"),
    ("Full Stack Intern at Global Retail Systems: Integrated Stripe payment gateway with Node.js backend.", "EXPERIENCE"),
    ("Work History: Software Engineering Contractor, implemented CI/CD pipelines using GitHub Actions.", "EXPERIENCE"),
    ("Machine Learning Intern at MedAI Labs: Preprocessed tabular clinical datasets and evaluated XGBoost models.", "EXPERIENCE"),
    ("DevOps Intern at Serverless Co: Automated infrastructure provisioning using Terraform and AWS CloudFormation.", "EXPERIENCE"),
    ("Undergraduate Research Assistant, worked on distributed consensus algorithms and benchmarked latency.", "EXPERIENCE"),
    ("QA Automation Intern at TestFirst Systems: Wrote end-to-end integration tests using Selenium and pytest.", "EXPERIENCE"),
    ("Backend Intern at FinTech Startup: Designed high-throughput financial transaction processing endpoints.", "EXPERIENCE"),
    ("Software Engineering Fellow at TechForward: Collaborated with cross-functional team on enterprise features.", "EXPERIENCE"),
    ("Junior Data Engineer at DataStream LLC: Maintained ETL pipelines using Apache Spark and AWS S3.", "EXPERIENCE"),
    ("Professional Experience: Mobile Developer at AppStudio, maintained cross-platform Flutter application.", "EXPERIENCE"),
    ("Cloud Engineering Intern at Enterprise Cloud Solutions: Configured AWS VPCs, EC2 instances, and RDS.", "EXPERIENCE"),
    ("Web Development Intern at Digital Media Agency: Built customized WordPress plugins and REST endpoints.", "EXPERIENCE"),
    ("Research Intern at AI Lab: Trained transformer models on biomedical text corpora and measured BLEU scores.", "EXPERIENCE"),
    ("Systems Analyst Intern at HealthCare Systems: Audited database logs and resolved data integrity tickets.", "EXPERIENCE"),
    ("Employment: Junior Full Stack Engineer at StartupX, built GraphQL resolvers and optimized caching in Redis.", "EXPERIENCE"),
    ("Software Engineer at MicroServices Inc: Refactored monolith into decoupled microservices communicating via Kafka.", "EXPERIENCE"),
    ("Technical Support Specialist at Campus IT Helpdesk: Resolved network connectivity and workstation issues.", "EXPERIENCE"),
    ("Product Engineering Intern at SaaSify: Implemented role-based access control and JWT token authentication.", "EXPERIENCE"),
    ("Database Administrator Assistant at University Registrar: Maintained daily SQL backups and index optimization.", "EXPERIENCE"),
    ("Embedded Software Intern at Robotics Corp: Programmed microcontroller firmware in C++ for motor control.", "EXPERIENCE"),
    ("Software Engineer Intern (Remote) at OpenTech: Contributed pull requests to core open source framework.", "EXPERIENCE"),
    ("Work Experience: Associate Software Developer at Global IT Services (Sept 2023 - Present)", "EXPERIENCE"),
    ("Data Science Intern at Marketing Hub: Conducted A/B testing analysis and customer churn prediction modeling.", "EXPERIENCE"),
    ("Frontend Intern at Creative Web Agency: Converted Figma designs into accessible React code.", "EXPERIENCE"),
    ("Site Reliability Intern at CloudOps: Monitored system health metrics with Prometheus and Grafana dashboards.", "EXPERIENCE"),
    ("Application Developer Intern at Insurance Corp: Developed customer claim submission forms in Angular.", "EXPERIENCE"),
    ("Cybersecurity Intern at SecureNet: Performed vulnerability scans and assisted in OWASP compliance audit.", "EXPERIENCE"),
    ("Backend Developer Co-op at Logistics Solutions: Engineered automated shipment tracking webhooks in Django.", "EXPERIENCE"),
    ("Teaching Assistant for Algorithms & Data Structures, mentored 60+ undergraduate engineering students.", "EXPERIENCE"),
    ("Junior Python Developer at DataCorp: Wrote web scraping scripts using Scrapy and BeautifulSoup.", "EXPERIENCE"),
    ("Full Stack Intern at EduTech Solutions: Built interactive quiz application using Express and MongoDB.", "EXPERIENCE"),
    ("Software Developer Intern at Financial Services Group: Automated reconciliation reports with Pandas.", "EXPERIENCE"),
    ("Engineering Intern at SmartHardware: Tested I2C sensor communications and logged telemetry to cloud server.", "EXPERIENCE"),
    ("DevOps Engineering Intern at ScaleFast: Maintained Kubernetes cluster manifests and Helm chart deployments.", "EXPERIENCE"),
    ("Experience: Peer Tutor in Computer Science, assisted students in debugging C and Java programs.", "EXPERIENCE"),
    ("Cloud Intern at Infrastructure Inc: Assisted with migration of 20+ on-premise servers to AWS EC2.", "EXPERIENCE"),
    ("Machine Learning Engineering Intern: Built computer vision object detection pipeline using YOLOv8.", "EXPERIENCE"),
    ("Software Engineering Intern at Telecom Systems: Developed network throughput diagnostics CLI in Go.", "EXPERIENCE"),
    ("Professional Work History: Junior Web Developer at Local Design Firm, handled responsive client websites.", "EXPERIENCE"),

    # --- PROJECTS ---
    ("NLP Resume Parser: Built a resume parsing pipeline using Python, PyMuPDF, and scikit-learn for ATS scoring.", "PROJECTS"),
    ("E-Commerce Web Application: Developed full stack online shopping portal using React, Node.js, and MongoDB.", "PROJECTS"),
    ("Distributed Task Queue: Implemented asynchronous worker pool in Go with Redis as message broker.", "PROJECTS"),
    ("Real-Time Chat App: Created WebSocket-based messaging platform using FastAPI, React, and Docker.", "PROJECTS"),
    ("Algorithmic Trading Bot: Built Python simulation engine backtesting trading strategies on historical data.", "PROJECTS"),
    ("Capstone Project: Autonomous rover obstacle detection system powered by ROS and OpenCV on Raspberry Pi.", "PROJECTS"),
    ("Movie Recommendation Engine: Implemented collaborative filtering using Python, NumPy, and Scikit-learn.", "PROJECTS"),
    ("Academic Project: Compiler for custom subset of C language built using Lex and Yacc in Linux environment.", "PROJECTS"),
    ("Personal Portfolio Website: Designed and deployed modern responsive portfolio using Next.js and Tailwind CSS.", "PROJECTS"),
    ("COVID-19 Data Tracker: Automated daily infection statistics pipeline scraping data and rendering Chart.js graphs.", "PROJECTS"),
    ("Cloud File Storage Service: Engineered scalable file upload and sharing service using AWS S3 and Express.js.", "PROJECTS"),
    ("Project Title: Microservices Order Management System built with Spring Boot, PostgreSQL, and RabbitMQ.", "PROJECTS"),
    ("Smart Attendance System: Face recognition attendance logging software using Python and OpenCV.", "PROJECTS"),
    ("Multiplayer Chess Game: Built interactive browser chess application with minimax AI engine and WebSockets.", "PROJECTS"),
    ("Blockchain Ledger Simulator: Developed simplified proof-of-work blockchain implementation in Python.", "PROJECTS"),
    ("Search Engine Indexer: Built inverted index and TF-IDF document ranking tool over 50,000 Wikipedia articles.", "PROJECTS"),
    ("Expense Tracker Mobile App: Created cross-platform budget management app using Flutter and SQLite.", "PROJECTS"),
    ("IoT Weather Station: Programmed ESP32 sensor node broadcasting temperature and humidity data to MQTT broker.", "PROJECTS"),
    ("Key-Value Database Engine: Created embedded key-value storage engine in C++ with LSM-tree storage layout.", "PROJECTS"),
    ("Traffic Sign Classifier: Trained convolutional neural network in TensorFlow achieving 96% test accuracy.", "PROJECTS"),
    ("Selected Projects: GitHub Repository Analyzer using GitHub REST API and Dash dashboard visualization.", "PROJECTS"),
    ("API Rate Limiter: Developed distributed sliding window token bucket rate limiter middleware in Go.", "PROJECTS"),
    ("Customer Sentiment Classifier: Built text classification pipeline analyzing Twitter data using Hugging Face.", "PROJECTS"),
    ("Virtual Whiteboard: Collaborative drawing web canvas application using HTML5 Canvas API and Socket.io.", "PROJECTS"),
    ("Linux Shell Clone: Implemented custom command line interpreter supporting piping, redirection, and signals.", "PROJECTS"),
    ("Music Streaming Clone: Built web audio player with playlist management using React, Redux, and Node.js.", "PROJECTS"),
    ("Library Management Portal: Web app for book cataloging and borrowing tracking built with Django and SQLite.", "PROJECTS"),
    ("Neural Machine Translation: Trained sequence-to-sequence attention model for French to English translation.", "PROJECTS"),
    ("Automated Resume Screener: Implemented TF-IDF cosine similarity matcher between job descriptions and resumes.", "PROJECTS"),
    ("Peer-to-Peer File Sharing: Developed BitTorrent-like chunked file distribution protocol in Python.", "PROJECTS"),
    ("Gym Workout Logger: Mobile application built with React Native and Firebase real-time database.", "PROJECTS"),
    ("Markdown Note-Taking App: Built desktop Electron application with instant preview and local file saving.", "PROJECTS"),
    ("Image Captioning Model: Implemented CNN-LSTM encoder-decoder model for generating captions from photos.", "PROJECTS"),
    ("Hotel Room Reservation Engine: RESTful booking API with room availability locking built with FastAPI.", "PROJECTS"),
    ("Network Packet Sniffer: Wrote raw socket packet inspection utility in C displaying TCP/IP headers.", "PROJECTS"),
    ("URL Shortener Microservice: Developed bit.ly clone using Python, Redis caching, and PostgreSQL database.", "PROJECTS"),
    ("Autonomous Drone Navigation: Programmed indoor positioning algorithms using optical flow and ultrasonic sensors.", "PROJECTS"),
    ("Project: Hospital Management Information System with appointment booking and patient records in PHP & MySQL.", "PROJECTS"),
    ("Job Board Scraper: Scraped technical job postings across 5 platforms and stored structured records in MongoDB.", "PROJECTS"),
    ("Interactive Data Visualization Dashboard: Built dynamic dashboard in D3.js illustrating global trade flows.", "PROJECTS"),
    ("Smart Home Automation Hub: Created home control dashboard communicating with Zigbee IoT devices.", "PROJECTS"),
    ("Spam Email Classifier: Trained Naive Bayes classifier on Enron email corpus achieving 98% precision.", "PROJECTS"),
    ("Voice Assistant Prototype: Speech-to-text and intent parsing desktop utility built with Python speech libraries.", "PROJECTS"),
    ("Compiler Optimization Pass: Developed dead code elimination and constant folding pass in LLVM framework.", "PROJECTS"),
    ("Food Delivery Dispatch Simulator: Implemented Dijkstra's algorithm for route optimization in urban delivery.", "PROJECTS"),

    # --- SKILLS ---
    ("Programming Languages: Python, Java, C++, TypeScript, JavaScript, SQL, Go, HTML, CSS", "SKILLS"),
    ("Frameworks & Libraries: React, Node.js, FastAPI, Django, Flask, Express, Spring Boot, PyTorch", "SKILLS"),
    ("Databases: PostgreSQL, MySQL, MongoDB, Redis, SQLite, Microsoft SQL Server, Cassandra", "SKILLS"),
    ("Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, Git, GitHub Actions, Linux, CI/CD", "SKILLS"),
    ("Machine Learning & Data: Scikit-learn, Pandas, NumPy, TensorFlow, Matplotlib, Tableau, NLP", "SKILLS"),
    ("Tools & Platforms: Postman, VS Code, Jira, Git, Docker Compose, Jupyter Notebooks, Swagger", "SKILLS"),
    ("Technical Skills: Object-Oriented Programming, Data Structures, Algorithms, RESTful APIs, System Design", "SKILLS"),
    ("Core Competencies: Agile Methodologies, Test-Driven Development, Microservices Architecture, Clean Code", "SKILLS"),
    ("Web Technologies: HTML5, CSS3, Tailwind CSS, Bootstrap, GraphQL, WebSockets, Redux Toolkit", "SKILLS"),
    ("Operating Systems: Linux (Ubuntu, Debian), macOS, Windows Server, Bash scripting", "SKILLS"),
    ("Proficient in: Python, JavaScript, React, PostgreSQL, Docker, Git, REST API development", "SKILLS"),
    ("Familiar with: C++, Go, Kubernetes, AWS, Apache Kafka, GraphQL, MongoDB, Redis", "SKILLS"),
    ("Software Proficiencies: Java SE, Spring Framework, Hibernate, Maven, JUnit, Mockito", "SKILLS"),
    ("Frontend Skills: React.js, Next.js, Vue.js, JavaScript (ES6+), TypeScript, Sass, Responsive Design", "SKILLS"),
    ("Backend Skills: Python, Node.js, Express, FastAPI, Django REST Framework, SQLAlchemy", "SKILLS"),
    ("DevOps Tools: Docker, Kubernetes, Jenkins, Terraform, Ansible, Prometheus, Grafana, Nginx", "SKILLS"),
    ("Database Management: Relational modeling, indexing, ACID transactions, database normalization", "SKILLS"),
    ("Data Analysis: Exploratory Data Analysis, A/B Testing, Feature Engineering, Regression, Hypothesis Testing", "SKILLS"),
    ("Deep Learning: Convolutional Neural Networks, Recurrent Neural Networks, Transformers, Hugging Face", "SKILLS"),
    ("Technical Expertise: Git version control, branch management, pull request review, merge conflict resolution", "SKILLS"),
    ("Languages: Python (Advanced), Java (Intermediate), C (Basic), SQL (Advanced), JavaScript (Proficient)", "SKILLS"),
    ("Mobile Development: Flutter, Dart, React Native, Android Studio, Xcode, Mobile UI Design", "SKILLS"),
    ("Testing Tools: Pytest, Jest, React Testing Library, Selenium, Postman API testing, Mocha, Chai", "SKILLS"),
    ("API Technologies: RESTful Services, OpenAPI/Swagger specifications, gRPC, Protocol Buffers, Webhooks", "SKILLS"),
    ("Architectures: MVC, Microservices, Event-Driven Architecture, Serverless, Domain-Driven Design", "SKILLS"),
    ("Security & Auth: OAuth2, OpenID Connect, JWT, HTTPS/TLS, OWASP Top 10 vulnerabilities, bcrypt", "SKILLS"),
    ("Big Data: Apache Spark, Apache Hadoop, PySpark, Databricks, Apache Airflow, Kafka streams", "SKILLS"),
    ("Cloud Services: Amazon Web Services, Google Cloud Platform, Microsoft Azure, Serverless Framework", "SKILLS"),
    ("Data Visualization: Matplotlib, Seaborn, Plotly, D3.js, Tableau Desktop, Microsoft Power BI", "SKILLS"),
    ("Operating Environment: Unix shell scripting, command line utilities, SSH, Cron, Vim, Git CLI", "SKILLS"),
    ("Skills & Proficiencies: Full stack development, API integration, schema migration, unit testing", "SKILLS"),
    ("Software Development: SDLC, Scrum sprint planning, code review, continuous integration pipelines", "SKILLS"),
    ("Embedded Skills: C, C++, Arduino, RTOS concepts, I2C, SPI, UART serial protocols, microcontrollers", "SKILLS"),
    ("Mathematical Foundations: Linear Algebra, Multivariate Calculus, Probability, Discrete Mathematics", "SKILLS"),
    ("Methodologies: Test-Driven Development (TDD), Behavior-Driven Development (BDD), Pair Programming", "SKILLS"),
    ("Networking: TCP/IP, DNS, HTTP/HTTPS, SSL certificates, Subnets, Reverse Proxies, Load Balancers", "SKILLS"),
    ("Programming: Python, C#, .NET Core, TypeScript, SQL, Bash script automation", "SKILLS"),
    ("Database Systems: PostgreSQL, MongoDB, Redis in-memory cache, MySQL relational design", "SKILLS"),
    ("Cloud Architecture: IAM policies, S3 bucket management, CloudWatch monitoring, Lambda triggers", "SKILLS"),
    ("Technical Toolbox: Git, VS Code, Postman, Docker, Linux CLI, npm, bun, GitHub Actions", "SKILLS"),
    ("Libraries: Pandas, NumPy, Scikit-learn, SciPy, Beautiful Soup, Requests, Pydantic, Bleach", "SKILLS"),
    ("Frontend Stack: HTML5, CSS3, Tailwind CSS, React, TypeScript, Component Lifecycle, Hooks", "SKILLS"),
    ("Backend Stack: Python 3, FastAPI, Uvicorn, ASGI, Pydantic data validation, SQLAlchemy ORM", "SKILLS"),
    ("Collaboration Tools: Jira, Confluence, Slack, Trello, Notion, GitHub Projects, GitLab", "SKILLS"),
    ("Languages & Tools: Python, SQL, Git, Linux, Docker, PostgreSQL, React, TypeScript, VS Code", "SKILLS"),

    # --- CERTIFICATIONS ---
    ("AWS Certified Solutions Architect – Associate (Amazon Web Services, Valid 2023 - 2026)", "CERTIFICATIONS"),
    ("Google Cloud Certified Associate Cloud Engineer (GCP, Credential ID: GCP-987654)", "CERTIFICATIONS"),
    ("Certified Kubernetes Administrator (CKA), Cloud Native Computing Foundation, 2023", "CERTIFICATIONS"),
    ("Microsoft Certified: Azure Fundamentals (AZ-900), Microsoft, Issued Nov 2022", "CERTIFICATIONS"),
    ("Deep Learning Specialization by Andrew Ng on Coursera (5-course certificate)", "CERTIFICATIONS"),
    ("Oracle Certified Professional: Java SE 11 Developer (1Z0-819), Oracle University", "CERTIFICATIONS"),
    ("Professional Scrum Master I (PSM I), Scrum.org, Credential Verification #54321", "CERTIFICATIONS"),
    ("CompTIA Security+ (SY0-601) Certification, CompTIA, Valid through 2025", "CERTIFICATIONS"),
    ("TensorFlow Developer Certificate, Google Brain Team, Verified Certificate 2023", "CERTIFICATIONS"),
    ("HashiCorp Certified: Terraform Associate (002), Issued October 2023", "CERTIFICATIONS"),
    ("Certifications & Licenses: AWS Certified Cloud Practitioner (CLF-C01), Amazon Web Services", "CERTIFICATIONS"),
    ("Meta Frontend Developer Professional Certificate, Coursera, 9-course program", "CERTIFICATIONS"),
    ("Python for Everybody Specialization, University of Michigan, Coursera", "CERTIFICATIONS"),
    ("Cisco Certified Network Associate (CCNA 200-301), Cisco Systems, 2022", "CERTIFICATIONS"),
    ("Certified Ethical Hacker (CEH v12), EC-Council, Certificate #ECC987654", "CERTIFICATIONS"),
    ("Docker Certified Associate (DCA), Mirantis, Completed July 2023", "CERTIFICATIONS"),
    ("Machine Learning Certificate by Stanford University on Coursera (with Honors)", "CERTIFICATIONS"),
    ("Databricks Certified Associate Developer for Apache Spark 3.0", "CERTIFICATIONS"),
    ("IBM Data Science Professional Certificate, 10-course series on Coursera", "CERTIFICATIONS"),
    ("MongoDB Certified Developer Associate (C100DEV), MongoDB Inc, 2023", "CERTIFICATIONS"),
    ("Certificates: Complete Python Bootcamp: Go from zero to hero in Python, Udemy", "CERTIFICATIONS"),
    ("Red Hat Certified System Administrator (RHCSA), Red Hat Inc, Exam EX200", "CERTIFICATIONS"),
    ("Natural Language Processing Specialization by DeepLearning.AI on Coursera", "CERTIFICATIONS"),
    ("Microsoft Certified: Azure Data Fundamentals (DP-900), Microsoft, 2023", "CERTIFICATIONS"),
    ("Postman API Fundamentals Student Expert Certification, Postman Inc, 2024", "CERTIFICATIONS"),
    ("AWS Certified Developer – Associate (DVA-C02), Amazon Web Services, 2024", "CERTIFICATIONS"),
    ("Google Data Analytics Professional Certificate, Google Career Certificates", "CERTIFICATIONS"),
    ("Professional Certificate in Computer Science for Web Programming, HarvardX", "CERTIFICATIONS"),
    ("Confluent Certified Operator for Apache Kafka, Confluent, 2023", "CERTIFICATIONS"),
    ("FinOps Certified Practitioner (FOCP), The Linux Foundation, 2023", "CERTIFICATIONS"),
    ("Certification: Algorithms Specialization by Stanford University, Coursera, 2022", "CERTIFICATIONS"),
    ("Certified SAFe 5 Practitioner, Scaled Agile Inc, Credential #87654321", "CERTIFICATIONS"),
    ("GitHub Actions Certification, GitHub / Microsoft Learn, Completed 2024", "CERTIFICATIONS"),
    ("Tableau Desktop Specialist, Tableau Software, Verified Certificate 2023", "CERTIFICATIONS"),
    ("Kubernetes and Cloud Native Associate (KCNA), Linux Foundation, 2023", "CERTIFICATIONS"),
    ("Professional Certificate in Machine Learning and Artificial Intelligence, UC Berkeley ExecEd", "CERTIFICATIONS"),
    ("Snowflake SnowPro Core Certification, Snowflake Inc, Completed Dec 2023", "CERTIFICATIONS"),
    ("Professional Scrum Developer (PSD), Scrum.org, Verified Credential, 2023", "CERTIFICATIONS"),
    ("Linux Foundation Certified System Administrator (LFCS), The Linux Foundation", "CERTIFICATIONS"),
    ("Applied Data Science with Python Specialization, University of Michigan", "CERTIFICATIONS"),
    ("Alteryx Designer Core Certified, Alteryx Inc, Verification ID: ALT-2023", "CERTIFICATIONS"),
    ("Certified Information Systems Security Professional (CISSP Associate), (ISC)²", "CERTIFICATIONS"),
    ("GitLab Certified CI/CD Specialist, GitLab Inc, Awarded May 2024", "CERTIFICATIONS"),
    ("Certified Data Privacy Solutions Engineer (CDPSE), ISACA, 2023", "CERTIFICATIONS"),
    ("Coursera Verified Certificate: Mathematics for Machine Learning Specialization, Imperial College London", "CERTIFICATIONS"),

    # --- ACHIEVEMENTS ---
    ("1st Place Winner at National Hackathon 2023 (out of 120+ participating collegiate teams).", "ACHIEVEMENTS"),
    ("Published academic research paper on NLP Transformers in IEEE Student Conference Proceedings.", "ACHIEVEMENTS"),
    ("Awarded Dean's Honor Roll for academic excellence across 6 consecutive undergraduate semesters.", "ACHIEVEMENTS"),
    ("Ranked in the top 1% among 50,000+ candidates in National Engineering Entrance Examination.", "ACHIEVEMENTS"),
    ("Achieved 5-star rating in Python and Problem Solving on HackerRank competitive programming platform.", "ACHIEVEMENTS"),
    ("Recipient of University Merit Scholarship covering 100% of undergraduate tuition fees.", "ACHIEVEMENTS"),
    ("Solved 500+ algorithmic coding problems on LeetCode with top 5% contest rating globally.", "ACHIEVEMENTS"),
    ("Selected as Google Developer Student Clubs (GDSC) Lead for campus chapter (2023 - 2024).", "ACHIEVEMENTS"),
    ("Won Best UI/UX Design Award at State University Annual HackFest for accessibility web application.", "ACHIEVEMENTS"),
    ("Co-authored technical poster presented at ACM International Computing Education Conference.", "ACHIEVEMENTS"),
    ("Honors & Awards: Top Performer Award at TechCorp summer internship program.", "ACHIEVEMENTS"),
    ("Recognized as GitHub Campus Expert, leading campus workshops on Git and open source.", "ACHIEVEMENTS"),
    ("Finalist in Global CodeJam competition, finishing 42nd out of 10,000+ international developers.", "ACHIEVEMENTS"),
    ("Received Best Capstone Project Award from the Department of Computer Science & Engineering.", "ACHIEVEMENTS"),
    ("Awarded National Science Foundation (NSF) Undergraduate Research Fellowship, 2023.", "ACHIEVEMENTS"),
    ("Captain of University Chess Team, led team to victory in Inter-Collegiate State Championship.", "ACHIEVEMENTS"),
    ("Maintained competitive rating of 1850+ on Codeforces competitive programming platform.", "ACHIEVEMENTS"),
    ("Selected among top 50 student open source contributors in Google Summer of Code (GSoC) 2023.", "ACHIEVEMENTS"),
    ("Granted full departmental tuition waiver based on outstanding academic and research performance.", "ACHIEVEMENTS"),
    ("Won 2nd Runner Up in Microsoft Imagine Cup Regional Finals for healthcare AI prototype.", "ACHIEVEMENTS"),
    ("Academic Honors: Valedictorian of Computer Engineering graduating class of 2024.", "ACHIEVEMENTS"),
    ("Organized university's largest annual hackathon with 800+ attendees and $15,000 in sponsor funding.", "ACHIEVEMENTS"),
    ("Recognized with Outstanding Student Contributor Award by Open Source Software Foundation.", "ACHIEVEMENTS"),
    ("Placed 3rd in Smart India Hackathon (Hardware Edition), Ministry of Education, Govt of India.", "ACHIEVEMENTS"),
    ("Author of technical blog with over 50,000 unique monthly readers on software engineering best practices.", "ACHIEVEMENTS"),
    ("Awarded First Prize in Inter-University Algorithm Optimization Coding Challenge.", "ACHIEVEMENTS"),
    ("Earned Knight Badge on LeetCode with top 3.5% contest rating ranking.", "ACHIEVEMENTS"),
    ("Received Academic Excellence Award from Chancellor for maintaining 4.0 cumulative GPA.", "ACHIEVEMENTS"),
    ("Won Best Open Source Project at PyCon Student Showcase for automated testing library.", "ACHIEVEMENTS"),
    ("Selected for competitive Amazon Future Engineer Mentorship Program out of 5,000+ applicants.", "ACHIEVEMENTS"),
    ("Key Achievements: Published 2 peer-reviewed workshop papers in computational linguistics.", "ACHIEVEMENTS"),
    ("Nominated for Best Graduate Teaching Assistant Award by undergraduate student body.", "ACHIEVEMENTS"),
    ("Secured 1st Place in University Data Science Hackathon sponsored by Snowflake.", "ACHIEVEMENTS"),
    ("Received Rotary Youth Leadership Award for establishing local coding club in high schools.", "ACHIEVEMENTS"),
    ("Awarded Best Paper Award at International Student Conference on Information Technology.", "ACHIEVEMENTS"),
    ("Graduated in the top 2% of the Computer Science department class of 2023.", "ACHIEVEMENTS"),
    ("Built open source developer CLI tool with over 1,200 GitHub stars and 20,000 downloads.", "ACHIEVEMENTS"),
    ("Selected as Intel Edge AI Youth Ambassador, conducting 4 technical workshops.", "ACHIEVEMENTS"),
    ("Winner of Fintech Innovation Challenge with $5,000 grant to build prototype product.", "ACHIEVEMENTS"),
    ("Achieved rank 12 out of 8,000 participants in National Cyber Security CTF Competition.", "ACHIEVEMENTS"),
    ("Honored with State Governor's Youth Excellence Medal for community software solutions.", "ACHIEVEMENTS"),
    ("Top 10 Finalist in Kaggle Tabular Playground Machine Learning Competition (Top 0.5%).", "ACHIEVEMENTS"),
    ("Invited guest speaker at DevFest 2024 to deliver workshop on FastAPI microservice architecture.", "ACHIEVEMENTS"),
    ("Received Outstanding Academic Achievement Award from Engineering Alumni Association.", "ACHIEVEMENTS"),
    ("Gold Medalist in State Mathematics Olympiad for undergraduate college students.", "ACHIEVEMENTS"),

    # --- OTHER ---
    ("Languages: English (Fluent), Spanish (Conversational), Mandarin (Basic)", "OTHER"),
    ("Interests: Competitive chess, long-distance marathon running, and open source software.", "OTHER"),
    ("Volunteer Work: Taught weekly coding classes to middle school students at local community center.", "OTHER"),
    ("Hobbies: Landscape photography, playing classical piano, and hiking national parks.", "OTHER"),
    ("Extracurricular Activities: Active member of University Robotics Club and ACM Student Chapter.", "OTHER"),
    ("Personal Interests: Astronomy, electronic music production, and home brewing espresso.", "OTHER"),
    ("Volunteer Experience: Organized quarterly food drives with local non-profit food bank.", "OTHER"),
    ("Fluent in German and English; intermediate proficiency in conversational French.", "OTHER"),
    ("Community Involvement: Volunteered 100+ hours as disaster relief coordinator with Red Cross.", "OTHER"),
    ("Hobbies & Interests: Reading science fiction, playing acoustic guitar, and rock climbing.", "OTHER"),
    ("Languages Spoken: Hindi (Native), English (Professional), Japanese (JLPT N4 Level)", "OTHER"),
    ("Extracurricular: President of University Board Game Society, organizing weekly strategy nights.", "OTHER"),
    ("Personal: Avid marathon runner, completed Boston Marathon in 3 hours 15 minutes.", "OTHER"),
    ("Volunteer Tutor: Mentored underprivileged high school students in STEM subjects and SAT prep.", "OTHER"),
    ("Interests & Pastimes: Urban gardening, woodworking, and retro computer hardware restoration.", "OTHER"),
    ("Languages: Bilingual in English and French; basic knowledge of conversational Italian.", "OTHER"),
    ("Volunteering: Built and maintained informational website for local animal rescue shelter.", "OTHER"),
    ("Hobbies: Cycling, cooking traditional Mediterranean recipes, and digital illustration.", "OTHER"),
    ("Extracurricular Involvement: Secretary of Society of Women Engineers (SWE) campus branch.", "OTHER"),
    ("Personal Passions: Podcasts on history and philosophy, independent indie game development.", "OTHER"),
    ("Spoken Languages: English (Native), Portuguese (Fluent), Spanish (Intermediate)", "OTHER"),
    ("Community Service: Assisted elderly residents with digital literacy and smartphone setup.", "OTHER"),
    ("Interests: Table tennis, film photography, and participating in local trivia tournaments.", "OTHER"),
    ("Volunteer Experience: Blood donor coordinator for university bi-annual health camps.", "OTHER"),
    ("Other Activities: Member of university cycling club, competing in state inter-collegiate rides.", "OTHER"),
    ("Languages: English, Arabic (Fluent written and spoken), German (Beginner)", "OTHER"),
    ("Personal Pursuits: 3D printing and designing custom mechanical keyboard enclosures.", "OTHER"),
    ("Hobbies: Playing violin in community orchestra and studying history of mathematics.", "OTHER"),
    ("Volunteer: Habitat for Humanity build crew volunteer, constructing affordable housing.", "OTHER"),
    ("Extracurricular: Event host for university annual cultural symposium and debate society.", "OTHER"),
    ("Languages known: English, Bengali, Hindi (Proficient in reading, writing, and speaking)", "OTHER"),
    ("Interests: Mountain biking, bird watching, and baking artisanal sourdough bread.", "OTHER"),
    ("Community Work: Tech volunteer at local public library, conducting internet safety classes.", "OTHER"),
    ("Hobbies include: Camping, building custom PC rigs, and playing strategy board games.", "OTHER"),
    ("Personal: Traveled to 15+ countries, passionate about exploring different global cultures.", "OTHER"),
    ("Languages: Fluent in Russian and English; basic conversational competence in Korean.", "OTHER"),
    ("Volunteer: Tree planting campaign volunteer with city urban forestry initiative.", "OTHER"),
    ("Interests: Podcasting about technology ethics, playing badminton, and home automation.", "OTHER"),
    ("Extracurriculars: Treasurer of University Debate Union, managing $8,000 annual budget.", "OTHER"),
    ("Hobbies: Calligraphy, watercolor landscape painting, and solving crossword puzzles.", "OTHER"),
    ("Languages: English (Native), Cantonese (Fluent conversational), Mandarin (Basic)", "OTHER"),
    ("Volunteer: Audio recording reader for blind and visually impaired students.", "OTHER"),
    ("Personal Interests: Specialty coffee roasting, playing ultimate frisbee, and reading non-fiction.", "OTHER"),
    ("Community: Volunteer webmaster for neighborhood association civic improvement board.", "OTHER"),
    ("References available upon request. Willing to relocate for full-time opportunities.", "OTHER"),
]

# Separate held-out evaluation test cases: 7 examples per class = 63 unseen test cases
TEST_CASES: List[Tuple[str, str]] = [
    # SUMMARY
    ("Self-motivated software engineer with deep interest in backend infrastructure and clean API design.", "SUMMARY"),
    ("Dedicated undergraduate in Information Technology seeking an internship in cloud systems.", "SUMMARY"),
    ("Experienced frontend specialist focused on accessible, high-performance web applications.", "SUMMARY"),
    ("Passionate data science student with experience in predictive modeling and quantitative analysis.", "SUMMARY"),
    ("Creative full stack engineer committed to building scalable tools for collaborative teams.", "SUMMARY"),
    ("Results-oriented developer with solid grounding in relational databases and algorithms.", "SUMMARY"),
    ("Profile: Junior engineer seeking opportunities in distributed systems and cloud services.", "SUMMARY"),

    # CONTACT
    ("Email: marcus.vance@techcorp.io | Phone: +1 555 456 7891 | Seattle, WA", "CONTACT"),
    ("github.com/developer-alex | alex.dev@inbox.com | Tel: 555-012-3456", "CONTACT"),
    ("Contact: sophia.chen@university.edu | Mobile: 555-890-1234 | San Jose, CA", "CONTACT"),
    ("linkedin.com/in/carlos-mendez | carlos.mendez@mail.net | +1 (555) 321-6549", "CONTACT"),
    ("Address: 789 Innovation Way, New York, NY | email: dev.hire@testdomain.com", "CONTACT"),
    ("tel: +44 20 8123 4567 | email: uk.applicant@oxford.edu | London, UK", "CONTACT"),
    ("portfolio: candidate-work.dev | phone: 555-987-1122 | email: hello@candidate-work.dev", "CONTACT"),

    # EDUCATION
    ("Bachelor of Science in Information Technology, University of Washington, 2021 - 2025", "EDUCATION"),
    ("B.Tech in Computer Engineering, Indian Institute of Technology, CGPA 9.1/10.0, 2024", "EDUCATION"),
    ("Master of Science in Software Engineering, Carnegie Mellon University, Silicon Valley, 2023", "EDUCATION"),
    ("B.S. in Computer Science with Honors, University of Texas at Dallas, GPA: 3.82", "EDUCATION"),
    ("Relevant Coursework: Distributed Systems, Compiler Optimization, Database Management, Linear Algebra", "EDUCATION"),
    ("Associate Degree in Computer Programming, City College of San Francisco, 2022", "EDUCATION"),
    ("High School Diploma, St. Paul's Academy, Physics & Mathematics, 96%", "EDUCATION"),

    # EXPERIENCE
    ("Software Engineer Intern at Stripe (Summer 2024): Built webhook reconciliation endpoints in Python.", "EXPERIENCE"),
    ("Junior Backend Developer at CloudScale Inc: Optimized Redis caching and PostgreSQL query latency.", "EXPERIENCE"),
    ("Frontend Developer Intern at UI Studios: Designed responsive checkout workflow using React and Tailwind.", "EXPERIENCE"),
    ("Graduate Research Assistant at AI Institute: Trained transformer language models on clinical abstracts.", "EXPERIENCE"),
    ("Site Reliability Intern at DataPipeline Co: Automated Grafana alerts and Prometheus metrics collection.", "EXPERIENCE"),
    ("QA Engineering Intern at FinTech Labs: Wrote automated integration test suite using pytest and Docker.", "EXPERIENCE"),
    ("Undergraduate Teaching Assistant: Led weekly programming lab sessions for 45 computer science students.", "EXPERIENCE"),

    # PROJECTS
    ("Microservices Order Tracker: Built event-driven order processing application with FastAPI and Kafka.", "PROJECTS"),
    ("Search Query Ranking Engine: Implemented TF-IDF indexing and vector search over 20,000 documents in Python.", "PROJECTS"),
    ("Collaborative Canvas Application: Developed real-time whiteboard in React with WebSockets and Canvas API.", "PROJECTS"),
    ("Cryptocurrency Portfolio Manager: Mobile app built with Flutter and SQLite for offline asset tracking.", "PROJECTS"),
    ("Image Segmentation Pipeline: Trained U-Net architecture in PyTorch achieving 91% IoU on test set.", "PROJECTS"),
    ("Autonomous Drone Controller: Programmed sensor fusion and obstacle avoidance on Raspberry Pi in C++.", "PROJECTS"),
    ("Smart Contract Voting DApp: Implemented decentralized voting protocol using Solidity and Ethereum web3.", "PROJECTS"),

    # SKILLS
    ("Languages: Python, Go, C++, TypeScript, SQL, JavaScript, HTML, CSS, Bash", "SKILLS"),
    ("Frameworks: React, Next.js, FastAPI, Node.js, Express, PyTorch, Scikit-learn, Tailwind CSS", "SKILLS"),
    ("Databases & Cloud: PostgreSQL, MongoDB, Redis, AWS (EC2, S3, RDS), Docker, Kubernetes", "SKILLS"),
    ("Tools & Methodologies: Git, GitHub Actions, Linux CLI, Postman, Jira, Agile Scrum, CI/CD", "SKILLS"),
    ("Data Science Tools: Pandas, NumPy, SciPy, Matplotlib, Seaborn, Tableau, Jupyter Notebook", "SKILLS"),
    ("Technical Competencies: RESTful API Design, Microservices, Unit Testing, Schema Optimization", "SKILLS"),
    ("Core Skills: Data Structures, Algorithms, Object-Oriented Design, Automated Testing, Linux", "SKILLS"),

    # CERTIFICATIONS
    ("AWS Certified Solutions Architect – Associate (Credential ID: AWS-87654321)", "CERTIFICATIONS"),
    ("Certified Kubernetes Administrator (CKA), Linux Foundation & CNCF, 2024", "CERTIFICATIONS"),
    ("Microsoft Certified: Azure Fundamentals (AZ-900), Microsoft, 2023", "CERTIFICATIONS"),
    ("Google Cloud Certified Professional Cloud Architect, Google, 2023 - 2026", "CERTIFICATIONS"),
    ("Deep Learning Specialization by Andrew Ng on Coursera, 5-course certificate with Honors", "CERTIFICATIONS"),
    ("HashiCorp Certified: Terraform Associate, HashiCorp, Verified Badge 2023", "CERTIFICATIONS"),
    ("Oracle Certified Professional: Java SE 17 Developer, Oracle Corporation, 2023", "CERTIFICATIONS"),

    # ACHIEVEMENTS
    ("1st Place Winner at HackMIT 2023 among 250+ collegiate engineering teams.", "ACHIEVEMENTS"),
    ("Ranked in the top 0.5% globally in Google Kickstart competitive programming round.", "ACHIEVEMENTS"),
    ("Published first-author paper on NLP model evaluation at EMNLP Student Workshop 2024.", "ACHIEVEMENTS"),
    ("Awarded University Chancellor's Gold Medal for highest cumulative GPA in Engineering.", "ACHIEVEMENTS"),
    ("Recipient of Microsoft Undergraduate Diversity Scholarship ($10,000 merit award).", "ACHIEVEMENTS"),
    ("Solved 600+ problems on LeetCode with top 4% worldwide contest ranking.", "ACHIEVEMENTS"),
    ("Won Best Open Source Tool Award at Global Python Conference 2023.", "ACHIEVEMENTS"),

    # OTHER
    ("Fluent in English and Spanish; conversational proficiency in Mandarin Chinese.", "OTHER"),
    ("Interests: Marathon training, competitive chess, and volunteering at animal shelters.", "OTHER"),
    ("Hobbies: Acoustic guitar, landscape film photography, and hiking national parks.", "OTHER"),
    ("Volunteer Experience: Conducted weekly weekend coding workshops for local high school students.", "OTHER"),
    ("Extracurricular: President of University Open Source Club, organizing annual hackathons.", "OTHER"),
    ("Personal: Amateur radio operator (Callsign: W1AW), interested in wireless mesh networks.", "OTHER"),
    ("Willing to relocate. References and transcripts available upon request.", "OTHER"),
]


def validate_and_save_dataset():
    """Validates the dataset rows, checks distribution, and writes files."""
    os.makedirs(os.path.join("data", "training"), exist_ok=True)
    os.makedirs(os.path.join("data", "tests"), exist_ok=True)
    os.makedirs(os.path.join("data", "models"), exist_ok=True)

    train_path = os.path.join("data", "training", "resume_sections.csv")
    test_path = os.path.join("data", "tests", "resume_section_test_cases.csv")
    stats_path = os.path.join("data", "training", "dataset_statistics.json")

    # 1. Validation checks
    texts_seen = set()
    duplicates = []
    empty_rows = 0
    invalid_labels = []

    for idx, (text, label) in enumerate(TRAINING_EXAMPLES):
        clean_text = text.strip()
        if not clean_text:
            empty_rows += 1
        if label not in VALID_LABELS:
            invalid_labels.append((idx, label))
        if clean_text in texts_seen:
            duplicates.append((idx, clean_text[:50]))
        texts_seen.add(clean_text)

    # Check for leakage between train and test
    leakage = []
    for test_text, _ in TEST_CASES:
        if test_text.strip() in texts_seen:
            leakage.append(test_text)

    train_counter = Counter(label for _, label in TRAINING_EXAMPLES)
    test_counter = Counter(label for _, label in TEST_CASES)

    statistics = {
        "dataset_name": "Academic Resume Section Classification Dataset",
        "provenance": "Curated realistic synthetic academic dataset (no real PII)",
        "total_training_examples": len(TRAINING_EXAMPLES),
        "total_held_out_test_cases": len(TEST_CASES),
        "number_of_classes": len(VALID_LABELS),
        "valid_classes": VALID_LABELS,
        "class_distribution_training": dict(train_counter),
        "class_distribution_test_cases": dict(test_counter),
        "validation_report": {
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
            "empty_row_count": empty_rows,
            "invalid_labels": invalid_labels,
            "train_test_leakage_count": len(leakage),
            "is_valid": (
                len(duplicates) == 0
                and empty_rows == 0
                and len(invalid_labels) == 0
                and len(leakage) == 0
                and set(train_counter.keys()) == set(VALID_LABELS)
            ),
        },
    }

    # Write training dataset
    with open(train_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for text, label in TRAINING_EXAMPLES:
            writer.writerow([text.strip(), label.strip()])

    # Write separate unseen test cases
    with open(test_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "expected_label"])
        for text, label in TEST_CASES:
            writer.writerow([text.strip(), label.strip()])

    # Write statistics JSON
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(statistics, f, indent=2)

    print("=== DATASET GENERATION & VALIDATION REPORT ===")
    print(f"Training examples: {len(TRAINING_EXAMPLES)}")
    print(f"Unseen test cases: {len(TEST_CASES)}")
    print(f"Classes: {len(VALID_LABELS)} (45 training / 7 test per class)")
    print(f"Dataset Valid: {statistics['validation_report']['is_valid']}")
    print(f"Output files: {train_path}, {test_path}, {stats_path}")


if __name__ == "__main__":
    validate_and_save_dataset()

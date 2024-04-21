
# HR Insights Dashboard with Candidates Recommendation Project

## Introduction

Welcome to our HR Insights Dashboard with Candidates Recommendation project! This project aims to provide valuable insights into HR data and recommend suitable candidates for various positions within an organization. Leveraging state-of-the-art machine learning models and visualization tools, we strive to enhance the efficiency and effectiveness of the recruitment process.

## Overview

In today's competitive job market, organizations face the challenge of identifying and hiring the best talent swiftly. Traditional methods of recruitment often fall short in providing actionable insights and personalized recommendations. Our project addresses this issue by employing cutting-edge technologies, including H2O.ai's Large Language Model and Wave H2O for intuitive dashboard visualization.
## Team

This project was brought to life by the collaborative efforts of the following team members:

# HR Insights Dashboard with Candidates Recommendation Project

## Team

This project was brought to life by the collaborative efforts of the following team members:

- **Lian Kah Seng**：Frontend Developer
- **Qiu Qishuo**：Frontend Developer
- **Wang Zhuoyu**：Frontend Developer
- **Liau Zhan Yi**：Backend Developer
- **Wang Jianing**：Backend Developer
- **Zhang Xiangyu**：Backend Developer

We appreciate the dedication and expertise of each team member in making this project a success!

## Key Features

- **Seamless Resume Parsing**: Empowered by H2O, our system effortlessly parses resumes of diverse formats including: DOC, DOCX, PDF, HTML and etc.

- **LLMs and Prompt Engineering**: We utilize H2O.ai's powerful LLM platform h20eGPT, to analyze and extract meaningful patterns from the HR data. These models are trained to predict candidate suitability for specific roles based on historical data and relevant features.

- **Candidate Recommendation**: Leveraging the insights generated by our machine learning models, the dashboard provides personalized recommendations for candidates best suited for particular job positions. These recommendations consider factors like skills, experience, education, and cultural fit.

- **Visualization Dashboard**: Wave H2O's intuitive dashboard allows users to visualize key HR metrics, candidate profiles, and recommendation results in an interactive and customizable manner. This enables HR professionals and hiring managers to make informed decisions quickly.

- **H20eGPT chatbot**: Embedded chatbox enable employees to further understand candidates from customized prespective and therefore effectively assist decision-making under evaluation of different metrics.

## Installation with Python
### File structure
```bash
.
├── README.md
├── frontend
│   ├── chatbot.py
│   └── dashboard.py
├── requirements.txt
└── server
    ├── config.py
    ├── flask_app
    │   ├── __init__.py
    │   ├── routes.py
    │   └── services
    ├── main.py
    ├── schema
    │   ├── 0310.sql
    │   └── dummy.sql
    └── utils.py
```

### 1. Create virtual environments 
    
    python -m venv /path/to/new/virtual/environment

### 2. Install requirements

    pip install -r requirements.txt

### 3. Set server folder as the working directory and Start flask app
    
    cd /server -> python main.py

### 4. Open another teriminal, Set the frontend folder as the working directory and Start wave app

    cd /frontend -> wave run dashboard.py
    
## Usage

Once the installation is complete and the system is configured, you can use the HR Insights Dashboard with Candidates Recommendation project as follows:

1. Access the Wave H2O dashboard interface through your web browser.
2. Explore the various HR metrics and visualizations available on the dashboard to gain insights into your organization's recruitment process.
3. Utilize the candidate recommendation feature to identify suitable candidates for specific job positions based on the generated insights.
4. Customize the dashboard settings and filters to tailor the recommendations according to your organization's requirements.
5. Take advantage of the chatbot to further understand candidate and assist your descision making.

## License

Our HR Insights Dashboard with Candidates Recommendation project is licensed under the [MIT License](LICENSE.md). Feel free to use, modify, and distribute the code for both commercial and non-commercial purposes, with appropriate attribution.

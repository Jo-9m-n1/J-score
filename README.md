
<img src="https://readme-typing-svg.herokuapp.com?font=Roboto+Bold&size=35&pause=1000&color=87CEEB&width=500&height=70&lines=J-score*" alt="J-score*"/>

![Python](https://img.shields.io/badge/Python-yellow)

[**J-score**](https://j-score.vercel.app/) is a dedicated platform designed to **help CÉGEP students** navigate and plan their academic futures. By leveraging **mathematical logic rooted in probability and statistics** (201-SN1-RE), it provides students with data-driven insights into their academic trajectory. 

## Creators
- [Jongmin Lee](https://www.linkedin.com/in/jo-9m-n1/)
- [James Ferdinand Combista](https://www.linkedin.com/in/james-ferdinand-combista-88039b316/)

<img src="https://user-images.githubusercontent.com/74038190/216654116-d0e8d227-7977-4edc-8d36-63461bda9503.gif" width="90">

## Key Features

- **R-score calculation**: Estimate your R-Score using weighted averages and course-specific data to gauge academic performance. 
- **Admission probability calculation**: Evaluate your chances of acceptance into competitive university programs based on historical the cut-off and your R-score.
- **Target R-score Projection**: Determine the specific R-Score required in future semesters to reach your academic goals.
- **Probabilistic Learning Modules**: Educational tools that demonstrate the mathematical logic of probability and statistics used in the R-Score system.

## Tech Stack

- **Frontend**: HTML, CSS & JavaScript
- **Backend**: Python (Flask)  

## Getting Started

### 1. Clone the repository  
```bash
git clone https://github.com/yourusername/j-score.git
cd j-score
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies
Ensure you have Python installed, then run:

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase
To connect the app to Supabase, create a Supabase project and set these environment variables in `.env`:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
# Optional, use this if you want server-side access for all operations
# This is required for signup/account creation if your Supabase tables use row-level security.
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Create two tables in Supabase:

- `profiles` with at least the columns:
  - `id` uuid primary key default `gen_random_uuid()` or `uuid_generate_v4()`
  - `name` text
  - `nickname` text unique
  - `password` text
- `scores` with at least the columns:
  - `id` uuid primary key default `gen_random_uuid()` or `uuid_generate_v4()`
  - `profile_id` uuid references `profiles.id`
  - `nickname` text
  - `subject` text
  - `grade` numeric
  - `class_grade` numeric
  - `std` numeric
  - `class_high_grade` numeric
  - `credits` numeric
  - `class_type` text
  - `r_score` numeric
  - `created_at` timestamp with time zone default `now()`

The app now exposes a Flask JSON endpoint at `/api/scores` that fetches data from Supabase and allows the frontend to display it.

### 5. Run the Application
You can start the server using the standard Python command:

```Bash
python app.py
```

Or use the Flask CLI for an enhanced development experience (includes auto-reload):

```Bash
flask run --debug
```

Then, open your browser and navigate to http://127.0.0.1:5000.

# Aegis Engine

This is the codebase for the Aegis Engine. 

I built this engine to solve a massive headache I kept seeing during multi-day hiring drives and assessments: candidates from Slot 1 inevitably memorize the questions and leak them on Telegram or WhatsApp. By Slot 5, the passing rate magically skyrockets, and the test becomes completely useless. 

I wanted to fix this programmatically. I didn't just want to shuffle questions aroundâ€”I designed this system to actually detect when a leak likely happened and mathematically shift the testing patterns to stop the cheating in its tracks.

## How I built it

Instead of relying on a static question bank, I created a dynamic 10-slot assembler with a built-in automated defense mechanism.

* **It eats messy files:** You can upload basically any CSV, PDF, or TXT file. Since PDF parsing is usually a nightmare, I wrote a highly aggressive custom regex and PyMuPDF parser. It hunts down question numbers, figures out where the multiple-choice options are, and rips them out. I also made sure it automatically strips out hidden "Ans: C" text so the system doesn't accidentally print the answers.
* **Smart overlap control:** You tell it how many slots you need and the max overlap (e.g., 10%). I set up a constrained optimizer to build the slots so no two adjacent slots share too many questions.
* **The "Leak Defense" (CUSUM):** After each slot, you punch in the average passing percentage. I integrated a statistical CUSUM algorithm to track this baseline. If it sees an unnatural spike (like a sudden 15% jump in passing rates), the system assumes the test leaked.
* **Pattern Shifting & SymPy:** This is my favorite part. When the engine detects a leak, it triggers a "Pattern Shift". Instead of just pulling harder questions, it changes the *methodology* (e.g., swapping standard equations for abstract visual topology). I also integrated `sympy` (Symbolic Python) as a guardrail to verify the math on these shifted quantitative questions, guaranteeing I don't accidentally generate unsolvable garbage.
* **PDF Export:** Once a slot is generated, you just click a button and it spits out a cleanly formatted PDF using `fpdf2`, automatically leaving blank spaces for descriptive questions.

## Tech Stack

I kept the stack mostly Python-native:
* **UI:** Streamlit (it was super fast for me to build this internal dashboard)
* **Document Parsing:** `PyMuPDF` (fitz) + heavy Regex
* **Math & Logic:** `pandas`, `numpy`, `sympy` 
* **Exports:** `fpdf2`

## Running it locally

It's pretty straightforward to get this running on your machine. 

1. **Clone and setup:**
   Navigate to the folder and install the dependencies I used.
   ```bash
   cd aptitude_platform
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   If you want to use the AI gateway features I prepped, copy `.env.example` to `.env` and drop in your Google Cloud / Gemini API keys. 

3. **Spin up the app:**
   ```bash
   streamlit run app.py
   ```
   This will open the dashboard at `http://localhost:8501`. 

## Playing around with it

If you want to see the leak defense I built in action:
1. Upload a sample PDF or CSV question bank.
2. Hit "Generate Slot 1".
3. For Slot 2, put in a normal passing percentage (like 65%).
4. For Slot 3, pretend the test leaked and put in something like 85%. You'll see the UI throw red alerts, trigger the CUSUM defense, and completely alter the test methodologies for the exported PDF.

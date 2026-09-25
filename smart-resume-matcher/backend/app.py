import re

from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader

app = Flask(__name__)

CORS(app)


# =========================================================
# CANONICAL SKILL -> (CATEGORY, ALIASES)
# =========================================================

SKILLS = {

    "Python": ("lang", ["python", "python3"]),
    "Java": ("lang", ["java"]),
    "JavaScript": ("lang", ["javascript", "js", "es6"]),
    "TypeScript": ("lang", ["typescript"]),
    "C++": ("lang", ["c++"]),
    "C#": ("lang", ["c#"]),
    "Go": ("lang", ["golang"]),
    "PHP": ("lang", ["php"]),
    "Ruby": ("lang", ["ruby"]),

    "SQL": ("data", ["sql", "t-sql", "pl/sql"]),
    "MySQL": ("data", ["mysql"]),
    "PostgreSQL": ("data", ["postgresql", "postgres"]),
    "MongoDB": ("data", ["mongodb", "mongo"]),
    "Redis": ("data", ["redis"]),
    "Pandas": ("ml", ["pandas"]),
    "NumPy": ("ml", ["numpy"]),

    "React": ("web", ["react", "reactjs", "react.js"]),
    "Angular": ("web", ["angular"]),
    "Vue": ("web", ["vue", "vuejs", "vue.js"]),
    "Node.js": ("web", ["node.js", "nodejs", "node"]),
    "HTML": ("web", ["html", "html5"]),
    "CSS": ("web", ["css", "css3"]),
    "Flask": ("web", ["flask"]),
    "Django": ("web", ["django"]),
    "FastAPI": ("web", ["fastapi"]),
    "Spring Boot": ("web", ["spring boot", "springboot", "spring"]),
    "REST APIs": ("web", ["rest", "restful", "rest api", "rest apis"]),

    "AWS": ("cloud", ["aws", "amazon web services", "ec2", "s3"]),
    "Azure": ("cloud", ["azure"]),
    "GCP": ("cloud", ["gcp", "google cloud"]),

    "Docker": ("devops", ["docker", "containers", "containerization"]),
    "Kubernetes": ("devops", ["kubernetes", "k8s"]),
    "Terraform": ("devops", ["terraform"]),
    "CI/CD": ("devops", ["ci/cd", "cicd", "jenkins", "github actions"]),
    "Git": ("devops", ["git", "github", "gitlab"]),
    "Linux": ("devops", ["linux", "unix"]),

    "Machine Learning": ("ml", ["machine learning", "ml"]),
    "Deep Learning": ("ml", ["deep learning"]),
    "TensorFlow": ("ml", ["tensorflow"]),
    "PyTorch": ("ml", ["pytorch"]),
    "Scikit-learn": ("ml", ["scikit-learn", "sklearn"]),
    "NLP": ("ml", ["nlp", "natural language processing"]),

    "Data Analysis": ("data", ["data analysis", "data analytics"]),
    "Tableau": ("data", ["tableau"]),
    "Power BI": ("data", ["power bi", "powerbi"]),
    "Excel": ("data", ["excel"]),

    "Agile": ("soft", ["agile", "scrum", "kanban"]),
    "Communication": ("soft", ["communication"]),
    "Leadership": ("soft", ["leadership", "team lead"]),
    "Problem Solving": ("soft", ["problem solving", "problem-solving"]),
}


# =========================================================
# FIND SKILLS
# =========================================================

def find_skills(text):

    t = " " + re.sub(
        r"[^a-z0-9+#./ ]",
        " ",
        text.lower()
    ) + " "

    found = []

    for name, (_, aliases) in SKILLS.items():

        for alias in set(aliases) | {name.lower()}:

            pattern = (
                r"(?<![a-z0-9+#])"
                + re.escape(alias)
                + r"(?![a-z0-9+#])"
            )

            if re.search(pattern, t):
                found.append(name)
                break

    return found


# =========================================================
# RESUME SECTIONS
# =========================================================

SECTIONS = {

    "education": [
        "education",
        "academic"
    ],

    "experience": [
        "experience",
        "employment",
        "work history"
    ],

    "projects": [
        "projects",
        "project"
    ],

    "skills": [
        "skills",
        "technical skills"
    ],

    "certifications": [
        "certifications",
        "certificates"
    ],

    "leadership": [
        "leadership",
        "volunteering",
        "activities"
    ]
}


def split_sections(text):

    out = {}
    current = None

    for line in text.splitlines():

        s = line.strip()

        key = next(
            (
                k
                for k, values in SECTIONS.items()
                if s.lower().strip(":") in values
            ),
            None
        )

        if key:

            current = key
            out[current] = []

        elif current and s:

            out[current].append(s)

    # IMPORTANT:
    # We no longer limit every section to 8 lines.
    return out


# =========================================================
# RESUME INFORMATION
# =========================================================

def resume_info(text, skills):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    email = re.search(
        r"[\w.+-]+@[\w-]+\.[\w.-]+",
        text
    )

    phone = re.search(
        r"(\+?\d[\d\s().-]{8,}\d)",
        text
    )

    sections = split_sections(text)

    return {

        "name": lines[0] if lines else "",

        "email": (
            email.group(0)
            if email
            else ""
        ),

        "phone": (
            phone.group(0).strip()
            if phone
            else ""
        ),

        "education": sections.get(
            "education",
            []
        ),

        "experience": sections.get(
            "experience",
            []
        ),

        "projects": sections.get(
            "projects",
            []
        ),

        "skills": skills,

        "certifications": sections.get(
            "certifications",
            []
        ),

        "leadership": sections.get(
            "leadership",
            []
        )
    }


# =========================================================
# ANALYSIS EXPLANATION
# =========================================================

def explain(match, missing, related):

    def join_items(items):
        return ", ".join(items[:6])

    parts = []

    if match:

        parts.append(
            f"The resume demonstrates "
            f"{join_items(match)}, "
            f"which are directly required "
            f"by the job description."
        )

    else:

        parts.append(
            "None of the skills required by "
            "the job description were clearly "
            "found in the resume."
        )

    if missing:

        parts.append(
            f"However, {join_items(missing)} "
            f"{'is' if len(missing) == 1 else 'are'} "
            "required but not clearly present."
        )

    if related:

        parts.append(
            f"Related experience such as "
            f"{join_items(related)} may partly "
            "offset these gaps."
        )

    parts.append(
        "This is a keyword-based estimate, "
        "not an official ATS score."
    )

    return " ".join(parts)


# =========================================================
# RESUME TAILORING
# =========================================================

def polish_bullet(text):

    replacements = {

        "built": "Developed",
        "made": "Created",
        "used": "Utilized",
        "helped": "Supported",
        "did": "Performed"

    }

    result = text.strip()

    for old, new in replacements.items():

        result = re.sub(
            r"^" + re.escape(old) + r"\b",
            new,
            result,
            flags=re.IGNORECASE
        )

    if result:

        result = (
            result[0].upper()
            + result[1:]
        )

    if result and result[-1] not in ".!?":

        result += "."

    return result


def build_tailored_resume(text, jd):

    resume_skills = find_skills(text)

    jd_skills = find_skills(jd)

    matching = [
        skill
        for skill in jd_skills
        if skill in resume_skills
    ]

    missing = [
        skill
        for skill in jd_skills
        if skill not in resume_skills
    ]

    sections = split_sections(text)

    experience = sections.get(
        "experience",
        []
    )

    projects = sections.get(
        "projects",
        []
    )

    # Prioritize experience/projects
    # that contain JD-required skills.

    def priority_score(line):

        line_skills = find_skills(line)

        return sum(
            1
            for skill in line_skills
            if skill in matching
        )

    experience = sorted(
        experience,
        key=priority_score,
        reverse=True
    )

    projects = sorted(
        projects,
        key=priority_score,
        reverse=True
    )

    # -----------------------------------------------------
    # BUILD TAILORED RESUME
    # -----------------------------------------------------

    lines = []

    resume_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # NAME

    if resume_lines:

        lines.append(
            resume_lines[0]
        )

        lines.append("")

    # CONTACT

    email = re.search(
        r"[\w.+-]+@[\w-]+\.[\w.-]+",
        text
    )

    phone = re.search(
        r"(\+?\d[\d\s().-]{8,}\d)",
        text
    )

    contact = []

    if email:
        contact.append(
            email.group(0)
        )

    if phone:
        contact.append(
            phone.group(0).strip()
        )

    if contact:

        lines.append(
            " | ".join(contact)
        )

        lines.append("")

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    lines.append(
        "PROFESSIONAL SUMMARY"
    )

    if matching:

        lines.append(
            "Computer Science student with "
            "experience in "
            + ", ".join(matching[:6])
            + "."
        )

    else:

        lines.append(
            "Computer Science student with "
            "experience across software "
            "development and technical projects."
        )

    lines.append("")

    # -----------------------------------------------------
    # TECHNICAL SKILLS
    # -----------------------------------------------------

    lines.append(
        "TECHNICAL SKILLS"
    )

    prioritized_skills = (
        matching
        + [
            skill
            for skill in resume_skills
            if skill not in matching
        ]
    )

    if prioritized_skills:

        lines.append(
            ", ".join(prioritized_skills)
        )

    lines.append("")

    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    if experience:

        lines.append(
            "EXPERIENCE"
        )

        for item in experience:

            lines.append(
                polish_bullet(item)
            )

        lines.append("")

    # -----------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------

    if projects:

        lines.append(
            "PROJECTS"
        )

        for item in projects:

            lines.append(
                polish_bullet(item)
            )

        lines.append("")

    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    education = sections.get(
        "education",
        []
    )

    if education:

        lines.append(
            "EDUCATION"
        )

        for item in education:

            lines.append(item)

        lines.append("")

    # -----------------------------------------------------
    # CERTIFICATIONS
    # -----------------------------------------------------

    certifications = sections.get(
        "certifications",
        []
    )

    if certifications:

        lines.append(
            "CERTIFICATIONS"
        )

        for item in certifications:

            lines.append(item)

        lines.append("")

    # -----------------------------------------------------
    # LEADERSHIP
    # -----------------------------------------------------

    leadership = sections.get(
        "leadership",
        []
    )

    if leadership:

        lines.append(
            "LEADERSHIP / ACTIVITIES"
        )

        for item in leadership:

            lines.append(item)

        lines.append("")

    return {

        "resume_text":
            "\n".join(lines).strip(),

        "matching_skills":
            matching,

        "missing_skills":
            missing,

        "resume_skills":
            resume_skills,

        "jd_skills":
            jd_skills
    }


# =========================================================
# ANALYZE API
# =========================================================

@app.post("/api/analyze")
def analyze():

    f = request.files.get(
        "resume"
    )

    jd = (
        request.form.get(
            "job_description"
        )
        or ""
    ).strip()

    if not f or not f.filename:

        return jsonify(
            error="Please upload a PDF resume."
        ), 400

    if not f.filename.lower().endswith(".pdf"):

        return jsonify(
            error="Only PDF files are supported."
        ), 400

    if len(jd) < 20:

        return jsonify(
            error="Please paste a job description "
                  "(at least a few sentences)."
        ), 400

    try:

        text = "\n".join(
            (
                page.extract_text()
                or ""
            )
            for page in PdfReader(f).pages
        )

    except Exception:

        return jsonify(
            error="Could not read this PDF. "
                  "It may be corrupted or password protected."
        ), 400

    if len(text.strip()) < 30:

        return jsonify(
            error="No text found in the PDF. "
                  "Scanned/image resumes are not supported."
        ), 400

    resume_skills = find_skills(text)

    jd_skills = find_skills(jd)

    matching = [
        skill
        for skill in jd_skills
        if skill in resume_skills
    ]

    missing = [
        skill
        for skill in jd_skills
        if skill not in resume_skills
    ]

    categories = {
        SKILLS[skill][0]
        for skill in missing
    }

    related = [
        skill
        for skill in resume_skills
        if skill not in jd_skills
        and SKILLS[skill][0] in categories
    ]

    score = (
        round(
            len(matching)
            / len(jd_skills)
            * 100
        )
        if jd_skills
        else 0
    )

    title = next(
        (
            line.strip()
            for line in jd.splitlines()
            if line.strip()
        ),
        "Job description"
    )[:80]

    return jsonify(

        match_percentage=score,

        resume_file=f.filename,

        jd_title=title,

        resume_info=resume_info(
            text,
            resume_skills
        ),

        jd_requirements=jd_skills,

        matching_skills=matching,

        missing_skills=missing,

        related_skills=related,

        resume_keywords=resume_skills,

        jd_keywords=jd_skills,

        analysis=(
            explain(
                matching,
                missing,
                related
            )
            if jd_skills
            else
            "No known skills were detected in "
            "the job description. Try including "
            "specific technologies."
        )
    )


# =========================================================
# TAILORED RESUME API
# =========================================================

@app.post("/api/tailor")
def tailor_resume():

    f = request.files.get(
        "resume"
    )

    jd = (
        request.form.get(
            "job_description"
        )
        or ""
    ).strip()

    if not f or not f.filename:

        return jsonify(
            error="Please upload a PDF resume."
        ), 400

    if not f.filename.lower().endswith(".pdf"):

        return jsonify(
            error="Only PDF files are supported."
        ), 400

    if len(jd) < 20:

        return jsonify(
            error="Please provide a job description."
        ), 400

    try:

        text = "\n".join(
            (
                page.extract_text()
                or ""
            )
            for page in PdfReader(f).pages
        )

    except Exception:

        return jsonify(
            error="Could not read the resume PDF."
        ), 400

    if len(text.strip()) < 30:

        return jsonify(
            error="No readable text found in the resume."
        ), 400

    result = build_tailored_resume(
        text,
        jd
    )

    return jsonify(result)


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        port=5000,
        debug=True
    )
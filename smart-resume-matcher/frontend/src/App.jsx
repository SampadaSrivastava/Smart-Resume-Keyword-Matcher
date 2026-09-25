import React, { useState, useRef } from 'react'

const Chips = ({ items, cls, icon = '' }) =>
  items?.length ? (
    <div className="chips">
      {items.map(s => (
        <span key={s} className={'chip ' + cls}>
          {icon}{s}
        </span>
      ))}
    </div>
  ) : (
    <p className="muted">None found.</p>
  )

function Score({ value }) {
  const r = 54
  const c = 2 * Math.PI * r

  const color =
    value >= 70
      ? 'var(--ok)'
      : value >= 40
        ? 'var(--warn)'
        : 'var(--bad)'

  return (
    <svg
      viewBox="0 0 130 130"
      className="ring"
      role="img"
      aria-label={`Score ${value}%`}
    >
      <circle
        cx="65"
        cy="65"
        r={r}
        fill="none"
        stroke="#e4e8ef"
        strokeWidth="12"
      />

      <circle
        cx="65"
        cy="65"
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="12"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={c * (1 - value / 100)}
        transform="rotate(-90 65 65)"
      />

      <text
        x="65"
        y="74"
        textAnchor="middle"
        className="ring-num"
      >
        {value}%
      </text>
    </svg>
  )
}

const List = ({ title, items }) => (
  <div>
    <h4>{title}</h4>

    {items?.length ? (
      <ul>
        {items.map((x, i) => (
          <li key={i}>{x}</li>
        ))}
      </ul>
    ) : (
      <p className="muted">Not found.</p>
    )}
  </div>
)

export default function App() {
  const [file, setFile] = useState(null)
  const [jd, setJd] = useState('')

  const [loading, setLoading] = useState(false)
  const [tailoring, setTailoring] = useState(false)

  const [error, setError] = useState('')
  const [res, setRes] = useState(null)
  const [tailored, setTailored] = useState(null)

  const [drag, setDrag] = useState(false)

  const input = useRef()

  const pick = f => {
    if (f) {
      setFile(f)
      setError('')
      setTailored(null)
    }
  }

  // =====================================================
  // ANALYZE RESUME
  // =====================================================

  const analyze = async () => {
    setError('')

    if (!file) {
      return setError('Choose a PDF resume first.')
    }

    if (jd.trim().length < 20) {
      return setError('Paste a job description first.')
    }

    const fd = new FormData()

    fd.append('resume', file)
    fd.append('job_description', jd)

    setLoading(true)

    try {
      const r = await fetch(
        'http://127.0.0.1:5000/api/analyze',
        {
          method: 'POST',
          body: fd
        }
      )

      const d = await r.json()

      if (!r.ok) {
        throw new Error(
          d.error || 'Analysis failed.'
        )
      }

      setRes(d)
      setTailored(null)

    } catch (e) {
      setError(
        e.message === 'Failed to fetch'
          ? 'Cannot reach the backend. Is Flask running on port 5000?'
          : e.message
      )

      setRes(null)
    }

    setLoading(false)
  }

  // =====================================================
  // CREATE TAILORED RESUME
  // =====================================================

  const createTailoredResume = async () => {
    setError('')

    if (!file) {
      return setError('Upload your resume first.')
    }

    if (jd.trim().length < 20) {
      return setError('Paste a job description first.')
    }

    setTailoring(true)

    try {
      const fd = new FormData()

      fd.append('resume', file)
      fd.append('job_description', jd)

      const r = await fetch(
        'http://127.0.0.1:5000/api/tailor',
        {
          method: 'POST',
          body: fd
        }
      )

      const d = await r.json()

      if (!r.ok) {
        throw new Error(
          d.error || 'Could not create tailored resume.'
        )
      }

      setTailored(d)

    } catch (e) {
      setError(
        e.message === 'Failed to fetch'
          ? 'Cannot reach the backend. Is Flask running on port 5000?'
          : e.message
      )
    }

    setTailoring(false)
  }

  // =====================================================
  // DOWNLOAD TAILORED RESUME
  // =====================================================

  const downloadResume = () => {
    if (!tailored?.resume_text) {
      return
    }

    const blob = new Blob(
      [tailored.resume_text],
      {
        type: 'text/plain'
      }
    )

    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')

    a.href = url
    a.download = 'tailored-resume.txt'

    document.body.appendChild(a)

    a.click()

    a.remove()

    URL.revokeObjectURL(url)
  }

  const info = res?.resume_info

  return (
    <>
      <header className="nav">
        <div className="wrap nav-in">
          <span className="logo">
            Resume Matcher
          </span>

          <span className="muted">
            Resume vs. job description
          </span>
        </div>
      </header>

      <main className="wrap">

        {/* HERO */}

        <section className="hero">

          <h1>
            Smart Resume Keyword Matcher
          </h1>

          <p>
            Analyze how closely your resume matches a
            job description and create a tailored version.
          </p>

        </section>


        {/* INPUT FORM */}

        <section className="card form">

          <div
            className={
              'drop' +
              (drag ? ' drag' : '') +
              (file ? ' has' : '')
            }

            tabIndex={0}

            onClick={() =>
              input.current.click()
            }

            onKeyDown={e =>
              e.key === 'Enter' &&
              input.current.click()
            }

            onDragOver={e => {
              e.preventDefault()
              setDrag(true)
            }}

            onDragLeave={() =>
              setDrag(false)
            }

            onDrop={e => {
              e.preventDefault()
              setDrag(false)
              pick(e.dataTransfer.files[0])
            }}
          >

            <input
              ref={input}
              type="file"
              accept=".pdf,application/pdf"
              hidden
              onChange={e =>
                pick(e.target.files[0])
              }
            />

            <strong>
              {file
                ? file.name
                : 'Upload resume'}
            </strong>

            <span className="muted">
              {file
                ? 'Click to replace'
                : 'PDF only. Drag and drop or choose a file'}
            </span>

          </div>


          <div>

            <label htmlFor="jd">
              <strong>
                Job description
              </strong>
            </label>

            <textarea
              id="jd"
              value={jd}
              onChange={e =>
                setJd(e.target.value)
              }
              placeholder="Paste the full job description here..."
            />

          </div>


          {error && (
            <div
              className="error"
              role="alert"
            >
              {error}
            </div>
          )}


          <button
            className="btn"
            onClick={analyze}
            disabled={loading}
          >
            {loading
              ? 'Analyzing…'
              : 'Analyze resume'}
          </button>

        </section>


        {/* LOADING */}

        {loading && (
          <div className="card center">

            <div className="spin" />

            <p className="muted">
              Reading your resume and comparing skills…
            </p>

          </div>
        )}


        {/* EMPTY STATE */}

        {!res && !loading && (
          <div className="card center">

            <h3>
              No results yet
            </h3>

            <p className="muted">
              Upload a resume and paste a job
              description to see your match.
            </p>

          </div>
        )}


        {/* RESULTS */}

        {res && !loading && (
          <section>

            {/* SCORE */}

            <div className="card score-card">

              <Score
                value={res.match_percentage}
              />

              <div>

                <h2>
                  Compatibility score
                </h2>

                <p className="muted">
                  Resume: {res.resume_file}
                </p>

                <p className="muted">
                  Job description: {res.jd_title}
                </p>

                <p className="muted">
                  {res.matching_skills.length} of{' '}
                  {res.jd_requirements.length}{' '}
                  required skills found
                </p>

              </div>

            </div>


            {/* SKILL MATCH */}

            <div className="card">

              <h3>
                Skill match
              </h3>

              <div className="grid3">

                <div>

                  <h4>
                    Matching skills
                  </h4>

                  <Chips
                    items={res.matching_skills}
                    cls="ok"
                    icon="✓ "
                  />

                </div>


                <div>

                  <h4>
                    Missing skills
                  </h4>

                  <Chips
                    items={res.missing_skills}
                    cls="bad"
                    icon="✗ "
                  />

                </div>


                <div>

                  <h4>
                    Related skills
                  </h4>

                  <Chips
                    items={res.related_skills}
                    cls="rel"
                    icon="• "
                  />

                </div>

              </div>

            </div>


            {/* KEYWORD ANALYSIS */}

            <div className="card">

              <h3>
                Keyword analysis
              </h3>

              <div className="grid2">

                <div>

                  <h4>
                    JD keywords
                  </h4>

                  <Chips
                    items={res.jd_keywords}
                    cls="neutral"
                  />

                </div>


                <div>

                  <h4>
                    Resume keywords
                  </h4>

                  <Chips
                    items={res.resume_keywords}
                    cls="neutral"
                  />

                </div>


                <div>

                  <h4>
                    Matched keywords
                  </h4>

                  <Chips
                    items={res.matching_skills}
                    cls="ok"
                  />

                </div>


                <div>

                  <h4>
                    Missing keywords
                  </h4>

                  <Chips
                    items={res.missing_skills}
                    cls="bad"
                  />

                </div>

              </div>

            </div>


            {/* COMPATIBILITY ANALYSIS */}

            <div className="card">

              <h3>
                Compatibility analysis
              </h3>

              <p className="analysis">
                {res.analysis}
              </p>

            </div>


            {/* TAILOR RESUME */}

            <div className="card">

              <h3>
                Tailor your resume
              </h3>

              <p className="muted">
                Create a job-specific version of your
                resume using only information already
                present in your resume.
              </p>

              <p className="muted">
                Missing skills will NOT be invented
                or added to your resume.
              </p>

              <button
                className="btn"
                onClick={createTailoredResume}
                disabled={tailoring}
              >
                {tailoring
                  ? 'Creating tailored resume…'
                  : 'Create Tailored Resume'}
              </button>

            </div>


            {/* TAILORED RESUME */}

            {tailored && (
              <div className="card">

                <h3>
                  Tailored Resume
                </h3>

                <p className="muted">
                  The resume has been reorganized
                  and lightly rewritten to emphasize
                  skills relevant to this job description.
                </p>


                <h4>
                  Skills emphasized
                </h4>

                <Chips
                  items={tailored.matching_skills}
                  cls="ok"
                  icon="✓ "
                />


                <h4>
                  Skills still missing
                </h4>

                <Chips
                  items={tailored.missing_skills}
                  cls="bad"
                  icon="✗ "
                />


                <h4>
                  Resume Preview
                </h4>

                <pre
                  style={{
                    whiteSpace: 'pre-wrap',
                    background: '#f7f8fa',
                    padding: '20px',
                    borderRadius: '10px',
                    lineHeight: '1.6',
                    overflowX: 'auto'
                  }}
                >
                  {tailored.resume_text}
                </pre>


                <button
                  className="btn"
                  onClick={downloadResume}
                >
                  Download Tailored Resume
                </button>

              </div>
            )}


            {/* RESUME INFORMATION */}

            <div className="card">

              <h3>
                Resume information
              </h3>

              <div className="grid2 info">

                <div>

                  <h4>
                    Name
                  </h4>

                  <p>
                    {info.name || '—'}
                  </p>

                </div>


                <div>

                  <h4>
                    Email
                  </h4>

                  <p>
                    {info.email || '—'}
                  </p>

                </div>


                <div>

                  <h4>
                    Phone
                  </h4>

                  <p>
                    {info.phone || '—'}
                  </p>

                </div>


                <div>

                  <h4>
                    Skills
                  </h4>

                  <Chips
                    items={info.skills}
                    cls="neutral"
                  />

                </div>


                <List
                  title="Education"
                  items={info.education}
                />

                <List
                  title="Experience"
                  items={info.experience}
                />

                <List
                  title="Projects"
                  items={info.projects}
                />

                <List
                  title="Certifications"
                  items={info.certifications}
                />

              </div>

            </div>

          </section>
        )}

      </main>
    </>
  )
}
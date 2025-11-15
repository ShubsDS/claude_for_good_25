import React, { useState, useEffect } from "react";
import "./EssayGrader.css";

interface Highlight {
  criterion: string;
  start: number;
  end: number;
  text: string;
}

interface CriterionInfo {
  name: string;
  score: string;
  feedback: string;
  count: number;
  key: string;
}

const EssayGrader: React.FC = () => {
  const [lockedCriterion, setLockedCriterion] = useState<string | null>(null);
  const [renderedEssay, setRenderedEssay] = useState<string>("");

  // -----------------------------
  // Data (normally would come from API)
  // -----------------------------
  const essayText = `A Simple Essay with Citations

This essay demonstrates the importance of structured writing and proper citation formatting when developing academic arguments. Well-organized essays improve readability and comprehension for readers.

First, clarity of structure is essential. When an essay follows a logical progression from introduction to conclusion, readers can easily follow the argument being presented (Smith, 2019). This organizational clarity serves both the writer and the audience.

Second, citations allow automated systems and human readers to identify and verify bibliographic elements. Proper citation practices demonstrate academic integrity and allow readers to explore source materials (Lee & Patel, 2020). This strengthens the credibility of the work.

In conclusion, simple essays with clear structure and proper citations remain valuable tools for testing text processing software. They provide predictable patterns while maintaining the essential elements of academic writing (Garcia, 2018).

References

Doe, J. (2021). Testing Text Analysis Systems. Journal of Software Engineering, 15(3), 45–52.

Smith, A. (2019). Essay Structure and Readability. Academic Writing Quarterly, 12(2), 101–115.

Lee, M., & Patel, R. (2020). Automated Citation Detection in Digital Documents. Computational Linguistics Review, 8(1), 23–38.

Garcia, L. (2018). Simple Examples in Software Testing. Testing Methods Journal, 5(4), 88–95.`;

  const highlights: Highlight[] = [
    { criterion: "THESIS", start: 34, end: 162, text: "" },
    { criterion: "CITATIONS", start: 438, end: 451, text: "" },
    { criterion: "CITATIONS", start: 682, end: 701, text: "" },
    { criterion: "CITATIONS", start: 945, end: 959, text: "" },
    { criterion: "SUPPORTING_EVIDENCE", start: 239, end: 291, text: "" },
    { criterion: "SUPPORTING_EVIDENCE", start: 504, end: 619, text: "" },
    { criterion: "STRUCTURE", start: 0, end: 32, text: "" },
    { criterion: "STRUCTURE", start: 195, end: 237, text: "" },
    { criterion: "STRUCTURE", start: 770, end: 784, text: "" },
    {
      criterion: "REFERENCES",
      start: 962,
      end: 1279,
      text: "",
    },
  ];

  const criteria: CriterionInfo[] = [
    { key: "THESIS", name: "Thesis", score: "8/10", feedback: "Clear thesis statement present", count: 1 },
    { key: "CITATIONS", name: "Citations", score: "9/10", feedback: "Multiple well-formatted citations", count: 3 },
    { key: "SUPPORTING_EVIDENCE", name: "Supporting Evidence", score: "8/10", feedback: "Strong examples", count: 2 },
    { key: "STRUCTURE", name: "Structure", score: "9/10", feedback: "Well-organized writing", count: 3 },
    { key: "REFERENCES", name: "References", score: "8/10", feedback: "Good reference list", count: 1 },
  ];

  // -----------------------------
  // Render text + highlight spans
  // -----------------------------
  useEffect(() => {
    const sorted = [...highlights].sort((a, b) => a.start - b.start);

    let html = "";
    let last = 0;

    sorted.forEach((h) => {
      html += escapeHtml(essayText.slice(last, h.start));
      html += `<mark data-criterion="${h.criterion}">${escapeHtml(
        essayText.slice(h.start, h.end)
      )}</mark>`;
      last = h.end;
    });

    html += escapeHtml(essayText.slice(last));
    setRenderedEssay(html);
  }, []);

  const escapeHtml = (t: string) => {
    const div = document.createElement("div");
    div.textContent = t;
    return div.innerHTML;
  };

  // -----------------------------
  // Highlight logic
  // -----------------------------
  const handleToggle = (c: string) => {
    setLockedCriterion((prev) => (prev === c ? null : c));
  };

  return (
    <div className="container">
      <h1>Essay Grading with Highlighted Text</h1>
      <p className="subtitle">React + TypeScript version</p>

      <div className="instructions">
        <h3>How to Use</h3>
        <p>Click a criterion on the right to highlight related text.</p>
      </div>

      <div className="layout">

        {/* ESSAY PANEL */}
        <div className="essay-panel">
          <h2>Essay with Highlights</h2>

          <div
            className="essay-content"
            dangerouslySetInnerHTML={{ __html: renderedEssay }}
          ></div>
        </div>

        {/* SCORE PANEL */}
        <div className="score-panel">
          <h2>Grading Results</h2>

          <div className="total-score">
            <div className="score">8.4/10</div>
            <div className="label">Total Score</div>
          </div>

          {criteria.map((c) => (
            <div
              key={c.key}
              data-criterion={c.key}
              className={`criterion ${lockedCriterion === c.key ? "active" : ""}`}
              onClick={() => handleToggle(c.key)}
            >
              <div className="criterion-header">
                <span className="criterion-name">{c.name}</span>
                <span className="criterion-score">{c.score}</span>
              </div>

              <div className="criterion-feedback">{c.feedback}</div>
              <div className="criterion-count">{c.count} sections highlighted</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EssayGrader;

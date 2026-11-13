# AI in hiring: the "synthetic signal loop" and what still carries signal

Facilitator's research note (verified via web sources, Nov 2026). Relates mainly to P3, P4, P5, P6 and P10.

## 1. The AI doom loop — in numbers

- LinkedIn applications rose **more than 45 % year on year**, to about **11,000 applications per minute** (June 2025; CNBC reports about 9,500/min). [Fortune](https://fortune.com/2025/11/18/hiring-job-seekers-recruiters-talent-acquisition-ai-doom-loop-application-technology/), [CNBC](https://www.cnbc.com/make-it/2025/10/29/recruiters-are-drinking-through-a-fire-hose-of-job-applications-experts-say.html), [Korn Ferry](https://www.kornferry.com/insights/this-week-in-leadership/the-application-avalanche)
- **Greenhouse 2025 AI in Hiring Report** (4,100+ jobseekers, recruiters and hiring managers in the US, UK, Ireland and Germany) [Greenhouse](https://www.greenhouse.com/newsroom/an-ai-trust-crisis-70-of-hiring-managers-trust-ai-to-make-faster-and-better-hiring-decisions-only-8-of-job-seekers-call-it-fair):
  - 70 % of hiring managers trust AI to make faster and better hiring decisions. Only **8 % of jobseekers** think AI screening makes hiring fairer.
  - About half of jobseekers send more applications than a year ago. **41 % of US jobseekers admit using prompt injections** (hidden text to get past AI filters).
  - **91 % of recruiters** have spotted candidate deception. **34 % spend up to half their week filtering spam/junk applications.**
  - 3 in 4 US jobseekers use AI to polish applications, and 87 % want employers to be open about their own AI use.
- Recruiters spend **30 seconds to 2 minutes per CV**. [CNBC](https://www.cnbc.com/make-it/2025/10/29/recruiters-are-drinking-through-a-fire-hose-of-job-applications-experts-say.html)

**Interpretation:** both sides are automating, so volume goes up while signal and trust go down. What is scarce is **credible human signal** and **recruiter attention**. This is exactly the brief's P4 + P6 and its north star, "stronger signal and less noise".

## 2. Why "detect the AI" is the wrong answer

- Liang et al. (2023, *Patterns*) tested seven GPT detectors. On average they flagged **61.3 % of human-written TOEFL essays (non-native writers) as AI-generated**, while native essays were classified almost perfectly. At least one detector flagged **97.8 %** of the TOEFL essays. Simple prompt changes evade the detectors. [Patterns / Cell](https://www.cell.com/patterns/fulltext/S2666-3899(23)00130-7)
- In Espoo, 25.9 % of residents are foreign-language speakers ([context note](01-context-espoo-and-talentmatch.md)). An AI detector would therefore **systematically penalise exactly the target group** (P10). It would also clash with the Non-Discrimination Act, which lists language and origin as protected grounds.

**Design principle:** don't police *how* a text was written. Change *what* is evaluated (evidence, live interaction, structured answers) and treat AI assistance as legitimate and transparent.

## 3. LLM / embedding screening reproduces bias

- Wilson & Caliskan (2024, AIES; University of Washington) had three massive-text-embedding models rank 550+ résumés against 500+ job descriptions. The models favoured **White-associated names in 85.1 %** of cases and **female-associated names in only 11.1 %**. Black male names were disadvantaged in up to 100 % of comparisons, and document length and name frequency also changed the outcome. [arXiv 2407.20371](https://arxiv.org/abs/2407.20371), [UW News](https://www.washington.edu/news/2024/10/31/ai-bias-resume-screening-race-gender/)

**Implication:** never rank people with LLMs or embeddings on raw CV text. Strip identity cues (name, photo, nationality, age, gender markers) before any similarity computation. Prove neutrality with counterfactual synthetic profiles.

## 4. What actually predicts job performance, and is fairer

Sackett, Zhang, Berry & Lievens (2022, *Journal of Applied Psychology*), revised validity estimates. [DOI 10.1037/apl0000994](https://doi.org/10.1037/apl0000994), [table via Annual Reviews](https://www.annualreviews.org/content/table/10.1146/annurev-orgpsych-020924-072127.t1)

| Predictor | Validity (ρ) | Black–White *d* (adverse-impact proxy) |
|---|---|---|
| **Structured interviews** | **.42** (top-ranked) | .23 |
| Job knowledge tests | .40 | .54 |
| Empirically keyed biodata | .38 | .33 |
| Work sample tests | .33 | .67 |
| General mental ability tests | .31 | .79 |
| Unstructured interviews | .19 | .32 |
| Job experience (years) | **.07** | .49 |

**Implication:** a typical job-fair conversation is unstructured (ρ ≈ .19), and CVs foreground years of experience (ρ ≈ .07). Both are among the **weakest predictors**. Structured, job-related questions asked consistently are **both the most valid and among the least adverse**. So the event gains signal by structuring the human conversation around the company's real needs, not by adding AI judgement.

## 5. Signals that survive the AI era (synthesis)

| Signal | Why it is hard to fake | Cost | Fairness notes |
|---|---|---|---|
| Live, structured conversation at the event | Happens in real time, with follow-up questions | Medium | Structure reduces interviewer bias |
| Specific evidence (artefacts, portfolio, code, concrete outcomes) | Can be checked and discussed | Low–medium | Must accept non-Finnish formats and career paths |
| Short work-sample / challenge responses tied to a company's real problem | Job-specific; defended live | Medium | Time-boxed, accessible, optional alternatives |
| Verified credentials (Europass / EU Digital Credentials, Open Badges, EUDI wallet) | Cryptographically signed | Low once the infrastructure exists | Gaps in recognising foreign degrees |
| Behaviour over time (follow-through, mutual-interest history) | Accumulated, not authored | Low | Minimise, consent, short retention |
| Company side: concrete first-90-days problems instead of a wish-list | Forces a genuine statement of need (P2) | Low | Exposes unnecessary requirements, e.g. a Finnish requirement for an English-only team |

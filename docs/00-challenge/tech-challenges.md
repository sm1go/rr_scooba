# Junction 2026 — tech challenges (stackable on top of the Espoo track)

Pasted by the team from the Junction Platform (`hackjunction.app/participate/45/challenges`) on
14 Nov 2026. Kept verbatim except that personal redemption codes are redacted — credits are claimed via
the platform's Hackerpacks page. Our fit analysis: `docs/01-research/05-junction-2026-tech-partners.md`.

---

## Best Use of Codex — by OpenAI

**The Challenge.** OpenAI challenges you to push the boundaries of what's possible with AI-powered
software development. Use Codex as part of your development process to build, iterate, and ship an
ambitious project during Junction 2026. Whether you're building AI agents, complex applications, or
entirely new products, show us how Codex can accelerate your development and help you achieve more in
just 48 hours.

This is an open challenge: you can participate alongside any other Junction challenge. The key is
demonstrating how you've meaningfully used Codex in building your solution.

**Resources.** [OpenAI Codex](https://developers.openai.com/codex) ·
[Codex quickstart](https://developers.openai.com/codex/quickstart) ·
[OpenAI developer platform](https://platform.openai.com/docs) · Exclusive Junction 2026 offer: OpenAI
is providing $100 in credits per participant through unique redemption links distributed by Junction
(Hackerpacks page on the platform).

---

## Best Use of Gemini API — by Google DeepMind

**The Challenge.** Build something extraordinary with Google's Gemini API. This is an open innovation
challenge: there are no predefined problems or industries to focus on. Whether you're building an AI
agent, a developer tool, a creative application, or something entirely new, we want to see what you can
create with Gemini. The challenge is to demonstrate a meaningful, innovative, and technically impressive
use of Gemini. Show us why Gemini matters to your solution and what makes your project stand out.

**Insight.** We're looking for projects that go beyond simply adding an LLM to an application. Think
about how Gemini's capabilities can enable something genuinely new or significantly improve an existing
solution. Your submission should clearly explain:
- What problem you're solving and why it matters
- How you've integrated the Gemini API
- What makes your use of Gemini innovative or technically impressive
- Why Gemini is an important part of your solution

The challenge is open to all industries, use cases, and creative ideas.

**Resources.** [Google AI Studio](https://aistudio.google.com/) – get your Gemini API key and experiment
with models · [Gemini API documentation](https://ai.google.dev/gemini-api/docs) ·
[Gemini API quickstart](https://ai.google.dev/gemini-api/docs/quickstart).

**Junction participant credits.** Google DeepMind is providing access to Gemini API credits for up to
400 participating teams. To receive credits your team will have to fill
[this form](https://forms.gle/bByXvjGkW9WZuYwW9). Eligible teams will receive instructions for
accessing their accounts during the event. API keys can be generated through Google AI Studio.
Participation and access to the Google-provided accounts are restricted to participants aged 18 or older.

**Technical support.** Google DeepMind booth during Junction; "Build with Google DeepMind" workshop on Friday.

---

## Best Use of Gemma — by Google DeepMind

**The Challenge.** Awarded to the team that demonstrates the most innovative and impactful use of
Google's Gemma open models. We're looking for creative applications, strong technical execution, and
solutions that showcase the potential of open AI models to solve real-world problems.

**How to access Gemma** (incl. Junction 2026 partners):
- [Featherless AI](https://featherless.ai/models?families=gemma) – hosted Gemma models through an API.
- [Modal](https://modal.com/) – deploy and run Gemma models on serverless GPU infrastructure.
- [Verda](https://verda.com/) – cloud GPU resources to deploy and run Gemma yourself.
- [Google AI Studio](https://aistudio.google.com/) – experiment with Gemma in your browser.
- [Hugging Face](https://huggingface.co/google) – download Gemma models.

Setup: [official Gemma documentation](https://ai.google.dev/gemma/docs). Check the Junction Hackerpack
for event-specific credits or access instructions.

---

## Best Use of Nemotron — by NVIDIA

**The Challenge.** Build a project powered by NVIDIA Nemotron that solves a real problem through
reasoning, tool use, or coordinated workflows. Applies to: any track.

**Introduction.** What can you build when AI moves beyond answering questions and starts getting things
done? NVIDIA invites you to use Nemotron to build a project that tackles a real problem for a clear
audience. Connect it to tools, ground it in useful data, or combine it with other models to turn an idea
into a working solution. Show us what Nemotron enables and why it matters to the people using your project.

**The technology.** Nemotron 3.5 Super VL, NVIDIA's newest open model: 120B parameters, 12B active per
token, so it runs fast for its size, and it can read text, images, documents and even video in a single
workflow — an agent can look at a screenshot, read a PDF, watch a clip, call a tool and write the code to
act on it, all with one model.

**The challenge.** Build a project where Nemotron plays a meaningful role in doing real work. Use it on
its own or alongside other models, tools, and data sources to solve a problem for a clear audience.
Nemotron must contribute directly to the project's core functionality, and your demo should make that
contribution visible.

**Minimum requirements**
- Use the NVIDIA Nemotron 3.5 Super VL model in the working solution.
- Demonstrate its contribution to the project's core functionality.
- Submit a short explanation identifying the model used, what it does, why it matters, and how you
  improved its outputs (as text in the submission form).

**Getting started**
- NVIDIA Build: free hosted APIs. OpenAI-compatible, base URL `https://integrate.api.nvidia.com/v1`
  (example model `nvidia/nemotron-3.5-lightning-30b-a3b`). The free tier is rate-limited (about 40
  requests per minute per key), so agent loops should use retries with backoff and each teammate should
  use their own key.
- OpenRouter API: free variants (`:free`) capped at 20 requests/minute and 50/day (1,000/day after
  buying at least 10 credits).
- Hugging Face: open weights for local runs, fine-tuning or deployment on Brev.

**Support.** NVIDIA Discord channel and the NVIDIA table. Mentors: Maxime Pariente, Ryan Reese.
Main contact: Elliot Winch (Community Program Manager, EMEA). Judges: NVIDIA team.

**Prize.** 2 winners of 1× RTX 5080.

**Judging criteria**
- **Meaningful Nemotron usage:** Nemotron is central to the project's value; the team clearly explains
  what it does and why it matters.
- **Technical execution:** the demo works reliably and shows thoughtful implementation choices around
  architecture, data flow, tool use, latency, or error handling.
- **Quality of AI output:** outputs are useful, relevant, and grounded where appropriate; the team
  demonstrates efforts to improve quality through prompting, evaluation, or feedback loops.
- **Creativity and differentiation:** Nemotron is used thoughtfully or inventively, with a distinct
  approach to the problem.

---

## Best use of Modal — by Modal

**The Challenge.** Take your Junction project from laptop to production AI on Modal.

**Description.** Every Junction team is building with AI, and most hit the same wall: the model runs on
a laptop, but too slowly, not on a GPU, and not behind a URL the judges can open. Modal gets you past
that wall. Use Modal to power the project you're already building for your main Junction challenge:
serve an open model on a GPU, run your agent's code in secure Sandboxes, fine-tune a model on your own
data, or fan out a big batch job, all in plain Python with no Dockerfiles, Kubernetes or YAML. We're
looking for **the most ambitious working AI system built on Modal, where Modal does the heavy lifting**
and the team spends its 48 hours on the problem. Inference, agents, sandboxes and training: your whole
AI stack on one platform.

**Insight.** Best use of Modal is a tech challenge, so you compete in it on top of your main challenge.
The same project can enter other tech challenges too.

**What Modal brings.** $100 in Modal credits per participant (CPUs and GPUs up to NVIDIA B300, billed
per second, scale to zero). `modal run` executes in the cloud; `modal deploy` turns it into an
autoscaling web endpoint with a public URL for the demo. Serve open-weight LLMs, vision-language and
speech models; run untrusted, LLM-generated code in isolated Sandboxes; fine-tune or RL post-train with
Modal Dojo; store weights and datasets in Volumes. Junction starter kit of ready-to-run examples
(LLM serving with vLLM/SGLang, speech-to-text, text-to-speech, vision, RAG, agents, RL). Kick-off
workshop at the Modal booth; engineers on site all weekend. Main contact: Filip Makraduli (DevRel).

**Claiming credits.** Sign up for a Modal account, then redeem the credits via the redemption link and
code given on the Junction Platform (redacted here). Credits are valid for one year from redemption.

---

## Best Use of ElevenLabs — by Major League Hacking

Deploy natural, human-sounding audio with ElevenLabs. Create realistic, dynamic, and emotionally
expressive voices for any project, from interactive AI companions to narrated stories and voice-enabled
apps. Integrate fully autonomous audio experiences into your hack with ElevenLabs — prize: wireless earbuds.

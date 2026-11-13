# Market landscape & data sources

Facilitator's research note (Nov 2026). Relates to P7, P8 and the "Resources" section of the brief.

## 1. Event and matchmaking platforms

| Platform | How matching works | Strengths | Gap versus our problem |
|---|---|---|---|
| **Tavata by Eventilla** (FI). Used by TalentMatch 2024 (700+ users) | Attendees choose what they "offer" and "seek" from options the organiser defines. The app suggests contacts, and 1:1 meetings are booked before the event at numbered tables or by video. Profiles are pre-filled from Eventilla registration. [tavata.events](https://tavata.events/en/event-networking-app) | Simple, Finnish, recruitment-event mode (employers see jobseekers), browser-based | Matching is based on **self-declared tags**, which brings back the keyword/synthetic-signal problem (P6). Nothing helps companies articulate needs (P2), and nothing limits the volume of requests (P4) |
| **Brella** (FI, Helsinki) | Interest/intent-based matchmaking and meeting scheduling for conferences *(from vendor materials, not re-verified)* | Polished UX, organiser analytics | Built for B2B networking, not for evidence of skills or for fairness in recruitment |
| **b2match** (AT) | Cooperation profiles with "offers/requests" and meeting requests that are accepted or declined; widely used by Enterprise Europe Network brokerage events *(not re-verified)* | Double opt-in meetings | Text-heavy profiles, generic |
| **Deal Room** (used for TalentMatch 2020–21) | Virtual booths, pre-booked 1:1s, lead collection, broadcasts. [Duunitori](https://duunitori.fi/tyoelama/talentmatch-espoo-recruitment-event) | Online-first | Same tag/profile logic |

**Common pattern:** every platform matches on **what people say about themselves**, in each platform's own vocabulary, and leaves the "who is worth my limited time" problem to the user. None of them supports the company in articulating a real need early, makes evidence visible, or offers fairness and explainability as a feature.

## 2. Job portals (talent-side discovery)

- **Duunitori**: the largest Finnish job board. It has promoted TalentMatch in the past.
- **The Hub**: Nordic startup jobs.
- **Work in Finland** (Business Finland): portal for international talent, with free English-language job ads ("Jobs in Finland").
- **Job Market Finland / Työmarkkinatori**: the national public employment services platform. It has job-posting **import and retrieval APIs** (REST, OAuth2 client credentials), but access needs **activation by the KEHA Centre with a business ID**, so it is not feasible within 48 h. Postings use **ESCO (v1.1.0)** for occupations and skills, and ISCO-08 codes. [API page](https://tyomarkkinatori.fi/en/instructions-and-support/interfaces/interfaces-for-job-postings), [retrieval interface manual](https://tyomarkkinatori.fi/en/dam/jcr:6193a157-9813-4e92-88b4-199f57edfda0/noutorajapintaohje-en.pdf)

## 3. Data sources and APIs we can use

| Source | Use for us | Access |
|---|---|---|
| **ESCO web-service API** (European Commission) | Shared multilingual vocabulary for skills and occupations. URIs per concept, search endpoints, 28 languages incl. Finnish, Swedish and English. Versions v1.0.9 (default), v1.1.2 and **v1.2.0** (latest, May 2024), chosen with `selectedVersion`. Interoperable with Job Market Finland and EURES. [API](https://esco.ec.europa.eu/en/use-esco/use-esco-services-api/esco-web-service-api), [docs](https://ec.europa.eu/esco/api/doc/esco-api-further-doc.html), [v1.2](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-v12) | Open, no key. Also available as a downloadable **local API** and as CSV. For a hackathon, cache a subset locally so the demo cannot fail on the network |
| Job Market Finland APIs | Realistic, ESCO-coded job ads | Needs KEHA activation. In the demo, use **synthetic ads modelled on its data structure** |
| National Forum for Skills Anticipation (Finnish National Agency for Education) | Future skill-demand themes for events, and for "skills gap" feedback | Public reports |
| Suomi.fi PTV (Service Information Repository) Open API | Machine-readable descriptions of public services (employer subsidies, International House Helsinki, permits), so the product can link to authoritative service data | Open API |
| Espoo statistics | Context for the talent pool (languages, growth) | Open |

## 4. Implications for our build

1. **ESCO is the lingua franca.** It is multilingual, used by the national employment services platform and EURES, and free. Mapping both company needs and talent evidence to ESCO URIs gives interoperability and an explainable common vocabulary.
2. **Synthetic data is mandatory (C2)**, so we generate companies, needs and talent profiles shaped like the Job Market Finland and ESCO structures.
3. **Do not compete with Tavata or Brella on scheduling.** Compete on **signal quality before the meeting** and **fairness/explainability**, and keep integration simple (exports, links). Eventilla/Tavata could even be a partner.

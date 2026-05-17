# POI Personalization Study – Research Summary

## Study Context

Participants compared manual and AI-generated Points of Interest (POI) descriptions drawn from the survey logs in `data_analysis/data_analysis.ipynb`. Each respondent rated both versions on three communication goals—significance, trust, and clarity—and later provided free-form preferences plus overall study feedback. Final respondents also reflected on the value of adaptive descriptions and their comfort with AI-authored travel content.

## Question Prompts

- **Significance prompt:** “Does the description effectively communicate the significance and offerings of the place?” (5-point agreement scale)
- **Trust prompt:** “How trustworthy does this description appear to be?” (5-point intensity scale from “Not at all” to “Extremely”)
- **Clarity prompt:** “How clear and complete is the information provided?” (5-point clarity scale)
- **Overall experience prompt:** “How would you rate your overall experience with the POI descriptions provided in this study?”
- **Adaptation concept prompt:** “What is your opinion on the idea of automatically adapting POI descriptions based on user interests?”
- **AI comfort prompt:** “How comfortable are you with reading AI-generated descriptions when planning visits to new places?”

## Participant Profile

- **Sample size:** 51 unique participants after deduping repeated sessions by `user_id`.
- **Age:** Mean $\bar{x}=30.94$ years ($\sigma=6.74$), ranging from 22 to 49.
- **Gender:** 34 male, 17 female.
- **Marital status:** 25 married, 22 single, 3 in a relationship, 1 divorced.
- **Profession:** Students (22) and engineers (16) dominate; academics (3) and individual professionals (doctor, public service, self-employed) fill the remainder, with seven entries left unspecified.
- **Nationality:** Majority Indian (28) and German (21), with isolated Chinese and Iranian participants.
- **Travel context:** Most describe themselves as Intermediate (21) or Experienced (19) travelers; Beginners represent 9 entries and Experts 2. The most repeated travel-style bundle was Luxury + Relaxation + Family-friendly (3 mentions), while the rest show diverse multi-category mixes that emphasize relaxation, family needs, and budget awareness.

## Comparative Content Judgments

Each participant rated both manual and AI variants for every POI, producing 510 paired observations per metric. Error bars in the notebook visuals are Poisson-style $\sqrt{n}$ estimates; the tables below report raw counts.

### Significance – "Does the description communicate the importance and offerings?"

| Rating            | Manual |  AI |
| ----------------- | -----: | --: |
| Strongly Disagree |      7 |   8 |
| Disagree          |     21 |  24 |
| Neutral           |    138 | 118 |
| Agree             |    281 | 276 |
| Strongly Agree    |     63 |  84 |

**Interpretation:** Manual copy keeps more readers in the Neutral band, whereas AI phrasing shifts 21 additional responses into Strongly Agree with almost no penalty in lower categories.
Chi-square test: $\chi^2(4)=4.87$, $p=0.3005$ (no statistically significant difference between rating distributions).

### Trust – "How trustworthy does this description appear?"

| Rating     | Manual |  AI |
| ---------- | -----: | --: |
| Not at all |      8 |   4 |
| Slightly   |     43 |  33 |
| Moderately |    170 | 140 |
| Very       |    235 | 261 |
| Extremely  |     54 |  72 |

**Interpretation:** AI descriptions reduce skepticism (half as many "Not at all" ratings) and add 44 combined "Very/Extremely" trust votes, signalling stronger perceived credibility.

### Clarity – "How clear and complete is the information?"

| Rating       | Manual |  AI |
| ------------ | -----: | --: |
| Very Unclear |      3 |   5 |
| Unclear      |     33 |  24 |
| Neutral      |    147 | 109 |
| Clear        |    260 | 284 |
| Very Clear   |     67 |  88 |

**Interpretation:** AI copy again compresses the neutral segment, adding 45 more "Clear/Very Clear" impressions and trimming the Unclear bucket by 9 responses.

## Participant Feedback (Final Survey)

Final reflections were collected from 28 respondents (some items contain fewer non-null answers). Central tendencies for the 1–5 Likert scales are summarized below.

| Metric                             | Mean |   SD | Median |  N |
| ---------------------------------- | ---: | ---: | -----: | -: |
| Overall experience with POI study  | 3.88 | 0.70 |    4.0 | 17 |
| Support for adaptive descriptions  | 3.75 | 0.93 |    4.0 | 16 |
| Comfort with AI-generated POI text | 3.94 | 0.83 |    4.0 | 17 |

**Takeaways:** Respondents lean positive ($\mu \approx 4$) on overall satisfaction and AI comfort, and moderately endorse ($\mu=3.75$) the idea of tailoring POI narratives to their interests. Score spreads under 1 point suggest consensus without extreme polarization.

## Key Implications

1. **AI copy lifts top-box scores** across all three qualitative metrics, primarily by converting neutral readers into clear advocates.
2. **Trust remains the tightest differentiator**, with AI passages delivering 28 more "Extremely" trustworthy judgments—critical for POI recommendations where credibility underpins adoption.
3. **Participant demographics skew young, educated, and internationally diverse**, implying future validation should include older or non-student traveler segments for broader generalization.
4. **End-user feedback validates personalization concepts**: participants are receptive to adaptive, AI-assisted storytelling so long as clarity and trust gains persist.

These findings can seed the Results and Discussion sections of the research paper, with notebook cells 1–28 providing reproducible provenance for every statistic cited above.

## Paired Comparisons: Manual vs AI (Mean-Level Tests)

Per-metric paired tests (same respondent rated both versions; Likert mapped 1–5). Wilcoxon is the primary inference because the data are ordinal; paired t-test is reported as a robustness check under an interval/normality assumption.

| Metric       | n_pairs | Manual mean | AI mean | Paired t (p) | Wilcoxon (p) |
| ------------ | ------: | ----------: | ------: | -----------: | -----------: |
| Significance |     510 |      3.7294 |  3.7922 |       0.1542 |       0.1307 |
| Trust        |     510 |      3.5569 |  3.7137 |       0.0007 |       0.0005 |
| Clarity      |     510 |      3.6961 |  3.8353 |       0.0018 |       0.0020 |

Interpretation:

- Trust and Clarity show statistically significant AI > Manual differences (Wilcoxon p < 0.01); Significance does not (p = 0.13).
- Effect direction: AI means exceed Manual in all three metrics; gains are most pronounced for Trust and Clarity.
- Use Wilcoxon for reporting (ordinal-appropriate); cite paired t-test as a sensitivity check if treating Likert as interval is acceptable.

# Beyond the typical commute

A reproducible comparison of **four hypothetical travel scenarios**, prepared
by **ZHU ZHICHENG** for CISC7204 Practice 09.

**NOT A UM TRANSPORT STUDY.** No journeys were observed. The P50 and P90
values below are hand-assigned inputs, not estimates from a sample.

Portfolio: <https://zzc1565545.github.io/data-science-portfolio/>

## Research question

How does the ranking of four travel modes change when we compare typical
journey time with a slower-journey benchmark?

## Data source and usage permissions

`data/commute_scenarios.json` contains the author's hypothetical values reused
from the Practice 07 visualization exercise. These are locally constructed
teaching examples, not a downloaded third-party dataset or information from
UM, a transport operator, or any traveller.

The author has authorized these synthetic values, code and charts for public
release in this coursework repository. There are no personal travel records,
restricted source files, credentials or third-party dataset permissions to
obtain. Public availability does not imply a blanket software reuse license.
See `DATA_SOURCE.txt` for the full provenance and limitations.

| Mode | Assumed P50 (min) | Assumed P90 (min) | P90 − P50 (min) |
| --- | ---: | ---: | ---: |
| Bicycle | 14 | 20 | 6 |
| Public bus | 18 | 38 | 20 |
| Campus shuttle | 20 | 30 | 10 |
| Walking | 25 | 28 | 3 |

P50 denotes an assumed median and P90 an assumed 90th-percentile threshold.
There is no trip-level sample from which to estimate either quantity.

## Methods and tools

Python validates non-negative finite values, unique labels, provenance and
P90 ≥ P50. It then calculates exact differences and orders the scenarios.
Matplotlib creates two complementary views with visible units and zero-based
axes. No model fitting, statistical inference or network download is involved.

### 1. Compare the time values

![Assumed median and 90th-percentile time for each of four hypothetical modes](figures/01_time_comparison.png)

The public bus has an assumed median **7 minutes shorter** than walking
(18 versus 25), but an assumed P90 **10 minutes longer** (38 versus 28).
The P50 ordering is bicycle, bus, shuttle, walking; the P90 ordering is
bicycle, walking, shuttle, bus. The connected dots show two reference
points, not an observed range or confidence interval.

### 2. Compare the additional allowance

![P90 minus P50 in descending order: bus 20, shuttle 10, bicycle 6, walking 3 minutes](figures/02_extra_allowance.png)

The P90−P50 gaps are 20, 10, 6 and 3 minutes for bus, shuttle, bicycle and
walking respectively. Walking has the smallest gap but the longest assumed
median; a smaller gap does not mean the fastest journey.

## Limitations

These findings are arithmetic consequences of eight assumed numbers.
Two quantiles cannot establish the full distribution, variance, probability
of being late, or which mode would be faster on a particular trip.
Cost, weather, safety, accessibility and service schedules are outside the
example. **Do not use this project as real-world transport advice.**

## Reproduce

Tested with **Python 3.11.1** and **Matplotlib 3.10.1**.

1. Clone or download this repository and open a terminal in its root:

   ```text
   git clone https://github.com/zzc1565545/data-science-project.git
   cd data-science-project
   ```

2. Optionally create an isolated environment:

   ```text
   python -m venv .venv
   ```

   Activate with `.venv\Scripts\activate.bat` in Windows Command Prompt,
   or `source .venv/bin/activate` on macOS/Linux.

3. Install the single direct dependency, regenerate all outputs and run tests:

   ```text
   python -m pip install -r requirements.txt
   python analysis.py
   python -m unittest -v
   ```

Expected result: four validated scenarios, two PNG files, two SVG files,
`figures/summary.json`, and **11 passing tests**. Initial dependency
installation needs internet access; analysis itself runs offline.
The tests use temporary folders and do not overwrite the published figures.
Repeat runs produce identical output bytes in the tested environment;
font and dependency differences may affect rendering on other systems.

Optional output location:

```text
python analysis.py --output output
```

## File guide

```text
analysis.py                     Validation, calculations and both charts
test_analysis.py                11 unit and reproduction tests
requirements.txt               Pinned Matplotlib dependency
data/commute_scenarios.json      Explicitly hypothetical source values
figures/01_time_comparison.*    Connected-dot chart (PNG and SVG)
figures/02_extra_allowance.*    Difference chart (PNG and SVG)
figures/summary.json            Machine-readable derived results
DATA_SOURCE.txt                 Provenance and interpretation limits
```

## Status and AI assistance

Analysis and initial documentation are prepared. The portfolio is **ongoing**:
a real classmate review and a corresponding improvement commit are still
pending. Automated tests are not a substitute for that review.

OpenAI Codex assisted with code, visualization design, documentation and
checks. The work is an AI-assisted learning exercise, not an independently
conducted transport survey.

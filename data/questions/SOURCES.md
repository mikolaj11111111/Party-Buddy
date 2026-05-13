# Sources for initial M2 trivia batch

Initial dataset files:

- `geography.json`
- `history.json`
- `science.json`

Primary source: Open Trivia Database API, https://opentdb.com/api_config.php

Used API endpoints:

- `https://opentdb.com/api.php?amount=10&category=22&type=multiple&encode=url3986`
- `https://opentdb.com/api.php?amount=10&category=23&type=multiple&encode=url3986`
- `https://opentdb.com/api.php?amount=10&category=17&type=multiple&encode=url3986`

License note: Open Trivia Database states that all API data is available under the Creative Commons Attribution-ShareAlike 4.0 International License.

Transformation note: Questions and answers were translated into Polish, paraphrased for the local ABCD trivia format, and given locally written Polish explanations and speech aliases. A few distractors were adjusted to be clearer in Polish.

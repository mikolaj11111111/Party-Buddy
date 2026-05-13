# Sources for M2 trivia batch

Dataset files:

- `geography.json`
- `history.json`
- `popculture.json`
- `movies.json`
- `music.json`
- `science.json`
- `internet_games.json`
- `sport.json`
- `technology.json`
- `language_literature.json`
- `general.json`

Primary source for the initial imported seed questions: Open Trivia Database API, https://opentdb.com/api_config.php

Used API endpoints for the initial seed batch:

- `https://opentdb.com/api.php?amount=10&category=22&type=multiple&encode=url3986`
- `https://opentdb.com/api.php?amount=10&category=23&type=multiple&encode=url3986`
- `https://opentdb.com/api.php?amount=10&category=17&type=multiple&encode=url3986`

License note: Open Trivia Database states that all API data is available under the Creative Commons Attribution-ShareAlike 4.0 International License: https://creativecommons.org/licenses/by-sa/4.0/

Expansion note: The rest of this M2 batch was locally authored in Polish as short ABCD trivia questions. Facts were checked against broadly available reference sources where needed, especially Wikidata/Wikipedia pages and official/common reference pages for stable facts. No long source passages were copied; question wording, explanations, distractors, and speech aliases are original local text.

Transformation note for Open Trivia Database seed items: Questions and answers were translated into Polish, paraphrased for the local ABCD trivia format, and given locally written Polish explanations and speech aliases. A few distractors were adjusted to be clearer in Polish.

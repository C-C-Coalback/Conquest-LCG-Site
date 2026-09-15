# Contribution Guidelines

The entire website is open-source, and contributions are appreciated. Please follow the guidelines laid out below.

## Types of Contributions

### Bug Fix

- Outline what the previous behaviour was, and what it was supposed to do.
- You do not need to say what was changed exactly; most bug fixes should be relatively small, so I will just review the changes of the files.
- Bonus points if you include a unit test for this bug fix, but not required.
- AI-generated code is allowed for bug fixes. Please disclose your LLM usage if this is the case.

### New Feature

- Explain what the new feature is and how it works.
- Include a note stating if any other features had to be changed in order to accomodate this new one, and if so what those changes were. (e.g. if you add a new feature to the Lobby system, did you have to rework how the lobby code works?)
- The usage of an LLM, in addition to what parts of the code that it wrote, must be disclosed.
- If your contribution is very large (i.e. roughly 500+ lines) and an LLM was used, please improve the quality of the code. I only have so much time in my day, and I would rather not spend it reading 1000+ lines of AI-generated slop that badly accomplishes a task, when a more careful approach could get it done in 100 lines.

### Several New Features

- Don't.
- Split the contribution into each individual feature, and make a separate pull request for each.

### Unit Tests

- List all cards that had their unit tests changed.
- If the unit test(s) is for a card that previously had no unit tests, include whether the test is "Full" (i.e. covers many edge cases), "basic" (checks that each of the card's functionality works a single time), or "incomplete" (i.e. not fully done, e.g. card has two abilities and only one is tested, or unit test isn't working for whatever reason). Further details are not necessary.
- If the unit test(s) is for a card that previously had at least one unit test, explain what new case you are testing for.
- If a unit test is not passing, please include a reason for why (e.g. website is handling a card interaction wrong)
- AI-generated unit tests are permitted so long as the usage of an LLM is disclosed. Please keep in mind that LLMs are notorious for making things up to get unit tests to pass; that doesn't mean they can't be used, just that you should be careful.
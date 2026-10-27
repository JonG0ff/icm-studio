# Security Policy

## Report A Problem

Please do not open a public issue for a security problem.

Use GitHub's private vulnerability reporting instead:

1. Open the repository's **Security** tab.
2. Choose **Report a vulnerability**.
3. Describe the problem and how to reproduce it.

We will reply in the advisory thread.

## What Counts

- A secret, key, or personal data committed to the repository.
- A script that can write outside the repository or leak local files.
- A setup step that sends data somewhere the docs do not say.

## Keeping Your Own Copy Safe

- Never commit `.env`. Only `.env.example`, with blank values, belongs in Git.
- Raw media stays in ignored local folders.
- Do not commit browser cookie files used for downloads.

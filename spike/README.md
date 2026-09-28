# Spike: Word files and skills on claude.ai and in Claude Code

This folder is build step 1 of PLAN.md. It is a throwaway test, not part of the toolkit.
It will be deleted once the shared scripts exist.

What is here:

1. docx-spike/: a tiny test skill. Its script reads a Word file and writes tracked changes into a copy.
2. build.py: builds dist/spike-sample.docx (an invented report) and three zips of the skill.
3. RESULTS.md: what the spike found.

To build the files, run `python3 spike/build.py`.

## The claude.ai test

You need a claude.ai account with code execution turned on: Settings, Capabilities, "Code execution and file creation".

1. Download docx-spike-A.zip and spike-sample.docx.
2. On claude.ai, open Customize, then Skills. Click "+", then "Create skill", then "Upload a skill". Choose docx-spike-A.zip.
3. If the upload fails, write down the error message. Then try docx-spike-B.zip. If that fails too, try docx-spike-C.zip.
4. Start a new chat, outside any Project. Attach spike-sample.docx. Type: Run the docx spike on this file.
5. Watch the grey steps in the chat. Note which skills Claude opens.
6. Download the Word file Claude returns. Open it in Word and check:
   1. Word opens it without a repair message.
   2. It shows tracked changes by "Claude": a new paragraph under Summary, word changes in the Background paragraph, and a deleted paragraph under Volunteers.
   3. "local volunteers" is still bold, and "neighbourhood" is still italic.
   4. The three comments are still there.
   5. Reject All gives back the original text. Accept All gives the edited text.
7. Optional: repeat step 4 in a chat inside a Project.
8. Send back the SPIKE REPORT block from the chat, which zip worked (with any error messages), which skills Claude opened, and what Word showed.
9. After the test, turn off or delete the docx-spike skill.

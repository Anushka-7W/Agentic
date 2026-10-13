# Customer Complaint Urgency Classifier

## Aim
Demonstrate zero-shot and few-shot prompting by classifying customer complaints as `Urgent` or `Not Urgent`.

## Requirements
- Python 3.9+
- Groq API key

Install dependencies:
```bash
pip install groq python-dotenv
```

Create a `.env` file in the same folder:
```text
GROQ_API_KEY=your_actual_api_key
```

Run:
```bash
python complaint_urgency_classifier_best.py
```

## How it works
1. The user selects zero-shot, few-shot, or a comparison of both.
2. The program builds the appropriate prompt.
3. The Groq chat API generates a JSON classification.
4. The program parses and validates the JSON and prints the label and reason.

## Prompting methods
- **Zero-shot:** gives the model task instructions and label definitions without labeled examples.
- **Few-shot:** adds five labeled sample complaints to demonstrate how the labels should be applied.
- **Compare:** runs both prompt styles on the same complaint so their outputs can be examined.

## Example input
`Someone changed my account email without permission, and I cannot log in.`

Expected label: `Urgent` (the model response may vary).

## Limitations
This is a teaching/demo classifier, not a replacement for a support team's incident policy. Model predictions can be wrong; urgent security and payment incidents should be reviewed by a human.

# Bilingual visual CV downloads

The Spanish and English one-page PDFs use the original blue visual identity with a smaller portrait/header, larger body type and leading, consistent medium-weight date capsules, and a three-column footer for software, languages and contact. Role descriptions are concise versions of the current portfolio responsibilities. Experience precedes education. Standalone AI software labels are omitted.

Regenerate with Python 3, reportlab and Pillow:

```powershell
python scripts/generate_cv.py
```

The generator uses assets/cv/design and downloads Montserrat TTF fonts from the author's repository on first use. Review role summaries and dates when portfolio content changes. All PDFs contain selectable text and six active links: phone, email, portfolio, LinkedIn, Behance and YouTube.

Copy the English PDF to CV-Sergio-Coll-English/assets/cv for the standalone English site. Bump the download-link version query after replacement to avoid cached older PDFs.

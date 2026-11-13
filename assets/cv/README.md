# Visual bilingual CV downloads

The one-page PDFs preserve the supplied CV design: Montserrat typography, portrait, blue edge bands, two-column education and experience, software icons, language rings and portfolio button. Content comes from the current Spanish and English portfolio HTML.

Regenerate from the repository root:

```powershell
python -m pip install reportlab Pillow
python scripts/generate_cv.py
```

The generator uses the design assets in assets/cv/design and downloads Montserrat TTF fonts from the author's public repository on first use. The PDFs retain selectable text and six active links: phone, email, portfolio, LinkedIn, Behance and YouTube.

Copy the English PDF to CV-Sergio-Coll-English/assets/cv for the standalone English site. When replacing the PDFs, update the version query on each download link to avoid a cached previous version. The download file names and analytics attributes remain stable.

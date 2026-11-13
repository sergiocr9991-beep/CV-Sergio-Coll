# Downloadable CVs

The Spanish and English PDF files are generated from index.html and en/index.html. Keep the PDFs in sync after profile updates.

Regenerate from the repository root with Python 3 and reportlab installed:

```powershell
python scripts/generate_cv.py
```

The default font directory is C:/Windows/Fonts (Arial regular and bold). An alternative directory containing arial.ttf and arialbd.ttf may be passed as the second argument, after the repository root.

The English PDF is also copied into CV-Sergio-Coll-English/assets/cv/ for the standalone English site. All downloads use a same-origin HTML download link and remain usable without JavaScript. The existing GTM container receives a cv_download data-layer event with language, file name, URL and placement; collecting that custom event in a reporting destination depends on its GTM configuration.

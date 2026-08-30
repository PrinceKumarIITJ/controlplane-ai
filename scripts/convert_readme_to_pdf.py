import os
import re
import subprocess
import markdown

def convert_readme_to_html(readme_path, html_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Pre-process GitHub Alerts > [!NOTE] and > [!IMPORTANT]
    text = re.sub(
        r'>\s*\[!NOTE\]\s*\n>\s*(.*)',
        r'<div class="callout callout-note"><strong>NOTE:</strong> \1</div>',
        text
    )
    text = re.sub(
        r'>\s*\[!IMPORTANT\]\s*\n>\s*(.*)',
        r'<div class="callout callout-important"><strong>IMPORTANT:</strong> \1</div>',
        text
    )

    # Pre-process math blocks for clear HTML presentation
    text = re.sub(
        r'\$\$\s*(.*?)\s*\$\$',
        r'<div class="math-block">\1</div>',
        text,
        flags=re.DOTALL
    )

    # Convert markdown to html
    html_content = markdown.markdown(
        text,
        extensions=['tables', 'fenced_code', 'toc', 'nl2br']
    )

    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ControlPlane.ai — README Documentation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        @page {{
            size: A4;
            margin: 16mm 14mm 16mm 14mm;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b;
            background: #ffffff;
            line-height: 1.55;
            font-size: 9.5pt;
            margin: 0;
            padding: 0;
        }}
        
        h1 {{
            font-size: 22pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 6px;
            margin-top: 0;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}
        
        h2 {{
            font-size: 14pt;
            font-weight: 700;
            color: #0f172a;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;
            page-break-after: avoid;
            letter-spacing: -0.01em;
        }}
        
        h3 {{
            font-size: 11pt;
            font-weight: 600;
            color: #1e293b;
            margin-top: 14px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}
        
        p {{
            margin-top: 0;
            margin-bottom: 10px;
        }}
        
        ul, ol {{
            margin-top: 0;
            margin-bottom: 10px;
            padding-left: 20px;
        }}
        
        li {{
            margin-bottom: 3px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 8.5pt;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #cbd5e1;
            padding: 6px 8px;
            text-align: left;
            vertical-align: top;
        }}
        
        th {{
            background-color: #f1f5f9;
            font-weight: 600;
            color: #0f172a;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        pre, code {{
            font-family: 'JetBrains Mono', Consolas, 'Courier New', monospace;
        }}
        
        code {{
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 8.5pt;
            border: 1px solid #e2e8f0;
        }}
        
        pre {{
            background-color: #0f172a;
            color: #f8fafc;
            padding: 10px 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 8.5pt;
            line-height: 1.4;
            margin: 10px 0;
            page-break-inside: avoid;
            border: 1px solid #1e293b;
        }}
        
        pre code {{
            background-color: transparent;
            color: inherit;
            padding: 0;
            border: none;
        }}
        
        .callout {{
            margin: 12px 0;
            padding: 10px 12px;
            border-left: 4px solid #3b82f6;
            background-color: #eff6ff;
            color: #1e40af;
            border-radius: 0 6px 6px 0;
            font-size: 9pt;
        }}
        
        .callout-important {{
            border-left-color: #f59e0b;
            background-color: #fffbeb;
            color: #92400e;
        }}

        .math-block {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #0f172a;
            padding: 10px 14px;
            margin: 12px 0;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: #0f172a;
            text-align: center;
            border-radius: 4px;
            font-size: 9.5pt;
            page-break-inside: avoid;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 18px 0;
        }}
        
        a {{
            color: #2563eb;
            text-decoration: none;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(styled_html)
    print(f"HTML generated at: {html_path}")

def generate_pdf(html_path, pdf_path):
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    
    print(f"Running Edge headless PDF generation...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"PDF successfully generated at: {pdf_path}")
    else:
        print(f"PDF generation failed: {result.stderr}")

if __name__ == "__main__":
    workspace_dir = r"c:\Users\Prince Kumar\OneDrive\Documents\controlplane-ai"
    readme_file = os.path.join(workspace_dir, "README.md")
    html_file = os.path.join(workspace_dir, "README.html")
    pdf_file = os.path.join(workspace_dir, "README.pdf")
    
    convert_readme_to_html(readme_file, html_file)
    generate_pdf(html_file, pdf_file)

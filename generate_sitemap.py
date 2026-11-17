import json
import os
import datetime

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
DEPLOYED_LOG = os.path.join(WORKSPACE, "deployed_tools.json")
SITEMAP_PATH = os.path.join(WORKSPACE, "sitemap.xml")

def generate_sitemap():
    if not os.path.exists(DEPLOYED_LOG):
        print("No deployed tools found. Skipping sitemap generation.")
        return

    with open(DEPLOYED_LOG, "r", encoding="utf-8") as f:
        tools = json.load(f)

    today = datetime.date.today().isoformat()
    
    xml_content = []
    xml_content.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Homepage
    xml_content.append('  <!-- Homepage / Directory -->')
    xml_content.append('  <url>')
    xml_content.append('    <loc>https://vinatools.vercel.app/</loc>')
    xml_content.append(f'    <lastmod>{today}</lastmod>')
    xml_content.append('    <changefreq>weekly</changefreq>')
    xml_content.append('    <priority>1.0</priority>')
    xml_content.append('  </url>')
    
    # Core Trust & Developer Pages
    xml_content.append('  <!-- Core Trust & Developer Pages -->')
    trust_pages = ["api-docs.html", "privacy.html", "terms.html", "about.html", "contact.html", "refund.html"]
    for page in trust_pages:
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>https://vinatools.vercel.app/{page}</loc>')
        xml_content.append(f'    <lastmod>{today}</lastmod>')
        xml_content.append('    <changefreq>monthly</changefreq>')
        xml_content.append('    <priority>0.5</priority>')
        xml_content.append('  </url>')
    
    # Categorize tools for formatting (optional, but clean)
    xml_content.append('  <!-- Deployed Tools -->')
    for tool in tools:
        slug = tool["slug"]
        kw = tool["keyword"]
        # Standardize URL to vinatools.vercel.app production domain
        url = f"https://vinatools.vercel.app/{slug}"
        
        # Estimate lastmod from deployed_at or today
        deployed_at = tool.get("deployed_at", today)
        if "T" in deployed_at:
            lastmod = deployed_at.split("T")[0]
        else:
            lastmod = today
            
        priority = "0.9" if "lao động" in kw or "xin việc" in kw else "0.8"
        
        xml_content.append(f'  <!-- {kw.capitalize()} -->')
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>{url}</loc>')
        xml_content.append(f'    <lastmod>{lastmod}</lastmod>')
        xml_content.append('    <changefreq>monthly</changefreq>')
        xml_content.append(f'    <priority>{priority}</priority>')
        xml_content.append('  </url>')
        
    xml_content.append('</urlset>')
    
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_content))
        
    print(f"sitemap.xml successfully generated for {len(tools)} tools!")

if __name__ == "__main__":
    generate_sitemap()

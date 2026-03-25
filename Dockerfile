FROM odoo:15

USER root
# Install external python dependencies for custom modules safely
RUN pip3 install --no-cache-dir \
    "urllib3<2" "cryptography<39" "pyOpenSSL>=22.0.0" \
    anthropic openai PyPDF2==2.12.1 "google-generativeai>=0.8.0" \
    google-genai \
    google-auth-httplib2 google-auth-oauthlib google-api-python-client

USER odoo

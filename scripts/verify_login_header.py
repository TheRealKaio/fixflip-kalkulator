"""Check the generated login header integration without altering authentication logic."""
from pathlib import Path
import re
workflow=Path('.github/workflows/pages.yml').read_text(encoding='utf-8')
access=Path('assets/user-access.js').read_text(encoding='utf-8')
css=Path('assets/immocheck-ui-refresh.css').read_text(encoding='utf-8')
assert 'PY_LOGIN_HEADER' in workflow, 'Login header build integration missing'
assert 'nic-account-label' in workflow, 'Real login text not generated'
assert 'href="/#anmelden"' in workflow, 'Header still targets admin'
assert 'aria-label="Jetzt anmelden"' in workflow, 'Login accessible label missing'
assert "(user?profile():login())" in access, 'Login click is not hooked up'
assert "if(!config?.enabled){alert(" in access, 'Disabled account service would fall back to admin link'
assert '.nic-account-label' in css and '.nic-account-link::after' not in css
# The isolated practical build must use the same selector as the page build.
# Previously a double-escaped word boundary skipped the login label on test pages.
import ast
practical=Path('.github/workflows/immocheck-practical-tests.yml').read_text(encoding='utf-8')
def header_pattern(text):
    line=next((line for line in text.splitlines() if "html=re.sub(r'(<a" in line),None)
    assert line, 'Login anchor selector missing in build workflow'
    match=re.search(r"html=re.sub\\((r'[^']+')",line)
    assert match, 'Cannot inspect login anchor selector'
    return ast.literal_eval(match.group(1))
pattern=header_pattern(workflow)
assert pattern==header_pattern(practical), 'Practical build login selector differs from page build'
assert re.search(pattern,'<a href="/#admin" class="nic-account-link">Konto</a>',re.S), 'Login selector does not match account link'
print('Login header source integration checks passed (browser activation not verified).')

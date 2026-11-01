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
print('Login header source integration checks passed (browser activation not verified).')

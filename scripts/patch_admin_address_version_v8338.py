"""Release marker for synchronized admin version and postal-code/city line."""
from pathlib import Path
import sys
if not Path(sys.argv[1]).is_file():
    raise SystemExit('Generated index missing')
print('V8.338 admin version and address formatting enabled')

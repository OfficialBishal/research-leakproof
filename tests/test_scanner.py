import research_leakproof as leakproof
from research_leakproof.finding import Severity

LEAKY = """
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

X = np.random.rand(100, 5)
y = np.random.rand(100)
X = StandardScaler().fit_transform(X)            # fit on everything, then split
X_train, X_test, y_train, y_test = train_test_split(X, y)
"""

CLEAN = """
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

X = np.random.rand(100, 5)
y = np.random.rand(100)
X_train, X_test, y_train, y_test = train_test_split(X, y)
scaler = StandardScaler().fit(X_train)            # fit on train only
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)
"""


def test_scanner_flags_fit_before_split(tmp_path):
    f = tmp_path / "leaky.py"
    f.write_text(LEAKY)
    findings = leakproof.scan(str(f))
    assert any(x.check == "preprocessing_leakage" and x.severity == Severity.WARN
               for x in findings)
    assert str(f) in findings[0].location


def test_scanner_clean_when_fit_after_split(tmp_path):
    f = tmp_path / "clean.py"
    f.write_text(CLEAN)
    findings = leakproof.scan(str(f))
    assert findings == []


def test_scanner_ignores_model_fit_with_xy(tmp_path):
    code = (
        "from sklearn.linear_model import LinearRegression\n"
        "from sklearn.model_selection import train_test_split\n"
        "X, y = [[1]], [1]\n"
        "Xtr, Xte, ytr, yte = train_test_split(X, y)\n"
        "LinearRegression().fit(Xtr, ytr)\n"
    )
    f = tmp_path / "model.py"
    f.write_text(code)
    assert leakproof.scan(str(f)) == []

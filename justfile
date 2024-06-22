locations := "src/ tests/"

_default: fix check

[private]
alias t := test
test *args:
    rye run pytest -s --cov {{ args }}

[private]
alias f := fix
fix: (_lint "--fix") _format

[private]
alias c := check
check: _lint (_format "--check") _type-check

_lint *args:
    rye lint {{ locations }} {{ args }}

_format *args:
    rye fmt {{ locations }} {{ args }}

_type-check:
    mypy {{ locations }}
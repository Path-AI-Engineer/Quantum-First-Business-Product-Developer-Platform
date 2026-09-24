# Contract examples

`claim.valid.json` is a real source-linked claim from the corpus.
`claim.invalid-missing-source.json` removes the required provenance on an
external fact and must fail semantic validation with Pydantic.

Draft 2020-12 schemas cover field types, enumerations and structure.
Cross-record references, confidence provenance, interval ordering, scope and
interview-state rules additionally require `venture evidence validate`.
A syntactically valid JSON document is not automatically valid evidence.

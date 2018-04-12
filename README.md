[![https://img.shields.io/badge/license-Apache%202.0-blue.svg](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

# TapCliPy
Python Client Library for [TAP](https://github.com/heta-io/tap)

### Example

```python

from TapCliPy import TapConnect

# Create TAP connection
tap = TapConnect.Connect('http://tap.mycompany.com')
print(tap.url())

# Get the current schema
tap.fetch_schema()
for query,type in tap.schema_query_name_types().items():
    print("{} : {}".format(query, type))

# Try a simple query
query = tap.query('metrics')
print('query:', query)

text = "This is a test of TAP."
json = tap.analyse_text(query, text)

print("Output json object from TAP:\n")
print(json)

```
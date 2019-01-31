from tapclipy import tap_connect
from IPython.core.display import display, HTML

# Create TAP Connection
tap = tap_connect.Connect('http://localhost:9000')
tap.fetch_schema()
print(tap.url())

query = tap.query('reflectExpressions')

string = "This is the first great happy blue angry cold sentence I know. This is the second fantastic sentence."

strResult = tap.analyse_text(query, string)

output = tap.markup(string, strResult)

display(HTML(output))












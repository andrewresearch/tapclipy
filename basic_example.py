from tapclipy import tap_connect

# Create TAP Connection
tap = tap_connect.Connect('http://tap.yourdomain.com')

# Get and print the Current Schema
tap.fetch_schema()
for query,type in tap.schema_query_name_types().items():
    print("{} >> {}".format(query, type))
print("----------------------------------------------")

# Analyse some text for some basic metrics
query = tap.query('metrics')
text = "This is a very small test of TAP. It should produce some metrics on these two sentences!"
json = tap.analyse_text(query, text)

print()
print("METRICS:\n", json)

query = dict()

query['metrics'] = "query Metrics($input: String!){ metrics(text: $input) { analytics {words, sentences, sentWordCounts, averageSentWordCount } } }"


query['schema'] = '''
    { __schema { queryType { name ...subtypes } } }
    fragment subtypes on __Type { fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
        name
        type {
          ofType {
            name
          }
         fields {
          name
        }}}}}}}}}}}}}}
'''
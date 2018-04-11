query = dict()

query['metrics'] = "query Metrics($input: String!){ metrics(text: $input) { analytics {words, sentences, sentWordCounts, averageSentWordCount } } }"
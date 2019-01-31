from tapclipy import queries
from urllib import request
import json
import re


class Connect:

    def __init__(self, url='http://localhost:9000', endpoint='/graphql'):
        self.__full_url = url + endpoint
        self.__can_connect = False
        self.__current_schema = ""
        self.__current_query_name_types = dict()

    def url(self):
        return self.__full_url

    def schema_query_name_types(self):
        return self.__current_query_name_types

    def query(self, name):
        if name in self.__current_query_name_types:
            return queries.query[name]
        else:
            return ""

    def parameters(self, name):
        if name in self.__current_query_name_types:
            return queries.parameters[name]

    def fetch_schema(self):
        schema_query = json.dumps({'query': queries.query['schema']})
        jbody = self.__tap_connect(schema_query)
        if jbody == '{}':
            return jbody
        else:
            self.__current_schema = jbody['data']['__schema']['queryType']['fields']
            self.__current_query_name_types = dict()
            for field in self.__current_schema:
                name = field['name']
                self.__current_query_name_types[name] = field['type']['ofType']['name']
            return self.__current_schema

    def analyse_text(self, query, text, parameters=''):
        variables = {'input': text,'parameters': parameters}
        #escaped_query = query.replace("\n", "\\n")  # query.encode('utf8').decode('unicode_escape')
        analyse_query = json.dumps({'query': query, 'variables': variables})
        return self.__tap_connect(analyse_query)

    def process_sentences(self, tags):

        # create empty array to hold completed sentences
        sentences = []

        # loop tag data
        for data in tags:
            # get copy of sentence we are working on
            newString = data['sentence']

            # loop phrase tags
            for phrase in data['phrases']:
                capturedPhrase = re.search("^([a-z A-Z']+)\[", phrase).group(1)
                tag = re.search("\[([a-zA-Z]+),", phrase).group(1)
                print(tag)
                newString = newString.lower().replace(capturedPhrase, "<span class='badge'>{word}</span>".format(word=capturedPhrase))
            sentences.append(newString)

        return sentences

    def markup(self, text, results):

        analytics = results['data']['reflectExpressions']['analytics']
        counts = analytics['counts']

        sentences = self.process_sentences(analytics['tags'])

        wordCount = counts['wordCount']

        avgWordLength = counts["avgWordLength"]

        sentenceCount = counts['sentenceCount']

        avgSentenceLength = counts['avgSentenceLength']

        sentenceRows = ""

        for i in range(len(sentences)):
            sentenceRows += "<tr><td>{count}</td><td>{sen}</td><td>nil</td></tr>".format(count=(i + 1), sen=sentences[i])

        style = '''
        <style type="text/css" media="screen">
        
            .rendered_html th, .rendered_html td {
                text-align: left;        
            }
            .rendered_html table, .rendered_html th, .rendered_html td {
                border: 1px solid black;
                border-collapse: collapse;            
            }
            .rendered_html table {
                table-layout: auto;
            }
            .rendered_html .column1 {
                float: left;
                width: 60%;
                margin-right: 10px;
            }
            .rendered_html .column2 {
                float: left;
                width: 35%;
            }
            .rendered_html .row:after {
                content:"";
                display: table;
                clear: both;
            }
            
        </style>
        
        '''

        output = style + """
        <h1>Results from Query</h1>
        <br />
        <div class="row">
            <div class="column1">
                <table style="width:100%">
                    <tr>
                        <th>No</th>
                        <th>Sentence</th>
                        <th>Meta Tags</th>
                    </tr>
                    {sentencerows}
                </table>            
            </div>
            <div class="column2">
                <table style="width:100%">
                    <tr>
                        <th>Summary</th>
                        <th></th>                
                    </tr>
                    <tr>
                        <td>Word Count</td>
                        <td>{wordcount}</td>                
                    </tr>
                    <tr>
                        <td>Avg Word Length</td>
                        <td>{wordlength}</td>                
                    </tr>
                    <tr>
                        <td>Sentence Count</td>
                        <td>{sentencecount}</td>                
                    </tr>
                    <tr>
                        <td>Avg Sentence Length</td>
                        <td>{avgsentencelength}</td>                
                    </tr>
                </table>
            </div>
        </div>   
        """.format(
            wordcount="{0} words".format(wordCount),
            wordlength="{0:.2f} characters".format(avgWordLength),
            sentencecount="{0} sentences".format(sentenceCount),
            avgsentencelength="{0} words".format(avgSentenceLength),
            sentencerows=sentenceRows
        )

        return output

    def __tap_connect(self, query):
        try:
            json_header = {'Content-Type': 'application/json'}
            tap_request = request.Request(self.__full_url, data=query.encode('utf8'), headers=json_header)
            tap_response = request.urlopen(tap_request)
            body = tap_response.read().decode('utf8')
            self.__can_connect = True
            return json.loads(body)
        except Exception as error:
            self.__can_connect = False
            print('QUERY:', query)
            print('ERROR', error)
            return json.dumps({})

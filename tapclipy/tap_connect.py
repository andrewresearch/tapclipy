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

    def process_sentences(self, tags, customClass=""):

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

                if customClass is not "":
                    newString = newString.lower().replace(capturedPhrase, "<span class='{tagType} {custom}'>{word}</span>".format( word=capturedPhrase, tagType=tag.lower(), custom=customClass))
                else:
                    newString = newString.lower().replace(capturedPhrase,
                                                      "<span class='{tagType}'>{word}</span>".format(
                                                          word=capturedPhrase, tagType=tag.lower()))

            sentences.append(newString)

        return sentences

    def make_css(self, custom_style):
        styles = ""
        if custom_style is not None:
            for key in custom_style:
                rules = ""
                for rule in custom_style[key]:
                    rules += "  " + rule + ": " + custom_style[key][rule] + ";\n"
                styles += "." + key + "{\n" + rules + "}\n"

        return styles

    def make_table_html(self, result_data, custom_class=""):

        analytics = result_data['data']['reflectExpressions']['analytics']

        counts = analytics['counts']

        sentences = self.process_sentences(analytics['tags'], custom_class)

        word_count = counts['wordCount']

        avg_word_length = counts["avgWordLength"]

        sentence_count = counts['sentenceCount']

        avg_sentence_length = counts['avgSentenceLength']

        sentence_rows = ""

        for i in range(len(sentences)):
            sentence_rows += "<tr><td>{count}</td><td>{sen}</td><td>nil</td></tr>".format(count=(i + 1), sen=sentences[i])

        output = """                
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
            wordcount="{0} words".format(word_count),
            wordlength="{0:.2f} characters".format(avg_word_length),
            sentencecount="{0} sentences".format(sentence_count),
            avgsentencelength="{0} words".format(avg_sentence_length),
            sentencerows=sentence_rows
        )

        return output

    def make_html(self, result_data, custom_class=""):
        output = ""
        analytics = result_data['data']['reflectExpressions']['analytics']

        sentences = self.process_sentences(analytics['tags'], custom_class)

        for sentence in sentences:
            output += sentence

        return output

    def get_table_css(self):
        return """
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
        """

    def markup(self, html, css="""
            .anticipate{
                background-color: red;
            }
            .compare{
                background-color: blue;
            }
            .consider{
                background-color: green;
            }
            .definite{
                background-color: aqua;
            }
            .generalpronounverb {
                background-color: cadetblue;
            }
            .grouppossessive{
                background-color: gold;
            }
            .pertains{
                background-color: blueviolet;
            }
            .selfpossessive{
                background-color: brown;
            }            
            .selfreflexive{
                background-color: chocolate;
            }"""):

        style = '''
        <style type="text/css" media="screen">
        {custom_style}
        </style>
        '''.format(custom_style=css)

        return style + html

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

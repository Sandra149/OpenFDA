
#<Buscador medicamentos OpenFDA>
#Copyright (C) <2017>  <Sandra Torres>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import http.client
import http.server
import json

#ejecutar con pyhton3

class OpenFDAClient():

    OPENFDA_API_URL = "api.fda.gov"
    OPENFDA_API_EVENT='/drug/event.json'

    def get_response(self, query = '',limite = ''):
        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)

        if len(query) == 0:
            limite = '?limit='+str(limite)
        else:
            limite = '&limit=10'
        
        
        print (self.OPENFDA_API_EVENT +limite)

        conn.request("GET", self.OPENFDA_API_EVENT + query+limite)

        response = conn.getresponse()
        print (response.status, response.reason)

        return response.read().decode('utf8')    

class OpenFDAParser():
    
    def get_drugs_from_medicines(self,medicines_list):
        drugs=[]
        for medicine in medicines_list:
            drugs+= [medicine['patient']['drug'][0]['medicinalproduct']]

        return drugs

    def get_companynumb(self,medicines_list):  
        number_list=[]
        for medicine in medicines_list:
            number_list += [medicine['companynumb']]
        return number_list

    def get_company_from_events(self,events):
        drugs=[]
        for event in events:
            drugs += [event['companynumb']]
        return drugs

    def get_patient_sex(self,events):
        gender=[]
        for event in events:
            gender += [event['patient']['patientsex']]
        return gender

class OpenFDAHTML():

    def get_html(self,drugs):

        drugs_html = '''
        <html>
            <head>
                <title>OpenFDA Cool App</title>
            </head>
            <body>
                <ol>
                '''
        for drug in drugs:
            drugs_html+= '<li>'+drug+'</li>\n'

        drugs_html+= '''
                </ol>
            </body>
        </html>
        '''
        return drugs_html

    def get_main_page(self):

        with open ('codigo_html.html','r') as f:
            html = f.read()
            
        return html

    def get_error_page(self):

        with open ('codigo_html_error.html','r') as f:

            html = ''
            for line in f:
                html+= line

            return html
    

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    
    SEARCH_MEDICINE = "?search=patient.drug.medicinalproduct:"
    SEARCH_COMPANY = "?search=companynumb"

    def pass_limit(self,path):

        limite_usuario = path.split('=')[1]
        return str(limite_usuario)

    def correct_server_answer(self):

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    def is_query_ok(self, query):
        if 'limit' in query:
            try:
                limit = self.path.split('=')[1]

                limit = int(limit)

            except ValueError:
                return False

        return True

    def do_GET(self):
                
        print(self.path)

        correct = self.is_query_ok(self.path)
        client = OpenFDAClient()
        parser = OpenFDAParser()
        html = OpenFDAHTML()

        if not correct:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = html.get_error_page()

            self.wfile.write(bytes(html, 'utf8'))

            return         

        if self.path=='/':
            
            self.correct_server_answer()
        
            html = html.get_main_page()

            self.wfile.write(bytes(html, "utf8")) 

        elif '/listDrugs?limit=' in self.path:

            self.correct_server_answer()

            query=''
            jsons=client.get_response(query,self.pass_limit(self.path))
            medicines_list=json.loads(jsons)['results']

            drugs= parser.get_drugs_from_medicines(medicines_list)

            html = html.get_html(drugs)
            self.wfile.write(bytes(html, "utf8"))

        elif '/searchDrug?' in self.path:

            self.correct_server_answer()

            limite = 10

            medicamento_usuario=self.path.split('=')[1]
            
            jsons = client.get_response(self.SEARCH_MEDICINE+medicamento_usuario,limite)
            medicines_list = json.loads(jsons)['results']

            company_numb = parser.get_companynumb(medicines_list)

            html = html.get_html(company_numb)
            self.wfile.write(bytes(html, "utf8"))

        elif '/listCompanies?limit=' in self.path:

            self.correct_server_answer()

            query=''

            jsons=client.get_response(query, self.pass_limit(self.path))
            company_list=json.loads(jsons)['results']

            drugs = parser.get_company_from_events(company_list)

            html = html.get_html(drugs)
            self.wfile.write(bytes(html, "utf8"))

        elif '/searchCompany?' in self.path:

            self.correct_server_answer()

            limite=10

            company_numb = self.path.split('=')[1]

            print(self.path)

            jsons = client.get_response(self.SEARCH_COMPANY.replace('companynumb', company_numb),limite)
            company = json.loads(jsons)['results']

            company_numb= parser.get_drugs_from_medicines(company)
            html = html.get_html(company_numb)
            self.wfile.write(bytes(html, "utf8"))
        
        elif '/listGender?limit=' in self.path:
            
	self.correct_server_answer()

            query = ''

            jsons = client.get_response(query,self.pass_limit(self.path))
            gender_list = json.loads(jsons)['results']

            drugs = parser.get_patient_sex(gender_list)

            html = html.get_html(drugs)
            self.wfile.write(bytes(html, "utf8"))
        else:

            self.send_response(404)
            self.send_header('Content-type','text/html')
            self.end_headers()

            html = html.get_error_page()
            self.wfile.write(bytes(html, "utf8"))

        return

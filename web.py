
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
import food

'''
 Clase que se conectará a la API.
'''
class OpenFDAClient():

    OPENFDA_API_URL = "api.fda.gov"
    OPENFDA_API_EVENT = '/drug/event.json'

    '''
     Función que devuelve la respuesta sin parsear.
    '''
    def get_response(self, query = '', limit = ''):

        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)

        if len(query) == 0:
            limit = '?limit=' + str(limit)
        else:
            limit = '&limit=10'
        
        print (self.OPENFDA_API_EVENT + limit)

        conn.request("GET", self.OPENFDA_API_EVENT + query + limit)

        response = conn.getresponse()
        print (response.status, response.reason)

        return response.read().decode('utf8')    

'''
 Clase que parseará los JSONs.
'''
class OpenFDAParser():
    
    '''
     Función que devuelve la lista de 
    '''
    def get_drugs_from_medicines(self, medicines_list):

        drugs = []
        for medicine in medicines_list:
            drugs += [medicine['patient']['drug'][0]['medicinalproduct']]

        return drugs

    '''
     Función que devuelve la lista de 
    '''
    def get_companynumb(self, medicines_list):  

        number_list = []
        for medicine in medicines_list:
            number_list += [medicine['companynumb']]

        return number_list

    '''
    Se llama get company pero devuelve drugs
    '''
    def get_company_from_events(self, events):

        drugs = []
        for event in events:
            drugs += [event['companynumb']]
            
        return drugs

    '''
     Función que devuelve la lista de 
    '''
    def get_patient_sex(self, events):

        gender = []
        for event in events:
            gender += [event['patient']['patientsex']]
            
        return gender

'''
 Clase que forma los distintos HTMLs.
'''
class OpenFDAHTML():

    '''
     Función que devuelve la página con una lista de elementos.
    '''
    def get_html(self, elems):

        html = '''
        <html>
            <head>
                <title>OpenFDA Cool App</title>
            </head>
            <body>
                <ol>
                '''
        for elem in elems:
            html += '<li>' + elem + '</li>\n'

        html += '''
                </ol>
            </body>
        </html>
        '''
        return html

    '''
     Función que devuelve la página principal.
    '''
    def get_main_page(self):

        with open ('codigo_html.html', 'r') as f:
            html = f.read()
            
        return html

    '''
     Función que devuelve la página de error.
    '''
    def get_error_page(self):

        with open ('codigo_html_error.html', 'r') as f:
            html = ''
            for line in f:
                html += line

            return html
    

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    SEARCH_MEDICINE = "?search=patient.drug.medicinalproduct:"
    SEARCH_COMPANY = "?search=companynumb"
    FILE_NAME = 'openfda.log'
    DRUG = 'medicamentos'
    COMPANY = 'compania'
    
    '''
     Función que devuelve el límite introducido por el usuario.
    '''
    def get_limit(self, path):

        limite_usuario = path.split('=')[1]
        return limite_usuario

    '''
     Función que establece las cabeceras HTTPs con el código recibido.
    '''
    def set_headers(self, http_code):

        self.send_response(http_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    '''
     Función que comprueba que el límite es un número.
    '''
    def is_query_ok(self, query):

        if 'limit' in query:
            try:
                int(self.get_limit(query))

            except ValueError:
                return False

        return True

    '''
     Función que almacena lo que ha buscado el usuario en un fichero.
    '''
    def store_info(self, list_response, file_name, search_type, search = None):

        with open (file_name, 'a') as file:
            if search == None:
                file.write('El usuario ha buscado ' + search_type + ':\n')
            else:
                file.write('El usuario ha buscado ' + search_type + ' ' + search + ':\n')
                
            for words in list_response:
                file.write(words + '\n')

            file.write('\n')

    def do_GET(self):
                
        print(self.path)

        correct = self.is_query_ok(self.path)

        client = OpenFDAClient()
        parser = OpenFDAParser()
        html = OpenFDAHTML()

        food_client = food.OpenFDAClient()

        if not correct:

            self.set_headers(404)
            
            html_page = html.get_error_page()

            self.wfile.write(bytes(html_page, 'utf8'))

            return         

        if self.path == '/':

            self.set_headers(200)
        
            html_page = html.get_main_page()

            self.wfile.write(bytes(html_page, "utf8")) 

        elif '/listDrugs?limit=' in self.path:

            self.set_headers(200)

            query = ''
            jsons = client.get_response(query, self.get_limit(self.path))
            medicines_list = json.loads(jsons)['results']

            drugs = parser.get_drugs_from_medicines(medicines_list)

            html_page = html.get_html(drugs)

            self.wfile.write(bytes(html_page, 'utf8'))

        elif '/searchDrug?' in self.path:

            self.set_headers(200)

            limite = 10
            medicamento_usuario = self.path.split('=')[1]
            
            jsons = client.get_response(self.SEARCH_MEDICINE + medicamento_usuario, limite)
            medicines_list = json.loads(jsons)['results']

            company_numb = parser.get_companynumb(medicines_list)

            self.store_info(company_numb, self.FILE_NAME, self.DRUG, medicamento_usuario)

            html_page = html.get_html(company_numb)

            self.wfile.write(bytes(html_page, 'utf8'))

        elif '/listCompanies?limit=' in self.path:

            self.set_headers(200)

            query = ''
            jsons = client.get_response(query, self.get_limit(self.path))
            company_list = json.loads(jsons)['results']

            drugs = parser.get_company_from_events(company_list)

            html_page = html.get_html(drugs)

            self.wfile.write(bytes(html_page, 'utf8'))

        elif '/searchCompany?' in self.path:

            self.set_headers(200)

            limite = 10
            company_numb = self.path.split('=')[1]

            jsons = client.get_response(self.SEARCH_COMPANY.replace('companynumb', company_numb), limite)
            company = json.loads(jsons)['results']

            company_numb = parser.get_drugs_from_medicines(company)
            html_page = html.get_html(company_numb)

            self.wfile.write(bytes(html_page, 'utf8'))
        
        elif '/listGender?limit=' in self.path:

            self.set_headers(200)

            query = ''
            jsons = client.get_response(query, self.get_limit(self.path))
            gender_list = json.loads(jsons)['results']

            drugs = parser.get_patient_sex(gender_list)

            html_page = html.get_html(drugs)

            self.wfile.write(bytes(html_page, 'utf8'))

        elif '/secret' in self.path:

            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="My Realm"')
            self.end_headers()

        elif '/redirect' in self.path:

            self.send_response(302)
            self.send_header('Location', 'http://localhost:8000/')
            self.end_headers()
            
        else:

            self.set_headers(404)

            html_page = html.get_error_page()

            self.wfile.write(bytes(html_page, 'utf8'))

        return

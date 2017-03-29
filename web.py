
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

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
	OPENFDA_API_URL="api.fda.gov"
	OPENFDA_API_EVENT='/drug/event.json'
	SEARCH_MEDICINE = "?search=patient.drug.medicinalproduct:"
	SEARCH_COMPANY = "?search=companynumb"

	def get_html(self,drugs):
		drugs_html='''
		<html>
			<head>
				<title>OpenFDA Cool App</title>
			</head>
			<body>
				<ol>
				'''
		for drug in drugs:
			drugs_html+='<li>'+drug+'</li>\n'

		drugs_html+='''
				</ol>
			</body>
		</html>
		'''
		return drugs_html

	def get_main_page(self):
		html= """
		<html>
			<head>
				<link rel="shortcut icon" href="https://www.catalystmints.com/templates/noscope_new/favicon.ico">
				<title>OpenFDA Cool App</title>
			</head>
			<body>
				<h1>Open FDA</h1>
				<form method='get' action='listDrugs'>
					<input type='submit' value='Drug List: Send to OpenFDA'></input>
					Limit:<input type='text' size='4' name='limit'></input>
				</form>
				<form method='get' action='searchDrug'>
					<input type='text' name='drug'></input>
					<input type='submit' value='Drug Search: Send to OpenFDA'></input>

				</form>
				<form method='get' action='listCompanies'>
					<input type='submit' value='Company List: Send to OpenFDA'></input>
					Limit:<input type='text' size='4' name='limit'></input>
				</form>
				<form method='get' action='searchCompany'>
					<input type='text' name='company'></input>
					<input type='submit' value='Company Search: Send to OpenFDA'></input>
				</form>
				<form method='get' action='listPatientsex'>
					<input type='submit' value='Patient Sex List: Send to OpenFDA'></input>
					Limit:<input type='text' size='4' name='limit'></input>
				</form>
			</body>
		</html>
		"""
		return html

	def get_error_page(self):
		html= """
		<html>
			<head>
				<link rel="shortcut icon" href="http://gashuynhlien.vn/Images/error.png">
				<title>Error OpenFDA</title>
			</head>
			<body>
				<h1>Error</h1>
				<p>404 File not found</p>
			</body>
		</html>
		"""
		return html

	def get_response(self, query='',limite=''):
		conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)	#con es un objeto utilizado para interactuar con el servidor remoto

		if len(query)==0:
			limite='?limit='+str(limite)
		else:
			limite='&limit=10'
		
		
		print (self.OPENFDA_API_EVENT +limite)

		conn.request("GET", self.OPENFDA_API_EVENT + query+limite)

		response = conn.getresponse()
		print (response.status, response.reason)

		return response.read().decode('utf8')	#decodificar a un string porque no entendemos los bytes

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
	
	def pass_limit(self,path):
		limite_usuario=path.split('=')[1]
		return str(limite_usuario)

	def correct_server_answer(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		

	def do_GET(self):
		
		if self.path=='/':
			self.correct_server_answer()
		
			html=self.get_main_page()

			self.wfile.write(bytes(html, "utf8")) #wfile es un fichero de escritura que llega al cliente

		elif self.path=='/listDrugs?limit='+self.pass_limit(self.path):

			self.correct_server_answer()

			query=''
			jsons=self.get_response(query,self.pass_limit(self.path))
			medicines_list=json.loads(jsons)['results']

			drugs=self.get_drugs_from_medicines(medicines_list)

			html=self.get_html(drugs)
			self.wfile.write(bytes(html, "utf8"))

		elif '/searchDrug?' in self.path:

			self.correct_server_answer()

			limite=10

			medicamento_usuario=self.path.split('=')[1]
			
			jsons=self.get_response(self.SEARCH_MEDICINE+medicamento_usuario,limite)
			medicines_list=json.loads(jsons)['results']

			company_numb=self.get_companynumb(medicines_list)

			html=self.get_html(company_numb)
			self.wfile.write(bytes(html, "utf8"))

		elif self.path=='/listCompanies?limit='+self.pass_limit(self.path):

			self.correct_server_answer()

			query=''

			jsons=self.get_response(query, self.pass_limit(self.path))
			company_list=json.loads(jsons)['results']

			drugs=self.get_company_from_events(company_list)

			html=self.get_html(drugs)
			self.wfile.write(bytes(html, "utf8"))

		elif '/searchCompany?' in self.path:

			self.correct_server_answer()

			limite=10

			company_numb = self.path.split('=')[1]

			print(self.path)

			jsons = self.get_response(self.SEARCH_COMPANY.replace('companynumb', company_numb),limite)
			company = json.loads(jsons)['results']

			company_numb=self.get_drugs_from_medicines(company)
			html=self.get_html(company_numb)
			self.wfile.write(bytes(html, "utf8"))
		
		elif self.path=='/listPatientsex?limit='+self.pass_limit(self.path):
			
			self.correct_server_answer()

			query=''

			jsons=self.get_response(query,self.pass_limit(self.path))
			gender_list=json.loads(jsons)['results']

			drugs=self.get_patient_sex(gender_list)

			html=self.get_html(drugs)
			self.wfile.write(bytes(html, "utf8"))
		else:

			self.send_response(404)
			self.send_header('Content-type','text/html')
			self.end_headers()

			html=self.get_error_page()
			self.wfile.write(bytes(html, "utf8"))


		return

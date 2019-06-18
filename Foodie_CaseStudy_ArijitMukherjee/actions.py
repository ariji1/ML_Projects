from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
import zomatopy
import json
import re
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

resrnt_df10 = pd.DataFrame()

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"00a997bbeedd13f3f1d0bae2d5ac19a7"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		cuisine = cuisine.lower()
		price = tracker.get_slot('price')
		if price == 'low':
			cost_to_filer_min = 0
			cost_to_filer_max = 300
		elif price == 'mid':
			cost_to_filer_min = 301
			cost_to_filer_max = 700
		elif price == 'high':
			cost_to_filer_min = 701
			cost_to_filer_max = 9999
			
		cols = ['restaurant name', 'restaurant address', 'avg. budget for two', 'zomato rating']
		resrnt_df = pd.DataFrame(columns = cols)
		location_detail=zomato.get_location(loc, 1)
			
		
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		
		cuisines_dict={'american':1,'chinese':25,'mexican':73,'italian':55,'north indian':50,'south indian':85}
		
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)),15)
		response=""
		d = json.loads(results)
		if d['results_found'] == 0:
			response= "no results"			
		else:	
			for restaurant in d['restaurants']:
				curr_res = {'zomato rating':restaurant['restaurant']["user_rating"]["aggregate_rating"],'restaurant name':restaurant['restaurant']['name'],'restaurant address': restaurant['restaurant']['location']['address'], 'avg. budget for two': restaurant['restaurant']['average_cost_for_two']}		
				if (curr_res['avg. budget for two'] >= cost_to_filer_min) and (curr_res['avg. budget for two'] <= cost_to_filer_max):						
						resrnt_df.loc[len(resrnt_df)] = curr_res		
		 
		resrnt_df = resrnt_df.sort_values(['zomato rating','avg. budget for two'], ascending=[False,True])
		global resrnt_df10
		resrnt_df10 = resrnt_df.head(10)	
		
		resrnt_df = resrnt_df.head(5)
		resrnt_df = resrnt_df.reset_index(drop=True)
		resrnt_df.index = resrnt_df.index.map(str)

		
		if len(resrnt_df) != 0:
			response = "Showing you top rated restaurants: \n"
			for index, row in resrnt_df.iterrows():			    
				response = response+ index + ". Found \""+ row['restaurant name']+ "\" in "+ row['restaurant address']+" has been rated "+ row['zomato rating']+"\n"
		else:
			response = 'Found 0 restaurants in given price range'
		
		dispatcher.utter_message(response)
		return [SlotSet('price',price),SlotSet('location',loc)]
		
class ActionValidatePrice(Action):
	def name(self):
		return 'action_validate_price'
		
	def run(self, dispatcher, tracker, domain):
		cost_queried = tracker.get_slot('price')
		if cost_queried.find('300') != -1 and cost_queried.find('700') == -1 :
			return[SlotSet('price', 'low')]
		elif cost_queried.find('700') != -1 and cost_queried.find('300') == -1 :
			return[SlotSet('price', 'high')]
		else:
			return[SlotSet('price', 'mid')]

class ActionValidateEmail(Action):
	def name(self):
		return 'action_validate_email'
		
	def run(self, dispatcher, tracker, domain):
		pattern = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
		email_check = tracker.get_slot('email')
		if email_check is not None:
			if re.search("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",email_check):
				return[SlotSet('email',email_check)]
			else:
				dispatcher.utter_message("This is not a valid email")
				return[SlotSet('email',None)]
		else:
			dispatcher.utter_message("this is not a valid email")
			return[SlotSet('email', None)]	

class ActionSendEmail(Action):
	def name(self):
		return 'action_email'		
    		
	def run(self, dispatcher, tracker, domain):
		
		global resrnt_df10
		email = tracker.get_slot('email')
		gmail_user = 'autobot.test101@gmail.com'  
		gmail_password = 'forupgrad1234' 
		sent_from = gmail_user  
		to = str(email)
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Important -- Foodie friend here"
		msg['From'] = gmail_user
		msg['To'] = to
		if len(resrnt_df10) != 0:
			resrnt_df10.reset_index(drop=True)
			resrnt_df10.index.map(str)
			html = """
			<html>
			<head>			
			</head>
			<body>
			<p>Hi!</p>
			<p>Foddie friend here , Please find the resturants below.</p>			
			"""
			html = html+resrnt_df10.to_html()
		
		part2 = MIMEText(html, 'html')
		msg.attach(part2)
		server = smtplib.SMTP_SSL('smtp.gmail.com',465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, msg.as_string())
		server.close()
		dispatcher.utter_message("Email Sent to you")
		return [SlotSet('email',email)]


class ActionValidateLocation(Action):
	def name(self):
		return 'action_validate_location'
		
	def run(self, dispatcher, tracker, domain):
		list_loc = ["ahmedabad","bangalore","chennai","delhi","hyderabad","kolkata","mumbai","pune","agra","ajmer","aligarh","allahabad","amravati","amritsar",
					"asansol","aurangabad","bareilly","belgaum","bhavnagar","bhiwandi","bhopal","bhubaneswar","bikaner","bokaro steel city","chandigarh","coimbatore",
					"cuttack","dehradun","dhanbad","durg-bhilai nagar","durgapur","erode","faridabad","firozabad","ghaziabad","gorakhpur","gulbarga","guntur","gurgaon",
					"guwahati","gwalior","hubli-dharwad","indore","jabalpur","jaipur","jalandhar","jammu","jamnagar","jamshedpur","jhansi","jodhpur","kannur","kanpur","kakinada",
					"kochi","kottayam","kolhapur","kollam","kota","kozhikode","kurnool","lucknow","ludhiana","madurai","malappuram","mathura","goa","mangalore","meerut",
					"moradabad","mysore","nagpur","nanded","nashik","nellore","noida","palakkad","patna","pondicherry","raipur","rajkot","rajahmundry","ranchi","rourkela",
					"salem","sangli","siliguri","solapur","srinagar","sultanpur","surat","thiruvananthapuram","thrissur","tiruchirappalli","tirunelveli","tiruppur","ujjain",
					"vijayapura","vadodara","varanasi","vasai-virar city","vijayawada","visakhapatnam","warangal"]
		loc = tracker.get_slot('location')
		if loc is not None:
			if loc.lower() in list_loc:
				return[SlotSet('location',loc)]
			else:
				dispatcher.utter_message("Sorry we do not operate in this area yet. try some other location")
				return[SlotSet('location',None)]
		else:
			dispatcher.utter_message("Sorry we do not operate in this area yet. try some other location")
			return[SlotSet('location', None)]
			
			
class ActionResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("location", None),SlotSet("email", None),SlotSet("cuisine", None),SlotSet("price", None)]
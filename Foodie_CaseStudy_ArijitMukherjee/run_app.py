from rasa_core.channels import HttpInputChannel
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_slack_connector import SlackInput


nlu_interpreter = RasaNLUInterpreter('./models/nlu/default/restaurantnlu')
agent = Agent.load('./models/dialogue', interpreter = nlu_interpreter)

input_channel = SlackInput('xoxp-521318622976-521888364628-522065453826-443f6bd3add2ef39df405000c5e755c6', #app verification token
							'xoxb-521318622976-522266667093-nwnPzjBvULZgZjqZbZIN73jf', # bot verification token
							'ZaStfqzk2pS5OSmwQ5M7RLkL', # slack verification token
							True)

agent.handle_channel(HttpInputChannel(5004, '/', input_channel))
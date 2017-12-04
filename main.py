from message import MessageParser
from analyzer import Analyzer
from colorama import init, deinit, Fore, Back, Style

# Main function
def main():
  # Init colorama
  init(autoreset=True)

  # Create a new message list
  messages = []
  #messages += MessageParser.read('corpus/2014-01-24 (Atlantisch-Helekronische Liga).html.messages')
  #messages += MessageParser.read('corpus/2014-02-12 (Liga Atlantica).html.messages')
  #messages += MessageParser.read('corpus/2014-05-03 (Atlantische Liga).html.messages')
  #messages += MessageParser.read('corpus/2014-09-21 (Atlantische Liga zonder Chris).html.messages')
  #messages += MessageParser.read('corpus/2016-06-13 (Existentialistische Liga).html.messages')
  #messages += MessageParser.parse_whatsapp_txt('corpus/WhatsApp-chat met S p i r i t u a l e l m o.txt')
  messages += MessageParser.parse_whatsapp_txt('corpus/WhatsApp-chat met Atlantisch Ligaatje.txt')
    
  # Analyze the messages
  analyzer = Analyzer(messages)
  analyzer.analyze()
  analyzer.print_report()
    
  # De-init colorama
  deinit()
  
  
# Execute the main functon
if __name__ == '__main__':
  main()
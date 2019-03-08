import colorama
from message import MessageParser
from analyzer import Analyzer
from cmd import Cmd
from colorama import Fore, Back, Style


# Command class
class Prompt(Cmd):
  # Constructor
  def __init__(self, messages, analyzer):
    Cmd.__init__(self)

    self.messages = messages
    self.analyzer = analyzer

  # Quit the program
  def do_exit(self, args):
    """Quit the analyzer."""
    return True

  #Print
  def do_print(self, args):
    self.analyzer.print_report()


# Main method
def main():
  # Init colorama
  colorama.init(autoreset=True)

  # Load the messages
  messages = []
  messages += MessageParser.read('corpus/2013-09-16 tot 2014-01-24.messages')
  messages += MessageParser.read('corpus/2014-01-26 tot 2014-02-12.messages')
  messages += MessageParser.read('corpus/2014-02-07 tot 2014-03-03.messages')
  messages += MessageParser.read('corpus/2014-03-03 tot 2014-05-03.messages')
  messages += MessageParser.read('corpus/2014-05-03 tot 2014-09-20.messages')
  messages += MessageParser.read('corpus/2014-09-20 tot 2016-06-13.messages')
  messages += MessageParser.read('corpus/2016-06-13 tot 2018-01-23.messages')

  # Analyze the messages
  analyzer = Analyzer(messages)
  analyzer.analyze()

  # Use the prompt
  prompt = Prompt(messages,analyzer)
  prompt.prompt = '> '
  prompt.cmdloop('\nDone loading! List available commands with "help" or detailed help with "help cmd".')

  # De-init colorama
  colorama.deinit()

# Execute the main method
if __name__ == '__main__':
  main()

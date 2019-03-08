import re
import random
from message import Message
from collections import Counter
from markovify import Chain
from colorama import Fore, Back, Style


# Print iterations progress
def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
  """
  Call in a loop to create terminal progress bar
  @params:
    iteration   - Required  : current iteration (Int)
    total       - Required  : total iterations (Int)
    prefix      - Optional  : prefix string (Str)
    suffix      - Optional  : suffix string (Str)
    decimals    - Optional  : positive number of decimals in percent complete (Int)
    length      - Optional  : character length of bar (Int)
    fill        - Optional  : bar fill character (Str)
  """
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + '-' * (length - filledLength)
  print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
  # Print New Line on Complete
  if iteration == total: 
    print()
    
    
# User class (for convenient storing of results)
class User:

  # Constructor
  def __init__(self, name):
    self.name = name
    
    self.message_count = Counter()
    self.total_message_count = 0
    self.word_count = Counter()
    self.total_word_count = 0
    self.unique_word_count = Counter()
    self.tokens = []
    self.markov_chain = None
    
  # Create a markov chain from the messages
  def create_markov_chain(self):
    # Set the markov chain
    self.markov_chain = Chain(self.tokens,state_size=2)
    
    
# Analyzer class
class Analyzer:

  # Tokenizer pattern
  split_pattern = re.compile(r'[\s+.,!?:;]+(?=\w)',re.UNICODE)

  # Constructor
  def __init__(self, messages):
    self.messages = messages
    
    self.users = {}
    self.message_count = Counter()
    self.total_message_count = 0
    self.word_count = Counter()
    self.total_word_count = 0
    
  # Analyze the corpus
  def analyze(self):  
    # Iterate over the messages
    printProgressBar(0,len(self.messages),prefix = 'Analyzing corpus...',length = 50)
    for index, message in enumerate(self.messages):
      # Add the user if not yet present
      if message.user not in self.users:
        user = self.users[message.user] = User(message.user)
      else:
        user = self.users[message.user]
        
      # Tokenize the message text if any
      if message.text:
        # Update message count
        user.message_count[message.text.lower()] += 1
      
        # Split the text in tokens
        tokens = [token.lower() for token in self.split_pattern.split(message.text)]
                
        # If there are tokens
        if tokens:
          # Add the tokens to the counter
          user.word_count.update(tokens)
          
          # Add the tokens to the user
          user.tokens.append(tokens)
      
      # Print progress bar      
      if index % 1000 == 0 or index + 1 == len(self.messages):
        printProgressBar(index + 1,len(self.messages),prefix = 'Analyzing corpus...',length = 50)
        
    # Handle users
    printProgressBar(0,len(self.users),prefix = 'Creating users and Markov chains...',length = 50)
    for index, user in enumerate(self.users.values()):
      # Handle own variables
      user.total_message_count = sum(user.message_count.values())
      user.total_word_count = sum(user.word_count.values())
      
      # Update the total message and word count
      self.message_count.update(user.message_count)
      self.word_count.update(user.word_count)
      
      # Search for unique words (words user said - words other users said)
      user.unique_word_count = Counter(user.word_count)
      for other_user in self.users.values():
        if user != other_user:
          # Subtract words
          user.unique_word_count -= other_user.word_count
          
      # Create a markov chain for this user
      user.create_markov_chain()
          
      # Print progress bar
      printProgressBar(index + 1,len(self.users),prefix = 'Creating users and Markov chains...',length = 50)
      
    # Handle own variables
    self.total_message_count = sum(self.message_count.values())
    self.total_word_count = sum(self.word_count.values())
    
      
  # Generate a new corpus based on the markov chains
  def generate(self, n=30):
    # Create a new message list
    messages = []
    
    # Create a list representing the user probability
    user_probability = Counter({user: user.total_message_count for user in self.users.values()})
  
    # Loop for n times
    printProgressBar(0,n,prefix = 'Generating corpus...',length = 50)
    for i in range(n):
      # Choose a user based on chance
      user = random.choice(list(user_probability.elements()))
      
      # Generate a sentence
      text = ' '.join(user.markov_chain.walk()).capitalize()
      
      # Create a message and append it
      message = Message(user.name,None,text)
      messages.append(message)
      
      # Print progress bar
      printProgressBar(i + 1,n,prefix = 'Generating corpus...',length = 50)
    
    # Return the messages
    return messages
        
  # Print the report
  def print_report(self):
    # Print title and total words
    print()
    print(Back.GREEN + Fore.BLACK + 'Analysis report for {:,} messages'.format(self.total_message_count).upper())
    print('Total word count: ' + Fore.CYAN + '{:,}'.format(self.total_word_count))
    print()
    
    # Print the most common messages
    print(Back.GREEN + Fore.BLACK + 'Most common messages')
    for message, count in self.message_count.most_common(10):
      print((Fore.CYAN + '{:,}' + Fore.RESET + 'x ' + Style.BRIGHT + Fore.RED + '{}' + Style.RESET_ALL + ' ({:.2f}%)').format(count,message,100 * count / self.total_message_count))
    print()
        
    # Print the most common words
    print(Back.GREEN + Fore.BLACK + 'Most common words')
    for word, count in self.word_count.most_common(20):
      print((Fore.CYAN + '{:,}' + Fore.RESET + 'x ' + Style.BRIGHT + Fore.RED + '{}' + Style.RESET_ALL + ' ({:.2f}%)').format(count,word,100 * count / self.total_word_count))
    print()
  
    # Print the users and most common words
    n = 10
    print(Back.GREEN + Fore.BLACK + 'Users in the corpus, sorted by word count')
    # Get the sorted user keys
    sorted_user_names = sorted(self.users.keys(),key = lambda user: self.users[user].total_word_count, reverse=True)
    for user_name in sorted_user_names:
      # Get the user
      user = self.users[user_name]
    
      # Print total word count
      print((Fore.GREEN + '{}:').format(user.name))
      print(('  ' + Fore.CYAN + '{:,}' + Fore.RESET + ' words ({:.2f}%),' + Fore.CYAN + '{:,}' + Fore.RESET + ' messages ({:.2f}%), avg. ' + Fore.CYAN + '{:.2f}' + Fore.RESET + ' words per message').format(user.total_word_count,100 * user.total_word_count / self.total_word_count,user.total_message_count,100 * user.total_message_count / self.total_message_count,user.total_word_count / user.total_message_count))
      
      # Print most common messages
      messages = ", ".join([(Style.BRIGHT + Fore.RED + '{}' + Style.RESET_ALL).format(message) for message, count in user.message_count.most_common(5)])
      print('  Most common messages: {}'.format(messages))
      
      # Print most common words
      words = ', '.join([(Style.BRIGHT + Fore.RED + '{}' + Style.RESET_ALL).format(word) for word, count in user.word_count.most_common(n)])
      print('  Most common words: {}'.format(words))
      
      # Print unique words
      unique_words = ', '.join([(Style.BRIGHT + Fore.RED + '{}' + Style.RESET_ALL).format(word) for word, count in user.unique_word_count.most_common(n)])
      print('  Most common unique words: {}'.format(unique_words))
    print()
    
    # Generate a conversation
    generated_messages = self.generate(50)
    print((Back.GREEN + Fore.BLACK + 'Generated chat conversation ({} lines)').format(len(generated_messages)))
    for message in generated_messages:
      print(('<' + Fore.GREEN + '{}' + Fore.RESET + '> {}').format(message.user,message.text))
    print()

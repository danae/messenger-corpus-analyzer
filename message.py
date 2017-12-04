import io
import re
import os.path
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style

# Message class
class Message:
  
  # Constructor
  def __init__(self, user, text):
    self.user = user
    self.text = text
    
  # Read a message from a string
  @classmethod
  def read_string(cls, string):
    # Match the string to the message pattern
    pattern = re.compile(r'\<(.+?)\> (.*)',re.UNICODE)
    matches = pattern.match(string)
    
    # If it matches, create a new message, otherwise None
    return cls(matches.group(1),matches.group(2)) if matches else None
    
  # Write the message to a string
  def write_string(self):
    # Return a string in the message format
    return '<{}> {}'.format(self.user,self.text if self.text else '')
    
  # Convert to string
  def __str__(self):
    return self.write_string()
    

# Message parser class
class MessageParser:
  
  # Read messages from a file
  @staticmethod
  def read(file_name):
    # Create a new message list
    messages = []
  
    # Open the file
    print((Fore.GREEN + 'Reading file ' + Style.BRIGHT + '{}' + Style.RESET_ALL + Fore.GREEN + '...').format(file_name))
    with io.open(file_name,mode = 'r',encoding='utf-8') as file:
      # Iterate over all the files
      for index, line in enumerate(file):
        # Try to read the line as a message
        message = Message.read_string(line)
        
        # If succeeded, add it to the corpus
        if message:
          messages.append(message)
        # Otherwise throw an error
        else:
          raise Exception('Invalid message format in line {}: "{}"'.format(index + 1,line))
          
    # Return the messages
    return messages
    
  # Write messages to a file
  @staticmethod
  def write(file_name, messages):
    # Open the file
    print((Fore.RED + 'Writing file ' + Style.BRIGHT + '{}' + Style.RESET_ALL + Fore.RED + '...').format(file_name))
    with io.open(file_name,mode = 'w', encoding='utf-8') as file:
      # Iterate over all the messages
      for message in messages:
        # Write to the file
        file.write(message.write_string() + '\n')
    
  # Parse a Facebook Backup HTML file into a message list
  @staticmethod
  def parse_facebook_html(html_file_name):
    # Check if there is a messages file for us available to speed up things
    messages_file_name = '{}.messages'.format(html_file_name)
    if os.path.isfile(messages_file_name):
      # Read the message file instead
      print(('Found messages file ' + Style.BRIGHT + '{}' + Style.RESET_ALL + '!').format(messages_file_name))
      return MessageParser.read(messages_file_name)
  
    # Create a new message list
    messages = []
  
    # Open the file
    print((Fore.GREEN + 'Reading file ' + Style.BRIGHT + '{}' + Style.RESET_ALL + Fore.GREEN + '...').format(html_file_name))
    with io.open(html_file_name,mode = 'r',encoding = 'utf-8') as html_file:
      # Parse the string or file
      html = BeautifulSoup(html_file,'lxml')
      print((Fore.GREEN + 'Parsing HTML document of with title ' + Style.BRIGHT + '{}' + Style.RESET_ALL + Fore.GREEN + '...').format(html.title.string))
    
      # Iterate over all children of <div class="thread">
      thread = html.find('div',class_ = 'thread')
      if thread is None:
        raise 'No <div class="thread"> tag found, skipping'
    
      current_message = None    
      for child in thread.children:      
        # Check for <div class="message">
        if child.name == 'div' and 'message' in child['class']:
          # Add the old message is any
          if current_message:
            messages.append(current_message)
          
          # Create a new message
          user = child.select_one('span.user').string
          current_message = Message(user,None)
        
        # Check for <p>
        elif child.name == 'p':
          # Set the message text if any
          if current_message:
            current_message.text = child.string.replace('\n',' ') if child.string else None
            
      # Add the latest message if any
      if current_message:
        messages.append(current_message)
            
      # Revert the messages list
      messages.reverse()
      
      # Write the messages to a file to speed up future lookups
      print(('Writing messages to ' + Style.BRIGHT + '{}' + Style.RESET_ALL + ' to speed up future lookups').format(messages_file_name))
      MessageParser.write(messages_file_name,messages)
      
    # Return the messages
    return messages
    
  # Parse a WhatsApp "e-mail chat" TXT file into a message list
  @staticmethod
  def parse_whatsapp_txt(txt_file_name):
    # Check if there is a messages file for us available to speed up things
    messages_file_name = '{}.messages'.format(txt_file_name)
    if os.path.isfile(messages_file_name):
      # Read the message file instead
      print(('Found messages file ' + Style.BRIGHT + '{}' + Style.RESET_ALL + '!').format(messages_file_name))
      return MessageParser.read(messages_file_name)
  
    # Create a new message list
    messages = []
    
    # Initialize other variables
    text_pattern = re.compile(r'\d{2}-\d{2}-\d{2}, \d{2}:\d{2} - (.+?): (.+)')
  
    # Open the file
    print((Fore.GREEN + 'Reading file ' + Style.BRIGHT + '{}' + Style.RESET_ALL + Fore.GREEN + '...').format(txt_file_name))
    with io.open(txt_file_name,mode = 'rb') as txt_file:
      # Iterate over the lines
      for line in txt_file:
        # Convert to unicode
        line = line.decode('utf-8')
        
        # Try to parse the line
        matches = text_pattern.match(line)
        if matches:
          # Create a new message and store it
          user = matches.group(1)
          text = matches.group(2)
          # If the text is media, then continue
          if '<Media weggelaten>' in text or 'heeft het onderwerp gewijzigd' in user:
            continue
          message = Message(user,text)
          messages.append(message)
          
      # Write the messages to a file to speed up future lookups
      print(('Writing messages to ' + Style.BRIGHT + '{}' + Style.RESET_ALL + ' to speed up future lookups').format(messages_file_name))
      MessageParser.write(messages_file_name,messages)
      
    # Return the messages
    return messages
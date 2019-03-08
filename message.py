import io
import re
import os.path
from shutil import copyfile
from datetime import datetime
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style


# Date patterns
months = ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december']
date_pattern = re.compile(r'\w+ (\d{1,2}) (\w+) (\d{1,4}) om (\d{1,2}):(\d{2})')

# Function to parse a date
def parse_date(date_string):
  # Match the date string with the date pattern
  matches = date_pattern.match(date_string)
  
  # If it matches create a new datetime, otherwise None
  if matches:
    # Parse the date
    year = int(matches.group(3))
    month = months.index(matches.group(2)) + 1
    day = int(matches.group(1))
    hour = int(matches.group(4))
    minute = int(matches.group(5))
    # Return a new datetime object
    return datetime(year,month,day,hour,minute)
  else:
    return None
    

# Message class
class Message:
  
  # Message string pattern    
  message_pattern = re.compile(r'(\[(\d{4})-([01]\d)-([0-3]\d)T([0-2]\d):([0-5]\d)(?::([0-5]\d))?\])?\s*\<(.+?)\>\s*(.*)',re.UNICODE)
  message_format = '[{0:%Y-%m-%dT%H:%M}] <{1}> {2}'
  
  # Constructor
  def __init__(self, user, date = None, text = ''):
    self.user = user
    self.date = date
    self.text = text
    
  # Read a message from a string
  @classmethod
  def read_string(cls, string):
    # Match the string to the message pattern
    matches = cls.message_pattern.match(string)
    
    # If it matches, create a new message, otherwise None
    if matches:
      # Get the user and group
      user = matches.group(8)
      text = matches.group(9)
      
      # Check if there is a date
      if matches.group(1):
        # Parse the date
        year = int(matches.group(2))
        month = int(matches.group(3))
        day = int(matches.group(4))
        hour = int(matches.group(5))
        minute = int(matches.group(6))
        second = int(matches.group(7)) if matches.group(7) else 0
        # Create a datetime object
        date = datetime(year,month,day,hour,minute,second)
      
      # Return a new message
      return cls(user,date or None,text)
      
    # No match
    else:
      return None
    
  # Write the message to a string
  def write_string(self):
    # Return a string in the message format
    return self.message_format.format(self.date,self.user,self.text if self.text else '')
    
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
  def parse_html(html_file_name):
    # Check if there is a messages file for us available to speed up things
    messages_file_name = '{}.messages'.format(os.path.splitext(html_file_name)[0])
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
        raise RuntimeError('No <div class="thread"> tag found, skipping')
      current_message = None    
      for child in thread.children:      
        # Check for <div class="message">
        if child.name == 'div' and 'message' in child['class']:
          # Add the old message is any
          if current_message:
            messages.append(current_message)
          
          # Create a new message
          user = child.select_one('span.user').string
          date_string = child.select_one('span.meta').string
          date = parse_date(date_string)
          current_message = Message(user,date)
        
        # Check for <p>
        elif child.name == 'p':
          # Check if we have a current message
          if not current_message:
            continue
          
          # Check if it contains an image
          if child.find('img'):
            src = child.select_one('img')['src']
            current_message.text += (' ' if current_message.text else '') + '<image:{}>'.format(os.path.basename(src))
            
          # Check if it contains audio
          elif child.find('audio'):
            src = child.select_one('audio')['src']
            current_message.text += (' ' if current_message.text else '') + '<image:{}>'.format(os.path.basename(src))
          
          # Set the message text if any
          else:
            if child.string and child.string.strip():
              current_message.text += (' ' if current_message.text else '') + child.string.replace('\n',' ')
            
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

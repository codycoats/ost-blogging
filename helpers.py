
import re

#Takes a string of input and returns list of tags
#input: "#tag1 #tag2 #tag3"
#output: ['#tag1', '#tag2', '#tag3']
def parse_tags(string):

  tags = re.findall(r'\S+', string)

  return tags

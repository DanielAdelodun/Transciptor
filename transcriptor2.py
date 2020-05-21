#!/usr/bin/python3

# The star of the show.
from bs4 import BeautifulSoup
import json

# Structure to store individual messages.
class Message:
    def __init__(self):
        self.message_number = None
        self.author = ""
        self.staff = False
        self.response = ""
        self.parent = {"author": "", "text": "", "message_number": None}
        self.children = []
        self.full = None

    def toJSON(self):
        dummy_message = Message()
        dummy_message.message_number = self.message_number
        dummy_message.author = self.author
        dummy_message.staff = self.staff
        dummy_message.response = self.response
        dummy_message.parent = self.parent
        dummy_message.children = self.children
        # The whole point of this weird dummy nonesense. 
        # json and bs4 don't play nice together, apparently.
        dummy_message.full = str(self.full)
        return json.dumps(dummy_message, default=lambda o: o.__dict__)

# List to store all messages.
messages = []

# HTML file saved to this location...
with open("/home/daniel/Documents/HTML-of-site.html") as f:

    contents = f.read()

    # Find the actual chat within the webpage.
    soup = BeautifulSoup(contents, 'lxml')
    chat_body = soup.find("div", attrs={"data-test-id" : "chat-body-scroll"})

    # Breakdown the chat into a list of the HTML elements that form each message. 
    # Each message is a HTML 'li' (list item).
    message_lis = chat_body.find_all("li")

    # Extract the important information from each message_li.
    for i in range(len(message_lis)):
        # Add a container for the current message to the list of messages.
        messages.append(Message())
        message_li = message_lis[i]
        messages[i].full = message_li 
        messages[i].message_number = i + 1

        # Find students name.
        author = message_li.find("div", class_="_1Tmb")
        if author == None:
            messages[i].staff = True
        if not messages[i].staff:
            author = author.getText()
            messages[i].author = author

        # Find staff name.
        message_bubble = message_li.find("div", attrs={"data-test-id" : "chat-message-bubble"})
        name_container = message_bubble.find("div", class_="_31Bt")
        if not name_container:
            author = "Self"
            messages[i].author = author
        elif messages[i].staff:
            name_container.find("svg").decompose()
            author = name_container.getText()
            messages[i].author = author

        # Get original question, if this is a reply.
        blockquote = message_bubble.find("blockquote")
        if blockquote:
            author = blockquote.find("span", attrs={"data-test-id" : "reply-author-highlight"})
            author = author.getText()
            text = blockquote.find("div", attrs={"data-test-id" : "quote-text"})
            text = text.getText()
            messages[i].parent["author"] = author
            messages[i].parent["text"] = text
            blockquote.decompose()

        # Get message body.
        response = message_bubble.find("span")
        response = response.getText()
        messages[i].response = response

    # Now we've got a list of messages, but no cross-references
    # Let's figure out what's a reply, and what's been replied to
    # First, get everyone's parent
    for message in messages:
        if message.parent["text"]:
            for compare in messages:
                # There is a bug here; if two messages match up the first 40 chars -> confusion.
                if compare.response[:40] == message.parent["text"][:40]:
                    message.parent["message_number"] = compare.message_number
                    break

    # Find all messages which consider the current message a parent (i.e. find Children).
    for message in messages:
        for compare in messages:
            if compare.parent["message_number"] == message.message_number:
                message.children.append(compare.message_number)

        print("Message number:", message.message_number)
        print("Author:", message.author)
        print("Faculty Member:", message.staff)
        print('--')
        print()
        print("Response:")
        print(message.response)
        print('--')
        print()
        print("Parent:", message.parent["message_number"], "(", message.parent["text"], ")")
        print("Children:", message.children)
        print('---------------------------------------------------------------------------')
        print()


    # uncomment to manually inspect all messages from students which have no reply.
    #for message in messages:
        #if message.staff or message.children:
            #continue
        #print("Message number:", message.message_number)
        #print("Author:", message.author)
        #print("Faculty Member:", message.staff)
        #print('--')
        #print()
        #print("Response:")
        #print(message.response)
        #print('--')
        #print()
        #print("Parent:", message.parent["message_number"], "(", message.parent["text"], ")")
        #print("Children:", message.children)
        #print('---------------------------------------------------------------------------')
        #print()
   
    # A function to print a given message at a given indentation 'level'
    # Is there a more efficient way to do this? Probably.
    def print_message(message, level):
        for i in range(level):
            print("    ", end=" ")
        print("Message number:", message.message_number)
        for i in range(level):
            print("    ", end=" ")
        print("Author:", message.author)
        for i in range(level):
            print("    ", end=" ")
        print("Faculty Member:", message.staff)
        for i in range(level):
            print("    ", end=" ")
        print('--')
        for i in range(level):
            print("    ", end=" ")
        print()
        for i in range(level):
            print("    ", end=" ")
        print("Response:")
        for i in range(level):
            print("    ", end=" ")
        print(message.response)
        for i in range(level):
            print("    ", end=" ")
        print('--')
        for i in range(level):
            print("    ", end=" ")
        print()
        for i in range(level):
            print("    ", end=" ")
        print("Parent:", message.parent["message_number"], "(", message.parent["text"], ")")
        for i in range(level):
            print("    ", end=" ")
        print("Children:", message.children)
        for i in range(level):
            print("    ", end=" ")
        print('---------------------------------------------------------------------------')
        for i in range(level):
            print("    ", end=" ")
        print()


    # Given a list of messages, and a starting message within that list,
    # Print the 'Q&A thread' starting at the message.
    def print_thread(message_list, entry_point, level):
        message = message_list[entry_point - 1]
        if level == 0:
            if message.staff or message.parent["message_number"]:
                return
        print_message(message, level)
        level = level + 1
        for child in message.children:
            print_thread(message_list, child, level)

    for i in range(len(messages)):
        print_thread(messages, i+1, 0)

    for i in range(len(messages)):
        print(messages[i].toJSON())

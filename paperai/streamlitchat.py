from datetime import datetime
import json
from paperai import paperai
import openai as oa
import tiktoken as tt

class Chat:
    def __init__(self, created=None, model='gpt-3.5-turbo', context=None, temperature=0.7, top_p=1.0, max_tokens=512,
                 max_context_tokens=4096, frequency_penalty=0.0, presence_penalty=0.0):
        self.created = int(datetime.now().timestamp()) if created is None else created
        self.model = model
        self.encoder = tt.encoding_for_model(model)
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.max_context_tokens = max_context_tokens - max_tokens
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        self.messages = {
            'role': 'user',
            'content': "",
            'next': [],
            'selected': None
        }

        if context is not None:
            self.messages['content'] = context

        self.messages['context_tokens'] = 0
        self.count_tokens(self.messages)

    def save(self, filename=None, folder='chats/'):
        if filename is None:
            filename = '%s.json' % self.created

        with open(folder + filename, 'w') as f:
            json.dump(self, f, default=lambda o: {k: v for k, v in o.__dict__.items() if k not in ('encoder', )},
                      sort_keys=True)

    @staticmethod
    def load(filename, folder='chats/'):
        with open(folder + filename, 'r') as f:
            chat = Chat()
            chat.__dict__ = json.load(f)

        chat.encoder = tt.encoding_for_model(chat.model)

        return chat

    def get_selected_path(self, length=None):
        path = [self.messages]

        while path[-1]['selected'] is not None and (length is None or len(path) < length):
            path.append(path[-1]['next'][path[-1]['selected']])

        return path

    def add_message(self, content, index=None, role='user'):
        current_tree = self.messages

        if index is None:
            while current_tree['selected'] is not None:
                current_tree = current_tree['next'][current_tree['selected']]
        else:
            for i in range(index - 1):
                current_tree = current_tree['next'][current_tree['selected']]

        current_tree['next'].append({'role': role,
                                     'content': content,
                                     'tokens': len(self.encoder.encode(content)) + 5,
                                     'context_tokens': current_tree['context_tokens'] + current_tree['tokens'],
                                     'next': [],
                                     'selected': None})
        current_tree['selected'] = len(current_tree['next']) - 1

    def delete_message(self, index):
        current_tree = self.messages

        for i in range(index - 1):
            current_tree = current_tree['next'][current_tree['selected']]

        del current_tree['next'][current_tree['selected']]
        current_tree['selected'] -= 1
        current_tree['selected'] = (None if len(current_tree['next']) == 0 else 0)\
            if current_tree['selected'] == -1 else current_tree['selected']

    def count_tokens(self, tree):
        tree['tokens'] = len(self.encoder.encode(tree['content'])) + 5

        for n in tree['next']:
            n['context_tokens'] = tree['context_tokens'] + tree['tokens']
            self.count_tokens(n)

    def generate(self, index=None):
        if index is None:
            path = self.get_selected_path()
        else:
            path = self.get_selected_path(length=index)

        i = 1
        token_count = self.messages['tokens']
        for i, m in list(enumerate(path))[1:][::-1]:
            if token_count + m['tokens'] <= self.max_context_tokens:
                token_count += m['tokens']
            else:
                i += 1
                break
        
        # print(f"THE MESSAGE ====>>>>>> {len(path)} and m is {path[0]}")
        result_dict = self.chat_completion([self.messages] + path[i:])
        if not result_dict:
            self.add_message("ERROR", index=index, role="assistant")
        else:
            result_fmt = result_dict.get('response')
            metadata = result_dict.get("metadata")
        
        # print(f"Final Result {result}")
        if metadata:
            source = metadata.get("source")
            page = metadata.get("page")
            content = metadata.get("content")
            result_fmt += f'\n ## PDF REFERENCE \n'
            result_fmt += f" <code>{source} {page}</code> \n"
            result_fmt += f" :pencil: :green{content}"
            # __PDF CONTENT:__
            # ```
            # {metadata.get("source")} {metadata.get("page")}```
            # _{metadata.get("content")}_
            # """
        self.add_message(result_fmt, index=index, role="assistant")
        # self.add_message(self.chat_completion([self.messages] + path[i:]), index=index, role='user')

    def chat_completion(self, path):
        conversation = {
            'engine': "gpt-35-turbo",
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'messages': [{'content': m['content']} for m in path]
        }

        all_messages = conversation['messages']
        return paperai.execute(all_messages[len(all_messages)-1]['content'])
        # return conversation['messages']

        # response = oa.ChatCompletion.create(**conversation)

        # # response = oa.ChatCompletion.create(
        # #         engine="gpt-35-turbo", # The deployment name you chose when you deployed the ChatGPT or GPT-4 model.
        # #         messages = [{'role': m['role'], 'content': m['content']} for m in path],
        # #         temperature=.7,
        # #         max_tokens=self.max_tokens,
        # #     )
        # response['choices'][0]['message']['content'] = response['choices'][0]['message']['content'].strip()

        # return response['choices'][0]['message']['content']
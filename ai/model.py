import json
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import List, Tuple

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


load_dotenv()


class Model:
    @staticmethod
    def _generate_prompt(message_history: List[str], current_deadlines: list[tuple[str, datetime]]):
        text_current_deadlines = []
        for i in range(len(current_deadlines)):
            text_current_deadlines.append((current_deadlines[i][0], current_deadlines[i][1].strftime("%d.%m.%Y %H:%M:%S")))

        message_text = "\n\n--- СЛЕДУЮЩЕЕ СООБЩЕНИЕ ---\n\n".join(message_history)

        current_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(current_dir, "prompt.txt")
        with open(prompt_path, "r") as f:
            prompt = f.read().format(
                message_text=message_text,
                current_deadlines=json.dumps(text_current_deadlines, ensure_ascii=False),
                current_date=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                year=datetime.now().year
            )

        return prompt

    def __init__(self, **kwargs):
        kwargs['credentials'] = kwargs.get('credentials', os.environ['GIGACHAT_TOKEN'])
        kwargs['scope'] = kwargs.get('scope', os.environ['GIGACHAT_SCOPE'])
        kwargs['verify_ssl_certs'] = kwargs.get('verify_ssl_certs', False)
        kwargs['model'] = kwargs.get('model', 'GigaChat-2')  # GigaChat Lite 2 работает сильно лучше первой версии

        self.model = GigaChat(**kwargs)

    async def get_response(self, message_history: List[str], current_deadlines: list[tuple[str, datetime]]) -> List[Tuple[str, datetime]]:
        PAYLOAD = Chat(
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=Model._generate_prompt(message_history, current_deadlines),
                ),
            ],
            update_interval=0.1,
        )

        answer = ""

        async for chunk in self.model.astream(PAYLOAD):
            answer += chunk.choices[0].delta.content

        print(answer)

        new_deadlines = json.loads(answer.replace('(', '[').replace(')', ']'))

        for i in range(len(new_deadlines)):
            new_deadlines[i] = (new_deadlines[i][0], datetime.strptime(new_deadlines[i][1], "%d.%m.%Y %H:%M:%S"))

        return new_deadlines

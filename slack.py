import logging
# 디버깅 로그
# logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_cleaner2 import *

# 환경변수에 넣어 전역으로 안전하게 한 번만 사용
# bot token이 잘못되었엇음 (아마 app token 사용한 듯)

os.environ['SLACK_BOT_TOKEN'] = "xoxb-5749189164226-5766390357650-jekmTWcZjf8U0PKeiNsXmfpX"
os.environ['APP_TOKEN'] = "xapp-1-A05P82KJCGY-5779019741233-47dfcf1bb2384550b05d59db432ea94ac127c2c90e26847e682661fb40f23d7cX"
os.environ['USER_AUTH_TOKEN'] = "xoxp-5749189164226-5772892368416-5764264840085-eb6a0a8fb6aa573154577d799723c556"

channel_name = "자동화-개발"

class SlackBot:
    def __init__(self):
        self.client = WebClient(os.environ['SLACK_BOT_TOKEN'])
        self.cleanear = SlackCleaner(os.environ['USER_AUTH_TOKEN'])

    # 특정 채널 이름으로 채널 id 얻기
    def get_channel_id(self, channel_name):
        result = self.client.conversations_list()
        channels = result.data['channels']

        channel = list(filter(lambda c: c["name"] == channel_name, channels))[0]
        channel_id = channel["id"]
        return channel_id
    
    # 케이스에 따른 챗봇 설정

    
    # 해당 채널에 메세지 보내기
    def send_message(self, channel_name, message):
        try:
            print('🔥 send message to %s' % channel_name)
            response = self.client.chat_postMessage(
                channel=channel_name,
                username="'재경이의 챗봇",
                icon_emoji=":robot_face:",
                text=message
            )

        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]

    # 봇이 스레드에 댓글 달아주기
    def post_message_in_thread(self, channel_id, message, text):
        result = self.client.chat_postMessage(
            channel=channel_id,
            thread_ts=message,
            text=text
        )

    # 특정 메세지 가져오기
    def get_message(self, channel_id, query):
        result = self.client.conversations_history(channel=channel_id)
        messages = result.data['messages']
        message = list(filter(lambda m : m['text'] == query , messages))[0]
        message_id = message["ts"]
        return message_id

    # 해당 채널 메세지 모두 삭제
    def delete_all_message(self, channel_name):
        try:
            # list of users
            self.cleanear.users

            # list of all channels
            self.cleanear.conversations

            for msg in self.cleanear.msgs(filter(match(channel_name), self.cleanear.conversations)):
                msg.delete(replies=True, files=True)

        except SlackApiError as e:
            assert e.response["error"]


myBot = SlackBot()
# channe_id = myBot.get_channel_id(channel_name)
# message = myBot.get_message(channe_id, "여기에 응원해줘!")
# myBot.send_message(channel_name=channe_id, message="Hi, Custom Message")
# myBot.post_message_in_thread(channe_id, message, '재경아 화이팅!')
myBot.delete_all_message("crypto")

from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from chatbot.response import ChatBotResponse
from chat.models import User, Message
from datetime import datetime


class ChatConsumer(AsyncJsonWebsocketConsumer):
    show_details = True
    chatbot = ChatBotResponse()
    username = ""

    """
    Called when the websocket is handshaking as part of initial connection.
    """
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'chat_%s' % self.user_id

        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # Accept the connection
        await self.accept()

    """
    Called when the Websocket closes for any reason.
    """
    async def disconnect(self, code):
        # Leave all the rooms we are still on
        await self.update_user_into_database()
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    """
    Called when we get a text frame. Channels will JSON-decode the payload for us and pass it as the first argument.
    """
    async def receive_json(self, content):
        if self.show_details:
            print(">>>>>>>>>>>>>>>> content: ", content)

        command = content.get("command", None)
        if command == "join":
            self.username = content.get("username", "Visitor")
            await self.update_user_into_database()
            await self.enter_website()
        elif command == "send":
            await self.send_room(content["message"])

    # -----Command helper methods called by receive_json----- #
    """
        Called by receive_json when someone enter the website
    """
    async def enter_website(self):

        # Chatbot welcome
        welcome = await ChatBotResponse.welcome(self.username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "room_id": self.user_id,
                "username": settings.BOT_NAME,
                "message": welcome,
            }
        )
        await self.insert_message_into_database(settings.BOT_NAME, welcome)

    """
    Called by receive_json when someone sends a message
    """
    async def send_room(self, message):

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "room_id": self.user_id,
                "username": self.username,
                "message": message,
            }
        )
        await self.insert_message_into_database(self.username, message)

        # Chat-bot response
        response = await self.chatbot.response(message, self.username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "room_id": self.user_id,
                "username": settings.BOT_NAME,
                "message": response,
            }
        )
        await self.insert_message_into_database(settings.BOT_NAME, response)

    # ----Get user and messages from database---- #
    async def update_user_into_database(self):

        query_set = User.objects.filter(user_id=self.user_id)
        date_now = datetime.now()
        if not query_set.exists():
            User.objects.create(user_id=self.user_id, username=self.username, email="", last_active_date=date_now)
        else:

            user = User.objects.get(user_id=self.user_id)
            if self.username.lower() != "visitor":
                user.username = self.username
            if date_now != user.last_active_date:
                user.last_active_date = date_now
            user.save()

    async def insert_message_into_database(self, name, content):
        Message.objects.create(user_id=self.user_id, name=name, content=content)

    async def get_messages_from_database(self):
        query_set = Message.objects.filter(user_id=self.user_id)
        if not query_set.exists():
            return ""
        for msg in query_set:
            print(msg)

    # ----Handlers for messages sent over the channel layer---- #
    """
    Called when someone has messaged our chat
    """
    async def chat_message(self, event):
        # Send a message down to the client
        if event["username"] != settings.BOT_NAME:
            await self.send_json(
                {
                    "msg_type": settings.MSG_TYPE_REQUEST,
                    "room": event["room_id"],
                    "username": event["username"],
                    "message": event["message"],
                },
            )
        else:
            await self.send_json(
                {
                    "msg_type": settings.MSG_TYPE_RESPONSE,
                    "room": event["room_id"],
                    "username": event["username"],
                    "message": event["message"],
                },
            )
import json
import logging
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Dict, Text, Any, List, Optional, Callable, Awaitable

from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage, flex_message)

logger = logging.getLogger(__name__)


class LineConnectorOutput(OutputChannel):
    """Output channel for Line."""

    @classmethod
    def name(cls) -> Text:
        return "line_assistant"

    def __init__(self,
                 channel_access_token: Optional[Text],
                 event: Any
                 ) -> None:
        self.line_client = LineBotApi(channel_access_token)
        self.reply_token = event.reply_token
        self.sender_id = event.source.user_id
        super().__init__()

    async def send_to_line(
            self,
            payload_object,
            **kwargs: Any) -> None:
        print('-------- SEND TO LINE -----------')
        try:
            if self.reply_token:
                self.line_client.reply_message(
                    self.reply_token,
                    messages=payload_object
                )
            else:
                self.line_client.push_message(to=self.sender_id,
                                              messages=payload_object)
        except LineBotApiError as e:
            logger.error(f"Line Error: {e.error.message}")
            if e.status_code == 400 or e.error.message == 'Invalid reply token, trying to push message.':
                logger.info('Pushing Message...')
                self.line_client.push_message(to=self.sender_id,
                                              messages=payload_object)

    async def send_text_message(
            self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        print('============ SEND_TEXT_MESSAGE =============')
        message_object = TextSendMessage(text=text)
        await self.send_to_line(message_object)

    async def send_image_url(
            self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        print('============ SEND_IMAGE_URL =============')
        message_object = ImageSendMessage(original_content_url=image,
                                          preview_image_url=image)
        await self.send_to_line(message_object)

    async def send_text_with_buttons(
            self,
            recipient_id: Text,
            text: Text,
            buttons: List[Dict[Text, Any]],
            **kwargs: Any,
    ) -> None:
        print('============ SEND_TEXT_WITH_BUTTONS =============')
        items = [QuickReplyButton(action=MessageAction(label=buttons[i].get("title"),
                                                       text=buttons[i].get("payload")))
                 for i in range(len(buttons))]
        message_object = TextSendMessage(text=text, quick_reply=QuickReply(
            items=items))
        await self.send_to_line(message_object)
        
    async def send_custom_json(
        self,
        recipient_id: Text,
        json_message: Dict[Text, Any],
        **kwargs: Any
    ) -> None:
        pass


class LineConnectorInput(InputChannel):
    """Line input channel"""

    @classmethod
    def name(cls) -> Text:
        return "line_assistant"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(
            credentials.get("line_channel_secret"),
            credentials.get("line_channel_access_token"),
        )

    def __init__(
            self,
            line_channel_secret: Text,
            line_channel_access_token: Text,
    ) -> None:
        self.channel_secret = line_channel_secret
        self.access_token = line_channel_access_token

    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        line_webhook = Blueprint("line_webhook", __name__)
        parser = self.get_line_message_parser()

        @line_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        # https://{HOST}/webhooks/line_assistant/callback
        @line_webhook.route("/callback", methods=["GET", "POST"])
        async def message(request: Request) -> Any:
            if request.method == "POST":
                # CHECK IF FROM LINE APP
                signature = request.headers.get('X-Line-Signature', None)
                if signature:
                    body = request.body.decode('utf-8')
                    events = parser.parse(body, signature)
                    for event in events:
                        line_output = LineConnectorOutput(self.access_token, event)
                        if isinstance(event, MessageEvent):
                            metadata = self.get_metadata(request)
                            msg = event.message
                            reply_token = event.reply_token
                            user_id = event.source.user_id
                            if isinstance(msg, TextMessage):
                                event_message = msg.text
                                await on_new_message(UserMessage(
                                    text=event_message,
                                    output_channel=line_output,
                                    input_channel=self.name(),
                                    sender_id=user_id,
                                    metadata=metadata
                                ))
                            elif isinstance(msg, LocationMessage):
                                # Send to RASA
                                event_message = f'latitude: {msg.latitude} longitude: {msg.longitude}'
                                await on_new_message(UserMessage(
                                    text=event_message,
                                    output_channel=line_output,
                                    input_channel=self.name(),
                                    sender_id=user_id,
                                    metadata=metadata
                                ))
                            else:
                                event_message = ''
                                if isinstance(msg, StickerMessage):
                                    event_message = "ʕ•́ᴥ•̀ʔっ♡"
                                if isinstance(msg, ImageMessage):
                                    event_message = "Images are not currently supported."
                                if isinstance(msg, VideoMessage):
                                    event_message = "Videos are not currently supported."
                                if isinstance(msg, AudioMessage):
                                    event_message = "Audios are not currently supported."
                        if isinstance(event, PostbackEvent):
                            self.process_postback_events(line_output, event)
                    return response.json({"status": "Line Webhook success"})

                # FROM CURL / EXTERNAL
                else:
                    return response.json(request.json)

            if request.method == "GET":
                bot_info = LineBotApi(self.access_token).get_bot_info()
                return response.json(bot_info)

        return line_webhook

    def get_line_message_parser(self) -> WebhookParser:
        """Loads Line WebhookParser"""
        parser = WebhookParser(self.channel_secret)
        return parser

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        body = request.body.decode('utf-8')
        metadata = json.loads(body)
        return metadata

    @staticmethod
    def process_postback_events(line_output, event):
        pass


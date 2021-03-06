"""
Slack platform for notify component.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/notify.slack/
"""
import logging

import voluptuous as vol

from homeassistant.components.notify import (
    PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['slacker==0.9.24']

_LOGGER = logging.getLogger(__name__)

CONF_CHANNEL = 'default_channel'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_CHANNEL): cv.string,
})


# pylint: disable=unused-variable
def get_service(hass, config):
    """Get the Slack notification service."""
    import slacker

    try:
        return SlackNotificationService(
            config[CONF_CHANNEL],
            config[CONF_API_KEY])

    except slacker.Error:
        _LOGGER.exception("Slack authentication failed")
        return None


# pylint: disable=too-few-public-methods
class SlackNotificationService(BaseNotificationService):
    """Implement the notification service for Slack."""

    def __init__(self, default_channel, api_token):
        """Initialize the service."""
        from slacker import Slacker
        self._default_channel = default_channel
        self._api_token = api_token
        self.slack = Slacker(self._api_token)
        self.slack.auth.test()

    def send_message(self, message="", **kwargs):
        """Send a message to a user."""
        import slacker

        channel = kwargs.get('target') or self._default_channel
        data = kwargs.get('data')
        attachments = data.get('attachments') if data else None

        try:
            self.slack.chat.post_message(channel, message,
                                         as_user=True,
                                         attachments=attachments,
                                         link_names=True)
        except slacker.Error as err:
            _LOGGER.error("Could not send slack notification. Error: %s", err)

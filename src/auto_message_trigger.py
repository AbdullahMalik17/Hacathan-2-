"""
Auto Message Trigger Dispatcher
Enables automated sending of messages to WhatsApp, Gmail, LinkedIn, Facebook, and Instagram.
"""
import asyncio
from typing import List
from src.mcp_servers.whatsapp_server import send_whatsapp_message
from src.mcp_servers.email_sender import send_email
from src.mcp_servers.meta_social_connector import post_to_facebook, post_to_instagram
from src.linkedin.linkedin_poster import LinkedInPoster

# Example trigger dispatcher function
def dispatch_auto_message(platform: str, **kwargs):
    """
    Dispatch an auto-message to the specified platform.
    platform: one of 'whatsapp', 'gmail', 'facebook', 'instagram', 'linkedin'
    kwargs: platform-specific parameters
    """
    if platform == 'whatsapp':
        return send_whatsapp_message(
            to=kwargs['to'],
            message=kwargs['message'],
            requires_approval=kwargs.get('requires_approval', True)
        )
    elif platform == 'gmail':
        return send_email(
            to=kwargs['to'],
            subject=kwargs['subject'],
            body=kwargs['body'],
            cc=kwargs.get('cc'),
            bcc=kwargs.get('bcc'),
            requires_approval=kwargs.get('requires_approval', False)
        )
    elif platform == 'facebook':
        return post_to_facebook(
            content=kwargs['content'],
            link=kwargs.get('link'),
            requires_approval=kwargs.get('requires_approval', True)
        )
    elif platform == 'instagram':
        return post_to_instagram(
            content=kwargs['content'],
            image_url=kwargs['image_url'],
            hashtags=kwargs.get('hashtags'),
            requires_approval=kwargs.get('requires_approval', True)
        )
    elif platform == 'linkedin':
        async def post_linkedin():
            poster = LinkedInPoster()
            return await poster.create_post(
                content=kwargs['content'],
                media_paths=kwargs.get('media_paths')
            )
        return asyncio.run(post_linkedin())
    else:
        raise ValueError(f"Unsupported platform: {platform}")

# Example usage (to be replaced with event/schedule logic)
if __name__ == "__main__":
    # Example: send WhatsApp message
    dispatch_auto_message(
        platform='whatsapp',
        to='John Doe',
        message='Hello from auto trigger!',
        requires_approval=False
    )
    # Example: send Gmail
    dispatch_auto_message(
        platform='gmail',
        to='someone@example.com',
        subject='Auto Subject',
        body='This is an automated email.',
        requires_approval=False
    )

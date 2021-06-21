from .user import User
from .const import EMPTY
from .member import Member
from .channel import get_channel
from .util import clear_postdata
from .dictobject import DictObject
from .exceptions import DiscordHTTPError

import base64
from io import BytesIO

__all__ = ["Guild"]

KEYLIST = ["id", "name", "icon", "icon_hash?", "splash", "discovery_splash",
           "owner", "owner_id", "permissions", "region", "afk_channel_id",
           "afk_timeout", "widget_enabled", "widget_channel_id",
           "verification_level", "default_message_notifications",
           "explicit_content_filter", "roles", "emojis", "features",
           "mfa_level", "application_id", "system_channel_id",
           "system_channel_flags", "rules_channel_id", "joined_at", "large",
           "unavailable", "member_count", "voice_states", "members",
           "channels", "threads", "presences", "max_presences", "max_members",
           "vanity_url_code", "description", "banner", "premium_tier",
           "premium_subscription_count", "preferred_locale",
           "public_updates_channel_id", "max_video_channel_users",
           "approximate_member_count", "approximate_presence_count",
           "welcome_screen", "nsfw_level", "stage_instances"]


class Guild(DictObject):
    def __init__(self, client, data):
        super(Guild, self).__init__(data, KEYLIST)
        self.client = client

        self.members = {
            member['user']['id']: Member(client, self, member)
            for member in self.members
        }

        self.channels = {
            channel['id']: get_channel(client, channel)
            for channel in self.channels
        }

    def get_preview(self):
        return self.client.get_guild_preiew(self.id)

    def modify(self, name=EMPTY, region=EMPTY, verification_level=EMPTY,
               default_message_notifications=EMPTY,
               explicit_content_filter=EMPTY, afk_channel_id=EMPTY,
               afk_timeout=EMPTY, icon=EMPTY, owner_id=EMPTY, splash=EMPTY,
               discovery_splash=EMPTY, banner=EMPTY, system_channel_id=EMPTY,
               system_channel_flags=EMPTY, rules_channel_id=EMPTY,
               public_updates_channel_id=EMPTY, preferred_locale=EMPTY,
               features=EMPTY, description=EMPTY):
        if icon is not None:
            if isinstance(icon, str):
                with open(icon, "rb") as f:
                    icon = f.read()
            elif isinstance(icon, BytesIO):
                icon = icon.read()

            icon = base64.b64encode(icon).decode()

        postdata = {
            "name": name,
            "region": region,
            "verification_level": verification_level,
            "default_message_notifications": default_message_notifications,
            "explicit_content_filter": explicit_content_filter,
            "afk_channel_id": afk_channel_id,
            "afk_timeout": afk_timeout,
            "icon": icon,
            "owner_id": owner_id,
            "splash": splash,
            "discovery_splash": discovery_splash,
            "banner": banner,
            "system_channel_id": system_channel_id,
            "system_channel_flags": system_channel_flags,
            "rules_channel_id": rules_channel_id,
            "public_updates_channel_id": public_updates_channel_id,
            "preferred_locale": preferred_locale,
            "features": features,
            "description": description
        }
        postdata = clear_postdata(postdata)

        guild = self.client.send_request(
            "PATCH", f"/guilds/{self.id}", postdata
        )

        self.__init__(self.client, guild)

        return self

    def delete(self):
        self.client.send_request(
            "DELETE", f"/guilds/{self.id}"
        )

    def leave(self):
        return self.client.user.leave_guild(self)

    def get_channels(self):
        if self.channels is not None:
            return self.channels
        
        raw_channels = self.client.send_request(
            "GET", f"/guilds/{self.id}/channels"
        )

        channels = [
            get_channel(self.client, channel) for channel in raw_channels
        ]
        self.channels = channels

        return channels

    def create_channel(self, name, type, topic=EMPTY, bitrate=EMPTY,
                       user_limit=EMPTY, rate_limit_per_user=EMPTY,
                       position=EMPTY, permission_overwrites=EMPTY,
                       parent_id=EMPTY, nsfw=EMPTY):
        postdata = {
            "name": name,
            "type": type,
            "topic": topic,
            "bitrate": bitrate,
            "user_limit": user_limit,
            "rate_limit_per_user": rate_limit_per_user,
            "position": position,
            "permission_overwrites": permission_overwrites,
            "parent_id": parent_id,
            "nsfw": nsfw
        }
        postdata = clear_postdata(postdata)

        channel = self.client.send_request(
            "POST", f"/guilds/{self.id}/channels", postdata
        )

        return get_channel(self.client, channel)

    def modify_channel_positions(self, params={}):
        self.client.send_request(
            "PATCH", f"/guilds/{self.id}/channels", params
        )

    def get_member(self, user):
        if isinstance(user, User):
            user = user.id
        member = self.client.send_request(
            "GET", f"/guilds/{self.id}/members/{user}"
        )

        return Member(self.client, self, member)

    def list_members(self, limit=EMPTY, after=EMPTY):
        postdata = {
            "limit": limit,
            "after": after
        }
        postdata = clear_postdata(postdata)

        endpoint = f"/guilds/{self.id}/members?"
        for key, val in postdata.items():
            endpoint += f"{key}={val}&"
        endpoint = endpoint[:-1]

        members = self.client.send_request(
            "GET", endpoint
        )

        return [Member(self.client, self, member) for member in members]

    def search_members(self, query=EMPTY, limit=EMPTY):
        postdata = {
            "query": query,
            "limit": limit
        }
        postdata = clear_postdata(postdata)

        endpoint = f"/guilds/{self.id}/members/search?"
        for key, val in postdata.items():
            endpoint += f"{key}={val}&"
        endpoint = endpoint[:-1]

        members = self.client.send_request(
            "GET", endpoint
        )

        return [Member(self.client, self, member) for member in members]

    def modify_member(self, member, nick=EMPTY, roles=EMPTY, mute=EMPTY,
                      deaf=EMPTY, channel_id=EMPTY):
        if isinstance(member, Member):
            member = member.user.id
        postdata = {
            "nick": nick,
            "roles": roles,
            "mute": mute,
            "deaf": deaf,
            "channel_id": channel_id 
        }
        postdata = clear_postdata(postdata)

        member = self.client.send_request(
            "PATCH", f"/guilds/{self.id}/members/{member}", postdata
        )

        return Member(self.client, self, member)

    def change_my_nick(self, nick):
        postdata = {
            "nick": nick
        }

        nick = self.client.send_request(
            "PATCH", f"/guilds/{self.id}/members/@me/nick", postdata
        )

        return nick

    def add_role_to_member(self, member, role):
        if isinstance(member, Member):
            member = member.user.id
        self.client.send_request(
            "PUT", f"/guilds/{self.id}/members/{member}/roles/{role}"
        )

    def remove_role_from_member(self, member, role):
        if isinstance(member, Member):
            member = member.user.id
        self.client.send_request(
            "DELETE", f"/guilds/{self.id}/members/{member}/roles/{role}"
        )

    def kick(self, member):
        if isinstance(member, Member):
            member = member.user.id

        self.client.send_request(
            "DELETE", f"/guilds/{self.id}/members/{member}"
        )

    def get_bans(self):
        bans = self.client.send_request(
            "GET", f"/guilds/{self.id}/bans"
        )

        return bans

    def get_ban(self, member):
        if isinstance(member, Member):
            member = member.user.id

        try:
            ban = self.client.send_request(
                "GET", f"/guilds/{self.id}/bans/{member}"
            )
        except DiscordHTTPError as e:
            if e.code == 404:
                return False
            else:
                raise

        return ban

    def ban(self, member):
        if isinstance(member, Member):
            member = member.user.id

        ban = self.client.send_request(
            "PUT", f"/guilds/{self.id}/bans/{member}"
        )
        
        return ban

    def remove_ban(self, member):
        if isinstance(member, Member):
            member = member.user.id

        self.client.send_request(
            "DELETE", f"/guilds/{self.id}/bans/{member}"
        )
    
    def get_roles(self):
        roles = self.client.send_request(
            "GET", f"/guilds/{self.id}/roles"
        )

        return roles

    def create_role(self, name, permission=EMPTY, color=EMPTY,
                    hoist=EMPTY, mentionable=EMPTY):
        postdata = {
            "name": name,
            "permission": permission,
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable
        }
        postdata = clear_postdata(postdata)

        role = self.client.send_request(
            "POST", f"/guilds/{self.id}/roles", postdata
        )

        return role

    def modify_role_position(self, params):
        roles = self.client.send_request(
            "PATCH", f"/guilds/{self.id}/roles", params
        )

        return roles

    def modify_guild_role(self, role, name=EMPTY, permissions=EMPTY,
                          color=EMPTY, hoist=EMPTY, mentionable=EMPTY):
        postdata = {
            "name": name,
            "permissions": permissions,
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable
        }
        postdata = clear_postdata(postdata)

        role = self.client.send_request(
            "PATCH", f"/guilds/{self.id}/roles/{role}", postdata
        )

    def delete_role(self, role):
        self.client.send_request(
            "DELETE", f"/guilds/{self.id}/roles/{role}"
        )

    def get_voice_regions(self):
        regions = self.client.send_request(
            "GET", f"/guilds/{self.id}/regions"
        )

        return regions

    def get_invites(self):
        invites = self.client.send_request(
            "GET", f"/guilds/{self.id}/invites"
        )

        return invites

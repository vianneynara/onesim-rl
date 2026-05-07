import asyncio
import codecs
import datetime
import os

import googletrans
import pytz
from googletrans import Translator
from typing import Union

import disnake
from disnake import GuildCommandInteraction, UserCommandInteraction
from disnake.ext import commands

from functions.general.usercommands import user_information, user_avatar
from functions.serverutils.servercommands import server_info

from utils.embedding.parse_json import json_to_embeds
from utils.exceptions import ForceReturn
from utils.views.paging_id_en_buttons import LanguageButtons

dt = disnake.utils.utcnow()

"""EMBED BUILDERS/FUNCTIONS"""


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """SLASH COMMANDS"""

    @commands.slash_command(name="user")
    async def _user(self, inter: GuildCommandInteraction):
        """Member information commands."""
        pass

    @_user.sub_command(name="avatar")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _avatar(self, inter: GuildCommandInteraction, member: disnake.Member):
        """Seeks a member avatar.

        Parameters
        ----------
        member: The member you want to seek.
        """
        embeduav = user_avatar(ctx=inter, user=member)
        await inter.response.send_message(embed=embeduav)

    @_user.sub_command(name="info")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _information(
            self, inter: GuildCommandInteraction, member: disnake.Member
    ):
        """Seeks a member information.

        Parameters
        ----------
        member: The member you want to seek.
        """
        embedui = user_information(ctx=inter, member=member)
        await inter.response.send_message(embed=embedui)

    @commands.slash_command(name="rules")
    async def _rules(self, inter: GuildCommandInteraction):
        """Sends rules for Asobi Playground server."""
        await inter.response.defer(ephemeral=True)
        if not os.path.exists(f"./decorator/command_rules.json"):
            return await inter.edit_original_message(
                content=f"**<:GrayX:989336624871669782> There is no file such as `command_rules.json` in decorator folder!**"
            )
        file = codecs.open(f"./decorator/command_rules.json", encoding="utf-8")
        embeds = json_to_embeds(file)

        file.close()

        await inter.edit_original_message(embed=embeds[0], view=LanguageButtons(ctx=inter, embeds=embeds))

    """NORMAL COMMANDS"""

    @commands.command(aliases=["av", "uav", "useravatar"])
    async def avatar(self, ctx, user: Union[disnake.Member, disnake.User] = None):
        if user is None:
            user = ctx.guild.get_member(ctx.author.id)
        else:
            if isinstance(user, disnake.Member):
                user = ctx.guild.get_member(user.id)
            else:
                try:
                    user = await self.bot.fetch_user(user.id)
                except:
                    await ctx.reply("**<:GrayX:989336624871669782> User not found! Try putting their id instead.**")
                    return

        embeduav = user_avatar(ctx=ctx, user=user)
        await ctx.reply(embed=embeduav)

    @commands.command(aliases=["ui", "info"])
    async def userinfo(self, ctx, member: disnake.Member = None):
        if member is None:
            member = ctx.guild.get_member(ctx.author.id)
        else:
            try:
                user = await self.bot.fetch_user(member.id)
            except:
                await ctx.reply("**<:GrayX:989336624871669782> Member not found! Try putting their id instead.**")
                return
        embeduui = user_information(ctx=ctx, member=member)
        await ctx.reply(embed=embeduui)

    @commands.command(aliases=["si", "sinfo", "server"])
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def serverinfo(self, ctx):
        embedsi = server_info(selp=self.bot, ctx=ctx)
        await ctx.reply(embed=embedsi)


def setup(bot):
    bot.add_cog(General(bot))
    

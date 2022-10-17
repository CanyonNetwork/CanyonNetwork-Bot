import discord
import datetime as DT
import asyncio
import re
import pytz
import aiosqlite
import time

from discord import app_commands
from discord.ext.commands import CommandNotFound
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.errors import BadArgument
from typing import Optional

intents = discord.Intents.all()
intents.message_content = True

class RasiaBotView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Test Button', style=discord.ButtonStyle.green, custom_id='test_button')
    async def test(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Test button!', ephemeral=True)

playing = discord.Game(name="canyonnetwork.net")
class RasiaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.', '!'), owner_id=503641822141349888, intents=intents, activity=playing, status=discord.Status.online)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(RasiaBotView())
            self.add_view(TicketButton())
            self.add_view(TicketDropdownView())
            self.add_view(TicketClose())
            self.add_view(AdminTicket())
            self.add_view(Verification())
            self.add_view(ForceTicketClose())
            self.add_view(HistoryView())
            self.add_view(DropdownView())
            self.add_view(DropdownViewStaff())
            self.add_view(DropdownViewAdmin())
            self.add_view(Roles())
            self.persistent_views_added = True

        print(f'Signed in as {self.user}')

        await self.tree.sync(guild=discord.Object(id=944668000072630312))
        await self.tree.sync()

    async def setup_hook(self):
        remindme.start()
        bans.start()
        mutes.start()

class Link(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        url = 'https://discord.com/channels/944668000072630312/1026079056669724724/1026079068787056711'

        self.add_item(discord.ui.Button(label='Click Here', url=url))

class Verification(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji='<a:pink_verify:1025241005936623689>', style=discord.ButtonStyle.blurple, custom_id='verification:1')
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        members = discord.utils.get(interaction.guild.roles,name='Members')
        muted = discord.utils.get(interaction.guild.roles,name='Muted')
        if members in interaction.user.roles:
            await interaction.response.send_message("You cannot unverify yourself!", ephemeral=True)
            return
        if muted in interaction.user.roles:
            await interaction.response.send_message("Don't try to get around a mute...", ephemeral=True)
            return
        else:
            await interaction.user.add_roles(members)
            await interaction.response.send_message('You have been verified!', ephemeral=True)
            return

class Roles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Announcement Pings', style=discord.ButtonStyle.blurple, custom_id='roles:1')
    async def announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        announcements = discord.utils.get(interaction.guild.roles,name='Announcement Ping')
        if announcements in interaction.user.roles:
            await interaction.user.remove_roles(announcements)
            await interaction.response.send_message("You have opt out of getting Announcement notification pings!", ephemeral=True)
        else:
            await interaction.user.add_roles(announcements)
            await interaction.response.send_message('You have opt into getting Announcement notification pings!', ephemeral=True)

    @discord.ui.button(label='Poll Pings', style=discord.ButtonStyle.green, custom_id='roles:2')
    async def poll(self, interaction: discord.Interaction, button: discord.ui.Button):
        polls = discord.utils.get(interaction.guild.roles,name='Poll Ping')
        if polls in interaction.user.roles:
            await interaction.user.remove_roles(polls)
            await interaction.response.send_message("You have opt out of getting Poll notification pings!", ephemeral=True)
        else:
            await interaction.user.add_roles(polls)
            await interaction.response.send_message('You have opt into getting Poll notification pings!', ephemeral=True)

    @discord.ui.button(label='YouTube Pings', style=discord.ButtonStyle.red, custom_id='roles:3')
    async def youtube(self, interaction: discord.Interaction, button: discord.ui.Button):
        youtubes = discord.utils.get(interaction.guild.roles,name='YouTube Ping')
        if youtubes in interaction.user.roles:
            await interaction.user.remove_roles(youtubes)
            await interaction.response.send_message("You have opt out of getting YouTube notification pings!", ephemeral=True)
        else:
            await interaction.user.add_roles(youtubes)
            await interaction.response.send_message('You have opt into getting YouTube notification pings!', ephemeral=True)  

    @discord.ui.button(label='Event Pings', style=discord.ButtonStyle.gray, custom_id='roles:4')
    async def event(self, interaction: discord.Interaction, button: discord.ui.Button):
        events = discord.utils.get(interaction.guild.roles,name='Event Ping')
        if events in interaction.user.roles:
            await interaction.user.remove_roles(events)
            await interaction.response.send_message("You have opt out of getting Event notification pings!", ephemeral=True)
        else:
            await interaction.user.add_roles(events)
            await interaction.response.send_message('You have opt into getting Event notification pings!', ephemeral=True) 

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Click Here', style=discord.ButtonStyle.blurple, custom_id='ticket_button')
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = TicketDropdownView()
        embed = discord.Embed(
            title="Support Tickets",
            description=
            f"""
Choose your option below to create a ticket in the right category!
        """,
            color=0xff00e6)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TicketDropdown(discord.ui.Select):
    def __init__(self):
            options = [
                discord.SelectOption(label='General Support'),
                discord.SelectOption(label='Staff Application'),
                discord.SelectOption(label='YouTube Application'),
                discord.SelectOption(label='Report Player'),
                discord.SelectOption(label='Appeals'),
                discord.SelectOption(label='Partnerships'),
                discord.SelectOption(label='Other')
            ]
            super().__init__(placeholder='Choose your option!', min_values=1, max_values=1, options=options, custom_id="ticket_dropdown")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'General Support':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(945108081807868005)
            ticket_channel = await category_channel.create_text_channel(
                f"general-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                            send_messages=False,
                                            read_messages=False)

            await interaction.response.edit_message(content=f'The ticket has been created at {ticket_channel.mention}.', view=None, embed=None)

            cursor = await db.execute('SELECT valid_roles FROM tickets')
            rows = await cursor.fetchall()
            for (role_id,) in rows:

                role = interaction.guild.get_role(role_id)
                
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
            
            await ticket_channel.set_permissions(interaction.user,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)

            await db.close()

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1/3",
                                description=f"What is your in game name?",
                                color=0xff00e6)

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2/3",
                                description=f"What do you need assistance with?",
                                color=0xff00e6)

            b.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)

            c = discord.Embed(title="Question 3/3",
                                description=f"Any other information you can provide? If not, reply with `N/A`.",
                                color=0xff00e6)

            await ticket_channel.send(embed=c)

            question3 = await client.wait_for('message', check=check)

        
            embed=discord.Embed(title="", 
            description=f"Support will be with you shortly! \nThis ticket will close in 24 hours of inactivity.", 
            color=discord.Color.green())

            embed.set_footer(text="Close this ticket by clicking the 🔒 button.")

            em = discord.Embed(title="Responses",
                                description=f"**IGN**: {question1.content} \n**Reason**: {question2.content} \n**Information**: {question3.content}",
                                color=discord.Color.green())

            view = TicketClose()

            await ticket_channel.send(embeds=[embed, em], view=view)

        if self.values[0] == 'Staff Application':
            await interaction.response.edit_message(content='To apply for staff, visit this Google Form: \nhttps://forms.gle/BSh6rR8H21EMHYX68', view=None, embed=None)
        
        if self.values[0] == 'YouTube Application':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(1031435203677278208)
            ticket_channel = await category_channel.create_text_channel(
                f"youtube-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                            send_messages=False,
                                            read_messages=False)

            await interaction.response.edit_message(content=f'The ticket has been created at {ticket_channel.mention}.', view=None, embed=None)

            cursor = await db.execute('SELECT valid_roles FROM tickets')
            rows = await cursor.fetchall()
            for (role_id,) in rows:

                role = interaction.guild.get_role(role_id)
                
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
            
            await ticket_channel.set_permissions(interaction.user,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)

            await db.close()

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1/3",
                                description="What is your in game name?",
                                color=0xff00e6)

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2/3",
                                description="What is the link to your channel?",
                                color=0xff00e6)

            b.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)

            c = discord.Embed(title="Question 3/3",
                                description="Do you agree that you have to make us at least one video a month to maintain the YouTube role?",
                                color=0xff00e6)

            await ticket_channel.send(embed=c)

            question3 = await client.wait_for('message', check=check)

        
            embed=discord.Embed(title="", 
            description=f"Support will be with you shortly! \nThis ticket will close in 24 hours of inactivity.", 
            color=discord.Color.green())

            embed.set_footer(text="Close this ticket by clicking the 🔒 button.")

            em = discord.Embed(title="Responses",
                                description=f"**IGN**: {question1.content} \n**Channel**: {question2.content} \n**Agreement**: {question3.content}",
                                color=discord.Color.green())

            view = TicketClose()

            await ticket_channel.send(embeds=[embed, em], view=view)

        if self.values[0] == 'Report Player':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(945107032149745864)
            ticket_channel = await category_channel.create_text_channel(
                f"report-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                            send_messages=False,
                                            read_messages=False)

            await interaction.response.edit_message(content=f'The ticket has been created at {ticket_channel.mention}.', view=None, embed=None)

            cursor = await db.execute('SELECT valid_roles FROM tickets')
            rows = await cursor.fetchall()
            for (role_id,) in rows:

                role = interaction.guild.get_role(role_id)
                
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
            
            await ticket_channel.set_permissions(interaction.user,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)

            await db.close()

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1/4",
                                description=f"What is your in game name?",
                                color=0xff00e6)

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2/4",
                                description=f"What is the name of the user you're reporting?",
                                color=0xff00e6)

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)

            c = discord.Embed(title="Question 3/4",
                                description=f"Why are you reporting this user?",
                                color=0xff00e6)

            await ticket_channel.send(embed=c)

            question3 = await client.wait_for('message', check=check)      

            d = discord.Embed(title="Question 4/4",
                                description=f"Do you have any evidence to back up your claims? \n \nIf you don't this ticket will most likely be closed.",
                                color=0xff00e6)

            await ticket_channel.send(embed=d)

            question4 = await client.wait_for('message', check=check)   

            embed=discord.Embed(title="", 
            description=f"Support will be with you shortly! \nThis ticket will close in 24 hours of inactivity.", 
            color=discord.Color.green())

            embed.set_footer(text="Close this ticket by clicking the 🔒 button.")

            em = discord.Embed(title="Responses",
                                description=f"**IGN**: {question1.content} \n**User**: {question2.content} \n**Reason**: {question3.content} \n**Evidence**: {question4.content}",
                                color=discord.Color.green())

            view = TicketClose()

            await ticket_channel.send(embeds=[embed, em], view=view)

        if self.values[0] == 'Appeals':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(945108020617154631)
            ticket_channel = await category_channel.create_text_channel(
                f"appeal-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                            send_messages=False,
                                            read_messages=False)

            await interaction.response.edit_message(content=f'The ticket has been created at {ticket_channel.mention}.', view=None, embed=None)

            cursor = await db.execute('SELECT valid_roles FROM tickets')
            rows = await cursor.fetchall()
            for (role_id,) in rows:

                role = interaction.guild.get_role(role_id)
                
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
            
            await ticket_channel.set_permissions(interaction.user,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)

            await db.close()

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1/4",
                                description=f"What is your in game name?",
                                color=0xff00e6)

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2/4",
                                description=f"Why were you punished?",
                                color=0xff00e6)

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)

            c = discord.Embed(title="Question 3/4",
                                description=f"Do you think this punishment was false?",
                                color=0xff00e6)

            await ticket_channel.send(embed=c)

            question3 = await client.wait_for('message', check=check)      

            d = discord.Embed(title="Question 4/4",
                                description=f"Why should we remove the punishment from you?",
                                color=0xff00e6)

            await ticket_channel.send(embed=d)

            question4 = await client.wait_for('message', check=check)   

            embed=discord.Embed(title="", 
            description=f"Support will be with you shortly! \nThis ticket will close in 24 hours of inactivity.", 
            color=discord.Color.green())

            embed.set_footer(text="Close this ticket by clicking the 🔒 button.")

            em = discord.Embed(title="Responses",
                                description=f"**IGN**: {question1.content} \n**Reason**: {question2.content} \n**False**: {question3.content} \n**Because**: {question4.content}",
                                color=discord.Color.green())

            view = TicketClose()

            await ticket_channel.send(embeds=[embed, em], view=view)

        if self.values[0] == 'Partnerships':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(1030383739735388180)
            ticket_channel = await category_channel.create_text_channel(
                f"partner-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                            send_messages=False,
                                            read_messages=False)

            await interaction.response.edit_message(content=f'The ticket has been created at {ticket_channel.mention}.', view=None, embed=None)

            cursor = await db.execute('SELECT valid_roles FROM tickets')
            rows = await cursor.fetchall()
            for (role_id,) in rows:

                role = interaction.guild.get_role(role_id)
                
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
            
            await ticket_channel.set_permissions(interaction.user,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)

            await db.close()

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1/4",
                                description=f"What is the invite to your server?",
                                color=0xff00e6)

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2/4",
                                description=f"What region is the server hosted in?",
                                color=0xff00e6)

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)

            c = discord.Embed(title="Question 3/4",
                                description=f"What is your server's IP?",
                                color=0xff00e6)

            await ticket_channel.send(embed=c)

            question3 = await client.wait_for('message', check=check)      

            d = discord.Embed(title="Question 4/4",
                                description=f"Is there anything else we should know?",
                                color=0xff00e6)

            await ticket_channel.send(embed=d)

            question4 = await client.wait_for('message', check=check)   

            embed=discord.Embed(title="", 
            description=f"An administator will be with you shortly. While you wait, please send us the advertisement to your server.", 
            color=discord.Color.green())

            embed.set_footer(text="Close this ticket by clicking the 🔒 button.")

            em = discord.Embed(title="Responses",
                                description=f"**Invite**: {question1.content} \n**Region**: {question2.content} \n**IP**: {question3.content} \n**Info**: {question4.content}",
                                color=discord.Color.green())

            view = TicketClose()

            await ticket_channel.send(embeds=[embed, em], view=view)

        if self.values[0] == 'Other':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(1025277588534460446)
            ticket_channel = await category_channel.create_text_channel(
                f"other-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                            send_messages=False,
                                            read_messages=False)

            await interaction.response.edit_message(content=f'The ticket has been created at {ticket_channel.mention}.', view=None, embed=None)

            cursor = await db.execute('SELECT valid_roles FROM tickets')
            rows = await cursor.fetchall()
            for (role_id,) in rows:

                role = interaction.guild.get_role(role_id)
                
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
            
            await ticket_channel.set_permissions(interaction.user,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)

            await db.close()

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1/2",
                                description=f"What is your in game name?",
                                color=0xff00e6)

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2/2",
                                description=f"How can we help?",
                                color=0xff00e6)

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)  

            embed=discord.Embed(title="", 
            description=f"Support will be with you shortly! \nThis ticket will close in 24 hours of inactivity.", 
            color=discord.Color.green())

            embed.set_footer(text="Close this ticket by clicking the 🔒 button.")

            em = discord.Embed(title="Responses",
                                description=f"**IGN**: {question1.content} \n**Reason**: {question2.content}",
                                color=discord.Color.green())

            view = TicketClose()

            await ticket_channel.send(embeds=[embed, em], view=view)

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class AdminTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id='adminticketclose')
    async def adminticketoclose(self, interaction: discord.Interaction, button: discord.ui.Button):
    
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)

            channel_id = interaction.channel_id

            await interaction.response.send_message('Ticket will close in 15 seconds.', ephemeral=True)

            time = datetime.now(tz=pytz.timezone('America/Tijuana'))
            with open("transcripts.html", "w", encoding="utf-8") as file:
                msg = [message async for message in interaction.channel.history(oldest_first=True, limit=1)]
                firstmessagetime = msg[0].created_at.strftime("%m/%d/%y, %I:%M %p")
                y = msg[0].mentions[0]
                file.write(f"""<information> \nTicket Creator: {msg[0].author} \nCreated At: {firstmessagetime} \nTicket Name: {interaction.channel} \n</information>
<!DOCTYPE html><html><head><title>Ticket Transcript</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta charset='UTF-8'><link href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap' rel='stylesheet'></head><body><style>information {{display: none;}} body {{background-color: #181d23;color: white;font-family: 'Open-Sans', sans-serif;margin: 50px;}}.ticket-header h2 {{font-weight: 400;text-transform: capitalize;margin-bottom: 0;color: #fff;}}.ticket-header p {{font-size: 14px;}}.ticket-header .children .item {{margin-right: 25px;display: flex;align-items: center;}}.ticket-header .children {{display: flex;}}.ticket-header .children .item a {{margin-right: 7px;padding: 5px 10px;padding-top: 6px;background-color: #3c434b;border-radius: 3px;font-size: 12px;}}.messages {{margin-top: 30px;display: flex;flex-direction: column;}}.messages .item {{display: flex;margin-bottom: 20px;}}.messages .item .left img {{border-radius: 100%;height: 50px;}}.messages .item .left {{margin-right: 20px;}}.messages .item .right a:nth-child(1) {{font-weight: 400;margin: 0 15px 0 0;font-size: 19px;color: #fff;}}.messages .item .right a:nth-child(2) {{text-transform: capitalize;color: #ffffff;font-size: 12px;}}.messages .item .right div {{display: flex;align-items: center;margin-top: 5px;}}.messages .item .right p {{margin: 0;white-space: normal;line-height: 2;color: #fff;font-size: 15px;}}.messages .item .right p {{max-width: 700px;margin-top: 10px;}}.messages .item {{margin-bottom: 31px;}}@media  only screen and (max-width: 600px) {{body {{margin: 0px;padding: 25px;width: calc(100% - 50px);}}.ticket-header h2 {{margin-top: 0px;}}.ticket-header .children {{display: flex;flex-wrap: wrap;}}</style><div class='ticket-header'><h2>{interaction.channel} Transcript</h2><div class='children'><div class='item'><a>CREATED</a><p>{firstmessagetime} GMT</p></div><div class='item'><a>USER</a><p>{y}</p></div></div></div><div class='messages'><div class='item'><div class='left'><img src='{interaction.guild.icon}'> </div><div class='right'><div><a>{interaction.guild.name}</a><a></a></div><p>Transcript File For Rasia Network</p></div></div>
""")
                async for message in interaction.channel.history(limit=None, oldest_first=True):
                    msgtime = message.created_at.strftime("%m/%d/%y, %I:%M %p")
                    file.write(f"""<div class='item'><div class='left'><img src='{message.author.display_avatar.url}'> </div><div class='right'><div><a>{message.author}</a><a>{msgtime} GMT</a></div><p>{message.content}</p></div></div>""")
                file.write(f"""
<div class='item'><div class='left'><p>If a message is from a bot, and appears empty, its because the bot sent a message with no text, only an embed.</p></div></div>
</div></body></html>
""")
            with open("transcripts.html", "rb") as file:
                transcripts = interaction.guild.get_channel(1025274312820801596)
                msg = await discord.utils.get(interaction.channel.history(oldest_first=True, limit=1))
                time = pytz.timezone('America/Tijuana')
                created_at = msg.created_at
                now = datetime.now(time)
                maths = now - created_at
                seconds = maths.total_seconds()
                math = round(seconds)

                embed = discord.Embed(
                    title=f"Ticket Closed!",
                    description=
                    f"├ **Channel Name:** {interaction.channel.name} \n├ **Opened By:** {y.mention} \n├ **Opened ID:** {y.id} \n├ **Closed By:** {interaction.user.mention} \n├ **Closed ID:** {interaction.user.id} \n└ **Time Opened:** {math} Seconds",
                color=0x202225)
                await transcripts.send(embed=embed)
                await transcripts.send(file=discord.File(file, f"{interaction.channel.name}.html"))
            try:
                embed = discord.Embed(
                    title=f"Ticket Closed!",
                    description=
                    f"├ **Channel Name:** {interaction.channel.name} \n└ **Time Opened:** {math} Seconds",
                color=0x202225)
                embed.set_footer(text="You can view the transcript below.")
                await y.send(embed=embed)
                with open("transcripts.html", "rb") as file:
                    await y.send(file=discord.File(file, f"{interaction.channel.name}.html"))
            except:
                pass

            await asyncio.sleep(15)
            await interaction.channel.delete()

    @discord.ui.button(label="Open", style=discord.ButtonStyle.green, custom_id='adminticketopen')
    async def adminticketopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        msg = [interaction.message async for interaction.message in interaction.channel.history(oldest_first=True, limit=1)]
        x = msg[0].mentions[0].id
        y = msg[0].mentions[0]

        try:
            await interaction.channel.set_permissions(y,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            attach_files=True,
                                            read_message_history=True,
                                            external_emojis=True)
        except:
            pass

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)
        x = f'{interaction.user.mention}'
        embed=discord.Embed(title="", 
        description=f"Ticket Opened by {interaction.user.mention}", 
        color=discord.Color.green())
        
        await interaction.response.send_message('Successfully opened the ticket!', ephemeral=True)

        view = TicketClose()

        await interaction.channel.send(content=x, embed=embed, view=view)

class TicketClose(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(emoji='🔒', style=discord.ButtonStyle.gray, custom_id='ticketclose')
    async def ticketclose(self, interaction: discord.Interaction, button: discord.ui.Button):

        msg = [interaction.message async for interaction.message in interaction.channel.history(oldest_first=True, limit=1)]

        x = msg[0].mentions[0].id
        y = msg[0].mentions[0]

        if x == interaction.user.id:

            await interaction.response.send_message('Closing the ticket...', ephemeral=True)

            await interaction.channel.set_permissions(interaction.user,
                                         send_messages=False,
                                         read_messages=False,
                                         add_reactions=False,
                                         embed_links=False,
                                         attach_files=False,
                                         read_message_history=False,
                                         external_emojis=False)

            view = AdminTicket()
            embed = discord.Embed(
                title="",
                description=
                f"Ticket Closed by {interaction.user.mention}",
                color=discord.Color.red())
            await interaction.channel.send(embed=embed, view=view)
            await interaction.edit_original_response(content='Successfully closed the ticket!')
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
            return

        else:

            await interaction.response.send_message('Closing the ticket...', ephemeral=True)

            try:
                await interaction.channel.set_permissions(y,
                                            send_messages=False,
                                            read_messages=False,
                                            add_reactions=False,
                                            embed_links=False,
                                            attach_files=False,
                                            read_message_history=False,
                                            external_emojis=False)
            except:
                pass

            view = AdminTicket()
            embed = discord.Embed(
                title="",
                description=
                f"Ticket Closed by {interaction.user.mention}",
                color=discord.Color.red())
            await interaction.channel.send(embed=embed, view=view)
            await interaction.edit_original_response(content='Successfully closed the ticket!')
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
            return

class ForceTicketClose(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Close', style=discord.ButtonStyle.red, custom_id='forceticketclose')
    async def forceticketclose(self, interaction: discord.Interaction, button: discord.ui.Button):

            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)

            time = datetime.now(tz=pytz.timezone('America/Tijuana'))
            with open("transcripts.html", "w", encoding="utf-8") as file:
                msg = [message async for message in interaction.channel.history(oldest_first=True, limit=1)]
                firstmessagetime = msg[0].created_at.strftime("%m/%d/%y, %I:%M %p")
                y = msg[0].mentions[0]
                file.write(f"""<information> \nTicket Creator: {msg[0].author} \nCreated At: {firstmessagetime} \nTicket Name: {interaction.channel} \n</information>
<!DOCTYPE html><html><head><title>Ticket Transcript</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta charset='UTF-8'><link href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap' rel='stylesheet'></head><body><style>information {{display: none;}} body {{background-color: #181d23;color: white;font-family: 'Open-Sans', sans-serif;margin: 50px;}}.ticket-header h2 {{font-weight: 400;text-transform: capitalize;margin-bottom: 0;color: #fff;}}.ticket-header p {{font-size: 14px;}}.ticket-header .children .item {{margin-right: 25px;display: flex;align-items: center;}}.ticket-header .children {{display: flex;}}.ticket-header .children .item a {{margin-right: 7px;padding: 5px 10px;padding-top: 6px;background-color: #3c434b;border-radius: 3px;font-size: 12px;}}.messages {{margin-top: 30px;display: flex;flex-direction: column;}}.messages .item {{display: flex;margin-bottom: 20px;}}.messages .item .left img {{border-radius: 100%;height: 50px;}}.messages .item .left {{margin-right: 20px;}}.messages .item .right a:nth-child(1) {{font-weight: 400;margin: 0 15px 0 0;font-size: 19px;color: #fff;}}.messages .item .right a:nth-child(2) {{text-transform: capitalize;color: #ffffff;font-size: 12px;}}.messages .item .right div {{display: flex;align-items: center;margin-top: 5px;}}.messages .item .right p {{margin: 0;white-space: normal;line-height: 2;color: #fff;font-size: 15px;}}.messages .item .right p {{max-width: 700px;margin-top: 10px;}}.messages .item {{margin-bottom: 31px;}}@media  only screen and (max-width: 600px) {{body {{margin: 0px;padding: 25px;width: calc(100% - 50px);}}.ticket-header h2 {{margin-top: 0px;}}.ticket-header .children {{display: flex;flex-wrap: wrap;}}</style><div class='ticket-header'><h2>{interaction.channel} Transcript</h2><div class='children'><div class='item'><a>CREATED</a><p>{firstmessagetime} GMT</p></div><div class='item'><a>USER</a><p>{y}</p></div></div></div><div class='messages'><div class='item'><div class='left'><img src='{interaction.guild.icon}'> </div><div class='right'><div><a>{interaction.guild.name}</a><a></a></div><p>Transcript File For Rasia Network</p></div></div>
""")
                async for message in interaction.channel.history(limit=None, oldest_first=True):
                    msgtime = message.created_at.strftime("%m/%d/%y, %I:%M %p")
                    file.write(f"""<div class='item'><div class='left'><img src='{message.author.display_avatar.url}'> </div><div class='right'><div><a>{message.author}</a><a>{msgtime} GMT</a></div><p>{message.content}</p></div></div>""")
                file.write(f"""
<div class='item'><div class='left'><p>If a message is from a bot, and appears empty, its because the bot sent a message with no text, only an embed.</p></div></div>
</div></body></html>
""")
            with open("transcripts.html", "rb") as file:
                transcripts = interaction.guild.get_channel(1025274312820801596)
                msg = await discord.utils.get(interaction.channel.history(oldest_first=True, limit=1))
                time = pytz.timezone('America/Tijuana')
                created_at = msg.created_at
                now = datetime.now(time)
                maths = now - created_at
                seconds = maths.total_seconds()
                math = round(seconds)

                embed = discord.Embed(
                    title=f"Ticket Closed!",
                    description=
                    f"├ **Channel Name:** {interaction.channel.name} \n├ **Opened By:** {y.mention} \n├ **Opened ID:** {y.id} \n├ **Closed By:** {interaction.user.mention} \n├ **Closed ID:** {interaction.user.id} \n└ **Time Opened:** {math} Seconds",
                color=0x202225)
                await transcripts.send(embed=embed)
                await transcripts.send(file=discord.File(file, f"{interaction.channel.name}.html"))

            try:
                embed = discord.Embed(
                    title=f"Ticket Closed!",
                    description=
                    f"├ **Channel Name:** {interaction.channel.name} \n└ **Time Opened:** {math} Seconds",
                color=0x202225)
                embed.set_footer(text="You can view the transcript below.")
                await y.send(embed=embed)
                with open("transcripts.html", "rb") as file:
                    await y.send(file=discord.File(file, f"{interaction.channel.name}.html"))
            except:
                pass

            await interaction.response.send_message('Ticket will close in 15 seconds.', ephemeral=True)
            await asyncio.sleep(15)
            await interaction.channel.delete()

class DropdownAdmin(discord.ui.Select):
    def __init__(self):
            options = [
                discord.SelectOption(label='General Commands'),
                discord.SelectOption(label='Admin Commands'),
                discord.SelectOption(label='Staff Commands'),
                discord.SelectOption(label='Close')
            ]
            super().__init__(placeholder='How may I help?', min_values=1, max_values=1, options=options, custom_id="help:1")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'General Commands':
            embed = discord.Embed(
                title=f"General Commands",
                description="`/help` - Shows this message. \n`/suggest` - Suggests something to the server. \n`.enlarge` - Turns an emoji into a png/gif file. \n`.pfp` - Gives you the server's pfp. \n`/ping` - Shows you the bot's ping. \n`/latency` - Shows you the bot's latency. \n`/uptime` - Shows you the bot's uptime. \n`/userinfo` - Shows you the userinfo of the specified user. \n`/remindme` - Reminds you of a message. \n`.ip` - Shows you the server's IP.",
                color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed)
        if self.values[0] == 'Admin Commands':
            embed = discord.Embed(
                title=f"Admin Commands",
                description="`/warn` - Warns the specified user. \n`/mute` - Mutes the specified user. \n`/kick` - Kicks the specified user. \n`/ban` - Bans the specified user. \n`/forceban` - Bans the specified user ID. \n`/die` - Instantly closes the ticket. \n`/addaccess` - Adds the specified user to the ticket. \n`/removeaccess` - Removes the specified user from the ticket. \n`/close` - Prompts the ticket to close. \n`/unmute` - Unmutes the specified user. \n`/unban` - Unbans the specified user ID. \n`/history` - Views the history of the specified user.",
                color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed)
        if self.values[0] == 'Staff Commands':
            embed = discord.Embed(
                title=f"Staff Commands",
                description="`/warn` - Warns the specified user. \n`/mute` - Mutes the specified user. \n`/history` - Views the history of the specified user.",
                color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed)
        if self.values[0] == 'Close':
            embed = discord.Embed(
                title=f"Closing",
                description="Closing this dropdown in 15 seconds!",
                color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(15)
            await interaction.delete_original_response()

class DropdownStaff(discord.ui.Select):
    def __init__(self):
            options = [
                discord.SelectOption(label='General Commands'),
                discord.SelectOption(label='Staff Commands'),
                discord.SelectOption(label='Close')
            ]
            super().__init__(placeholder='How may I help?', min_values=1, max_values=1, options=options, custom_id="help:2")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'General Commands':
            embed = discord.Embed(
                title=f"General Commands",
                description="`/help` - Shows this message. \n`/suggest` - Suggests something to the server. \n`.enlarge` - Turns an emoji into a png/gif file. \n`.pfp` - Gives you the server's pfp. \n`/ping` - Shows you the bot's ping. \n`/latency` - Shows you the bot's latency. \n`/uptime` - Shows you the bot's uptime. \n`/userinfo` - Shows you the userinfo of the specified user. \n`/remindme` - Reminds you of a message. \n`.ip` - Shows you the server's IP.",
                color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed)
        if self.values[0] == 'Staff Commands':
            embed = discord.Embed(
                title=f"Staff Commands",
                description="`/warn` - Warns the specified user. \n`/mute` - Mutes the specified user. \n`/history` - Views the history of the specified user.",
                color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed)
        if self.values[0] == 'Close':
            embed = discord.Embed(
                title=f"Closing",
                description="Closing this dropdown in 15 seconds!",
                color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(15)
            await interaction.delete_original_response()

class Dropdown(discord.ui.Select):
    def __init__(self):
            options = [
                discord.SelectOption(label='General Commands'),
                discord.SelectOption(label='Close')
            ]
            super().__init__(placeholder='How may I help?', min_values=1, max_values=1, options=options, custom_id="help:3")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'General Commands':
            embed = discord.Embed(
                title=f"General Commands",
                description="`/help` - Shows this message. \n`/suggest` - Suggests something to the server. \n`.enlarge` - Turns an emoji into a png/gif file. \n`.pfp` - Gives you the server's pfp. \n`/ping` - Shows you the bot's ping. \n`/latency` - Shows you the bot's latency. \n`/uptime` - Shows you the bot's uptime. \n`/userinfo` - Shows you the userinfo of the specified user. \n`/remindme` - Reminds you of a message. \n`.ip` - Shows you the server's IP.",
                color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed)
        if self.values[0] == 'Close':
            embed = discord.Embed(
                title=f"Closing",
                description="Closing this dropdown in 15 seconds!",
                color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(15)
            await interaction.delete_original_response()

class DropdownViewAdmin(discord.ui.View):
    def __init__(self):
        super().__init__()
        super().__init__(timeout=None)
        self.add_item(DropdownAdmin())

class DropdownViewStaff(discord.ui.View):
    def __init__(self):
        super().__init__()
        super().__init__(timeout=None)
        self.add_item(DropdownStaff())

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        super().__init__(timeout=None)
        self.add_item(Dropdown())

class History(discord.ui.Select):
    def __init__(self, member: discord.Member = None):
        self.member = member
        options = [
            discord.SelectOption(label='Warns'),
            discord.SelectOption(label='Mutes'),
            discord.SelectOption(label='Kicks'),
            discord.SelectOption(label='Bans'),
            discord.SelectOption(label='Close')
        ]
        super().__init__(placeholder='What Logs Would You Like To View?', min_values=1, max_values=1, options=options, custom_id="69420")

    async def callback(self, interaction: discord.Interaction):
        guild = client.get_guild(944668000072630312)
        if self.values[0] == 'Warns':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT * FROM warns WHERE user_ids=?', (self.member.id,))
            rows = await cursor.fetchall()
            await db.close()
            member = guild.get_member(self.member.id)
            embed = discord.Embed(
                title=f"Warns of {member}",
                color=discord.Color.red())
            for row in rows:
                embed.add_field(name=f"Case {row[4]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \n")
            await interaction.response.edit_message(embed=embed)
            return
        if self.values[0] == 'Mutes':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT * FROM mutes WHERE user_ids=?', (self.member.id,))
            rows = await cursor.fetchall()
            await db.close()
            member = guild.get_member(self.member.id)
            embed = discord.Embed(
                title=f"Mutes of {member}",
                color=discord.Color.red())
            for row in rows:
                if row[4] == 'null':
                    embed.add_field(name=f"Case {row[5]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \n*(Permanent)*")
                elif row[4] == 'expired':
                    embed.add_field(name=f"Case {row[5]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \n*(Expired)*")
                else:
                    a = int(row[4])
                    embed.add_field(name=f"Case {row[5]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \nTime Expired: <t:{a}:t>")
            await interaction.response.edit_message(embed=embed)
            return
        if self.values[0] == 'Kicks':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT * FROM kicks WHERE user_ids=?', (self.member.id,))
            rows = await cursor.fetchall()
            await db.close()
            member = guild.get_member(self.member.id)
            embed = discord.Embed(
                title=f"Kicks of {member}",
                color=discord.Color.red())
            for row in rows:
                embed.add_field(name=f"Case {row[4]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \n")
            await interaction.response.edit_message(embed=embed)
            return
        if self.values[0] == 'Bans':
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT * FROM bans WHERE user_ids=?', (self.member.id,))
            rows = await cursor.fetchall()
            await db.close()
            member = guild.get_member(self.member.id)
            embed = discord.Embed(
                title=f"Bans of {member}",
                color=discord.Color.red())
            for row in rows:
                if row[4] == 'null':
                    embed.add_field(name=f"Case {row[5]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \n*(Permanent)* \n")
                elif row[4] == 'expired':
                    embed.add_field(name=f"Case {row[5]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \n*(Expired)*")
                else:
                    a = int(row[4])
                    embed.add_field(name=f"Case {row[5]}", value=f"Reason: {row[1]} \nMod: {row[2]} \nTime: {row[3]} \nTime Expired: <t:{a}:t>")
            await interaction.response.edit_message(embed=embed)
            return
        if self.values[0] == 'Close':
            embed = discord.Embed(
                title=f"Closing The History View",
                description="Closing this dropdown in 15 seconds!",
                color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(15)
            await interaction.delete_original_response()

class HistoryView(discord.ui.View):
    def __init__(self, member: discord.Member = None):
        super().__init__(timeout=None)
        self.add_item(History(member))

client = RasiaBot()
client.launch_time = datetime.utcnow()

@client.tree.command(guild=discord.Object(id=944668000072630312), description="View what commands this bot has.")
async def help(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        view = DropdownViewAdmin()
    elif interaction.user.guild_permissions.manage_messages:
        view = DropdownViewStaff()
    else:
        view = DropdownView()
    embed = discord.Embed(
        title=f"Help",
        description=
        f"Choose the type of help you would like to view!",
        color=0xff00e6)
    await interaction.response.send_message(embed=embed, view=view)

@client.command()
async def enlarge(ctx, emoji: discord.PartialEmoji = None):
    if not emoji:
        await ctx.send("You need to provide an emoji!")
    else:
        await ctx.send(emoji.url)

@client.command()
async def pfp(ctx, member: discord.Member = None):
    if member is None:
        await ctx.reply(ctx.guild.icon.url)
    else:
        await ctx.reply(member.avatar.url)

#\\\\\\\\\\\\DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING////////////
@client.tree.command(guild=discord.Object(id=944668000072630312), description="Send the rules and verification buttons.")
@app_commands.default_permissions(administrator=True)
async def verification(interaction: discord.Interaction):
    view = Verification()
    embed = discord.Embed(
        title="Verification",
        description=
        f"""
**__Treat Others With Respect__**
There's no need to say or do things to make others feel bad or upset. Trolling, generally defined as provoking a person/situation to get a response, is also not allowed. This also includes attacking/killing players on the gamemodes.

**__Offensive Content Is Not Allowed__**
While some minor amount of swearing is allowed, severe or frequent vulgarity, especially when directed at others, is not. Offensive item/mob names, skins, minecraft structures, and usernames are not allowed, and you are required to change or remove any if asked by a staff member.

**__Keep Chat Friendly__**
Chat should be reasonably friendly. This means that certain subjects are not tolerated in chat. These include, but are not limited to, discussions about sex, politics, religion, vulgarity, and topics most would deem insensitive or inappropriate. If a staff member asks you to move a conversation elsewhere or drop it altogether, do so respectfully and cooperatively.

**__Advertising Is Not Allowed__**
Advertising other Minecraft servers, discords, buycraft shops, or minecraft networks is strictly prohibited. You  may not advertise websites, YouTube channels, Twitch streams, or anything unless content is related to CanyonNetwork or permission has been granted by Management.

**__Spamming Is Not Allowed__**
Spamming is filling chat with multiple unneeded characters or messages. Any form of character, letter, or command spam will not be tolerated.

**__Do Not Scam or Attempt To Scam Others__**
Scamming is taking IRL money, items, work, or anything else of value from another player dishonestly. This includes teleporting people into traps, dishonestly trading with a player, or deceiving another player to purchase a rank for you. Any of these will result in a permanent removal from the server.

**__Trading In-Game Items For Real Items Is Not Allowed__**
Transactions to buy or sell in-game items for real money or other external products are not allowed. This includes minecraft accounts, items, armor, ect. Our exception to this is the trading of  in-game items, labor, or work in exchange for items on the shop. Video proof of the agreement is recommended or staff can not assist you.

**__Freehitting Is Not Allowed__**
Freehitting is considered when you're randomly hitting people to make sure they want to fight you.

**__Cheating Is Not Tolerated__**
Cheating in any form is not allowed. Anything that would give you an unfair advantage over other players is considered cheating. This can include client mods to generate items easier or faster than otherwise possible, abusing server bugs, automining, x-raying, duping, or autoclicking. Any of these rules broken will result in a permanent removal from the server.

**__Allow Moderators To Do Their Job__**
You may not attempt to do a moderator's job by threatening to punish players for breaking the rules. You are not allowed to argue against any decision made by a staff member regarding enforcement of the rules in any public channel. If you do disagree, please contact that staff member privately to resolve the issue, and if you cannot, contact our support team through our discord support system.

Clicking the button below will give you access to the rest of the server. It also is an acknowledgement of the rules.
""",
        color=0xff00e6)
    embed.set_footer(text="If the bot isn't working properly, please PM Someone#0171.")
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message('Sent!', ephemeral=True)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Send the notification embed and buttons.")
@app_commands.default_permissions(administrator=True)
async def notifications(interaction: discord.Interaction):
    view = Roles()
    embed = discord.Embed(
        title="Notification Roles",
        description=
        f"If you would like to get Announcement, Poll, YouTube, or Event pings, choose the corresponding button!",
            color=0xff00e6)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message('Sent!', ephemeral=True)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Send the ticket embed and buttons.")
@app_commands.default_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    view = TicketButton()
    embed = discord.Embed(
        title="Support Tickets",
        description=
        f"""
Click the button below to create a ticket!
    """,
        color=0xff00e6)
    embed.set_footer(text="Opening and closing a ticket with no reason will result in a warn.")
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message('Sent!', ephemeral=True)

@client.tree.command(description="Ping Command")
async def ping(interaction: discord.Interaction):
    start = time.perf_counter()
    await interaction.response.send_message("Pinging...", ephemeral=True)
    end = time.perf_counter()
    duration = (end - start) * 1000
    await interaction.edit_original_response(content='Pong! {:.2f}ms'.format(duration))

@client.tree.command(description="Latency Command")
async def latency(interaction: discord.Interaction):
    await interaction.response.send_message('{0} ms'.format(round(client.latency, 1)), ephemeral=True)

@client.tree.command(description="Uptime Command")
async def uptime(interaction: discord.Interaction):
    delta_uptime = datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await interaction.response.send_message(f"{days}d, {hours}h, {minutes}m, {seconds}s", ephemeral=True)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Mute a Member.")
@app_commands.describe(member="Who do you want to mute?")
@app_commands.describe(time="How long do you want to mute them for?")
@app_commands.describe(reason="What's the reason to the mute?")
@app_commands.default_permissions(manage_messages=True)
async def mute(interaction: discord.Interaction, member: discord.Member, time: str, reason: str):
    format = datetime.now(tz=pytz.timezone('America/Tijuana'))
    formatted = format.strftime("%m/%d/%y, %I:%M %p")
    a = DT.datetime.now().timestamp()
    b = int(a)
    modlogs = client.get_channel(1027778386178875472)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM mutes')
    rows = await cursor.fetchall()
    muted = discord.utils.get(interaction.guild.roles, name="Muted")
    members = discord.utils.get(interaction.guild.roles, name="Members")
    view = Link()
    permanent_variable = ("none", "na", "n/a", "None", "Na", "NA", "N/A", "p", "P", "Permanent", "permanent", "perm", "Perm")
    if time in permanent_variable:
        try:
            embed = discord.Embed(
                title="Member Muted",
                description=
                f"""
{member} ({member.id}) was permanently muted by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xFFA200)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO mutes VALUES (?,?,?,?,?,?);', (member.id, f'{time}', f'{interaction.user}', f'{formatted}', 'null', len(rows)))
            await member.add_roles(muted)
            await member.remove_roles(members)
            embed = discord.Embed(
                title="",
                description=
                f"{member.mention}, you've been muted by the Rasia Discord Moderation Team for: \n \n{reason} \n \n**This Mute Will Not Expire**. \n \nIf you wish to appeal this punishment or think it was wrong, you may do so here: \nhttps://forms.gle/YNhQkjQi8JGsbb686",
            color=0xff00e6)
            await member.send(embed=embed)
            await interaction.response.send_message(f'Muted {member} indefinitely!')
            e = await interaction.original_response()
            await db.commit()
            await db.close()
            await asyncio.sleep(5)
            await e.delete()
            return
        except:
            embed = discord.Embed(
                title="Member Muted",
                description=
                f"""
{member} ({member.id}) was permanently muted by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xFFA200)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO mutes VALUES (?,?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', 'null', len(rows)))
            await member.add_roles(muted)
            await member.remove_roles(members)
            await interaction.response.send_message(f'Muted {member} indefinitely!')
            e = await interaction.original_response()
            await db.commit()
            await db.close()
            await asyncio.sleep(5)
            await e.delete()
            return
    else:
        try:
            time_list = re.split('(\d+)',time)
            if time_list[2] == "s":
                time_in_s = int(time_list[1])
            if time_list[2] == "m":
                time_in_s = int(time_list[1]) * 60
            if time_list[2] == "h":
                time_in_s = int(time_list[1]) * 60 * 60
            if time_list[2] == "d":
                time_in_s = int(time_list[1]) * 60 * 60 * 24
            timestamp = DT.datetime.now().timestamp()
            x = datetime.now() + timedelta(seconds=time_in_s)
            timestamp = x.timestamp()
            a = int(timestamp)
            b = int(a)
            embed = discord.Embed(
                title="Member Muted",
                description=
                f"""
{member} ({member.id}) was muted until <t:{a}:t> by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xFFA200)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO mutes VALUES (?,?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', timestamp, len(rows)))
            await db.commit()
            await db.close()
            try:
                await member.add_roles(muted)
                await member.remove_roles(members)
                embed = discord.Embed(
                    title="",
                    description=
                    f"{member.mention}, you've been muted by the Rasia Discord Moderation Team for: \n \n{reason} \n \nThis Mute Will Expire At <t:{a}:t>. \n \nIf you wish to appeal this punishment or think it was wrong, you may do so here: \nhttps://forms.gle/YNhQkjQi8JGsbb686",
                color=0xff00e6)
                await member.send(embed=embed)
                await interaction.response.send_message(f"They've been muted until <t:{a}:t>.")
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            except:
                await member.add_roles(muted)
                await member.remove_roles(members)
                await interaction.response.send_message(f"They've been muted until <t:{a}:t>.")
                e = await interaction.original_response()
                await interaction.followup.send('A DM was not sent to the member.', ephemeral=True)
                await asyncio.sleep(5)
                await e.delete()
                return
        except:
            await interaction.response.send_message(f'Please retry this command again! There seems to be an error. \nIn the time, assure that you only have `s`, `m`, `h` or `d`. For permanent mute options, click the button!', view=view)
            e = await interaction.original_response()
            await asyncio.sleep(10)
            await e.delete()
            return

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Ban a Member.")
@app_commands.describe(member="Who do you want to ban?")
@app_commands.describe(time="How long do you want the ban to last?")
@app_commands.describe(reason="What's the reason to the ban?")
@app_commands.default_permissions(administrator=True)
async def ban(interaction: discord.Interaction, member: discord.Member, time: str, reason: str):
    format = datetime.now(tz=pytz.timezone('America/Tijuana'))
    formatted = format.strftime("%m/%d/%y, %I:%M %p")
    a = DT.datetime.now().timestamp()
    b = int(a)
    modlogs = client.get_channel(1027778386178875472)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM bans')
    rows = await cursor.fetchall()
    view = Link()
    permanent_variable = ("none", "na", "n/a", "None", "Na", "NA", "N/A", "p", "P", "Permanent", "permanent", "perm", "Perm")
    if time in permanent_variable:
        try:
            embed = discord.Embed(
                title="Member Banned",
                description=
                f"""
{member} ({member.id}) was permanently banned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xA50000)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO bans VALUES (?,?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', 'null', len(rows)))
            embed = discord.Embed(
                description=
                f"{member.mention}, you've been banned by the Rasia Discord Moderation Team for: \n \n{reason} \n \n**This Ban Will Not Expire**. \n \nIf you wish to appeal this punishment or think it was wrong, you may do so here: \nhttps://forms.gle/YNhQkjQi8JGsbb686",
            color=0xA50000)
            await member.send(embed=embed)
            await member.ban(reason=reason)
            await interaction.response.send_message(f'Banned {member} indefinitely!')
            e = await interaction.original_response()
            await interaction.followup.send('A DM was not sent to the member.', ephemeral=True)
            await db.commit()
            await db.close()
            await asyncio.sleep(5)
            await e.delete()
            return
        except:
            embed = discord.Embed(
                title="Member Banned",
                description=
                f"""
{member} ({member.id}) was permanently banned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xA50000)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO bans VALUES (?,?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', 'null', len(rows)))
            await interaction.response.send_message(f'Banned {member} indefinitely!')
            e = await interaction.original_response()
            await member.ban(reason=reason)
            await db.commit()
            await db.close()
            await asyncio.sleep(5)
            await e.delete()
            return
    else:
        try:
            time_list = re.split('(\d+)',time)
            if time_list[2] == "s":
                time_in_s = int(time_list[1])
            if time_list[2] == "m":
                time_in_s = int(time_list[1]) * 60
            if time_list[2] == "h":
                time_in_s = int(time_list[1]) * 60 * 60
            if time_list[2] == "d":
                time_in_s = int(time_list[1]) * 60 * 60 * 24
            timestamp = DT.datetime.now().timestamp()
            x = datetime.now() + timedelta(seconds=time_in_s)
            timestamp = x.timestamp()
            a = int(timestamp)
            b = int(a)
            embed = discord.Embed(
                title="Member Banned",
                description=
                f"""
{member} ({member.id}) was banned until <t:{a}:t> by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xA50000)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO bans VALUES (?,?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', timestamp, len(rows)))
            await db.commit()
            await db.close()
            try:
                embed = discord.Embed(
                    description=
                    f"{member.mention}, you've been banned by the Rasia Discord Moderation Team for: \n \n{reason} \n \nThis Ban Will Expire At <t:{a}:t>. \n \nIf you wish to appeal this punishment or think it was wrong, you may do so here: \nhttps://forms.gle/YNhQkjQi8JGsbb686",
                color=0xA50000)
                await member.send(embed=embed)
                await member.ban(reason=reason)
                await interaction.response.send_messaged(f"They've been banned until <t:{a}:t>.")
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            except:
                await member.ban(reason=reason)
                await interaction.response.send_message(f"They've been banned until <t:{a}:t>.")
                e = await interaction.original_response()
                await interaction.followup.send('A DM was not sent to the member.', ephemeral=True)
                await asyncio.sleep(5)
                await e.delete()
                return
        except:
            await interaction.response.send_message(f'Please retry this command again! There seems to be an error. \nIn the time, assure that you only have `s`, `m`, `h` or `d`. For permanent ban options, click the button!', view=view)
            e = await interaction.original_response()
            await asyncio.sleep(10)
            await e.delete()
            return

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Ban a Member ID.")
@app_commands.describe(userid="What ID do you want to ban?")
@app_commands.describe(time="How long do you want the ban to last?")
@app_commands.describe(reason="What's the reason to the ban?")
@app_commands.default_permissions(administrator=True)
async def forceban(interaction: discord.Interaction, userid: str, time: str, reason: str):
    try:
        user = int(userid)
    except:
        await interaction.response.send_message("That's not a valid User ID!", ephemeral=True)
        return
    guild = client.get_guild(944668000072630312) 
    format = datetime.now(tz=pytz.timezone('America/Tijuana'))
    formatted = format.strftime("%m/%d/%y, %I:%M %p")
    a = DT.datetime.now().timestamp()
    b = int(a)
    modlogs = client.get_channel(1027778386178875472)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM bans')
    rows = await cursor.fetchall()
    view = Link()
    permanent_variable = ("none", "na", "n/a", "None", "Na", "NA", "N/A", "p", "P", "Permanent", "permanent", "perm", "Perm")
    if time in permanent_variable:
        try:
            await guild.ban(discord.Object(id=user), reason=reason)
            embed = discord.Embed(
                title="Member Banned",
                description=
                f"""
{user.id} was permanently banned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xA50000)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO bans VALUES (?,?,?,?,?,?);', (user, f'{reason}', f'{interaction.user}', f'{formatted}', 'null', len(rows)))
            await interaction.response.send_message(f'Banned <@{user}> (`{user}`) indefinitely!')
            e = await interaction.original_response()
            await db.commit()
            await db.close()
            await asyncio.sleep(5)
            await e.delete()
            return
        except:
            await interaction.response.send_message("I cannot ban that user! \n \nPlease ensure that the User ID is valid!")
            e = await interaction.original_response()
            await asyncio.sleep(5)
            await e.delete()
    else:
        try:
            time_list = re.split('(\d+)',time)
            if time_list[2] == "s":
                time_in_s = int(time_list[1])
            if time_list[2] == "m":
                time_in_s = int(time_list[1]) * 60
            if time_list[2] == "h":
                time_in_s = int(time_list[1]) * 60 * 60
            if time_list[2] == "d":
                time_in_s = int(time_list[1]) * 60 * 60 * 24
            timestamp = DT.datetime.now().timestamp()
            x = datetime.now() + timedelta(seconds=time_in_s)
            timestamp = x.timestamp()
            a = int(timestamp)
            b = int(a)
            embed = discord.Embed(
                title="Member Banned",
                description=
                f"""
{user.id} was banned until <t:{a}:t> by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0xA50000)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            cursor = await db.execute('INSERT INTO bans VALUES (?,?,?,?,?,?);', (user, f'{reason}', f'{interaction.user}', f'{formatted}', timestamp, len(rows)))
            await db.commit()
            await db.close()
            try:
                await guild.ban(discord.Object(id=user), reason=reason)
            except:
                await interaction.response.send_message("I cannot ban that user! \n \nPlease ensure that the User ID is valid!")
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            await interaction.response.send_message(f"They've been banned until <t:{a}:t>.")
            e = await interaction.original_response()
            await interaction.followup.send('A DM was not sent to the member.', ephemeral=True)
            await asyncio.sleep(5)
            await e.delete()
            return
        except:
            await interaction.response.send_message(f'Please retry this command again! There seems to be an error. \nIn the time, assure that you only have `s`, `m`, `h` or `d`. For permanent ban options, click the button!', view=view)
            e = await interaction.original_response()
            await asyncio.sleep(10)
            await e.delete()
            return

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Warn a Member.")
@app_commands.describe(member="Who do you want to warn?")
@app_commands.describe(reason="What's the reason to the warn?")
@app_commands.default_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    time = datetime.now(tz=pytz.timezone('America/Tijuana'))
    formatted = time.strftime("%m/%d/%y, %I:%M %p")
    modlogs = client.get_channel(1027778386178875472)
    b = DT.datetime.now().timestamp()
    b = int(b)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM warns')
    rows = await cursor.fetchall()

    embed = discord.Embed(
        title="Member Warned",
        description=
        f"""
{member} ({member.id}) was warned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
        color=0xFFFF00)
    embed.set_author(name=member, icon_url=member.display_avatar.url)
    embed.timestamp = datetime.now()
    await modlogs.send(embed=embed)
    cursor = await db.execute('INSERT INTO warns VALUES (?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', len(rows)))

    await db.commit()
    await db.close()
    try:
        await member.send(f'You have been warned in Rasia Network for `{reason}` at <t:{b}:t>.')
        await interaction.response.send_message(f'Successfully warned {member.mention}!')
        a = await interaction.original_response()
        await asyncio.sleep(5)
        await a.delete()
        return
    except:
        await interaction.response.send_message(f'Successfully warned {member.mention}!')
        a = await interaction.original_response()
        await interaction.followup.send('A DM was not sent to the member.', ephemeral=True)
        await asyncio.sleep(5)
        await a.delete()
        return

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Kick a Member.")
@app_commands.describe(member="Who do you want to kick?")
@app_commands.describe(reason="What's the reason to the kick?")
@app_commands.default_permissions(administrator=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    time = datetime.now(tz=pytz.timezone('America/Tijuana'))
    formatted = time.strftime("%m/%d/%y, %I:%M %p")
    modlogs = client.get_channel(1027778386178875472)
    b = DT.datetime.now().timestamp()
    b = int(b)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM kicks')
    rows = await cursor.fetchall()
    embed = discord.Embed(
        title="Member Kicked",
        description=
        f"""
{member} ({member.id}) was kicked by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
        color=0xFF0000)
    embed.set_author(name=member, icon_url=member.display_avatar.url)
    embed.timestamp = datetime.now()
    await modlogs.send(embed=embed)
    cursor = await db.execute('INSERT INTO kicks VALUES (?,?,?,?,?);', (member.id, f'{reason}', f'{interaction.user}', f'{formatted}', len(rows)))

    await db.commit()
    await db.close()
    try:
        await member.send(f'You have been kicked in Rasia Network for `{reason}` at <t:{b}:t>.')
        await interaction.response.send_message(f'Successfully kicked {member.mention}!')
        e = await interaction.original_response()
        await asyncio.sleep(5)
        await e.delete()
        return
    except:
        await interaction.response.send_message(f'Successfully kicked {member.mention}!')
        e = await interaction.original_response()
        await interaction.followup.send('A DM was not sent to the member.', ephemeral=True)
        await asyncio.sleep(5)
        await e.delete()
        return

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Instantly close a ticket.")
@app_commands.default_permissions(administrator=True)
async def die(interaction: discord.Interaction):
    valid_things = ("general", "apply", "report", "appeal", "other")
    if any(thing in interaction.channel.name for thing in valid_things):
        await interaction.response.send_message('Dying...')
        with open("transcripts.html", "w", encoding="utf-8") as file:
            msg = [message async for message in interaction.channel.history(oldest_first=True, limit=1)]
            firstmessagetime = msg[0].created_at.strftime("%m/%d/%y, %I:%M %p")
            y = msg[0].mentions[0]
            file.write(f"""<information> \nTicket Creator: {msg[0].author} \nCreated At: {firstmessagetime} \nTicket Name: {interaction.channel} \n</information>
<!DOCTYPE html><html><head><title>Ticket Transcript</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta charset='UTF-8'><link href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap' rel='stylesheet'></head><body><style>information {{display: none;}} body {{background-color: #181d23;color: white;font-family: 'Open-Sans', sans-serif;margin: 50px;}}.ticket-header h2 {{font-weight: 400;text-transform: capitalize;margin-bottom: 0;color: #fff;}}.ticket-header p {{font-size: 14px;}}.ticket-header .children .item {{margin-right: 25px;display: flex;align-items: center;}}.ticket-header .children {{display: flex;}}.ticket-header .children .item a {{margin-right: 7px;padding: 5px 10px;padding-top: 6px;background-color: #3c434b;border-radius: 3px;font-size: 12px;}}.messages {{margin-top: 30px;display: flex;flex-direction: column;}}.messages .item {{display: flex;margin-bottom: 20px;}}.messages .item .left img {{border-radius: 100%;height: 50px;}}.messages .item .left {{margin-right: 20px;}}.messages .item .right a:nth-child(1) {{font-weight: 400;margin: 0 15px 0 0;font-size: 19px;color: #fff;}}.messages .item .right a:nth-child(2) {{text-transform: capitalize;color: #ffffff;font-size: 12px;}}.messages .item .right div {{display: flex;align-items: center;margin-top: 5px;}}.messages .item .right p {{margin: 0;white-space: normal;line-height: 2;color: #fff;font-size: 15px;}}.messages .item .right p {{max-width: 700px;margin-top: 10px;}}.messages .item {{margin-bottom: 31px;}}@media  only screen and (max-width: 600px) {{body {{margin: 0px;padding: 25px;width: calc(100% - 50px);}}.ticket-header h2 {{margin-top: 0px;}}.ticket-header .children {{display: flex;flex-wrap: wrap;}}</style><div class='ticket-header'><h2>{interaction.channel} Transcript</h2><div class='children'><div class='item'><a>CREATED</a><p>{firstmessagetime} GMT</p></div><div class='item'><a>USER</a><p>{y}</p></div></div></div><div class='messages'><div class='item'><div class='left'><img src='{interaction.guild.icon}'> </div><div class='right'><div><a>{interaction.guild.name}</a><a></a></div><p>Transcript File For Rasia Network</p></div></div>
""")
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                msgtime = message.created_at.strftime("%m/%d/%y, %I:%M %p")
                file.write(f"""<div class='item'><div class='left'><img src='{message.author.display_avatar.url}'> </div><div class='right'><div><a>{message.author}</a><a>{msgtime} GMT</a></div><p>{message.content}</p></div></div>""")
            file.write(f"""
<div class='item'><div class='left'><p>If a message is from a bot, and appears empty, its because the bot sent a message with no text, only an embed.</p></div></div>
</div></body></html>
""")

        with open("transcripts.html", "rb") as file:
            transcripts = interaction.guild.get_channel(1025274312820801596)
            msg = await discord.utils.get(interaction.channel.history(oldest_first=True, limit=1))
                
            time = pytz.timezone('America/Tijuana')
            created_at = msg.created_at
            now = datetime.now(time)
            maths = now - created_at
            seconds = maths.total_seconds()
            math = round(seconds)

            embed = discord.Embed(
                title=f"Ticket Closed!",
                description=
                f"├ **Channel Name:** {interaction.channel.name} \n├ **Opened By:** {y.mention} \n├ **Opened ID:** {y.id} \n├ **Closed By:** {interaction.user.mention} \n├ **Closed ID:** {interaction.user.id} \n└ **Time Opened:** {math} Seconds",
            color=0x202225)
            await transcripts.send(embed=embed)
            await transcripts.send(file=discord.File(file, f"{interaction.channel.name}.html"))
        try:
            embed = discord.Embed(
                title=f"Ticket Closed!",
                description=
                f"├ **Channel Name:** {interaction.channel.name} \n└ **Time Opened:** {math} Seconds",
            color=0x202225)
            embed.set_footer(text="You can view the transcript below.")
            await y.send(embed=embed)
            with open("transcripts.html", "rb") as file:
                await y.send(file=discord.File(file, f"{interaction.channel.name}.html"))
        except:
            pass
        await asyncio.sleep(1)
        await interaction.channel.delete()
        return
    else:
        await interaction.response.send_message('This is not a ticket!', ephemeral=True)
        return

#\\\\\\\\\\\\Ticket Commmands////////////
@client.tree.command(guild=discord.Object(id=944668000072630312), description="Add someone to the ticket.")
@app_commands.describe(member="Who do you want to add to this ticket?")
@app_commands.default_permissions(administrator=True)
async def addaccess(interaction: discord.Interaction, member: discord.Member):
    valid_channels = ("general", "apply", "report", "appeal", "other")
    if any(thing in interaction.channel.name for thing in valid_channels):
        await interaction.channel.set_permissions(member,
                                            send_messages=True,
                                            read_messages=True,
                                            add_reactions=True,
                                            embed_links=True,
                                            read_message_hßistory=True,
                                            external_emojis=True)

        await interaction.response.send_message('Added.')
    else:
        await interaction.response.send_message('This is not a valid ticket!', ephemeral=True)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Remove someone from the ticket.")
@app_commands.describe(member="Who do you want to remove from this ticket?")
@app_commands.default_permissions(administrator=True)
async def removeaccess(interaction: discord.Interaction, member: discord.Member):
    valid_channels = ("general", "apply", "report", "appeal", "other")
    if any(thing in interaction.channel.name for thing in valid_channels):
        await interaction.channel.set_permissions(member,
                                            send_messages=False,
                                            read_messages=False,
                                            add_reactions=False,
                                            embed_links=False,
                                            read_message_history=False,
                                            external_emojis=False)
        await interaction.response.send_message('Removed.')
    else:
        await interaction.response.send_message('This is not a valid ticket!', ephemeral=True)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Prompt the ticket with a close button.")
async def close(interaction: discord.Interaction):
    valid_channels = ("general", "apply", "report", "appeal", "other")
    if any(thing in interaction.channel.name for thing in valid_channels):
        view = ForceTicketClose()
        embed = discord.Embed(
            title="Closure Confirmation",
            description=
            "Click the button if you want to close the ticket.",
            color=0x00a8ff)
        await interaction.response.send_message(embed=embed, view=view)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="View the userinfo of a Member.")
@app_commands.describe(member="Who's user info would you like to view?")
async def userinfo(interaction: discord.Interaction, member: Optional[discord.Member]):
    target = member
    author = interaction.user
    if member:

        embed = discord.Embed(
            title=f"User Information",
            color=0x00a8ff)

        embed.set_thumbnail(url=member.display_avatar.url)

        pp = target.created_at.timestamp()
        a = int(pp)
        po = target.joined_at.timestamp()
        b = int(po)

        fields = [("Name", str(target), True),
                ("ID", target.id, True),
                ("Bot?", target.bot, True),
                ("Top Role", target.top_role.mention, True),
                ("Status", str(target.status).title(), True),
                ("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
                ("Account Made", f"<t:{a}:R>", True),
                ("Joined Server", f"<t:{b}:R>", True),
                ("Boosting?", bool(target.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"User Information",
            color=0x00a8ff)

        embed.set_thumbnail(url=author.display_avatar.url)

        pp = author.created_at.timestamp()
        a = int(pp)
        po = author.joined_at.timestamp()
        b = int(po)

        fields = [("Name", str(author), True),
                  ("ID", author.id, True),
                  ("Bot?", author.bot, True),
                  ("Top Role", author.top_role.mention, True),
                  ("Status", str(author.status).title(), True),
                  ("Activity", f"{str(author.activity.type).split('.')[-1].title() if author.activity else 'N/A'} {author.activity.name if author.activity else ''}", True),
                  ("Account Made", f"<t:{a}:R>", True),
                  ("Joined Server", f"<t:{b}:R>", True),
                  ("Boosting?", bool(author.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await interaction.response.send_message(embed=embed)

@client.event
async def on_member_join(member):
    guild = client.get_guild(944668000072630312)
    if member.bot:
        return
    else:
        embed = discord.Embed(
            title=f"Welcome, {member}!",
            description=
            f"""
Welcome to Rasia Network, {member}! We hope you enjoy your stay.

Be sure to verify yourself in <#945400059544080424> to view the rest of the channels!
""",
            color=0xff00e6)
        embed.set_author(name=member, icon_url=member.display_avatar.url)
        embed.timestamp = datetime.now()
        welcomechannel = client.get_channel(944672899149754389)
        await welcomechannel.send(content=f'{member.mention}', embed=embed)
        db = await aiosqlite.connect('database.db')
        cursor = await db.execute('SELECT time_expired, user_ids FROM mutes WHERE user_ids=?', (member.id,))
        a = await cursor.fetchall()
        for row in a:
            await asyncio.sleep(1)
            if row[0] == 'expired':
                continue
            if row[0] == 'null':
                muted = discord.utils.get(guild.roles, name='Muted')
                member = guild.get_member(row[1])
                try:
                    embed = discord.Embed(
                        title="",
                        description=
                        f"{member.mention}, thank you for joining the server. Unfortunately your account has had a previous mute that hasn't expired yet and it has been re-added. \n \nIf you wish to appeal this punishment or think it was wrong, pleasse create a support ticket.",
                    color=0xff00e6)
                    await member.send(embed=embed)
                except:
                    continue
                await member.add_roles(muted)
                format = datetime.now(tz=pytz.timezone('America/Tijuana'))
                formatted = format.strftime("%I:%M %p")
                user = guild.get_member(row[1])
                cursor = await db.execute('SELECT * FROM mutes')
                continue
            if row[0] >= DT.datetime.now().timestamp():
                muted = discord.utils.get(guild.roles, name='Muted')
                member = guild.get_member(row[1])
                try:
                    embed = discord.Embed(
                        title="",
                        description=
                        f"{member.mention}, thank you for joining the server. Unfortunately your account has had a previous mute that hasn't expired yet and it has been re-added. \n \nIf you wish to appeal this punishment or think it was wrong, please create a support ticket.",
                    color=0xff00e6)
                    await member.send(embed=embed)
                except:
                    continue
                await member.add_roles(muted)
                format = datetime.now(tz=pytz.timezone('America/Tijuana'))
                formatted = format.strftime("%I:%M %p")
                user = guild.get_member(row[1])
                cursor = await db.execute('SELECT * FROM mutes')
                continue
        await db.close()

#\\\\\\\\\\\\ModMail////////////
@client.tree.command(guild=discord.Object(id=944668000072630312), description="DM a Member.")
@app_commands.describe(member="Who do you want to DM?")
@app_commands.describe(msg="What message do you want the member to recieve?")
@app_commands.default_permissions(administrator=True)
async def dm(interaction: discord.Interaction, member: discord.Member, msg: str):
    if interaction.channel.id != 1028508949516922910:
        await interaction.response.send_message('You must be in the <#1028508949516922910> channel!', ephemeral=True)
    else:
        try:
            author = interaction.user
            embed = discord.Embed()
            embed.set_author(name="Message", icon_url=interaction.channel.guild.icon)
            embed.color = author.color
            embed.add_field(name="Message from Rasia Network Moderation", value=msg[:1000] or "blank", inline=False)
            if len(msg) > 1000:
                embed.add_field(name="(Continued)", value=msg[1000:], inline=False)
            await member.send(embed=embed)

            author = interaction.user
            embed = discord.Embed()
            embed.set_author(name="DM Message", icon_url=interaction.channel.guild.icon)
            embed.color = author.color
            embed.add_field(name="Message:", value=msg[:1000] or "blank", inline=False)
            if len(msg) > 1000:
                embed.add_field(name="(Continued)", value=msg[1000:], inline=False)
            embed.add_field(name="To:", value=f"<@{member.id}> ({member.id})", inline=False)
            embed.add_field(name="From:", value=f"<@{author.id}> ({author.id})", inline=False)
            await interaction.response.send_message('Sent the following message:', embed=embed)

        except:
            await interaction.response.send_message("I cannot send that user a message! Please ask them to open their PMs!", ephemeral=True)

@client.listen()
async def on_message(message):
    if not isinstance(message.channel, discord.DMChannel) or message.author.bot:
        return
    else:
        guild = client.get_guild(944668000072630312)
        author = await guild.fetch_member(message.author.id)
        if not author:
            author = message.author

    content = message.clean_content

    embed = discord.Embed()
    embed.set_author(name="{} ({}#{})".format(author.display_name, author.name, author.discriminator),
            icon_url=author.avatar.url)
    embed.timestamp = message.created_at
    embed.set_footer(text='User ID: {}'.format(author.id))
    embed.color = author.color

    embed.add_field(name="Message", value=content[:1000] or "blank")
    if len(content[1000:]) > 0:
        embed.add_field(name="(Continued)", value=content[1000:])
    
    channel = client.get_channel(1028508949516922910)
    await channel.send(content=f"{message.author.id}", embed=embed)

    try:
        await message.add_reaction('📬')
    except discord.ext.commands.errors.CommandInvokeError:
        await message.channel.send('📬')

    client.last_user = author
    await client.process_commands(message)
        
@client.tree.command(guild=discord.Object(id=944668000072630312), description="Remind yourself something.")
@app_commands.describe(time="How long until I remind you?")
@app_commands.describe(reminder="What should I remind you?")
async def remindme(interaction: discord.Interaction, time: str, reminder: str):
    format = datetime.now(tz=pytz.timezone('America/Tijuana'))
    formatted = format.strftime("%m/%d/%y, %I:%M %p")
    a = DT.datetime.now().timestamp()
    b = int(a)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM reminders')
    rows = await cursor.fetchall()
    try:
        time_list = re.split('(\d+)',time)
        if time_list[2] == "s":
            time_in_s = int(time_list[1])
        if time_list[2] == "m":
            time_in_s = int(time_list[1]) * 60
        if time_list[2] == "h":
            time_in_s = int(time_list[1]) * 60 * 60
        if time_list[2] == "d":
            time_in_s = int(time_list[1]) * 60 * 60 * 24
        timestamp = DT.datetime.now().timestamp()
        x = datetime.now() + timedelta(seconds=time_in_s)
        timestamp = x.timestamp()
        a = int(timestamp)
        b = int(a)
        cursor = await db.execute('INSERT INTO reminders VALUES (?,?,?,?);', (interaction.user.id, f'{reminder}', timestamp, interaction.channel.id))
        await db.commit()
        await db.close()
        await interaction.response.send_message(f"I'll remind you of `{reminder}` at <t:{b}:F>! (<t:{b}:R>)")
        return
    except:
        await interaction.response.send_message(f'Please retry this command again! There seems to be an error. \nIn the time, assure that you only have `s`, `m`, `h` or `d`.')
        e = await interaction.original_response()
        await asyncio.sleep(10)
        await e.delete()
        return

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Unmute a member.")
@app_commands.describe(member="Who would you like to unmute?")
@app_commands.describe(reason="What's the reason to this unmute? (Optional)")
@app_commands.default_permissions(administrator=True)
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: Optional[str]):
    b = DT.datetime.now().timestamp()
    b = int(b)
    modlogs = client.get_channel(1027778386178875472)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT * FROM mutes')
    muted = discord.utils.get(interaction.guild.roles, name="Muted")
    members = discord.utils.get(interaction.guild.roles, name="Members")
    if muted not in member.roles:
        await interaction.response.send_message('That user seems to not be muted!')
    if reason == None:
        try:
            try:
                await db.execute('UPDATE mutes SET time_expired=? WHERE user_ids=?', ('expired', member.id))
                await db.commit()
                await db.close()
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=
                    f"""
{member} ({member.id}) was unmuted by {interaction.user} ({interaction.user.id}) for:

`None`
""",
                    color=0x0CFF00)
                embed.set_author(name=member, icon_url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                await modlogs.send(embed=embed)
                await member.remove_roles(muted)
                await member.add_roles(members)
                await member.send(f"You've been unmuted in **Rasia Network**!")
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            except:
                await db.close()
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=
                    f"""
{member} ({member.id}) was unmuted by {interaction.user} ({interaction.user.id}) for:

`None`
""",
                    color=0x0CFF00)
                embed.set_author(name=member, icon_url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                await modlogs.send(embed=embed)
                await member.remove_roles(muted)
                await member.add_roles(members)
                await member.send(f"You've been unmuted in **Rasia Network**!")
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
        except:
            try:
                await db.execute('UPDATE mutes SET time_expired=? WHERE user_ids=?', ('expired', member.id))
                await db.commit()
                await db.close()
                await member.remove_roles(muted)
                await member.add_roles(members)
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            except:
                await db.close()
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=
                    f"""
{member} ({member.id}) was unmuted by {interaction.user} ({interaction.user.id}) for:

`None`
""",
                    color=0x0CFF00)
                embed.set_author(name=member, icon_url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                await modlogs.send(embed=embed)
                await member.remove_roles(muted)
                await member.add_roles(members)
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
    else:
        try:
            try:
                await db.execute('UPDATE mutes SET time_expired=? WHERE user_ids=?', ('expired', member.id))
                await db.commit()
                await db.close()
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=
                    f"""
{member} ({member.id}) was unmuted by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                    color=0x0CFF00)
                embed.set_author(name=member, icon_url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                await modlogs.send(embed=embed)
                await member.remove_roles(muted)
                await member.add_roles(members)
                await member.send(f"You've been unmuted in **Rasia Network**!")
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            except:
                await db.close()
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=
                    f"""
{member} ({member.id}) was unmuted by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                    color=0x0CFF00)
                embed.set_author(name=member, icon_url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                await modlogs.send(embed=embed)
                await member.remove_roles(muted)
                await member.add_roles(members)
                await member.send(f"You've been unmuted in **Rasia Network**!")
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
        except:
            try:
                await db.execute('UPDATE mutes SET time_expired=? WHERE user_ids=?', ('expired', member.id))
                await db.commit()
                await db.close()
                await member.remove_roles(muted)
                await member.add_roles(members)
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return
            except:
                await db.close()
                await member.remove_roles(muted)
                await member.add_roles(members)
                await interaction.response.send_message(f'Unmuted {member}')
                e = await interaction.original_response()
                await asyncio.sleep(5)
                await e.delete()
                return


@client.tree.command(guild=discord.Object(id=944668000072630312), description="Unban a Member ID.")
@app_commands.describe(userid="What's the user's ID you would like to unban?")
@app_commands.describe(reason="What's the reason to the unban? (Optional)")
@app_commands.default_permissions(administrator=True)
async def unban(interaction: discord.Interaction, userid: str, reason: Optional[str]):
    try:
        id = int(userid)
    except:
        await interaction.response.send_message("You must send a valid integer!", ephemeral=True)
        return
    a = DT.datetime.now().timestamp()
    b = int(a)
    modlogs = client.get_channel(1027778386178875472)
    db = await aiosqlite.connect('database.db')
    await db.execute('SELECT * FROM bans')
    if reason == None:
        try:
            user = await client.fetch_user(id)
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title="Member Unbanned",
                description=
                f"""
{user} ({id}) was unbanned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0x08A200)
            embed.set_author(name=user, icon_url=user.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            try:
                try:
                    await db.execute('UPDATE bans SET time_expired=? WHERE user_ids=?', ('expired', id))
                    await db.commit()
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
                except:
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    e = await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
            except:
                embed = discord.Embed(
                    title="Member Unbanned",
                    description=
                    f"""
{user} ({id}) was unbanned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                    color=0x08A200)
                embed.set_author(name=user, icon_url=user.display_avatar.url)
                embed.timestamp = datetime.now()
                await modlogs.send(embed=embed)
                try:
                    await db.execute('UPDATE bans SET time_expired=? WHERE user_ids=?', ('expired', id))
                    await db.commit()
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    e = await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
                except:
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
        except:
            await interaction.response.send_message('That member seems to not be banned!', ephemeral=True)
    else:
        try:
            user = await client.fetch_user(id)
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title="Member Unbanned",
                description=
                f"""
{user} ({id}) was unbanned by {interaction.user} ({interaction.user.id}) for:

{reason}
""",
                color=0x08A200)
            embed.set_author(name=user, icon_url=user.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
            try:
                try:
                    await db.execute('UPDATE bans SET time_expired=? WHERE user_ids=?', ('expired', id))
                    await db.commit()
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
                except:
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
            except:
                try:
                    await db.execute('UPDATE bans SET time_expired=? WHERE user_ids=?', ('expired', id))
                    await db.commit()
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
                except:
                    await db.close()
                    await interaction.response.send_message(f'Unbanned {user}')
                    await interaction.original_response()
                    await asyncio.sleep(5)
                    await e.delete()
                    return
        except:
            await interaction.response.send_message('That member seems to not be banned!', ephemeral=True)

#\\\\\\\\\\\\Check For Reminders////////////
@tasks.loop(seconds = 30)
async def remindme():
    await client.wait_until_ready()
    guild = client.get_guild(944668000072630312)
    b = DT.datetime.now().timestamp()
    b = int(b)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT time_expired, user_ids, reminder, channel_id FROM reminders')
    a = await cursor.fetchall()
    for row in a:
        await asyncio.sleep(1)
        if row[0] == 'null':
            continue
        if row[0] <= DT.datetime.now().timestamp():
            cursor = await db.execute('UPDATE reminders SET time_expired=? WHERE time_expired=?', ('null', row[0]))
            await db.commit()
            cursor = await db.execute('SELECT * FROM bans')
            b = int(row[0])
            z = int(row[3])
            channel = client.get_channel(z)
            await channel.send(f'<@{row[1]}>, your reminder for `{row[2]}` just ended!')
    await db.close()

#\\\\\\\\\\\\Check For Un-Bans////////////
@tasks.loop(seconds = 30)
async def bans():
    await client.wait_until_ready()
    guild = client.get_guild(944668000072630312)
    b = DT.datetime.now().timestamp()
    b = int(b)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT time_expired, user_ids, time_issued FROM bans')
    a = await cursor.fetchall()
    for row in a:
        await asyncio.sleep(1)
        stored_timestamp = row[0]
        if row[0] == 'null':
            continue
        if row[0] == 'expired':
            continue
        if row[0] <= DT.datetime.now().timestamp():
            cursor = await db.execute('UPDATE bans SET time_expired=? WHERE time_expired=?', ('expired', row[0]))
            await db.commit()
            member = discord.Object(id=row[1])
            await guild.unban(member)
            modlogs = client.get_channel(1027778386178875472)
            user = guild.get_member(row[1])
            cursor = await db.execute('SELECT * FROM bans')
            b = int(row[0])
            embed = discord.Embed(
                title="Member Unbanned",
                description=
                f"{member} ({member.id}) was unbanned as their ban punishment expired.",
                color=0x08A200)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
    await db.close()

#\\\\\\\\\\\\Check For Un-Mutes////////////
@tasks.loop(seconds = 30)
async def mutes():
    await client.wait_until_ready()
    guild = client.get_guild(944668000072630312)
    b = DT.datetime.now().timestamp()
    b = int(b)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT time_expired, user_ids FROM mutes')
    a = await cursor.fetchall()
    for row in a:
        await asyncio.sleep(1)
        stored_timestamp = row[0]
        if row[0] == 'null':
            continue
        if row[0] == 'expired':
            continue
        if row[0] <= DT.datetime.now().timestamp():
            muted = discord.utils.get(guild.roles, name='Muted')
            farmer = discord.utils.get(guild.roles, name='Members')
            cursor = await db.execute('UPDATE mutes SET time_expired=? WHERE time_expired=?', ('expired', row[0]))
            await db.commit()
            member = guild.get_member(row[1])
            await member.remove_roles(muted)
            await member.add_roles(farmer)
            modlogs = client.get_channel(1027778386178875472)
            user = guild.get_member(row[1])
            cursor = await db.execute('SELECT * FROM mutes')
            b = int(row[0])
            embed = discord.Embed(
                title="Member Unmuted",
                description=
                f"{member} ({member.id}) was unmuted as their mute punishment expired.",
                color=0x0CFF00)
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.timestamp = datetime.now()
            await modlogs.send(embed=embed)
    await db.close()

@client.tree.command(guild=discord.Object(id=944668000072630312), description="View the moderation history of a user.")
@app_commands.describe(member="Who's history would you like to view?")
@app_commands.default_permissions(administrator=True)
async def history(interaction: discord.Interaction, member: discord.User):
    view = HistoryView(member)
    embed = discord.Embed(
        title=f"History of {member}",
        description=
        f"Choose the type of history you would like to view!",
        color=0xff00e6)
    await interaction.response.send_message(embed=embed, view=view)

#\\\\\\\\\\\\Suggestions////////////
@client.event
async def on_message(message):
    guild = client.get_guild(944668000072630312)
    suggestionchannel = guild.get_channel(1026054642968301598)
    if message.channel == suggestionchannel:
        if message.author.bot:
            pass
        if message.author.guild_permissions.administrator:
            pass
        else:
            a = await message.reply('You cannot send messages in this channel! You may only use slash commands.')
            await asyncio.sleep(3)
            await a.delete()
            await message.delete()
    await client.process_commands(message)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Create a server suggestion.")
@app_commands.describe(suggestion="What do you want to suggest?")
async def suggest(interaction: discord.Interaction, suggestion: str):
    suggestionchannel = interaction.guild.get_channel(1026054642968301598)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT suggestions FROM counter')
    rows = await cursor.fetchone()
    await db.execute('UPDATE counter SET suggestions=suggestions + ?', (1,))
    await db.commit()
    await db.close()
    if interaction.channel != suggestionchannel:
        em = discord.Embed(
            title=f"Suggestion #{rows[0]}",
            description=
            f"{suggestion}",
            color=0xff00e6)
        em.set_author(name=f"{interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(f"The suggestion has successfully been submitted to {suggestionchannel.mention}!", ephemeral=True)
        x = await suggestionchannel.send(embed=em)
        await x.add_reaction('<a:thumbsup:1029619486380277830>')
        await x.add_reaction('<a:thumbsdown:1029619500145987656>')
        return
    else:
        em = discord.Embed(
            title=f"Suggestion #{rows[0]}",
            description=
            f"{suggestion}",
            color=0xff00e6)
        em.set_author(name=f"{interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=em)
        x = await interaction.original_response()
        await x.add_reaction('<a:thumbsup:1029619486380277830>')
        await x.add_reaction('<a:thumbsdown:1029619500145987656>')
        return

@client.command()
async def suggestions(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title=f"Suggestions",
        description=
        """
You can make suggestions using the `/suggest` command.

Make them related to the server, any joke suggestions will get you blacklisted from the suggestions system and you will recieve punishments.
""",
        color=0xff00e6)
    await ctx.send(embed=embed)

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Shows what the IP of the server is.")
async def ip(interaction: discord.Interaction):
    await interaction.response.send_message("The server's IP is `canyonnetwork.net`!")

@client.tree.command(guild=discord.Object(id=944668000072630312), description="Shows what the numeric IP of the server is.")
@app_commands.default_permissions(manage_nicknames=True)
async def numip(interaction: discord.Interaction):
    valid_channels = ("general", "apply", "report", "appeal", "other")
    if any(thing in interaction.channel.name for thing in valid_channels):
        await interaction.response.send_message("Try to connect with `131.153.47.134:25621`. This should fix your issue!")
    else:
        await interaction.response.send_message('You can only use this in a ticket channel!', ephemeral=True)

@client.command()
async def ip(ctx):
    await ctx.reply("The server's IP is `canyonnetwork.net`!")

@client.command()
async def testpunishment(ctx, member: discord.Member, reason: str):
    embed = discord.Embed(
        title="Member Warned",
        description=
        f"""
{member} ({member.id}) was warned by {ctx.author} ({ctx.author.id}) for:

{reason}
""",
        color=0xFFFF00)
    embed.set_author(name=member, icon_url=member.display_avatar.url)
    embed.timestamp = datetime.now()
    embed2 = discord.Embed(
        title="Member Muted",
        description=
        f"""
{member} ({member.id}) was muted by {ctx.author} ({ctx.author.id}) for:

{reason}
""",
        color=0xFFA200)
    embed2.set_author(name=member, icon_url=member.display_avatar.url)
    embed2.timestamp = datetime.now()
    embed3 = discord.Embed(
        title="Member Kicked",
        description=
        f"""
{member} ({member.id}) was kicked by {ctx.author} ({ctx.author.id}) for:

{reason}
""",
        color=0xFF0000)
    embed3.set_author(name=member, icon_url=member.display_avatar.url)
    embed3.timestamp = datetime.now()
    embed4 = discord.Embed(
        title="Member Banned",
        description=
        f"""
{member} ({member.id}) was banned by {ctx.author} ({ctx.author.id}) for:

{reason}
""",
        color=0xA50000)
    embed4.set_author(name=member, icon_url=member.display_avatar.url)
    embed4.timestamp = datetime.now()
    embed5 = discord.Embed(
        title="Member Unmuted",
        description=
        f"""
{member} ({member.id}) was unmuted by {ctx.author} ({ctx.author.id}) for:

{reason}
""",
        color=0x0CFF00)
    embed5.set_author(name=member, icon_url=member.display_avatar.url)
    embed5.timestamp = datetime.now()
    embed6 = discord.Embed(
        title="Member Unbanned",
        description=
        f"""
{member} ({member.id}) was unbanned by {ctx.author} ({ctx.author.id}) for:

{reason}
""",
        color=0x08A200)
    embed6.set_author(name=member, icon_url=member.display_avatar.url)
    embed6.timestamp = datetime.now()
    await ctx.send(embeds=[embed, embed2, embed3, embed4, embed5, embed6])

#\\\\\\\\\\\\Error Handler////////////
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, BadArgument):
        a = await ctx.reply('Invalid usage!')
        await asyncio.sleep(5)
        await a.delete()
        await ctx.message.delete()
        return
    if isinstance(error, commands.NotOwner):
        await ctx.message.add_reaction('‼️')
        a = await ctx.reply('You may not use this command!')
        await asyncio.sleep(3)
        await a.delete()
        await ctx.message.delete()
        return
    raise error

client.run('')

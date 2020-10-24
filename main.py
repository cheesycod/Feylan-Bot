import discord
from discord.ext import commands
import asyncpg
import asyncio

free = True  # Whether we are using free plan or not
rp = "."  # Prefix requested by the user


async def setup_db():
	db = await asyncpg.create_pool(
	    host="database-1.civhw5bah3rj.us-east-2.rds.amazonaws.com",
	    user="postgres",
	    password="Waterbot123",
	    database="PantherDev")  #Login stuff
	await db.execute(
	    "CREATE TABLE IF NOT EXISTS stocks (category TEXT NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL)"
	)
	await db.execute(
	    "CREATE TABLE IF NOT EXISTS categories (category TEXT NOT NULL)")
	return db


client = discord.ext.commands.AutoShardedBot(command_prefix=rp)
db = asyncio.get_event_loop().run_until_complete(setup_db())


@client.event
async def on_ready():
	if free:
		await client.change_presence(
		    activity=discord.Game(name=f"{rp}help | Panther Development"))
	else:
		await client.change_presence(activity=discord.Game(name=f"{rp}help"))
	print(f"{str(client.user)}")


#@client.event
#async def on_command_error(ctx, error):
#  print(ctx, error)


@commands.has_permissions(manage_guild=True)
@client.command(pass_context=True)
async def stockadd(ctx, category, account):
	embed = discord.Embed()
	if category == None:
		embed.add_field(
		    name="**Error**",
		    value=
		    "You have not specified a category.\n**Usage: **.stockadd <category> <username>:<password>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	elif account == None:
		embed.add_field(
		    name="**Error**",
		    value=
		    "You have not given an account to add.\n**Usage: **.stockadd <category> <username>:<password>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	try:
		username = account.split(":")[0]
		password = account.split(":")[1]
	except IndexError:
		embed.add_field(
		    name="**Error**",
		    value=
		    "You have not specified a proper account of format <username>:<password> (EX: testuser:1234).\n**Usage: **.stockadd <category> <username>:<password>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	if username in ["", " "] or password in ["", " "]:
		embed.add_field(
		    name="**Error**",
		    value=
		    "You have not specified a proper account of format <username>:<password> (EX: testuser:1234).\n**Usage: **.stockadd <category> <username>:<password>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	r = await db.fetch("SELECT * from categories WHERE category = $1",
	                   category)
	if len(r) == 0:
		embed.add_field(
		    name="**Error**",
		    value=
		    "The specified category does not exist. Please create it using .add <category>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	r = await db.fetch("SELECT username from stocks WHERE username = $1",
	                   username)
	if len(r) != 0:
		embed.add_field(
		    name="**Error**",
		    value="The specified account is already in the stock")
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	await db.execute("INSERT INTO stocks VALUES ($1, $2, $3)", category,
	                 username, password)
	embed.add_field(
	    name="**Success**", value="Successfully added account to generator")
	if free:
		embed.set_footer(text="Bot Made By Panther Development")
	await ctx.send(embed=embed)


@commands.has_permissions(manage_guild=True)
@client.command(pass_context=True)
async def add(ctx, category):
	embed = discord.Embed()
	r = await db.fetch("SELECT category from categories WHERE category = $1",
	                   category)
	if len(r) != 0:
		embed.add_field(
		    name="**Error**",
		    value=
		    "The specified category already exists. You can add to the stock using .stockadd"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	await db.execute("INSERT INTO categories VALUES ($1)", category)
	embed.add_field(
	    name="**Success**", value="Successfully added category to generator")
	if free:
		embed.set_footer(text="Bot Made By Panther Development")
	await ctx.send(embed=embed)


@commands.has_permissions(manage_guild=True)
@client.command(pass_context=True)
async def delete(ctx, category):
	embed = discord.Embed()
	r = await db.fetch("SELECT category from categories WHERE category = $1",
	                   category)
	if len(r) == 0:
		embed.add_field(
		    name="**Error**",
		    value="The specified category does not already exist.")
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	await db.execute("DELETE FROM categories WHERE category = $1", category)
	await db.execute("DELETE FROM stocks WHERE category = $1", category)
	embed.add_field(
	    name="**Success**",
	    value="Successfully deleted category from generator")
	if free:
		embed.set_footer(text="Bot Made By Panther Development")
	await ctx.send(embed=embed)


@client.command(pass_context=True)
async def stock(ctx, category=None):
	if category == None:
		catlist = await db.fetch("SELECT category from categories")
		msg = discord.Embed(title="Stock", color=discord.Color.green())
		for category in catlist:
			category = category["category"]
			r = await db.fetch(
			    "SELECT COUNT(*) FROM stocks WHERE category = $1", category)
			msg.add_field(
			    name=f"**{category}**",
			    value=f"{r[0]['count']}\n",
			    inline=False)
		if free:
			msg.set_footer(text="Bot Made By Panther Development")
		await ctx.send(embed=msg)
	else:
		embed = discord.Embed()
		r = await db.fetch("SELECT COUNT(*) FROM stocks WHERE category = $1",
		                   category)
		if len(r) == 0:
			embed.add_field(
			    name="**Error**",
			    value=
			    "The specified category does not exist. Please create it using .add <category>"
			)
			if free:
				embed.set_footer(text="Bot Made By Panther Development")
			return await ctx.send(embed=embed)
		r = r[0]['count']
		msg = discord.Embed(title=category)
		msg.add_field(name=f"**Stock for category {category}.**", value=str(r))
		if free:
			msg.set_footer(text="Bot Made By Panther Development")
		await ctx.send(embed=msg)


@client.command(pass_context=True)
async def gen(ctx, category=None):
	# We must have a category. Otherwise, give a meaningful error in an embed
	embed = discord.Embed()
	if category == None:
		embed.add_field(
		    name="**Error**",
		    value=
		    "You have not specified a category.\n**Usage: **.gen <category>")
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	r = await db.fetch("SELECT * from categories WHERE category = $1",
	                   category)
	if len(r) == 0:
		embed.add_field(
		    name="**Error**",
		    value=
		    "The specified category does not exist. Please create it using .add <category>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	r = await db.fetch("SELECT * FROM stocks WHERE category = $1",
	                   category)  # Get a account from stock
	if len(r) == 0:
		embed.add_field(
		    name="**Error**",
		    value=
		    "The specified category is out of stock. Please try again later or add more stock using .stockadd <category> <username>:<password>"
		)
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	# Choose the first one in stock
	username = r[0]["username"]
	password = r[0]["password"]
	embed.add_field(
	    name="**Account Details**",
	    value=f"**Username: **{username}\n**Password: **{password}")
	if free:
		embed.set_footer(text="Bot Made By Panther Development")
	await db.execute("DELETE from stocks WHERE username = $1", username)
	await ctx.author.send(embed=embed)


@client.command(pass_context=True)
async def announce(ctx, role: discord.Role, channel: discord.TextChannel,
                   *msg):
	msg = " ".join(msg)
	await channel.send(f"{role.mention} {msg}")


@client.event
async def on_command_error(ctx, error):
	if ctx.message.content.startswith(".announce"):
		embed = discord.Embed()
		embed.add_field(
		    name="**Error**",
		    value=
		    "Incorrect usage\n**Usage: **.announce <role> <channel> <message>")
		if free:
			embed.set_footer(text="Bot Made By Panther Development")
		return await ctx.send(embed=embed)
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(":x: You don't have permission to do this!")
	print(ctx, error)


client.run("NzY4OTE2MDEzODEwNTgxNTM0.X5Ha1w.1m4DZhpWDvhllov1tzbbHYnDMxg")

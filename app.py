import discord
from discord.ext import commands
import os  # 👈 ADDED (needed for env token)

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================================================
# 🔧 CONFIG (YOUR STUFF KEPT)
# ==================================================

OWNER_ID = 632993587994296323

SHOP_TITLE = "<:Shop:1500983581340729375> Cop Shop"
SHOP_DESCRIPTION = "Welcome to Cop Shop.\nSelect a product below to open a ticket."
SHOP_COLOR = discord.Color.from_rgb(20, 20, 20)

SHOP_BANNER = "https://media.discordapp.net/attachments/1495421349953409124/1500989013824372838/fd25ee0e-6020-4477-b54c-166535df0e86.png?ex=69fa7073&is=69f91ef3&hm=2fa6a1e77ad3ff14f01b1e82e9ffa63e689326fd7ecc2c50000492b896da4a59&=&format=webp&quality=lossless&width=1086&height=543"
SHOP_FOOTER = "Fast • Secure • Trusted"

CATEGORY_ID = 1499570366350360687

CLOSE_BUTTON_LABEL = "Close Ticket"
CLOSE_BUTTON_EMOJI = "<:lock:1500987811007037633>"

# ==================================================
# 🛍️ PRODUCTS (UNCHANGED)
# ==================================================

PRODUCTS = [
    {
        "label": "Mines Access",
        "description": "Full access to Mines predictor",
        "emoji": "<:BombShock:1499540896658755834>",
        "ticket_name": "mines",
        "price": "350 Robux"
    },
    {
        "label": "Mines + Towers",
        "description": "Full bundle access",
        "emoji": "<:Bloxflip:1499540517183033504>",
        "ticket_name": "bundle",
        "price": "500 Robux"
    },
    {
        "label": "User Sniper",
        "description": "Snipe Rare users!",
        "emoji": "<:Scope:1500984269563101325>",
        "ticket_name": "user-sniper",
        "price": "100 Robux"
    }
]

# ==================================================
# 🎟️ CLOSE BUTTON
# ==================================================

class CloseView(discord.ui.View):
    def __init__(self, ticket_owner_id):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id

    @discord.ui.button(label=CLOSE_BUTTON_LABEL, style=discord.ButtonStyle.red, emoji=CLOSE_BUTTON_EMOJI)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.ticket_owner_id and interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ You can't close this ticket.", ephemeral=True)
            return

        await interaction.response.send_message("<:lock:1500987811007037633> Closing ticket...", ephemeral=True)
        await interaction.channel.delete()

# ==================================================
# 🎟️ DROPDOWN
# ==================================================

class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = []

        for product in PRODUCTS:
            options.append(
                discord.SelectOption(
                    label=product["label"],
                    description=f"{product['description']} • {product['price']}",
                    emoji=product["emoji"]
                )
            )

        super().__init__(
            placeholder="Select a product...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        product = next(p for p in PRODUCTS if p["label"] == selected)

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, id=CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_member(OWNER_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{product['ticket_name']}-{user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎟️ Purchase Ticket",
            description=f"{user.mention} selected **{product['label']}**\n\u200b",
            color=discord.Color.green()
        )

        embed.add_field(name="📦 Product", value=product["label"], inline=True)
        embed.add_field(name="<:robux:1500986555240550511> Price", value=product["price"], inline=True)

        embed.set_footer(text="Use the button below to close this ticket.")

        await channel.send(embed=embed, view=CloseView(user.id))

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

# ==================================================
# 🛒 SLASH COMMAND (UPGRADED UI)
# ==================================================

@bot.tree.command(name="shop", description="Open the shop panel")
async def shop(interaction: discord.Interaction):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Not allowed.", ephemeral=True)
        return

    embed = discord.Embed(
        title=SHOP_TITLE,
        description=f"{SHOP_DESCRIPTION}\n\u200b",
        color=SHOP_COLOR
    )

    if SHOP_BANNER != "PUT_YOUR_IMAGE_URL_HERE":
        embed.set_image(url=SHOP_BANNER)

    product_list = ""
    for p in PRODUCTS:
        product_list += (
            f"{p['emoji']} **{p['label']}**\n"
            f"<:robux:1500986555240550511> {p['price']}\n"
            f"\u200b\n"
        )

    embed.add_field(
        name="<:cash:1495540023104241787> Available Products",
        value=product_list,
        inline=False
    )

    embed.add_field(
        name="<a:emojigg_1:1500952766649073868> How to Buy",
        value="Select a product from the dropdown below.\n\u200b",
        inline=False
    )

    embed.set_footer(text=SHOP_FOOTER)

    await interaction.response.send_message(embed=embed, view=ShopView())

# ==================================================
# 🚀 READY
# ==================================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ==================================================
# 🔑 RUN (SECURE TOKEN)
# ==================================================

bot.run(os.getenv("DISCORD_TOKEN"))

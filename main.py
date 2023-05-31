import discord
import wavelink
from discord.ext import commands
from info import TOKEN
import aiohttp
import io
import time
import random
import openai
import subprocess
import threading
import os


class Bot(commands.Bot):
    
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix='!')

    async def on_ready(self) -> None:
        print(f'Logged in {self.user} | {self.user.id}')

    async def setup_hook(self) -> None:

        node: wavelink.Node = wavelink.Node(uri='http://localhost:5000', password='PASSWORD')
        await wavelink.NodePool.connect(client=self, nodes=[node])


bot = Bot()


@bot.command(name="play", aliases=["p"])
async def play(ctx: commands.Context, *, search: str) -> None:


    if not ctx.voice_client:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        vc: wavelink.Player = ctx.voice_client

    if search.startswith("http"):
        track = await wavelink.GenericTrack.search(search, return_first=True)
    else:
        track = await wavelink.YouTubeTrack.search(search, return_first=True)


    if track:
        if vc.is_playing():

            vc.queue.put(item=track)
            mbed = discord.Embed(title=f"Трек добавлен в очередь:", description=f"{track}", color=discord.Color.from_rgb(255, 255, 255))
            mbed.set_thumbnail(url=f"{track.thumb}")
            mbed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar.url)
            await ctx.send(embed=mbed)
        
        else:
            await vc.play(track)
            mbed = discord.Embed(title=f"Трек добавлен:", description=f"{track}", color=discord.Color.from_rgb(255, 255, 255))
            mbed.set_thumbnail(url=f"{track.thumb}")
            mbed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar.url)
            await ctx.send(embed=mbed)
        


@bot.command(name="disconnect", aliases=["dis", "leave", "l"])
async def disconnect(ctx: commands.Context) -> None:

        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()


@bot.command(name="pause")
async def pause(ctx: commands.Context) -> None:

        vc: wavelink.Player = ctx.voice_client
        await vc.pause()


@bot.command(name="resume")
async def resume(ctx: commands.Context) -> None:

        vc: wavelink.Player = ctx.voice_client
        await vc.resume()


@bot.command(name="volume", aliases=["vol"])
async def pause_command(ctx: commands.Context, to: int):

        vc: wavelink.Player = ctx.voice_client

        if 0 <= to <= 100:
            await vc.set_volume(to)
            mbed = discord.Embed(title=f"Громкость установлена: {to}%", color=discord.Color.from_rgb(255, 255, 255))
            await ctx.send(embed=mbed)


@bot.command(name="song")
async def song_name(ctx: commands.Context) -> None:

        vc: wavelink.Player = ctx.voice_client
        mbed = discord.Embed(title=f"Трек:", description=f"{vc.current}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)


# @bot.command(name="karaoke")
# async def karaoke_mode(ctx: commands.Context) -> None:

#     vc: wavelink.Karaoke.Player = ctx.voice_client
#     await vc.play(vc.current)


@bot.command(name="skip")
async def skip(ctx: commands.Context):

        vc: wavelink.Player = ctx.voice_client
        if vc:
            if not vc.is_playing():
                mbed = discord.Embed(title=f"Ничего не играет", color=discord.Color.from_rgb(255, 255, 255))
                await ctx.send(embed=mbed)
            if vc.queue.is_empty:
                await vc.stop()
            
            await vc.seek(vc.current.length * 1000)
            if not vc.queue.is_empty:
                await vc.play(vc.queue.get())

            if vc.is_paused():
                await vc.resume()
        
        else:
            mbed = discord.Embed(title=f"Бот не находится в канале", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)


@bot.command(name="create_teams6", aliases=['ct6'])
async def create_teams(ctx: commands.Context, team_length = 1, p1: discord.Member = None, p2: discord.Member = None, 
                       p3: discord.Member = None, p4: discord.Member = None, p5: discord.Member = None, 
                       p6: discord.Member = None) -> None:
        nums = [[p1.avatar.url, p1.name], [p2.avatar.url, p2.name], [p3.avatar.url, p3.name], [p4.avatar.url, p4.name], [p5.avatar.url, p5.name], [p6.avatar.url, p6.name]] 
        team = []
        number = 1
        count = 0

        while nums != []: 
            a = random.choice(nums) 
            nums.pop(nums.index(a)) 
            team.append(a)
            count += 1
            if len(team) == team_length:
                
                mbed = discord.Embed(title=f"Команда №{number}", color=discord.Color.from_rgb(255, 255, 255))
                for i in range(0, count):
                    mbed.add_field(name=team[i][1], value=' ')
                    
                mbed.set_thumbnail(url=team[0][0])
                await ctx.send(embed=mbed)
                team = []
                number += 1
                count = 0

    
@bot.command(name="create_teams", aliases=['ct'])
async def create_teams(ctx: commands.Context, people: int, team_length: int):

        nums = [i for i in range(1, people + 1)]
        team = []
        teams = []

        while nums != []: 
            a = random.choice(nums) 
            nums.pop(nums.index(a)) 
            team.append(a) 
            if len(team) == team_length: 
                teams.append(team)
                team = [] 
            if (team != team_length) and (nums == []):
                teams.append(team)
        
        await ctx.send(teams)
        # await ctx.send(' '.join(create_teams(nums, team_length, team, teams)))


@bot.command(name="gpt")
async def gpt_response(ctx: commands.Context, message_inp: str):

        openai.api_key = os.getenv("OPENAI_KEY")

        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"{message_inp}"}
        ],
        )

        mbed = discord.Embed(title="Response", description=f"{completion.choices[0].message.content}")
        await ctx.send(embed=mbed)

@bot.command(name="image")
async def gen_img(ctx: commands.Context, message_inp: str):
     
    openai.api_key = os.getenv("OPENAI_KEY")

    completion = openai.Image.create(
          prompt=message_inp,
          n=1,
          size="1024x1024"
    )

    image_url = completion["data"][0]["url"]
    async with aiohttp.ClientSession() as session: # creates session
        async with session.get(image_url) as response: # gets image from url
            image = await response.read() # reads image from response
            with io.BytesIO(image) as file: # converts to file-like object
                await ctx.send(file=discord.File(file, "testimage.png"))
            

def start_lavalink():
    try:
        subprocess.call([r'Directory to Lavalink.jar --> .bat'])
    except Exception as e:
        print(e)

    

if __name__ == "__main__":

    thr = threading.Thread(target=start_lavalink, name="thr-1")
    thr.start()

    time.sleep(6)

    try:
        bot.run(TOKEN)
    except Exception as e:
        print(e)
 

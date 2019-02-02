from imports import *

async def run():
    bot = Bot()
    await bot.start(config.bot_token)

class Bot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self._get_prefix)
        self.modules = {}
        self.loop.create_task(self.load_modules())
    
    async def _get_prefix(self, bot, message):
        prefix = utils.returnPrefix()
        return commands.when_mentioned_or(prefix)(bot, message)
    
    async def load_modules(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)
        modules = [x.stem for x in pathlib.Path('modules').glob('*.py')]
        for module in modules:
            try:
                self.load_extension(f"modules.{module}")
                utils.startupLogs.append(f"Loaded : {module}")
            except Exception as e:
                utils.startupLogs.append(f"Failed to load : {module} ({e})")
        
        e = embed(title="Startup Logs", description="\n".join(utils.startupLogs), customThumbnail=self.user.avatar_url, customFooter=True)
        footer(e, text="Logs", icon=self.user.avatar_url)
        
        channel = self.get_channel(utils.logsChannel)
        await channel.send(embed=e)
    
    async def on_ready(self):
        print("Ready")
        self.loop.create_task(self.reload_modules())

    async def on_message(self, message):
        if message.author.bot:
            return 
        
        await self.process_commands(message)

    async def reload_modules(self):
        enabled = True

        if not enabled:
            return 

        while True:
            utils.startupLogs.clear()
            modules = [x.stem for x in pathlib.Path('modules').glob('*.py')]
            files = []

            for module in modules:
                files.append(f'modules/{module}.py')

            for file in files:
                f = open(file, 'r')
                try:
                    if not self.modules[file] == f.read():
                        x = open(file, 'r')
                        self.modules[file] = x.read()

                        try:
                            self.unload_extension(f"modules.{file[8:-3]}")
                            self.load_extension(f"modules.{file[8:-3]}")
                            utils.startupLogs.append(f"Reloaded : {file}")
                        except Exception as e:
                            utils.startupLogs.append(f"Didn't reload : {file} ({e})")                           
                except KeyError:
                    self.modules[file] = f.read()
            
            if utils.startupLogs != []:
                channel = self.get_channel(utils.logsChannel)
                e = embed(title="Reload Module/s", description="\n".join(utils.startupLogs), customThumbnail=self.user.avatar_url, customFooter=True)
                footer(e, text="Bot", icon=self.user.avatar_url)
                await channel.send(embed=e) 

            await asyncio.sleep(1) 

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
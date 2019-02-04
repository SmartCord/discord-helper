from imports import * 

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

class Developer:
    def __init__(self, bot):
        self.bot = bot 


    @commands.command(pass_context=True, name="eval")
    @commands.is_owner()
    async def cool_eval_bullshit(self, ctx, *, body: str):
        """ Code from R.Danny bot yeyey k, modified to fit my other bullshit """
        env = {
            'self':self,
            'ctx':ctx,
            'discord':discord
        }
        env.update(globals())
        body = cleanup_code(body)
        std = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e}\n```')

        func = env['func']

        try:
            with redirect_stdout(std):
                ret = await func()
        except Exception as e:
            value = std.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = std.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass
            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

def setup(bot):
    bot.add_cog(Developer(bot))
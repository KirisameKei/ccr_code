import discord,random,asyncio,os

client = discord.Client()

@client.event
async def on_ready():
    print(f"{client.user.name}がログインしました。")

@client.event
async def on_message(message):
    if message.content == "!start":
        await bosyuu(message)

async def bosyuu(message):
    sankasya_list = []
    
    sankasya_list.append(message.author)

    n = 1
    while True:
        await message.channel.send(f"チンチロリン募集中「!join」で参加でき、「!leave」で抜けられます。(募集をかけた人は抜けられません)\n{message.author.name}さんが「!end」を実行すると募集を終了します。\n現在{n}人参加中")
        def check1(m):
            return m.channel == message.channel and ((m.content == "!join" and m.author not in sankasya_list) or (m.content == "!leave" and m.author in sankasya_list) or (m.content == "!end" and m.author == message.author))
        reply = await client.wait_for("message",check=check1)
        if reply.content == "!join":
            sankasya_list.append(reply.author)
            n = n + 1
        elif reply.content == "!leave":
            if reply.author == message.author:
                await message.channel.send("募集をかけた人は抜けられません。")
            else:
                sankasya_list.remove(reply.author)
                n = n - 1
        else:
            break

    await message.channel.send("募集終了")
    if len(sankasya_list) == 1:
        await message.channel.send("えー待ったんですけども参加者は誰一人来ませんでした。")
        return
    await dicide_oya(message,sankasya_list)


async def dicide_oya(message,sankasya_list):
    await message.channel.send("親になりたい人は「!oya」を入力してください。")

    def check2(m):
        return m.channel == message.channel and m.content == "!oya" and m.author in sankasya_list
    reply = await client.wait_for("message",check=check2)
    oya = reply.author
    await message.channel.send(f"{oya.name}さんが親です。")
    children_list = sankasya_list
    children_list.remove(oya)
    
    await dicide_max_bet(message,sankasya_list,oya,children_list)


async def dicide_max_bet(message,sankasya_list,oya,children_list):
    await message.channel.send(f"{oya.name}さん、bet額上限を入力してください。(半角数字とstが使用できます。)")
    while True:
        def check3(m):
            return m.channel == message.channel and m.author == oya
        reply = await client.wait_for("message",check=check3)
        try:
            reply = reply.content
            reply = reply.replace("st","*64")
            max_bet = eval(reply)
            if max_bet <= 0:
                await message.channel.send("1以上にしてください。")
            else:
                if max_bet % 1 == 0:
                    max_st,max_ko = divmod(max_bet,64)
                    break
                else:
                    await message.channel.send("小数点が発生しました。やり直してください。")
        except:
            await message.channel.send("使える文字は半角数字、stのみです。")
    await ko_bet_time(message,sankasya_list,oya,children_list,max_st,max_ko,max_bet)


async def ko_bet_time(message,sankasya_list,oya,children_list,max_st,max_ko,max_bet):
    bet_dic = {}
    for mem in children_list:
        await message.channel.send(f"{mem.name}さん、bet額を入力してください。上限は{max_st}st+{max_ko}個です。(半角数字とstが使用できます。)\n(この回を降りる場合0と入力できます。(でもさいころは振ってね))")
        while True:
            def check4(m):
                return m.channel == message.channel and m.author == mem
            try:
                reply_ = await client.wait_for("message",check=check4,timeout=30)
            except asyncio.TimeoutError:
                await message.channel.send(f"{mem.mention}あくしろよ")
            else:
                try:
                    reply = reply_.content
                    reply = reply.replace("st","*64")
                    bet = eval(reply)
                    if bet > max_bet:
                        await message.channel.send("上限より多い額を賭けています。やり直してください。")
                    elif bet < 0:
                        await message.channel.send("マイナスの額は賭けられません。やり直してください。")
                    elif not bet % 1 == 0:
                        await message.channel.send("小数点が発生しました。やり直してください。")
                    else:
                        bet_dic[reply_.author.id] = bet
                        break
                except:
                    await message.channel.send("使える文字は半角数字、stのみです。")

    await ccr_time(message,sankasya_list,oya,children_list,bet_dic,max_st,max_ko,max_bet)


async def ccr_time(message,sankasya_list,oya,children_list,bet_dic,max_st,max_ko,max_bet):
    def check5(m):
        return m.channel == message.channel and m.author == oya and m.content == "!ccr"

    for i in range(3):
        await message.channel.send(f"{oya.name}さん、「!ccr」を実行してください。")
        await client.wait_for("message",check=check5)
        parameter = await ccr(message,i)
        if parameter != 0:
            break

    if parameter == 1:
        bairitu = 5
    elif parameter == 2:
        bairitu = 3
    elif parameter == 3:
        bairitu = 2
    elif parameter == ":six:":
        bairitu = 1
    elif parameter == ":one:":
        bairitu = -1
    elif parameter == 5:
        bairitu = -1
    elif parameter == 6:
        bairitu = -2
    
    else:#returnで目が帰ってくるから絵文字を数値に変換する
        parameter = parameter.replace(":two:","2")
        parameter = parameter.replace(":three:","3")
        parameter = parameter.replace(":four:","4")
        parameter = parameter.replace(":five:","5")
        oya_deme = int(parameter)

    try:
        description = ""
        for mem_id in bet_dic.keys():
            bet = bet_dic[mem_id]
            siharai = bet * bairitu
            if siharai < 0:
                siharai = siharai * -1
                harau_morau = "貰う"
            elif siharai == 0:#子が勝負をおりていた場合
                harau_morau = "やり取りなし"
            else:#親が正の役を出した場合
                harau_morau = "払う"
            st,ko = divmod(siharai,64)
            description += f"<@!{mem_id}>:{st}st+{ko}個{harau_morau}\n"
        embed = discord.Embed(title="支払い額",description=description)
        await message.channel.send(embed=embed)
    except NameError:
        description = ""
        for mem in children_list:
            for i in range(3):
                while True:
                    await message.channel.send(f"{mem.name}さん、「!ccr」を実行してください。")
                    def check6(m):
                        return m.channel == message.channel and m.author == mem and m.content == "!ccr"
                    try:
                        reply = await client.wait_for("message",check=check6,timeout=10)
                    except asyncio.TimeoutError:
                        await message.channel.send(f"{mem.mention}あくしろよ")
                    else:
                        parameter = await ccr(message,i)
                        break
                if parameter != 0:
                    break

            if parameter == 1:
                bairitu = 5
            elif parameter == 2:
                bairitu = 3
            elif parameter == 3:
                bairitu = 2
            elif parameter == 5:
                bairitu = -1
            elif parameter == 6:
                bairitu = -2
    
            else:#returnで目が帰ってくるから絵文字を数値に変換する
                parameter = parameter.replace(":one:","1")
                parameter = parameter.replace(":two:","2")
                parameter = parameter.replace(":three:","3")
                parameter = parameter.replace(":four:","4")
                parameter = parameter.replace(":five:","5")
                parameter = parameter.replace(":six:","6")
                ko_deme = int(parameter)

                if oya_deme > ko_deme:
                    bairitu = -1
                if oya_deme == ko_deme:
                    bairitu = 0
                if oya_deme < ko_deme:
                    bairitu = 1
            bet = bet_dic[mem.id]
            siharai = bet * bairitu
            if siharai < 0:
                siharai = siharai * -1
                harau_morau = "払う"
            elif siharai == 0:
                harau_morau = "やり取りなし"
            else:
                harau_morau = "貰う"
            st,ko = divmod(siharai,64)
            description += f"{mem.mention}:{st}st+{ko}個{harau_morau}\n"
        embed = discord.Embed(title="支払い額",description=description)
        await message.channel.send(embed=embed)

    await next_match(message,sankasya_list,oya,children_list,bet_dic,max_st,max_ko,max_bet)

async def next_match(message,sankasya_list,oya,children_list,bet_dic,max_st,max_ko,max_bet):
    description = "1:現在の設定で続ける\n2:bet上限を変える\n3:親を変える\n4:メンバーを変える\n5:終了する"
    embed = discord.Embed(title="次の試合はどうしますか？親が数字で入力してください。",description=description)
    await message.channel.send(embed=embed)
    def check7(m):
        return m.channel == message.channel and m.author == oya and (m.content == "1" or m.content == "2" or m.content == "3" or m.content == "4" or m.content == "5")
    reply = await client.wait_for("message",check=check7)
    if reply.content == "1":
        await ko_bet_time(message,sankasya_list,oya,children_list,max_st,max_ko,max_bet)
    elif reply.content == "2":
        await dicide_max_bet(message,sankasya_list,oya,children_list)
    elif reply.content == "3":
        sankasya_list.append(oya)
        await dicide_oya(message,sankasya_list)
    elif reply.content == "4":
        await message.channel.send("「!start」からやり直してください。")
    else:
        await message.channel.send("試合を終了します。")
        await asyncio.sleep(60)
        await message.channel.send("「!start」で参加者の募集を開始します。")
        
        
async def ccr(message,i):
    kazu = [
        ":one:",
        ":two:",
        ":three:",
        ":four:",
        ":five:",
        ":six:"
    ]
    select = random.choices(kazu,k=3)#出たさいころの目
    saikoro_no_me = "".join(select)
    await message.channel.send(saikoro_no_me)

    select.sort()

    if select[0] == select[1] == select[2]:
        if select[0] == ":one:":
            await message.channel.send(f"ピンゾロ！5倍づけ！")
            return 1
        else:
            await message.channel.send(f"ゾロ目！3倍づけ！")
            return 2

    elif select[0] == select[1]:
        await message.channel.send(f"目は{select[2]}です。")
        return select[2]
    elif select[1] == select[2]:
        await message.channel.send(f"目は{select[0]}です。")
        return select[0]
    elif select[0] == select[2]:
        await message.channel.send(f"目は{select[1]}です。")
        return select[1]

    elif f"{select}" == "[':five:', ':four:', ':six:']":
        await message.channel.send(f"シゴロ！2倍づけ！")
        return 3

    elif f"{select}" == "[':one:', ':three:', ':two:']":
        await message.channel.send(f"ヒフミ！2倍払い！")
        return 6

    else:
        if i == 2:
            await message.channel.send(f"目なし！1倍払い！")
            return 5
        else:
            await message.channel.send(f"目なし！")
            return 0


try:
    import tokens
    token = tokens.discord_bot_3
    client.run(token)
except ModuleNotFoundError:
    token = os.getenv("discord_bot_3")
    client.run(token)

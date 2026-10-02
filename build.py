from pathlib import Path
import json, re, html, base64
from opencc import OpenCC

ROOT = Path(__file__).parent
s2t, t2s = OpenCC('s2t'), OpenCC('t2s')
source = json.loads((ROOT/'research/variants.json').read_text(encoding='utf-8'))
terms = {}
for row in json.loads((ROOT/'research/support-dictionary.json').read_text(encoding='utf-8')):
    en = row['url'].split('/tw/')[-1].replace('_',' ')
    if re.search('[\u4e00-\u9fff]',row['name']):
        terms[en] = dict(en=en, tw=row['name'], cn=t2s.convert(row['name']), url=row['url'])
for row in json.loads((ROOT/'research/term-pages.json').read_text(encoding='utf-8')):
    terms[row['en']] = dict(en=row['en'],tw=row['name'],cn=t2s.convert(row['name']),url=row['url'])
extra = {
 'Flameblast':'烈焰爆破','Oil Grenade':'燃油擲彈','Cast on Dodge':'閃避時施放','Gemling Legionnaire':'古靈軍團',
 'Mageblood':'魔血','Dousing Charm':'滅火護符','Paragon':'模範','Arctic Armour':'極地裝甲',
 'Essence of Virtue':'結晶美德','Advanced Thaumaturgy':'進階奇術','Implanted Gems':'植入寶石','Gem Studded':'鑲嵌的寶石',
 'Temporal Chains':'時空鎖鏈','Blasphemy':'瀆神','Curved Weapon':'彎曲武器','Colossal Weapon':'巨無霸武器',
 "Gemcutter's Prism":'寶石匠的稜鏡',"Greater Jeweller's Orb":'高階工匠石',"Lesser Jeweller's Orb":'低階工匠石',
 'Headhunter':'獵首','Gold Ring':'金光戒指'
}
for en,tw in extra.items():
    terms[en]=dict(en=en,tw=tw,cn=t2s.convert(tw),url='https://poe2db.tw/tw/'+en.replace("'",'').replace(' ','_'))
aliases = {"Khatal's Rejuvenation":'Khatals Rejuvenation',"Dialla's Desire":'Diallas Desire'}
for en,alias in aliases.items():
    if alias in terms: terms[en]={**terms[alias],'en':en}

def para(title,*text): return {'title':title,'text':list(text)}
stages = [
 dict(label='1–14 级',name='从手雷起步',subtitle='第一章：建立伤害与移动节奏',summary='用[[Explosive Grenade]]、[[Flash Grenade]]与[[Gas Grenade]]推进剧情。这个阶段先把武器与辅助宝石准备好，保留转型资源。',
 notes=[para('早期首领顺序','吞噬者（泥沼地洞／Devourer, Mud Burrow）→ 寒冷女巫（皆伐／Clearfell）→ 小屋女巫（狩猎之林／Grelwood）→ 锈蚀之王（赤谷／Red Vale）。这些地名采用中文说明并保留英文定位。','经验丰富的玩家可跳过吞噬者；作者认为多花约 2 分钟换一颗辅助宝石，对第一章不顺利的玩家很有价值。'),
 para('武器与防具','赤谷获取[[Tense Crossbow]]，10 级换[[Sturdy Crossbow]]。选择高伤害十字弓；这是冷却驱动的手雷流派，攻击速度不是武器首要目标。','防具以生命和抗性为主，作者优先抗性。练级时戒指、手套上的附加攻击伤害很有用；鞋子一定优先移动速度。胸甲选择高护甲或护甲／闪避底材。'),
 para('剧情药剂升级节点','生命与魔力药剂在 10、16、23、30、40、50、60 级有新一阶可用。达到等级要求后，可直接到商店购买，持续更新两种药剂。'),
 para('辅助顺序与操作','第一颗[[Multishot I]]给[[Explosive Grenade]]，第二颗给[[Flash Grenade]]，之后为爆炸掷弹加入[[Elemental Armament I]]。总共准备 3 颗多重射击 I；十字弓射击上的那颗只是暂存，14 级移到毒气掷弹。','闪光掷弹清理普通怪群；对首领交替投掷爆炸掷弹与毒气掷弹，约每 8 秒使用一次[[Frost Bomb]]维持曝晒。可选用武器组 2 的魔符使用[[Pounce]]提升移动能力。')]),
 dict(label='15–32 级',name='升级辅助与武器',subtitle='第二章：让手雷循环稳定起来',summary='替换二阶辅助、投入 16 级十字弓，并开始为 52 级的宝石插槽储备资源。31 级可将曝晒工具改为燃油掷弹。',
 notes=[para('16 级武器投入','选一把词缀好的[[Varnished Crossbow]]，使用富豪石或点金石，再按资源投入 2 颗工匠石、2 颗崇高石与 2 枚铁符文或风暴符文。它会一直使用到 33 级。物理伤害百分比词缀通常提供更高输出。','生命、抗性仍优先于底材。护甲／能量护盾底材可以考虑，胸甲继续承担主要防御。'),
 para('辅助与插槽优先级','获得二阶辅助后，优先将全部[[Multishot I]]换成[[Multishot II]]，[[Elemental Armament I]]也换为[[Elemental Armament II]]。','第一颗[[Lesser Jeweller\'s Orb]]用于爆炸掷弹，加[[Short Fuse I]]改善清图手感；若缺伤害，可改为[[Deliberation]]。第一颗[[Greater Jeweller\'s Orb]]留给 52 级的烈焰爆破，第二颗才考虑给燃油掷弹。'),
 para('31 级曝晒替换','31 级可用[[Oil Grenade]]替换[[Frost Bomb]]。曝晒较弱，但它受手雷天赋加成，且不要求智慧，更方便维持技能等级。对首领继续交替爆炸掷弹与毒气掷弹。')]),
 dict(label='33–51 级',name='最后一段手雷练级',subtitle='转型前：备齐长杖与品质通货',summary='33 级换轰击十字弓；36 级起开始寻找 +4 火焰技能长杖。手雷可以完成剧情，无须为了 52 级强行转型。',
 notes=[para('33 级：轰击十字弓','[[Bombard Crossbow]]是这一阶段的大幅武器升级，使用到 52 级。优先高物理百分比伤害，按资源使用富豪石、崇高石、工匠石与磨刀石强化。'),
 para('36 级起：检查商店与长杖掉落','作者建议每隔几级检查商店，并拾取长杖；此时开始有机会获取 +4 火焰技能等级长杖，这是顺利转型的重要准备。'),
 para('停止不必要的投入','[[Herald of Ash]]在 52 级转型时会移除，因此不要继续升级。存下所有[[Gemcutter\'s Prism]]，以及未切割技能、辅助与精魂宝石。','保留高阶工匠石给烈焰爆破；对首领用燃油掷弹维持曝晒。移动速度、生命、抗性和定期升级药剂仍然重要。')]),
 dict(label='52 级转型',name='点燃整片战场',subtitle='关键分界：由攻击手雷转为法术点燃',summary='烈焰爆破需要角色 52 级，不能提前转型。准备约 30,000 金币重置天赋、+3／+4 长杖、品质通货和新宝石；资源不足时继续手雷练级即可。',
 notes=[para('先检查资源，再重置天赋','完整材料见下方「转型准备清单」。至少准备一颗 13 级未切割技能宝石用于[[Flameblast]]；高阶工匠石优先给它，低阶工匠石给[[Oil Grenade]]，后者有第二颗高阶更好。','先将烈焰爆破提升至 20% 品质，之后提升[[Cast on Dodge]]品质改善翻滚距离。技能面板的辅助列表代表原作者目标连线；燃油掷弹仅使用低阶工匠石时只能容纳 3 颗辅助，第 4 颗需再升级插槽。'),
 para('武器组必须对应','武器组 1：长杖与烈焰爆破。武器组 2：十字弓与燃油掷弹。天赋也必须按照原文对应的武器组配置；下方交互天赋树可直接查看当前阶段的两组路线。','转型后十字弓不再负责主要伤害，长杖优先技能等级，其次法术伤害、火焰伤害与相关幅度。原文的“not a spellcaster”明显与后文矛盾，此处按紧接着的法术词缀要求与双武器设置整理。'),
 para('转型后的操作与试炼','烈焰爆破必须击中目标，再让燃油掷弹接入烈焰爆破的点燃。首领不一定一次就被点燃，可能需要第二次烈焰爆破。','拥有 100 精魂后启用闪避时施放。保留可手动施放的[[Tornado]]处理飞行敌人；继续升级[[Frost Bomb]]与[[Elemental Weakness]]，否则对高等级敌人可能失效。','作者提醒第三次丝克玛试炼较难：可先用手雷完成，或转型后通过混沌试炼取得第三次昇华。')]),
 dict(label='53–68 级',name='巩固点燃循环',subtitle='剧情后段：把技能、防护与涂抹补齐',summary='保持双武器组设置，逐步补满技能连线。灭火护符是必要配置；先用燃尽涂抹，再向模范品质方案升级。',
 notes=[para('配装方向改变','生命与抗性仍是基础，鞋子保持移动速度。长杖优先技能等级，再考虑法术／火焰伤害与幅度；十字弓本身的输出词缀不重要。','原文此阶段仍重复了练级时的附加攻击伤害建议，但这不能理解为允许转型后的附加火焰伤害。转型后以禁止燃油掷弹携带火焰伤害的规则为准。'),
 para('必要防护与涂抹','必须装备[[Dousing Charm]]。自身点燃可能扩散至油面并覆盖所需的强点燃快照，导致没有有效伤害。','[[Burnout]]是过渡涂抹；[[Paragon]]是作者首选，但赛季早期可能较贵。'),
 para('继续升级工具技能','先完成烈焰爆破 20% 品质，再强化闪避时施放。100 精魂启用触发龙卷风，手动龙卷风仍保留。寒霜爆与元素要害要随角色提升，以确保对高等级目标生效。')]),
 dict(label='85 级',name='实用终局起点',subtitle='作者认为已能舒适应对全部内容的版本',summary='堆叠生命与 Ward（守护），在基础生存满足后增加物品稀有度。魔血并非此阶段要求；优先完成品质、精魂和辅助宝石配置。',
 notes=[para('生命、守护与装备底材','各部位以生命、抗性和稀有度为主。力量是不错的后缀，可以增加生命；戒指上的增加火焰伤害百分比是小幅提升，不是必要条件。','原文优先高阶混合底材，偏好护甲／能量护盾或纯智慧底材，以提高生命与 Ward 池。未系统堆叠护甲前，先关注生命与守护。此处保留 Ward 英文以免与能量护盾混淆。'),
 para('胸甲、戒指与精魂','[[Morior Invictus]]选择每插槽生命版本，5 插槽搭配[[Perfect Body Rune]]可提供大量生命；同时带全抗、混沌抗性或精魂也是好选择。精魂不足时，可在十字弓加入[[Soul Core of Azcapa]]。','[[Blackflame]]是早期可选戒指，使用时配[[Withering Presence]]，连[[Prolonged Duration II]]和[[Chaos Mastery]]。最终可换为三项稀有度词缀的[[Gold Ring]]。'),
 para('护身符与资源方案','起步用[[Surefooted Sigil]]追求速度；有预算后换带 5% 全技能品质并涂抹模范的稀有[[Gold Amulet]]。模范昂贵时先用燃尽。','可选择[[Temporal Chains]]＋[[Blasphemy]]方案，或[[Mana Remnants]]＋[[Khatal\'s Rejuvenation]]方案。后者提供更多冷却恢复与充裕魔力；渎神路线需要更多精魂。','开始平衡红／绿／蓝辅助数量，使[[Gem Studded]]三项收益同时生效。武器组中的宝石也计入；长杖自带技能内的辅助不计入。')]),
 dict(label='终局',name='进一步投资品质与珠宝',subtitle='较高预算：精炼装备，提升清图体验',summary='以 85 级版本为基础，升级护身符、稀有度戒指与五词缀珠宝。高预算的价值集中在体验、品质与生存。',
 notes=[para('沿用生命与守护配装','继续生命、抗性、稀有度；不败亡者、黯炎与精魂补足的选择与 85 级相同。持续使用灭火护符。不要把“增加火焰伤害”百分比与“附加火焰伤害”混为一谈。'),
 para('护身符两条路线','带[[Cast on Dodge]]的[[Absent Amulet]]可受全局品质加成，进一步提升翻滚距离，使用与常规闪避时施放相同的连线。较便宜的替代是[[Gold Amulet]]。涂抹首选模范。'),
 para('理想五词缀珠宝','前缀 1：施加的异常状态幅度 15%；前缀 2：点燃幅度 15%；前缀 3：法术伤害或元素伤害。若配装开始扩展护甲／能量护盾，对应百分比也可以考虑。','后缀 1：额外 1 个前缀词缀；后缀 2：伤害型异常状态加快 7% 造成伤害。数值为原作者提出的理想词缀，购买时检查实际词缀与物品限制。'),
 para('额外技能栏与颜色平衡','通过[[Unset Ring]]和[[Augmented Flesh]]临时增加技能栏：戴上装备，装入技能，再移除装备。作者称失去栏位后无法使用的技能仍可参与昇华计数。','这是原作者在 0.5.5 版本描述的快照操作。平衡技能面板顶部的三色辅助数量，并排除长杖自带技能的辅助。')]),
 dict(label='魔血',name='转入护甲防御体系',subtitle='高预算：魔遗、霸体与极地装甲协作',summary='此版本必须拥有魔血。作者预计常规配置约 50,000 护甲，珠宝加入护甲百分比后可向 60,000–70,000 推进。',
 notes=[para('魔血与魔遗选择','[[Mageblood]]是此版本的前提；作者认为缺少它将损失一半以上护甲，防御体系难以成立。原文用 basalt／granite／jade 等“药剂”名称简称，对应本作魔血的石化／坚岩／翠玉魔遗效果。','三种防御效果任选两种，其余选择黄金额外稀有度、水银移动速度或灰岩元素抗性。理想共 4 个魔遗位置，3 种不同效果、其中 1 种重复，以利用魔血的重复魔遗加成。'),
 para('装备与元素伤害防护','使用高护甲或护甲／闪避装备，[[Iron Reflexes]]将闪避转为护甲；混合底材较容易满足属性，纯护甲胸甲可能要求很高力量。','头盔、手套、鞋、胸甲各自理想拥有 40%「护甲套用于元素伤害」词缀。与天赋合计，作者目标超过 200%。这些数字属于原配装规划，不代表伤害减免百分比。','护身符需要精魂以同时启用魔力痕迹与极地装甲；十字弓可用艾斯卡巴灵魂核心补精魂。继续装备灭火护符；[[Rite of Passage]]魂灵选择熊，牛也可。'),
 para('护甲珠宝与极地装甲','制作三前缀红玉珠宝：点燃幅度、增加护甲、增加元素或火焰伤害；后缀选择 40–60% 前缀词缀效果。作者认为第二后缀不重要。','极地装甲品质要达到 40%，取得额外层数。作者说明每层提供增加 40% 护甲，7 层合计增加 280% 护甲；达到技能等级 27 还可再加一层。','寒冰碎片起的若干技能只是用于昇华计数的占位宝石，并非战斗循环。技能面板标出这些占位组，保持红／绿／蓝辅助数量一致。'),
 para('可选高速配置','闪避时施放虚无护身符受全局品质加成，可额外增加约 1 米翻滚距离；鞋子选[[Decree of Flight]]或[[Ghostmarch]]；魔血加入水银之遗，天赋也可追加移动速度。作者用于首领速刷与长距离地图。')]),
 dict(label='持续伤害上限',name='极限配置',subtitle='最高预算：保留闪避，继续压榨点燃',summary='原作者描述接近 3,500 万持续伤害／秒、约 85,000 护甲、50% 闪避和 3,500 生命，约 200,000 有效承伤池。这些是作者该版本的目标／估算，不是所有角色的保证。',
 notes=[para('魔血与双防御配置','必须使用[[Mageblood]]。首选翠玉／坚岩／灰岩魔遗，可有 1 个重复；第四选择紫晶、水银或黄金。坚岩／石化也能用，但作者指出不会拥有约 50% 闪避。','这是与普通魔血版不同的防御分支：按持续伤害上限版天赋配置保留闪避，不能直接照搬普通魔血版的霸体转换。作者装备说明目标约 80,000 护甲和 45–50% 闪避；概览展示约 85,000 护甲。'),
 para('头盔、手套与生命扩展','高护甲头盔配[[Emergent Vigour]]，高护甲手套配[[Leather Bound Gauntlets]]。鞋子可选纯护甲或护甲／闪避混合。','头、手、鞋、胸依旧理想各 40% 护甲套用于元素伤害，连同天赋超过 200%。项链精魂支持魔力痕迹与极地装甲；若能解决耐力球生成，也可考虑[[Charge Regulation]]。'),
 para('珠宝与移动方案','沿用三前缀红玉珠宝：点燃幅度、护甲百分比、元素／火焰伤害，后缀 40–60% 前缀效果。灭火护符仍必要，仪式通道魂灵选熊或牛。','高速分支仍可用闪避时施放虚无护身符、翔天敕令／鬼行与水银魔血。这个版本投入很高；普通 85 级版本已经是作者建议的实用终局起点。'),
 para('技能差异','烈焰爆破以[[Deliberation]]替代[[Burgeon II]]。极地装甲增加[[Herbalism I]]；手动龙卷风增加[[Slow Potency]]。额外十字弓技能、战吼与图腾用于颜色／技能栏配置，不应误认为需要轮流施放所有技能。')])
]
for i,stage in enumerate(stages):
    text=source[i]['text']
    block=text.split('Collapse all\n',1)[1].split('Gem Priority',1)[0]
    groups=[]
    for match in re.finditer(r'(?:^|\n)(\d+)\n(.*?)(?=\n\d+\n|\Z)',block,re.S):
        lines=[a.strip() for a in match[2].splitlines() if a.strip()]
        name=lines.pop(0); level=None
        if lines and lines[0].startswith('Level '): level=int(lines.pop(0).split()[-1])
        groups.append({'name':name,'level':level,'supports':lines,'placeholder':i==7 and name in ['Ice Shards','Shockwave Totem','Seismic Cry','Crossbow Shot'] or i==8 and name in ['Incendiary Shot','Ice Shards','Infernal Cry','Shockwave Totem','Seismic Cry']})
    stage['skills']=groups
    attrib=re.search(r'Str (\d+)\s+Dex (\d+)\s+Int (\d+)',text)
    stage['attributes']=list(map(int,attrib.groups()))
    ids=['default-variant','1','2','3','4','5','6','ec6511a2-8023-4841-b1a2-731bf5fdcd93','600846cb-2882-4f6e-b16a-ca6f8c62464c']
    stage['url']='https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade?ws-ngf5-f7d82102-7e77-4a44-ad24-33b67e8ae7bf=activeVariantId%2C'+ids[i]

content={
 'title':'烈焰爆破 × 燃油掷弹', 'subtitle':'Fubgun 的古灵军团流派手册',
 'intro':'以一次强力点燃为起点，让燃油铺满战场。用手雷平稳完成前期，再以烈焰爆破、翻滚触发和双武器切换建立高速清图循环。',
 'nav':[['overview','流派概览'],['mechanics','战斗机制'],['stages','九阶段养成'],['swap','52 级转型'],['gear','装备与珠宝'],['ascendancy','天赋与昇华'],['quality','品质规划'],['troubleshoot','伤害排错'],['quests','剧情奖励'],['glossary','术语对照'],['sources','原文与导入']],
 'stages':stages,
 'overview':[
 para('从开荒到终局','职业为佣兵，昇华选择[[Gemling Legionnaire]]。1–51 级使用手雷；烈焰爆破需要 52 级。作者将本流派定位为速度和清图优先，因为基础伤害已经很高。'),
 para('选择适合自己的投资阶段','原作者认为 85 级方案即可舒适清理全部内容。终局版提高预算，魔血版构建护甲防御，持续伤害上限版追求极限伤害与生存。'),
 para('优先理解点燃条件','双武器设置、附加火焰伤害和自身点燃都会影响燃油的有效点燃。先确认这些条件，再投入更贵的装备。')],
 'mechanics':[
 para('烈焰爆破：制造强点燃','在武器组 1 使用长杖，引导[[Flameblast]]并命中敌人。蓄积的层数提高爆炸威力；在古灵军团的品质体系下，品质对异常状态幅度尤为重要。首领并非保证一次点燃，必要时再次施放。'),
 para('燃油掷弹：铺油与承接','在武器组 2 用十字弓释放[[Oil Grenade]]，将油面接入烈焰爆破的点燃。持续铺油提供覆盖与曝晒。转型后，作者的十字弓不以直接武器伤害为配装核心。'),
 para('翻滚：移动时触发龙卷风','启用[[Cast on Dodge]]后，翻滚积累能量并触发插槽中的[[Tornado]]。品质还可增加翻滚距离，兼顾清图与移动。保留手动龙卷风处理飞行怪物；燃烧地面地图改用其他触发法术。'),
 para('首领：工具技能维持有效','维持[[Frost Bomb]]曝晒与[[Elemental Weakness]]诅咒，随后烈焰爆破命中、燃油掷弹承接，并移动避招。寒霜爆与元素要害要持续升级，避免对高等级敌人失效。')],
 'swapItems':[
 ['gold','约 30,000 金币','用于重置手雷练级天赋；剧情中提前预留。'],
 ['gem13','1 颗 13 级未切割技能宝石','用于[[Flameblast]]。角色等级至少 52 级。'],
 ['gcp','2–4 颗宝石匠的棱镜','优先让烈焰爆破达到 20% 品质。'],
 ['greater','1 颗高阶工匠石','给烈焰爆破开 4 辅助槽；作者称第四章 Ngakanu 有保证来源。'],
 ['lesser','1 颗低阶工匠石','给燃油掷弹开 3 辅助槽；第二颗高阶工匠石可把它提升到 4 槽。'],
 ['staff','一把 +3／+4 火焰技能长杖','同时有增加法术伤害或火焰伤害更好；36 级起留意商店。'],
 ['support','约 9 颗未切割辅助宝石','用于新技能辅助；各阶段连线见上方面板。'],
 ['skills','额外 3 颗未切割技能宝石','用于龙卷风、寒霜爆与元素要害。'],
 ['spirit','1 颗未切割精魂宝石','准备闪避时施放配置；启用时需要 100 精魂。'],
 ['sets','正确设置技能与武器组天赋','烈焰爆破在组 1，燃油掷弹在组 2。'],
 ['fire','检查附加火焰伤害与灭火护符','油掷弹不应携带附加火焰伤害；必须使用[[Dousing Charm]]。']],
 'swapNote':'原作者称，若沿用 0.5 版本掉落安排，第二章 Keth 与第四章 Isle of Kin 的祭祀机制各有一颗保证宝石匠的棱镜。原文对“保证来源”保留了版本未变的前提；实际以当前游戏为准。材料不足时可继续手雷完成剧情。',
 'gear':[
 ['weapon','长杖与十字弓','转型前：十字弓高物理伤害。转型后：长杖技能等级 ＞ 法术／火焰伤害与幅度；十字弓用于燃油掷弹。长杖上的附加火焰伤害可以接受，因为使用油掷弹时切到十字弓。'],
 ['chest','胸甲','普通终局可用[[Morior Invictus]]，优先每插槽生命、5 插槽，配[[Perfect Body Rune]]。魔血阶段改为高护甲或护甲／闪避，并追求护甲套用于元素伤害词缀。'],
 ['rings','戒指','练级时生命、抗性、附加攻击伤害；转型后禁止污染油掷弹的附加火焰。[[Blackflame]]需配凋零光环；后期可换三稀有度词缀金光戒指。'],
 ['amulet','护身符','85 级起步[[Surefooted Sigil]]；升级带全技能品质的帝金护身符并涂抹[[Paragon]]。虚无护身符的闪避时施放是速度分支；护甲版本还需精魂。'],
 ['boots','鞋子与手套','鞋优先移动速度。普通魔血选高护甲／护甲闪避，持续伤害上限版的高护甲手套配皮革绑缚护手。高速分支可选[[Decree of Flight]]或[[Ghostmarch]]。'],
 ['charm','护符与腰带','[[Dousing Charm]]必备。[[Headhunter]]偷取的增益可能破坏点燃，不推荐。魔血版必须有[[Mageblood]]并选择合适魔遗，普通 85 级版本无此要求。'],
 ['jewels','珠宝','转型后，红玉／蓝玉珠宝优先相关点燃与可燃性幅度、异常状态伤害加速。终局五词缀路线与魔血三前缀效果路线不同，按阶段面板选择。'] ],
 'ascendancy':[
 ['Essence of Virtue','取得高尚御盾；建立古灵军团防御与技能数量体系。'],
 ['Advanced Thaumaturgy','宝石品质赋予技能额外效果，是烈焰爆破与极地装甲品质规划的关键。'],
 ['Implanted Gems','选择智慧方向的神经镶嵌物：全部具有智慧需求的技能等级 +2。'],
 ['Gem Studded','平衡红／蓝／绿辅助宝石计数，以同时获得三色收益。'] ],
 'treeNotes':[
 '手雷时期按当下属性需求选择属性节点；第二章务必升级寒霜爆，智慧不足时及时补足。原文也提到弯曲武器与巨无霸武器使前期属性较好处理。',
 '转型后保证智慧能支持烈焰爆破，珠宝优先点燃／可燃性幅度与伤害型异常状态加速。两组武器专用节点可在交互天赋树中分别查看。',
 '原页面天赋面板有剩余点数的负数显示，它们不是角色需求。本手册不将这些界面计数当成配点预算；交互天赋树按原始导出逐阶段显示配点，并分别统计两组武器节点。',
 '本页交互天赋树包含九阶段配点与昇华分支，PoB 导入码另在页面底部保存。'] ,
 'qualitySources':[['宝石自身品质',20,23],['狐狸魔偶',5,5],['模范涂抹',5,5],['护身符亵渎后缀',5,5],['古灵军团小昇华',6,6]],
 'qualityNotes':[
 '作者方案合计 41–44% 品质。40% 是重要门槛：极地装甲额外获得 1 层；技能等级 27 还可再增加 1 层，作者完整方案可达 8 层。',
 '品质同时大幅提升烈焰爆破。先让主技能自身达到 20% 品质，再考虑闪避时施放与全局品质。',
 '虚无护身符附带的技能无法直接使用品质通货，但可享受全局技能品质加成。本计算器只计算原作者五项来源，不计其他装备；结果是规划总和。'],
 'faq':[
 ['燃油掷弹没有伤害，先看哪里？','先检查装备是否存在附加火焰伤害或额外火焰伤害（长杖除外）。确认烈焰爆破绑定武器组 1、燃油掷弹绑定组 2。检查油掷弹伤害面板，确保没有污染它的附加火焰来源。'],
 ['武器组都对了，仍然无法点燃？','烈焰爆破必须击中目标，油掷弹要接入这次烈焰爆破点燃。首领不保证 100% 点燃，可能要第二次施放；提高伤害与可燃性幅度有帮助。'],
 ['为什么突然变成零伤害？','自身受到点燃后，低质量点燃可能扩散到油面并覆盖原有快照。始终装备并维持灭火护符。猎首偷取的怪物增益也可能导致失效。'],
 ['燃烧地面地图如何调整？','把闪避时施放中的龙卷风移除，改放其他法术，例如寒霜爆。原作者明确要求这种地图调整。'],
 ['怎么获得足够多的技能栏？','使用潜能之戒和增幅血肉临时增加栏位，装好技能再移除。原作者称无法使用的技能仍可被相关昇华计数。该技巧属于 0.5.5 原文快照方案，后续改版需重新确认。'],
 ['三色辅助如何平衡？','在额外十字弓技能等占位技能中填入所需颜色的辅助，使红／绿／蓝数量相等。计入另一武器组的技能；排除长杖自带技能里的辅助。魔血面板中的占位技能主要服务于此。'],
 ['缺少转型材料，52 级一定要换吗？','不必。原作者明确说可以用手雷完成剧情；没有宝石匠的棱镜或合适长杖时，延后转型。'],
 ['魔血上写的药剂名称是什么意思？','本作魔血使用魔遗（Mage\'s Legacies）赋予效果。原文 basalt、granite、jade、quicksilver 等为对应效果的简称，不是要求同时装备四瓶传统功能药剂。本页按魔遗说明。'] ],
 'quests':[
 ['第一章','Clearfell · Beira','+10% 冰冷抗性'],['第一章','Hunting Grounds · Crowbell','2 点武器组天赋'],['第一章','Freythorn · King in the Mists','+30 精魂'],['第一章','Ogham Farmlands · Una\'s Hut','2 点武器组天赋'],['第一章','Ogham Manor · Candlemass','+20 最大生命'],
 ['第二章','Keth · Kabala','2 点武器组天赋'],['第二章','Valley of the Titans · Medallion','增加 30% 护符充能获取、+1 护符栏位'],['第二章','Deshar · Final Letter','2 点武器组天赋'],['第二章','Spires of Deshar · Sisters of Garukhan','+10% 闪电抗性'],
 ['第三章','Jungle Ruins · Mighty Silverfist','2 点武器组天赋'],['第三章','Venom Crypts · Venom Draught','增加 25% 晕眩门槛'],['第三章','Jiquani\'s Machinarium · Blackjaw','+10% 火焰抗性'],['第三章','Azak Bog · Ignagduk','+30 精魂'],['第三章','Molten Vault','重铸台'],['第三章','Aggorat · Blood Sacrifice','2 点武器组天赋'],
 ['第四章','Journey\'s End · Captain Hartlin','2 点武器组天赋、13 级技能宝石、谵妄掉落'],['第四章','Whakapanu Island · Great White One','原文未指定选择（2 个选项）'],['第四章','Eye of Hinekora · Navali\'s Rest','增加 5% 最大魔力'],['第四章','Halls of the Dead · Yama','2 点武器组天赋'],['第四章','Halls of the Dead · Tawhoa\'s Test','+5% 闪电抗性'],['第四章','Halls of the Dead · Tasalio\'s Test','+5% 冰冷抗性'],['第四章','Halls of the Dead · Ngamahu\'s Test','+5% 火焰抗性'],['第四章','Abandoned Prison · Goddess of Justice','增加 30% 药剂生命回复'],['第四章','Halls of the Dead · Tribal Medicine','增加 30% 全域护甲、闪避、能量护盾'],
 ['间章','Wolvenhold · Oswin','2 点武器组天赋'],['间章','Khari Crossing · Akthi and Anundr','2 点武器组天赋'],['间章','Khari Crossing · Molten Shrine','增加 5% 最大生命'],['间章','Qimah · Tabana\'s Pillar','增加 3% 移动速度'],['间章','Kriar Village · Lythara','+40 精魂'],['间章','Howling Caves · Abominable Yeti','2 点武器组天赋'] ],
 'labels':{
 'manual':'流派手册','language':'阅读语言','simple':'简体中文','traditional':'繁體中文','print':'打印当前阶段／PDF','begin':'开始阅读','original':'查看原攻略','version':'原文版本','author':'原作者','updated':'原文更新','compiled':'整理日期','readProgress':'阅读进度','quick':'关键节点','unlock':'转型最低等级','qualityTarget':'重要品质门槛','goldReserve':'预留重置金币','sourceNote':'依原攻略 0.5.5 版本整理，数值与机制以该版本为背景。术语采用 poe2db 繁体名称，简体模式作字形转换，保留英文便于查找。',
 'overview':'一套流派，完整养成','overviewLead':'先用手雷建立节奏，再以高品质法术点燃接管输出。','mechanics':'先点燃，再铺开','mechanicsLead':'双武器组各司其职；理解这条链路，是伤害稳定的前提。','flow1':'长杖 · 武器组 1','flow2':'十字弓 · 武器组 2','flow3':'翻滚 · 触发龙卷风','flowDesc1':'烈焰爆破命中并造成强点燃','flowDesc2':'燃油掷弹承接点燃，持续铺油','flowDesc3':'扩大覆盖，移动避招','stages':'从第一颗手雷到极限终局','stagesLead':'选择当前阶段，配装重点与技能连线同步更新。辅助等级与排列保留原文。','equipmentNotes':'本阶段养成重点','skills':'技能与辅助连线','supportAttr':'原页面辅助宝石需求','strength':'力量','dexterity':'敏捷','intelligence':'智慧','supportAttrNote':'这是辅助需求统计，不是角色总属性或主技能需求。','skillName':'技能','supports':'按原文排列的辅助宝石','placeholder':'昇华计数占位','noSupports':'原文未配置辅助','set1':'武器组 1','set2':'武器组 2','tool':'工具／增益','treeLink':'打开本阶段完整天赋与装备','swap':'52 级转型准备清单','swapLead':'全部准备好，再重置天赋。勾选会保存在当前浏览器。','checked':'已准备','resetChecks':'重置清单','gear':'装备投资，用在关键位置','gearLead':'以下归纳各部位优先级；具体阶段差异以九阶段面板为准。','ascendancy':'昇华次序与天赋重点','ascendancyLead':'先建立品质体系，再平衡辅助颜色。精确的天赋连线可在交互天赋树查看。','quality':'算清你的品质门槛','qualityLead':'调整实际拥有的五项品质来源，检查是否达到作者强调的 40%。','totalQuality':'规划品质总和','thresholdReached':'已达到 40% 品质门槛','thresholdMissing':'距离 40% 门槛还差','qualityPoints':'个百分点','troubleshoot':'点燃失效，从这里排查','troubleshootLead':'这些问题来自原作者 FAQ。装备变动或地图词缀变化后，尤其要重新检查。','quests':'别漏掉剧情永久奖励','questsLead':'按原攻略任务奖励面板整理，保留英文地点便于地图定位；未指定选项明确标出。','questWhere':'地点／目标（原文）','questReward':'奖励或原文选择','questDone':'已完成','glossary':'中文与英文，随时对照','glossaryLead':'技能、辅助、装备与天赋采用编年史术语。点击名称可查看对应数据库条目。','searchLabel':'查询术语','searchPlaceholder':'输入中文或英文，例如：烈焰、Flameblast','termChinese':'当前中文名称','termEnglish':'英文名称','termNoResults':'没有匹配术语，请尝试中文或英文关键词。','sources':'保留原文，方便继续深入','sourcesLead':'中文手册包含阅读、交互天赋与配装；原版规划器可继续查看完整装备。','pobTitle':'Path of Building 导入码','pobDescription':'保存自原攻略页面的 PoB 导出，读取时为单个 98 级高预算配置。它不是全部九阶段的导入集合；九阶段配点可在本页交互天赋树查看。','copyPob':'复制 PoB 导入码','downloadPob':'下载导入码文本','copied':'已复制','copyFailed':'请选中文本手动复制','regexTitle':'商店搜索表达式（原文）','regexDescription':'适用于英文物品文本；中文客户端不能直接依赖其中的英文匹配。','copyRegex':'复制搜索表达式','filter':'打开练级过滤器','filterDescription':'原作者只建议用于进入地图前；进地图后更换过滤器。','credits':'攻略作者 Fubgun · 原文 Mobalytics · 术语参考 流亡2编年史 poe2db','footer':'中文翻译与结构整理：2026-10-02。保留原文版本边界；不将高预算目标数值当成所有角色的保证。','backTop':'返回顶部','allTerms':'条术语','qualityUnit':'%','chapter':'章节目录','jump':'跳至正文','precisionNote':'原文技能列表完整保留。技能等级仅在作者明确填写时显示；占位技能用于昇华配置。'
 }
}
content['labels'].update({
 'stageArt':'原文装备图示','stageArtNote':'悬停图标查看原文属性与词缀；点按可固定提示，Esc 关闭。相同外观的珠宝保留各自配置，武器注明所属武器组。',
 'slot_staff':'长杖','slot_crossbow':'十字弓','slot_weapon':'武器','slot_helmet':'头盔','slot_chest':'胸甲','slot_gloves':'手套','slot_boots':'鞋子','slot_rings':'戒指','slot_amulet':'护身符','slot_belt':'腰带','slot_charm':'护符','slot_flask':'药剂','slot_jewels':'珠宝','slot_item':'物品',
 'assetCredits':'字体、游戏素材与授权','gameCredits':'技能、辅助宝石、物品及昇华图像取自原攻略所用游戏素材；Path of Exile 2 游戏美术归 Grinding Gear Games 所有。',
 'fontRestore':'本页使用霞鹜新晰黑。若希望恢复为其原始授权字体，可从 IPA 官方下载 IPAex Gothic，解压后在这里选择 ipaexg.ttf；字体将在本页即时替换。',
 'ipaDownload':'下载原始 IPA 字体','fontImport':'选择本地 IPA 字体','fontReset':'恢复霞鹜新晰黑','fontApplied':'已应用字体：','fontError':'字体未能加载，请选择解压后的 TTF、OTF 或 WOFF 字体文件。','fontDefault':'已恢复霞鹜新晰黑。'
})

content['labels'].update({'treeTitle': '交互天赋树', 'treeLead': '按原作者九个阶段配点。拖动探索路线，点击节点查看效果；武器组与技能面板保持同步。', 'treeStageLabel': '天赋树养成阶段', 'treeFilterLabel': '显示武器组', 'treeAll': '全部武器组', 'treeSet1': '武器组 1 · 长杖', 'treeSet2': '武器组 2 · 十字弓', 'treeShared': '共用天赋', 'treeBoth': '两组武器共用此节点', 'treeUnallocated': '未配置', 'treeMainView': '主天赋树', 'treeAscView': '昇华树', 'treeFit': '定位配点', 'treeWhole': '完整主树', 'treeExpand': '展开查看', 'treeClose': '关闭展开', 'treeZoomIn': '放大天赋树', 'treeZoomOut': '缩小天赋树', 'treeMap': 'PASSIVE ATLAS · 配点路线', 'treeNormalCount': '导出主树节点', 'treeSet1Short': '组 1 专属', 'treeSet2Short': '组 2 专属', 'treeAscCount': '昇华点', 'treeSmall': '小型天赋', 'treeNotable': '核心天赋', 'treeKeystone': '关键天赋', 'treeJewel': '珠宝插槽', 'treeAscNode': '昇华天赋', 'treeChoice': '昇华选项', 'treeClassStart': '角色起点', 'treeAscStart': '昇华起点', 'treeClassName': '佣兵起点', 'treeAscName': '古灵军团', 'treeJewelHint': '在此插入珠宝；具体珠宝词缀请参照装备与珠宝章节。', 'treeStartHint': '起点不消耗天赋点。', 'treeChoiceHint': '此节点用于选择分支，请查看连接的选项。', 'treeInspectHint': '将鼠标移到节点，悬浮窗会显示名称与效果；点击可在此固定详情。也可在下方列表中选择节点。', 'treeHoverHint': '点击节点固定详情 · 英文原文可在详情栏展开', 'treeUnpin': '取消固定节点', 'treeEnglish': '英文原始说明', 'treeSearch': '搜索中文／英文名称或效果…', 'treeResults': '找到 {n} 个节点', 'treeResultsLimit': '显示前 60 个', 'treeAllocatedList': '当前阶段 · 已配置的重要节点', 'treeNoResults': '没有找到匹配节点。', 'treeCanvasLabel': '交互天赋地图。方向键平移，加减键缩放，Home 定位配点。使用旁边的搜索与节点列表也可查看详情。', 'treeHelp': '电脑：悬停查看节点提示 · 拖动平移 · 滚轮缩放 · 点击固定节点 · Esc 取消固定／关闭展开。触屏：单指拖动 · 双指缩放 · 点按节点。键盘：方向键平移，+/− 缩放，Home 定位配点。', 'treeSourceTitle': '数据来源、版本与开源授权', 'treeSourceNote': '配点来自 Fubgun 0.5.5 攻略的九份 .build 导出。地图与节点效果使用开源规划器的 0.5.2 数据，全部配点 ID 均已匹配；名称与中文术语参考流亡2编年史，保留该地图版本的数值。完整主树中未涉及的节点可能显示英文。', 'treeCountNote': '「导出主树节点」为作者导出中共用与两组武器节点的去重总数；部分阶段与原网页的 Main used 计数不同，此处忠实显示导出数据。两组专属数各自统计，不应相加当作角色所需总点数。昇华起点与免费分支选项不计入昇华点。作者的早期阶段也含目标昇华配点；并非要求在该等级完成。属性节点的具体属性选择未包含在 .build 导出中，因此保留「任意属性」说明。', 'treeLicense': '开源规划器 MIT 许可证', 'treePlanner': '开源规划器项目', 'treeDatabase': '中文术语来源'})
content['nav'].insert(3,['passive-tree','交互天赋树'])

def converted(obj):
    if isinstance(obj,str): return s2t.convert(obj)
    if isinstance(obj,list): return [converted(a) for a in obj]
    if isinstance(obj,dict): return {k:converted(v) for k,v in obj.items()}
    return obj
data={'cn':content,'tw':converted(content)}
data['tw']['labels']['intelligence']='智慧'
# The glossary supplies exact database names independently of text conversion.
used=set(extra)
for stage in stages:
    for group in stage['skills']: used.add(group['name']); used.update(group['supports'])
used.update(re.findall(r'\[\[([^\]]+)\]\]',json.dumps(content,ensure_ascii=False)))
missing=sorted(x for x in used if x not in terms)
if missing: raise ValueError(f'Missing terminology: {missing}')
glossary={k:terms[k] for k in sorted(used)}
pob=(ROOT/'research/build-pob.txt').read_text(encoding='utf-8').strip()
regex=re.search(r'Vendor Regex: \s*\n(.*?)\n',source[0]['text']).group(1)
manifest=json.loads((ROOT/'research/asset-manifest.json').read_text(encoding='utf-8'))
image_ids={key:f'i{i}' for i,key in enumerate(sorted(manifest['assets']))}
image_data={image_ids[key]:'data:'+row['mime']+';base64,'+base64.b64encode((ROOT/row['path']).read_bytes()).decode() for key,row in manifest['assets'].items()}
image_names={name:image_ids[key] for name,key in manifest['names'].items()}
for en,alias in aliases.items():
    if en in image_names: image_names[alias]=image_names[en]
asset_kinds=[('/Weapons/TwoHandWeapons/Staves/','staff'),('/Weapons/TwoHandWeapons/Crossbows/','crossbow'),('/Weapons/','weapon'),('/Helmets/','helmet'),('/BodyArmours/','chest'),('/Gloves/','gloves'),('/Boots/','boots'),('/Rings/','rings'),('/Amulets/','amulet'),('/Belts/','belt'),('/Charms/','charm'),('/Flasks/','flask'),('/Jewels/','jewels')]
def image_kind(key):
    return next((kind for fragment,kind in asset_kinds if fragment in key),'item')
by_image={}
for name,key in manifest['names'].items():
    if name in glossary: by_image[key]=name
from prepare_tooltips import compile_tooltips
tooltips=compile_tooltips(terms)
for en,alias in aliases.items():
    if en in tooltips['names']: tooltips['names'][alias]=tooltips['names'][en]
gear_images=[[{**item,'image':image_ids[item['key']]} for item in rows] for rows in tooltips.pop('gallery')]
categories={kind:image_ids[key] for keys in manifest['equipment'] for key in keys for kind in [image_kind(key)]}
assets={'images':image_data,'names':image_names,'gear':gear_images,'categories':categories}
font_file=ROOT/'assets/font/LXGWNeoXiHei.woff2'
font_data=base64.b64encode(font_file.read_bytes()).decode()
font_css='@font-face{font-family:"LXGW Neo XiHei";src:url(data:font/woff2;base64,'+font_data+') format("woff2");font-style:normal;font-weight:400;font-display:swap}'
font_license=html.escape((ROOT/'assets/font/LICENSE.md').read_text(encoding='utf-8'))
template=(ROOT/'template.html').read_text(encoding='utf-8')
from prepare_passives import compile_passives
passive=compile_passives(t2s)
passive_license=html.escape((ROOT/'assets/passive/LICENSE-planner.txt').read_text(encoding='utf-8'))
template=template.replace('__PASSIVE_DATA__',json.dumps(passive,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')).replace('__PASSIVE_STYLE__',(ROOT/'passive-tree.css').read_text(encoding='utf-8-sig')).replace('__PASSIVE_SCRIPT__',(ROOT/'passive-tree.js').read_text(encoding='utf-8-sig')).replace('__PASSIVE_LICENSE__',passive_license)
template=template.replace('__TOOLTIP_STYLE__',(ROOT/'tooltip-ui.css').read_text(encoding='utf-8')).replace('__TOOLTIP_SCRIPT__',(ROOT/'tooltip-ui.js').read_text(encoding='utf-8'))
output=template.replace('__GUIDE_DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/')).replace('__TERMS__',json.dumps(glossary,ensure_ascii=False)).replace('__POB__',json.dumps(pob)).replace('__REGEX__',json.dumps(regex,ensure_ascii=False)).replace('__ASSETS__',json.dumps(assets,ensure_ascii=False)).replace('__TOOLTIPS__',json.dumps(tooltips,ensure_ascii=False).replace('</','<\\/')).replace('__FONT_STYLE__',font_css).replace('__FONT_LICENSE__',font_license)
output_path=ROOT/'烈焰爆破-燃油掷弹攻略.html'
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Build the self-contained Chinese PoE 2 guide.')
    parser.add_argument('--output',help='Output HTML path; defaults to the Chinese offline filename.')
    args=parser.parse_args()
    if args.output: output_path=ROOT/args.output
output_path.parent.mkdir(parents=True,exist_ok=True)
output_path.write_text(output,encoding='utf-8')
print(f'Built {len(output.encode())} bytes; {len(stages)} stages; {sum(len(s["skills"]) for s in stages)} skill groups; {len(glossary)} terms')
print(f'Embedded {len(tooltips["tips"])} observed popovers; {len(tooltips["names"])} named objects')

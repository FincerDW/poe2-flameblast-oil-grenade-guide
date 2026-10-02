"""Compile observed Mobalytics popovers; keep English snapshots for comparison."""
from pathlib import Path
import json, re
from opencc import OpenCC

ROOT = Path(__file__).parent
RAW = json.loads((ROOT/'research/hover-captures.json').read_text(encoding='utf-8'))
TW = OpenCC('s2t')

# Descriptions are translations of the observed popup, not new build advice.
DESCRIPTIONS = {
'Flameblast':'引导并在自身周围积蓄毁灭能量。释放能量时产生强力爆炸；引导越久，爆炸范围越大、威力越强。',
'Oil Grenade':'发射一颗会弹跳的手雷，在引信结束或撞击敌人时喷洒燃油。伤害很低，但会让地面和附近敌人沾上燃油。此燃油可以被引爆技能或已点燃的地面点燃。',
'Cast on Dodge':'启用时，翻滚会积累能量；达到最大能量时，触发插槽中的法术。',
'Crossbow Shot':'从十字弓发射一枚弩箭。',
'Explosive Grenade':'发射一颗会弹跳的手雷，引信结束时产生毁灭性的火焰爆炸。',
'Flash Grenade':'发射一颗会弹跳的手雷，引信结束时产生使敌人致盲、晕眩的爆炸。',
'Gas Grenade':'发射一颗会弹跳的手雷，引信结束时喷出毒气，伤害敌人并留下逐渐扩大的毒云。燃烧效果或引爆技能会使毒云产生火焰爆炸。',
'Frost Bomb':'创造一颗不断脉动的冰霜法球。每次脉动对附近敌人施加元素曝晒；持续时间结束时引爆，对周围敌人造成冰冷伤害，并留下冰冷灌注。',
'Herald of Ash':'启用时，使用非捷类攻击对敌人造成足够的过量击杀伤害，会引发爆炸，根据过量伤害点燃附近敌人。',
'Pounce':'变身为狼人并跃向目标位置，伤害落点周围的敌人。触发捕猎者印记，目标为被击中敌人中稀有度最高者；若此技能插有印记宝石，则改为触发该印记。使用此技能也使你的狼类召唤物立即可以跳跃。',
'Tornado':'创造吸入敌人并持续造成物理伤害的风暴。龙卷风与元素地面重叠时，会吸收该地面的减益，施加给内部敌人，同时造成该元素的额外伤害。',
'Elemental Weakness':'短暂延迟后诅咒区域内全部目标，降低其元素抗性。',
'Arctic Armour':'启用时召唤冰冷屏障，随时间累积层数。有层数时，击中你的近战攻击会消耗一层，产生冰霜爆发，对攻击者造成冰冷法术伤害。',
'Withering Presence':'启用时释放光环，周期性使存在范围内的敌人凋零。',
'Mana Remnants':'召唤奥术能量恢复魔力。启用时，击杀受元素异常状态影响的敌人有机会生成魔力残留物；暴击此类目标也会每隔数秒生成一个。拾取残留物恢复魔力，且可以溢出最大魔力。',
'Temporal Chains':'诅咒区域内全部敌人，使其缓速，并使它们身上的其他效果更慢消退。',
'Blasphemy':'将插槽中的诅咒技能转为光环，将其效果施加给附近全部敌人。',
'Virtuous Barrier':'启用时召唤闪耀屏障，随时间积累各属性的防御宝石微粒；被击中时随机失去一颗微粒。',
'Ice Shards':'为十字弓装填一匣冰冻弩箭，快速射向地面，在落点留下延迟布设的冰片。布设后，敌人踩到冰片会引发爆炸；布设越久，伤害越高，直至上限。再次使用会重新装填。',
'Shockwave Totem':'升起图腾，反复重击周围地面，伤害附近敌人。锯齿地面被重击时会爆发，伤害站在上面的敌人；图腾本身不会创造锯齿地面。变身时也可以使用此技能。',
'Seismic Cry':'施放造成伤害的战吼，击退附近敌人，并重度晕眩已准备被晕眩的敌人。若重度晕眩敌人，或击中已经重度晕眩的敌人，会增幅后续重击，使其额外产生一次余震。可消耗耐力球绕过冷却。',
'Charge Regulation':'启用时，根据当前拥有的充能球获得强力增益；维持增益会每隔数秒消耗充能球。',
'Incendiary Shot':'为十字弓装填燃烧弩箭，在飞行中分裂。命中时伤害并点燃敌人，也会影响最终目标后方的小型锥形区域。碎片可以合并。',
'Infernal Cry':'施放战吼，附近有敌人时增幅后续近战攻击。范围内敌人变得不稳定，死亡时会燃烧爆炸。可消耗耐力球绕过冷却。',
'Multishot':'辅助投射物技能，使其发射额外投射物，同时降低技能速度与伤害。',
'Elemental Armament':'辅助攻击，使其造成更多元素伤害。',
'Brutality':'辅助造成伤害的技能，提高物理伤害，但无法造成元素或混沌伤害。',
'Brutality III':'辅助造成伤害的技能，提高物理伤害，但无法造成其他类型的伤害；同时使命中有机会无视物理伤害减免。',
'Short Fuse I':'辅助在经过一段时间后引爆的技能，缩短引爆等待时间。',
'Short Fuse II':'辅助在经过一段时间后引爆的技能，大幅缩短引爆等待时间，但降低伤害。',
'Potent Exposure':'辅助能施加曝晒的技能，增强其曝晒效果。',
'Magnified Area':'辅助具有范围效果的技能，扩大其范围。',
'Cooldown Recovery':'辅助具有冷却时间的技能，加快冷却恢复；不会影响召唤物技能。',
'Considered Casting':'辅助由你自行施放且能击中敌人的法术，降低施法速度以提高伤害。',
'Searing Flame':'辅助能击中敌人的技能，降低击中伤害，但提高造成的点燃幅度。',
'Concentrated Area':'辅助具有范围效果的技能，缩小范围，但提高范围伤害。',
'Burgeon':'辅助由你自行使用的引导技能；引导时间越久，伤害越高。',
'Nova Projectiles':'辅助投射物技能，使投射物环形发射；无法辅助从上方落下投射物的技能。',
'Heightened Curse':'辅助诅咒技能，增强诅咒幅度。',
'Focused Curse':'辅助诅咒技能，使其在施放后更快诅咒敌人。',
'Expand':'辅助由你自行施放的法术，使其随时间积累封印。施放时消耗封印以扩大范围。无法辅助引导、有冷却或已经获得封印的技能。',
'Advancing Storm':'辅助风暴技能，使其在使用者位置出现并朝目标位置移动。',
'Prolonged Duration':'辅助具有持续时间的技能，延长其持续时间。',
'Controlled Destruction':'辅助能击中敌人的法术，提高击中伤害，但无法造成暴击。',
'Overabundance':'辅助具有“限制”数量的技能，提高数量上限，但缩短持续时间。只影响明确使用 Limit 字样的限制。',
'Spell Echo':'辅助由你自行使用且可以串联的法术，使其回响。',
'Efficiency':'辅助技能，降低使用消耗；无法辅助保留精魂的技能。',
'Encroaching Ground':'辅助创造地面区域的技能，使地面随时间扩大，直至上限。',
'Boundless Energy':'辅助触发类元技能，使其更快生成能量。',
"Khatal's Rejuvenation":'辅助生成残留物的技能。拾取这些残留物时获得卡塔尔的再生。',
'Harmonic Remnants':'辅助创造残留物的技能，扩大拾取距离，并有机会创造额外残留物。',
"Dialla's Desire":'辅助具有等级的技能，提高等级与品质，并降低消耗和保留。',
'Armour Demolisher':'辅助技能，增强其造成的护甲破坏。',
'Bounty':'辅助能击中敌人的技能，使其击杀的敌人提供更多药剂与护符充能。',
'Remnant Potency':'辅助创造残留物的技能，增强其残留物效果。',
'Ammo Conservation':'辅助十字弓弹药技能，使发射弩箭有机会不消耗弹药。',
'Mobility':'辅助可在移动中使用的技能，使使用时的移动速度更快。',
'Fire Penetration':'辅助能击中敌人的技能，使其击中无视敌人的火焰抗性。',
'Hardy Totems':'辅助创造图腾的技能，提高图腾生命。',
'Reinforced Totems':'辅助创造图腾的技能，给予图腾额外元素抗性。',
'Ignite':'辅助能击中敌人的技能，使其更容易点燃，且点燃伤害更快结算。',
'Enraged Warcry':'辅助战吼，改为消耗怒气绕过通常的冷却。',
'Deliberation':'辅助可在移动中使用的技能，增加移动速度惩罚以换取更多伤害。',
'Pin':'辅助能击中敌人的技能，使其物理伤害能够钉身，但无法累积晕眩。',
'Pierce':'辅助投射物技能，使投射物穿透一个敌人，但穿透后造成更少伤害。',
'Herbalism':'辅助持续增益技能；技能启用时，增加生命药剂的回复量。',
'Slow Potency':'辅助技能，增强其造成的缓速。',
}

# Exact line translations also preserve awkward/missing values in the source.
EXACT = {
'Modifiers to cast speed also affect this skill\'s cost':'施法速度修正也影响此技能的消耗',
'75% more damage per Stage':'每层总伤害额外提高 75%',
'Explosion radius is 0.6 metres per Stage':'每层爆炸半径为 0.6 米',
'10 maximum Stages':'最多 10 层',
'Projectiles cannot Fork':'投射物无法分裂',
'Oil Slows enemy movement speed by 40%':'燃油使敌人移动速度降低 40%',
'Oil applies Exposure, lowering Total\nElemental Resistances by 20%':'燃油施加曝晒，使总元素抗性降低 20%',
'Gain 2 Energy per metre travelled while dodge rolling':'翻滚时每移动 1 米获得 2 点能量',
'Blinds Enemies':'使敌人致盲',
'500% more Stun buildup':'晕眩累积总量额外提高 500%',
'Consumes 15 Heat if possible to\nGain 50% of damage as Fire damage':'若可能，消耗 15 点热量，获得等同于伤害 50% 的额外火焰伤害',
'Converts 80% of Physical damage to Fire damage':'将 80% 物理伤害转换为火焰伤害',
'Fires +1 Projectiles':'额外发射 1 个投射物',
'Limit 1 Frost Bomb':'限制 1 颗寒霜爆',
'Initially applies 20% Elemental Exposure and 2% Exposure per pulse, up to a maximum of 50%':'初始施加 20% 元素曝晒，每次脉动额外施加 2%，上限 50%',
'Chills Enemies as though dealing 300% more damage':'计算冰缓时，视同造成的伤害总量额外提高 300%',
'Ignite surrounding enemies if Overkill damage is at least 20% of enemy\'s maximum Life':'过量击杀伤害至少达到敌人最大生命的 20% 时，点燃周围敌人',
'+0.2 seconds to Total Attack Time':'总攻击时间 +0.2 秒',
'Gem Quality grants Socketed Skills an additional effect':'宝石品质给予插槽中的技能额外效果',
'For each colour of Socketed Support Gem that is most numerous, gain:':'插槽中数量最多的每种辅助宝石颜色，分别给予：',
'•Red: Hits against you have no Critical Damage Bonus':'红色：击中你时没有暴击伤害加成',
'•Blue: Skills have 30% less cost':'蓝色：技能消耗总量额外降低 30%',
'•Green: 40% less Movement Speed Penalty from using Skills while Moving':'绿色：移动中使用技能的移动速度惩罚总量额外降低 40%',
'Grants 1 additional Skill Slot':'给予 1 个额外技能栏位',
'Grants 2 additional Skill Slots':'给予 2 个额外技能栏位',
'Body Armour: Idols socketed in this item gain the benefits of their Bonded modifiers':'胸甲：插入此物品的魔偶获得其契合词缀的收益',
'100% more Freeze Buildup':'冰冻累积总量额外提高 100%',
'100% more Magnitude of Chill inflicted':'造成的冰缓幅度总量额外提高 100%',
'Modifiers to Spell Damage apply to Debuff\'s Damage over Time':'法术伤害修正也套用于减益的持续伤害',
'Limit 1 Tornado':'限制 1 个龙卷风',
'Curse applies after 1.5 seconds delay':'诅咒在 1.5 秒延迟后施加',
'Supported Skills deal no Elemental Damage':'被辅助技能无法造成元素伤害',
'Supported Skills deal no Chaos Damage':'被辅助技能无法造成混沌伤害',
'Supported Skills cannot deal Critical Hits':'被辅助技能无法造成暴击',
'Supported Skills fire Projectiles in a circle':'被辅助技能以环形发射投射物',
'Supported Skills have a maximum of 3 Seals':'被辅助技能最多拥有 3 个封印',
'Supported Spells gain a Seal every 200% of cast time':'被辅助法术每经过等同于施法时间 200% 的时间获得一个封印',
'Supported Skills get 30% increased area of effect per Seal broken':'被辅助技能每消耗一个封印，范围效果增加 30%',
'Supported Skills originate from the player and move towards the target location':'被辅助技能从玩家位置出现，并朝目标位置移动',
'Supported Skills have +1 to Limit':'被辅助技能数量上限 +1',
'Supported Spells Echo 1 time':'被辅助法术回响 1 次',
'Ignites you inflict deal Damage 15% faster':'你造成的点燃伤害加速 15%',
'Enemies Ignited by you take Chaos Damage instead of Fire Damage from Ignite':'被你点燃的敌人受到的点燃伤害改为混沌伤害',
'Remnants created by Supported Skills grant Khatal\'s Rejuvenation when collected':'拾取被辅助技能创造的残留物时，获得卡塔尔的再生',
'Socketed Curse Skills apply in an Aura around you':'插槽中的诅咒技能以自身周围光环的形式施加',
'Reserves 60 Spirit per socketed Curse':'每个插槽中的诅咒保留 60 精魂',
'Converts all Evasion Rating to Armour':'将全部闪避值转换为护甲',
'Maximum amount of Guard is based on maximum Energy Shield instead':'守护值上限改为由最大能量护盾决定',
'Divine Flight':'神圣飞行',
'Dodge Roll passes through Enemies':'翻滚可以穿过敌人',
'2% increased maximum Life per Strength Mote':'每颗力量微粒增加 2% 最大生命',
'5% increased Life Regeneration rate per Intelligence Mote':'每颗智慧微粒增加 5% 生命再生率',
'5% increased Mana Regeneration rate per Intelligence Mote':'每颗智慧微粒增加 5% 魔力再生率',
'5% increased Armour, Evasion and\nEnergy Shield per Dexterity Mote':'每颗敏捷微粒增加 5% 护甲、闪避和能量护盾',
'Maximum of each Attribute of Mote is 3 plus the number of Skills you have which require that Attribute':'每种属性微粒上限为 3，加上你拥有的需要该属性的技能数量',
'Single-Attribute Skills grant twice as many maximum Motes':'单一属性技能给予双倍的微粒数量上限',
'Loads 16 additional bolts':'额外装填 16 枚弩箭',
'Loads an additional bolt':'额外装填 1 枚弩箭',
'Hits from Supported Skills ignore enemy Fire Resistance':'被辅助技能的击中无视敌人的火焰抗性',
'Physical Damage from Supported Skill is Pinning':'被辅助技能的物理伤害能够造成钉身',
'Modifiers to Stun Buildup for Supported Skills instead apply to Pin Buildup':'被辅助技能的晕眩累积修正改为套用于钉身累积',
'Supported Skills cannot cause Stun Buildup':'被辅助技能无法累积晕眩',
'Supported Warcries spend 15 Rage to bypass their Cooldown, instead of an Endurance Charge':'被辅助战吼改为消耗 15 点怒气绕过冷却，取代耐力球',
'Knocks Back Enemies':'击退敌人',
'Empowers one Slam per 10 enemy Power in\nrange, counting up to 50 Power':'范围内敌人每 10 点威能增幅一次重击，最多计入 50 点威能',
'Empowers one Attack per 10 enemy Power in\nrange, counting up to 50 Power':'范围内敌人每 10 点威能增幅一次攻击，最多计入 50 点威能',
'Consumes one of each Charge every 10 seconds':'每 10 秒消耗每种充能球各 1 颗',
'+1 to Evasion Rating per 1 Item Armour on Equipped Gloves':'已装备手套每具有 1 点物品护甲，获得 +1 闪避值',
'Grenade Skills Fire an additional Projectile':'手雷技能额外发射 1 个投射物',
'Grenade Skills have +1 Cooldown Use':'手雷技能可储存的冷却使用次数 +1',
'20% of Flask Recovery applied Instantly':'20% 药剂回复立即生效',
'This Flask cannot be Used but applies its Effect constantly':'此药剂无法使用，但其效果持续生效',
'Energy Shield Recharge starts on use':'使用时开始能量护盾充能',
'Grants Onslaught during effect':'效果期间给予猛攻',
'Used when you become Frozen':'被冰冻时使用',
'Used when you become Ignited':'被点燃时使用',
'Used when you are affected by a Slow':'受到缓速影响时使用',
'Used when you kill a Rare or Unique enemy':'击杀稀有或传奇敌人时使用',
'Limited to 1':'限制 1 个',
'Allocates Paragon':'配置「模范」',
'Has (1-3) Charm Slot':'具有 (1-3) 个护符栏位',
'Natural grace is born, not earned.':'天生优雅，非后天所得。',
'Rivers of power coursed through their veins.':'力量之河曾在他们的血管中奔流。',
'Now, that power is yours, for good or ill.':'如今，无论祸福，那份力量属于你。',
'Beyond the veil of death, there burns a fire':'死亡帷幕之外，有一团烈火燃烧，',
'by whose light night is borne.':'其光芒孕育黑夜。',
'Entropy can be reversed.':'熵可以逆转。',
'To become a warrior and a hunter, each young':'欲成为战士与猎人，每位年轻的',
'Azmeri must prove themselves before the Spirit.':'阿兹莫里人都须在神灵面前证明自己。',
'"How do I cope with what I witnessed on Wraeclast?':'「我该如何面对在瓦尔克拉斯的所见？',
'Thank the Ancestors! My cup, it overflows."':'感谢先祖！我的杯中之物，满溢而出。」',
'- Lavianga, former advisor to Kaom':'—— 拉维安加，卡奥姆的前顾问',
'"Soar. Be swift. Let none trespass here, from':'「翱翔吧。疾行吧。莫让任何人闯入此地，',
'above or below, lest your purpose be forfeit."':'无论来自天空还是地底，否则使命将被辜负。」',
'The cursed ones march forever,':'受诅咒者永远行军，',
'On their hopeless, last endeavour.':'踏上绝望的最后征途。',
}

# Join visual wrapping before translation; preserve source English separately.
JOIN = [
('Oil applies Exposure, lowering Total\nElemental Resistances by 20%','Oil applies Exposure, lowering Total\nElemental Resistances by 20%'),
]
PHRASES = {
'increased Explicit Fire Modifier magnitudes':'增加显性火焰词缀幅度',
'increased Global Armour, Evasion and Energy Shield':'增加全域护甲、闪避和能量护盾',
'increased Armour and Energy Shield':'增加护甲和能量护盾',
'increased Armour and Evasion':'增加护甲和闪避',
'increased Evasion and Energy Shield':'增加闪避和能量护盾',
'increased Area of Effect for Attacks':'增加攻击的范围效果',
'increased Magnitude of Ailments you inflict':'增加你造成的异常状态幅度',
'increased Reservation Efficiency of Skills':'增加技能保留效用',
'increased Life Regeneration rate':'增加生命再生率',
'increased Mana Regeneration Rate':'增加魔力再生率',
'increased Rarity of Items found':'增加物品稀有度',
'increased Flammability Magnitude':'增加可燃性幅度',
'increased Ignite Magnitude':'增加点燃幅度',
'increased Quantity of Gold Dropped by Slain Enemies':'增加击杀敌人掉落的金币数量',
'increased Stun Threshold':'增加晕眩门槛',
'increased Area of Effect':'增加范围效果',
'increased Presence Area of Effect':'增加存在范围效果',
'increased cooldown recovery rate':'增加冷却恢复速度',
'increased Cooldown Recovery Rate':'增加冷却恢复速度',
'increased Curse Magnitudes':'增加诅咒幅度',
'increased Magnitudes':'增加幅度',
'increased Fire Damage':'增加火焰伤害',
'increased Spell Damage':'增加法术伤害',
'increased Physical Damage':'增加物理伤害',
'increased Elemental Damage':'增加元素伤害',
'increased Armour':'增加护甲',
'increased Movement Speed':'增加移动速度',
'increased Evasion Rating':'增加闪避值',
'increased Accuracy Rating':'增加命中值',
'increased Attack Speed':'增加攻击速度',
'increased Cast Speed':'增加施法速度',
'increased Bolt Speed':'增加弩箭速度',
'increased Warcry Speed':'增加战吼速度',
'increased Stun Buildup':'增加晕眩累积',
'increased Curse Duration':'增加诅咒持续时间',
'increased Effect of Prefixes':'增加前缀效果',
'reduced Charges per use':'减少每次使用消耗的充能',
'reduced Amount Recovered':'减少回复量',
'to maximum Life per Socket filled':'每个已填入插槽给予最大生命',
'to Quality of all Skills':'全部技能品质',
'to maximum Energy Shield':'最大能量护盾',
'to maximum Life':'最大生命',
'to maximum Mana':'最大魔力',
'to Cold and Chaos Resistances':'冰冷和混沌抗性',
'to all Maximum Elemental Resistances':'全部最大元素抗性',
'to all Elemental Resistances':'全部元素抗性',
'to Chaos Resistance':'混沌抗性',
'to Cold Resistance':'冰冷抗性',
'to Lightning Resistance':'闪电抗性',
'to Fire Resistance':'火焰抗性',
'to Level of all Fire Spell Skills':'全部火焰法术技能等级',
'to Level of all Projectile Skills':'全部投射物技能等级',
'to Level of all Spell Skills':'全部法术技能等级',
'to Level of all <Random Skill Type> Skills':'全部〈随机技能类型〉技能等级',
'to Level of Supported Skill Gems':'被辅助技能宝石等级',
'to Quality of Supported Skills':'被辅助技能品质',
'to all Attributes':'全部属性',
'to Dexterity':'敏捷',
'to Strength':'力量',
'to Spirit':'精魂',
'to Evasion Rating':'闪避值',
'to Accuracy Rating':'命中值',
'to Armour':'护甲',
'of Armour also applies to Elemental Damage':'的护甲也套用于元素伤害',
'of Armour also applies to Chaos Damage':'的护甲也套用于混沌伤害',
'faster Dodge Roll':'更快的翻滚',
'more Elemental Attack damage':'更多元素攻击伤害',
'more Physical Damage':'更多物理伤害',
'more Hit Damage':'更多击中伤害',
'more Area Damage':'更多范围伤害',
'less Area of Effect':'更少范围效果',
'less Cast Speed':'更少施法速度',
'more Cast Speed':'更多施法速度',
'less Skill Speed':'更少技能速度',
'less Skill Effect Duration':'更少技能效果持续时间',
'more Skill Effect Duration':'更多技能效果持续时间',
'less Detonation Time':'更短引爆时间',
'less Damage with Hits':'更少击中伤害',
'less Damage':'更少伤害',
'more Damage':'更多伤害',
'less Cost':'更少消耗',
'increased Energy':'增加能量获取',
'Ignite Duration on Enemies':'敌人身上的点燃持续时间',
'Critical Strike Chance:':'暴击率：',
'Critical Hit Chance:':'暴击率：',
'Weapon Speed:':'武器速度：',
'Physical Damage:':'物理伤害：',
'Cold Damage:':'冰冷伤害：',
'Evasion Rating:':'闪避值：',
'Energy Shield:':'能量护盾：',
'Armour:':'护甲：',
'Item Level:':'物品等级：',
'Quality:':'品质：',
'Level:':'等级：',
'Cast Time:':'施放时间：',
'Mana Range:':'魔力消耗区间：',
'Reservaton:':'保留：',
'Grants Skill:':'给予技能：',
'Requires Level':'需求等级',
'Requires:':'需求：',
'Sockets:':'插槽：',
'Armour: ':'防具：',
'Body Armour:':'胸甲：',
'Boots:':'鞋子：',
'Gloves:':'手套：',
'Helmet:':'头盔：',
'Shield:':'盾牌：',
'Sceptre:':'权杖：',
'Wand or Staff:':'魔杖或长杖：',
'Martial Or Caster Weapon:':'武器或施法武器：',
'Martial Weapon:':'武器：',
'All:':'全部：',
'Additional Effects From Quality:':'品质提供的额外效果：',
'Supported Spell Skills':'被辅助的法术技能',
'Supported Spells':'被辅助法术',
'Supported Skills':'被辅助技能',
'Echoes from Supported Spells':'被辅助法术的回响',
'Meta Skills':'触发类元技能',
' more ':' 更多 ',
' less ':' 更少 ',
' increased ':' 增加 ',
' reduced ':' 减少 ',
' metres':' 米',
' seconds':' 秒',
' mana':' 魔力',
' per second':' 每秒',
}
TAGS = {'Spell':'法术','AoE':'范围效果','Fire':'火焰','Channelling':'引导','Nova':'新星','Staged':'分层','Attack':'攻击','Projectile':'投射物','Grenade':'手雷','Duration':'持续时间','Buff':'增益','Persistent':'持续','Trigger':'触发','Meta':'元技能','Ammunition':'弹药','Detonator':'引爆','Support':'辅助','Physical':'物理','Chaos':'混沌','Cold':'冰冷','Lightning':'闪电','Orb':'法球','Remnant':'残留物','Herald':'捷','Minion':'召唤物','Shapeshift':'变身','Werewolf':'狼人','Melee':'近战','Slam':'重击','Mark':'印记','Travel':'移动','Wind':'风','Storm':'风暴','Curse':'诅咒','Repeatable':'可重复','Sustained':'持续施放','Aura':'光环','Lineage':'谱系','Totem':'图腾','Warcry':'战吼','Hazard':'陷阱地面','Merging':'合并','Notable':'核心天赋','Keystone':'关键天赋','Crossbows':'十字弓','Staves':'长杖','Rings':'戒指','Amulets':'护身符','Helmets':'头盔','Body Armours':'胸甲','Gloves':'手套','Boots':'鞋子','Belts':'腰带','Charms':'护符','Life Flasks':'生命药剂','Mana Flasks':'魔力药剂','Corrupted':'已腐化','Sapphire':'蓝玉','Ruby':'红玉','Emerald':'翠绿'}

EXACT.update({
'Banner Skills have (15-25)% increased Duration':'斗旗技能持续时间增加 (15-25)%',
'(0-20)% more Cast Speed':'施法速度总量额外提高 (0-20)%',
'Fire a bolt from your crossbow.':'从十字弓发射一枚弩箭。',
'+(0-10)% maximum Elemental Exposure applied':'施加的元素曝晒上限 +(0-10)%',
'+(0-2) seconds to Tornado duration':'龙卷风持续时间 +(0-2) 秒',
'+1 metre to Dodge Roll distance':'翻滚距离 +1 米',
'+1 to Totem Limit':'图腾数量上限 +1',
'+12 seconds to Totem duration':'图腾持续时间 +12 秒',
'100% more Magnitude of Ignite inflicted with Supported Skills':'被辅助技能造成的点燃幅度总量额外提高 100%',
'Bolts fired by Supported Crossbow Attacks have 25% chance to not expend Ammunition':'被辅助十字弓攻击发射的弩箭有 25% 几率不消耗弹药',
'Curse zones from Supported\nSkills erupt after 50% less delay':'被辅助技能的诅咒区域生效延迟总量额外降低 50%',
'Totems created by Supported\nSkills have 50% more maximum Life':'被辅助技能创造的图腾，其最大生命总量额外提高 50%',
'Remnants from Supported Skills have\n20% increased effect':'被辅助技能的残留物效果增加 20%',
'25% less Movement Speed penalty while\nusing Supported Skills':'使用被辅助技能时，移动速度惩罚总量额外降低 25%',
'30% more Movement Speed penalty while\nusing Supported Skills':'使用被辅助技能时，移动速度惩罚总量额外提高 30%',
'Deals (72.9-292.2) damage per second of each absorbed\nElemental Damage type':'每种吸收的元素伤害类型，每秒造成 (72.9-292.2) 伤害',
'(24-26)% more Critical Hit Chance while\nyou have a Power Charge':'拥有暴击球时，暴击率总量额外提高 (24-26)%',
'Body Armour: Gain Maximum Energy Shield equal to 50% of total\nStrength Requirements of Equipped Armour Items':'胸甲：获得等同于已装备防具力量需求总和 50% 的最大能量护盾',
'Debuffs inflicted with Supported Skills have 15% increased Slow Magnitude':'被辅助技能施加的减益，其缓速幅度增加 15%',
'Destabilises Enemies for 8 seconds':'使敌人不稳定，持续 8 秒',
'Empowered Attack Aftershocks deal (0-10)% more damage':'被增幅攻击的余震，总伤害额外提高 (0-10)%',
'Empowered Attacks Gain (0-10)% of damage as extra Fire damage':'被增幅攻击获得等同于伤害 (0-10)% 的额外火焰伤害',
'Empowered Attacks Gain (32-49)% of damage as extra Fire damage':'被增幅攻击获得等同于伤害 (32-49)% 的额外火焰伤害',
'Exposure applied by Supported Skills has 20% increased effect':'被辅助技能施加的曝晒效果增加 20%',
'Gain Guard equal to (10-20)% of missing Energy Shield for 4 seconds when you Dodge Roll':'翻滚时获得等同于已损失能量护盾 (10-20)% 的守护值，持续 4 秒',
'Gains 20% more Area of Effect per second, up to a maximum of 100%':'每秒范围效果总量额外提高 20%，最多 100%',
'Ground Surfaces created by Supported Skills gain 20% increased Area of Effect per second, up to a maximum of 100%':'被辅助技能创造的地面每秒增加 20% 范围效果，最多 100%',
'Hits with Supported Skills have 20% chance to ignore Enemy Physical Damage reduction':'被辅助技能的击中有 20% 几率无视敌人的物理伤害减免',
'Ignites you inflict with this skill deal Damage 15% faster':'此技能造成的点燃伤害加速 15%',
'Spawn a Remnant on Critically Hitting a target affected by an Elemental Ailment, no more than once every 2 seconds':'暴击受元素异常状态影响的目标时生成一个残留物，每 2 秒最多一次',
'25% chance to spawn a Remnant on killing an enemy affected by an Elemental Ailment':'击杀受元素异常状态影响的敌人时，有 25% 几率生成一个残留物',
'20% chance for Supported Skills to create an additional Remnant':'被辅助技能有 20% 几率创造一个额外残留物',
'Remnants last for 8 seconds':'残留物持续 8 秒',
'Remnants created by Supported Skills can be collected from 35% further away':'被辅助技能创造的残留物，拾取距离增加 35%',
'30% Increased Recovery from Life Flasks while a Supported Skill is active':'被辅助技能启用时，生命药剂回复量增加 30%',
'When you kill a Rare monster, you gain its Modifiers for 60 seconds':'击杀稀有怪物时，获得其词缀，持续 60 秒',
'Helmet: +1 to maximum Life per 8 Armour on Equipped Helmet':'头盔：已装备头盔每有 8 点护甲，最大生命 +1',
'Boots: Hits against you have no Critical Damage Bonus while on Consecrated Ground':'鞋子：站在奉献地面时，击中你没有暴击伤害加成',
'Martial Weapon: Leeches 6% of Physical Damage as Life':'武器：物理伤害的 6% 偷取为生命',
'Gloves: Adds 1 to 4 Physical Damage to Attacks':'手套：攻击附加 1 至 4 物理伤害',
'Projectiles from Supported Skills Pierce an Enemy':'被辅助技能的投射物穿透一个敌人',
"Projectiles from Supported Skills deal 20% less Damage if they've Pierced an enemy":'被辅助技能的投射物穿透敌人后，总伤害额外降低 20%',
'Supported Skills Break 50% more Armour':'被辅助技能的护甲破坏量总量额外提高 50%',
'Supported Skills have 200% more Flammability Magnitude':'被辅助技能的可燃性幅度总量额外提高 200%',
'Supported Skills deal 20% more Damage per second spent Channelling, up to 40%':'被辅助技能每引导 1 秒，总伤害额外提高 20%，最多 40%',
'Echoes from Supported Spells have 40% increased Area of Effect':'被辅助法术的回响增加 40% 范围效果',
'Supported Spell Skills have 15% less Cast Speed':'被辅助法术技能的施法速度总量额外降低 15%',
'Gains a Stage every second, up to a maximum of (3-5) Stages':'每秒获得一层，上限 (3-5) 层',
'Gains a Stage every seconds, up to a maximum of (0-1) Stages':'每隔〈原文未显示数值〉秒获得一层，上限 (0-1) 层',
'+-1 Prefix Modifier allowed':'可拥有的前缀词缀数量 +-1',
'All: +-1 Suffix Modifier allowed':'全部：可拥有的后缀词缀数量 +-1',
})
PHRASES.update({
'Banners have ':'斗旗具有 ', 'Supported Skills gain ':'被辅助技能获得 ', 'Supported Curses have ':'被辅助诅咒具有 ',
'Mana Regeneration rate':'魔力再生率','per Intelligence Mote':'／每颗智慧微粒',
'increased Skill Speed while you have a Frenzy Charge':'拥有狂怒球时增加技能速度',
'more Armour, Evasion and Energy Shield while you have an Endurance Charge':'拥有耐力球时额外提高护甲、闪避和能量护盾总量',
'more maximum Life':'额外提高最大生命总量','more Flammability Magnitude':'额外提高可燃性幅度总量',
'increased Energy gained':'增加能量获取','increased Energy generation':'增加能量生成',
'Supported Curses':'被辅助诅咒','Meta Skills gain':'触发类元技能获得',
'Banners have':'斗旗具有',' Duration':' 持续时间',
"if you've Dodge Rolled Recently":'若近期有翻滚', 'Str ':'力量 ',
})

def translate(line, terms):
    if line in EXACT: return EXACT[line]
    if line in TAGS: return TAGS[line]
    if line in terms: return terms[line]['cn']
    # Numeric wording is translated by patterns without changing any value.
    patterns = [
        (r'(\d+)(Armour|Energy Shield|Evasion Rating|Critical Hit Chance|Weapon Speed)',lambda m:m[1]+' '+{'Armour':'护甲','Energy Shield':'能量护盾','Evasion Rating':'闪避值','Critical Hit Chance':'暴击率','Weapon Speed':'武器速度'}[m[2]]),
        (r'Each Remnant grants (.+) Mana',r'每个残留物给予 \1 魔力'),
        (r'Deals (.+) Physical damage per second',r'每秒造成 \1 物理伤害'),
        (r'Consumes one of each Charge every (.+) seconds',r'每 \1 秒消耗每种充能球各 1 颗'),
        (r'Withers enemies in your Presence every (.+) seconds',r'每 \1 秒使存在范围内的敌人凋零'),
        (r'Totems gain (.+) to (all Elemental Resistances|Chaos Resistance)',lambda m:'图腾获得 '+m[1]+' '+{'all Elemental Resistances':'全部元素抗性','Chaos Resistance':'混沌抗性'}[m[2]]),
        (r'Totems summoned by Supported Skills have (.+) to (all Elemental Resistances|all Maximum Elemental Resistances)',lambda m:'被辅助技能召唤的图腾获得 '+m[1]+' '+{'all Elemental Resistances':'全部元素抗性','all Maximum Elemental Resistances':'全部最大元素抗性'}[m[2]]),
        (r'Fires (.+) additional Projectiles',r'额外发射 \1 个投射物'),
        (r'Deals (.+) to (.+) (Fire|Cold|Physical) Damage(.*)',lambda m:f'造成 {m[1]} 至 {m[2]} {TAGS[m[3]]}伤害'+('／每层' if 'per Stage' in m[4] else '')),
        (r'(Detonation Time|Oil Duration|Exposure duration|Tornado duration|Withered duration) is (.+) seconds',lambda m:{'Detonation Time':'引爆时间','Oil Duration':'燃油持续时间','Exposure duration':'曝晒持续时间','Tornado duration':'龙卷风持续时间','Withered duration':'凋零持续时间'}[m[1]]+'为 '+m[2]+' 秒'),
        (r'(Explosion|Impact|Curse|Tornado|Warcry) radius is (.+) metres',lambda m:{'Explosion':'爆炸','Impact':'冲击','Curse':'诅咒','Tornado':'龙卷风','Warcry':'战吼'}[m[1]]+'半径为 '+m[2]+' 米'),
        (r'Damage and Oil spray radius is (.+) metres',r'伤害及燃油喷洒半径为 \1 米'),
        (r'Pulse and explosion radius are (.+) metres',r'脉动与爆炸半径为 \1 米'),
        (r'Cannot apply Exposure to enemies of level higher than (.+)',r'无法对等级高于 \1 的敌人施加曝晒'),
        (r'Curse does not apply to enemies above level (.+)',r'诅咒对等级高于 \1 的敌人无效'),
        (r'Curse duration is (.+) seconds',r'诅咒持续时间为 \1 秒'),
        (r'Curse inflicts (.+) to Elemental Resistances',r'诅咒施加 \1 元素抗性修正'),
        (r'Curse Slows targets by (.+)',r'诅咒使目标缓速 \1'),
        (r'Curse makes other effects on targets expire (.+) slower',r'诅咒使目标身上其他效果的消退速度减慢 \1'),
        (r'Gains a Stage every (.*) seconds?, up to a maximum of (.+) Stages',r'每 \1 秒获得一层，上限 \2 层'),
        (r'Gains a random Mote every (.+) seconds',r'每 \1 秒获得一颗随机微粒'),
        (r'Enemies killed by Hits from Supported Skills grant (.+) more (Mana Flask Charges|Life Flask Charges|Charm charges)',lambda m:f'被辅助技能击中所击杀的敌人给予额外 {m[1]} '+{'Mana Flask Charges':'魔力药剂充能','Life Flask Charges':'生命药剂充能','Charm charges':'护符充能'}[m[2]]),
        (r'Adds (.+) to (.+) (Physical|Cold) Damage(.*)',lambda m:f'附加 {m[1]} 至 {m[2]} {TAGS[m[3]]}伤害'+('至攻击' if 'Attacks' in m[4] else '')),
        (r'Gain (.+) of (Damage|Elemental Damage) as Extra (Fire|Cold) Damage',lambda m:f'获得等同于{("元素伤害" if m[2]=="Elemental Damage" else "伤害")} {m[1]} 的额外{TAGS[m[3]]}伤害'),
        (r'Damaging Ailments deal damage (.+) faster',r'伤害型异常状态的伤害加速 \1'),
        (r'Recover (.+) of maximum (Life|Mana) on Kill',lambda m:f'击杀时恢复 {m[1]} 最大'+{'Life':'生命','Mana':'魔力'}[m[2]]),
        (r'(.+) of Recovery applied Instantly',r'\1 的回复立即生效'),
        (r'(.+) Chance to gain a Charge when you kill an enemy',r'击杀敌人时有 \1 几率获得 1 次充能'),
        (r'Also grants (.+) Guard',r'同时给予 \1 守护值'),
        (r'Allocates (.+) Sinister Jewel Sockets',r'配置 \1 个阴险珠宝插槽'),
        (r'Possessed by Spirit Of The \[Azmeri Spirit\] for (.+) seconds on use',r'使用时被〈阿兹莫里神灵〉附身 \1 秒'),
        (r'Supported Skills deal (.+)',r'被辅助技能造成 \1'),
        (r'Supported Spells deal (.+)',r'被辅助法术造成 \1'),
        (r'Supported Skills have (.+)',r'被辅助技能具有 \1'),
    ]
    for pattern, replacement in patterns:
        if re.fullmatch(pattern,line):
            line=re.sub(pattern,replacement,line);break
    if line.startswith('Requires:'):
        line=line.replace('Requires:','需求：').replace('Level','等级').replace('Strength','力量').replace('Dexterity','敏捷').replace('Intelligence','智慧').replace('Int ','智慧 ')
    for en,value in sorted(PHRASES.items(),key=lambda x:-len(x[0])): line=line.replace(en,value)
    for en,row in sorted(terms.items(),key=lambda x:-len(x[0])): line=line.replace(en,row['cn'])
    return line

def localized_body(text,name,terms):
    body=text.split('\n',1)[1].strip() if '\n' in text else ''
    for wrapped in EXACT:
        if '\n' in wrapped: body=body.replace(wrapped,EXACT[wrapped])
    # Descriptions are consistently the paragraph following requirements.
    parts=body.split('\n\n')
    base=re.sub(r' (I|II|III)$','',name)
    description=DESCRIPTIONS.get(name,DESCRIPTIONS.get(base))
    result=[]
    for part in parts:
        if description and not re.search(r'\d',part) and (part.startswith(('Supports ','Support ','Channel ','Fire ','Create ','While active','Conjure ','Curse ','Turn ','Shapeshift ','Load ','Raise ','Perform '))):
            result.append(description)
        else:
            result.append('\n'.join(translate(line,terms) for line in part.splitlines()))
    return '\n\n'.join(result)

def canonical(url): return url[url.index('/assets/'):]
KINDS=[('/Weapons/TwoHandWeapons/Staves/','staff','Staves'),('/Weapons/TwoHandWeapons/Crossbows/','crossbow','Crossbows'),('/Weapons/','weapon',None),('/Helmets/','helmet','Helmets'),('/BodyArmours/','chest','Body Armours'),('/Gloves/','gloves','Gloves'),('/Boots/','boots','Boots'),('/Rings/','rings','Rings'),('/Amulets/','amulet','Amulets'),('/Belts/','belt','Belts'),('/Charms/','charm','Charms'),('/Flasks/','flask',None),('/Jewels/','jewels',None)]

def compile_tooltips(terms):
    tips={}; names={}; gallery=[[] for _ in range(9)]; seen={}
    def add(text,name,kind,stage=None,setno=None):
        identity=(text,kind,stage,setno)
        if identity in seen:return seen[identity]
        key='t'+str(len(tips));seen[identity]=key
        body=localized_body(text,name,terms)
        lookup=re.sub(r' \(life\)$','',name)
        tips[key]={'en':name,'cn':terms.get(lookup,{}).get('cn',name),'tw':terms.get(lookup,{}).get('tw',TW.convert(name)), 'body':{'cn':body,'tw':TW.convert(body)},'original':text,'kind':kind,'stage':stage,'set':setno}
        return key
    for r in RAW:
        if not r['name'] or not r['tips']:continue
        name=r['name'];text=r['tips'][0]['text'].strip()
        if text and text.splitlines()[0].strip()==name:
            names[name]=add(text,name,'named')
    names['Morior Invictus']=names.get('Morior Invictus (life)')
    for stage in range(9):
        primary={}
        for r in RAW:
            if r['stage']!=stage or r['kind']!='gear' or 'cdn-cgi' in r['image']:continue
            group=(r['id'],r['set'],canonical(r['image']))
            primary.setdefault(group,r)
            if r['tips']:primary[group]=r
        # Secondary weapon instances replace only the changed slots.
        unique=set()
        for (ident,setno,img),r in primary.items():
            kind,expected=next(((k,e) for frag,k,e in KINDS if frag in img),('item',None))
            def valid(row):
                if not row['tips']:return False
                text=row['tips'][0]['text']
                if expected:return expected in text.split('\n')[:5]
                return bool(text.strip()) and not text.startswith(('Perfect Body Rune','Fox Idol','Rune of','Raven-Touched Shard'))
            candidates=[x for x in RAW if x['stage']==stage and x['kind']=='gear' and canonical(x['image'])==img and valid(x) and (kind not in ['staff','crossbow','weapon'] or ('cdn-cgi' not in x['image'] and x['set']==setno))]
            if not valid(r):
                if not candidates:raise ValueError(f'Uncaptured equipment: stage {stage}, {img}')
                r=candidates[-1]
            text=r['tips'][0]['text'].strip();name=text.split('\n')[0]
            if (img,text) in unique:continue
            unique.add((img,text))
            tip=add(text,name,kind,stage,setno if kind in ['staff','crossbow','weapon'] else None)
            gallery[stage].append({'key':img,'kind':kind,'name':name,'tooltip':tip,'set':setno if kind in ['staff','crossbow','weapon'] else None})
            if name in terms and name not in names:names[name]=tip
    return {'tips':tips,'names':{k:v for k,v in names.items() if v},'gallery':gallery}

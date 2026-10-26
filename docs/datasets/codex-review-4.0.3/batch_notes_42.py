"""Actual L5-B022 review; one immutable pronunciation identity held."""
from record_batch import record, rows
r=rows("L5-B022")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B022", """
安邦定国 ānbāngdìngguó stabilize country; governance aspiration aligned.
百废俱兴 bǎifèijùxīng revive neglected tasks; post-earthquake reconstruction appropriate.
保家卫国 bǎojiāwèiguó protect homeland; soldier duty aligned.
本固枝荣 běngùzhīróng roots firm branches flourish; manufacturing base metaphor appropriate.
标本兼治 biāoběnjiānzhì roots and symptoms; 流域 liúyù corrected.
惩恶扬善 chéngèyángshàn punish evil/promote good; justice example aligned.
除暴安良 chúbàoānliáng protect citizens; police duty example correct.
大同世界 dàtóngshìjiè ideal harmony; historical quotation 与通举 jǔ requires repair by clear ordinary example.
德政 dézhèng benevolent governance; education/health support example aligned.
法度 fǎdù laws/standards; regulated administration correct.
反腐倡廉 fǎnfǔchànglián anti-corruption; integrity example aligned.
防微杜渐 fángwēidùjiàn prevent early; 干部 gànbù corrected.
国计民生 guójìmínshēng economy/livelihood; not nation's fate, fix gloss and doubled 战略.
海晏河清 hǎiyànhéqīng peace/prosperity; historical wish appropriate.
合力 hélì combined force; collaborative climate response aligned.
和衷共济 hézhōnggòngjì cooperate in hardship; unity example aligned.
惠民 huìmín benefit people; lifts/elder meal projects appropriate.
集思广益 jísīguǎngyì collective wisdom; expert consultation aligned.
经世致用 jīngshìzhìyòng practical learning; scholar social application appropriate.
开源节流 kāiyuánjiéliú raise income/reduce costs; remove doubled 财务.
克勤克俭 requires kèqínkèjiǎn; immutable key incorrectly jian4. Keep NEEDS_REVIEW pending pronunciation identity decision; example already jiǎn correct.
廉政公署 liánzhènggōngshǔ anti-corruption commission; special-region agency example aligned.
量入为出 liàngrùwéichū spend within income; duplicated 财政 and transcribed 财务 repaired.
民为邦本 mínwéibāngběn people are foundation; traditional political philosophy aligned.
民熙物阜 mínxīwùfù people happy/goods ample; prosperous village transformation appropriate.
谋篇布局 móupiānbùjú plan layout; strategic extension valid, include original writing-layout sense.
清正廉明 qīngzhèngliánmíng upright/incorruptible; admired judge appropriate.
求真务实 qiúzhēnwùshí truth/pragmatism; 干部 gànbù corrected.
群策群力 qúncèqúnlì pool wisdom/effort; joint crisis response aligned.
深谋远略 shēnmóuyuǎnlüè far-reaching strategy; economic strategy example appropriate.
实干兴邦 shígànxīngbāng practical work strengthens nation; construction metaphor aligned.
天下为公 tiānxiàwéigōng world for common good; classic public interest notion aligned.
立党为公 lìdǎngwéigōng party for common good; political statement linguistically aligned.
万象更新 wànxiànggēngxīn renewal; springtime vitality appropriate.
为民造福 wèimínzàofú benefit people; 干部 gànbù corrected.
问政 wènzhèng seek/question governance; narrow generic participate-in-politics English.
无为而治 wúwéiérzhì govern without excessive intervention; urban autonomy application coherent.
下情上达 xiàqíngshàngdá feedback upward; 机关 jīguān corrected.
协和万邦 xiéhéwànbāng harmonize nations; classical peaceful-relations ideal aligned.
修明 xiūmíng enlightened/well-ordered; clean administration appropriate.
严于律己 yányúlǜjǐ strict with self; 干部 gànbù and 律 lǜ corrected.
依法治国 yīfǎzhìguó rule by law; institutional law-based governance aligned.
治国理政 zhìguólǐzhèng statecraft; political theory application appropriate.
政通人和 zhèngtōngrénhé good governance/harmony; prosperous town appropriate.
至理名言 zhìlǐmíngyán wise saying; headteacher ancient maxim aligned.
中流砥柱 zhōngliúdǐzhù mainstay; wartime pillar metaphor aligned.
忠于职守 zhōngyúzhíshǒu devoted duty; emergency workers appropriate.
众望所归 zhòngwàngsuǒguī public confidence; 干部 gànbù corrected.
主心骨 zhǔxīngǔ mainstay; crisis leadership aligned.
自强不息 zìqiángbùxī constant self-improvement; classical quotation/modern application coherent. Remaining stable keys and advanced level retained.
""", [
 (5,"流域 liúyù.",py(5,"liùyù","liúyù")),
 (8,"Avoid misreading classical 与通举; clear ideal-world example.",{"example":{"simplified":"古代思想家向往人人安居乐业的大同世界。","pinyin":"Gǔdài sīxiǎngjiā xiàngwǎng rénrén ānjū-lèyè de dàtóng shìjiè.","vietnamese":"Các nhà tư tưởng cổ đại hướng tới một thế giới đại đồng nơi mọi người an cư lạc nghiệp."}}),
 (12,"干部 gànbù.",py(12,"gàngbù","gànbù")),
 (13,"Economy not fate; remove doubled 战略.",{"vietnamese_meanings":["quốc kế dân sinh","kinh tế quốc gia và đời sống nhân dân"],"example":{"simplified":r[12].examples[0].simplified.replace("战略战略","战略"),"pinyin":r[12].examples[0].pinyin.replace("zhànlüè zhànlüè","zhànlüè"),"vietnamese":r[12].examples[0].vietnamese.replace("vận mệnh đất nước","kinh tế quốc gia")}}),
 (20,"Remove doubled 财务.",{"example":{"simplified":r[19].examples[0].simplified.replace("财务财务","财务"),"pinyin":r[19].examples[0].pinyin.replace("cáiwù cáiwù","cáiwù")}}),
 (23,"Single 财政 budget.",{"example":{"simplified":r[22].examples[0].simplified.replace("财政财政","财政"),"pinyin":r[22].examples[0].pinyin.replace("cáizhèng cáiwù yùsuàn","cáizhèng yùsuàn")}}),
 (26,"Include writing layout origin and strategic extension.",{"vietnamese_meanings":["trù tính bố cục bài viết","sắp đặt tổng thể","bố cục chiến lược"],"english_meanings":["to plan the structure of a text","to plan an overall layout or strategy"]}),
 (28,"干部 gànbù.",py(28,"gàngbù","gànbù")),
 (35,"干部 gànbù.",py(35,"gàngbù","gànbù")),
 (36,"Question/seek advice on administration.",{"english_meanings":["to ask about government affairs","to question public administration"]}),
 (38,"机关 jīguān.",py(38,"jīgī","jīguān")),
 (41,"干部 and 律 pronunciation.",{"example":{"pinyin":r[40].examples[0].pinyin.replace("gàngbù","gànbù").replace("yányúlùjǐ","yányúlǜjǐ")}}),
 (48,"干部 gànbù.",py(48,"gàngbù","gànbù")),
], pending={21:{"reason":"Incorrect stable pronunciation identity 克勤克俭|ke4 qin2 ke4 jian4: 俭 must jian3 (jiǎn), as already correctly transcribed in the example. Renaming the pronunciation-specific lexical key requires an explicit identity resolution; source key preserved, excluded from local acceptance.","linguistic_uncertainty":True}})

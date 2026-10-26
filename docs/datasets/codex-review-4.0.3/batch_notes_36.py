"""Actual L5-B016 review and corrected-result recheck."""
from record_batch import record, rows
r=rows("L5-B016")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B016", """
丧失 sàngshī lose; crisis professional judgment example aligned.
骚扰 sāorǎo harass; network privacy example correct.
刹那 chànà instant; rocket ignition example supports special chà pronunciation.
山峦 shānluán mountains; Li River landscape aligned.
删改 shāngǎi revise/cut; manuscript editing correct.
赡养 shànyǎng support parents; thiệm not thiểm.
商榷 shāngquè discuss critically; academic objections example aligned.
上任 shàngrèn assume office; ambassador credentials example correct.
哨所 shàosuǒ outpost; high-altitude border garrison aligned.
奢侈 shēchǐ extravagant; frugality contrast correct.
摄取 shèqǔ ingest/capture; nutrition example coherent.
涉猎 shèliè read broadly; Vietnamese wrongly says deeply, correct.
深奥 shēn'ào abstruse; accessible physics explanation aligned.
审理 shěnlǐ hear case; 判决 pànjué malformed pàanjué corrected.
渗透 shèntòu permeate; sấm thấu attested, awkward traditional/modern manufacturing modifiers repaired.
升华 shēnghuá sublimate; artist raising aesthetic conception aligned.
生物多样性 shēngwùduōyàngxìng biodiversity; habitat preservation aligned.
失宠 shīchǒng lose favor; products rather than abstract capacity lose consumer favor, clarify example.
失调 shītiáo disordered; replace overcomplicated medical wording with ordinary sleep routine example.
诗情画意 shīqínghuàyì poetic/picturesque; Jiangnan canal scene appropriate.
十全十美 shíquánshíměi perfect; improving reforms correct.
实惠 shíhuì affordable/practical benefit; English and POS include actual adjective and noun senses.
实践性 shíjiànxìng practical nature; vocational education aligned.
拾金不昧 shíjīnbùmèi return found money; taxi wallet example correct sandhi bú.
食量 shíliàng food intake; amount rather than desire to eat; serving-size example aligned.
蚀本 shíběn lose capital; workshop price competition aligned.
始料未及 shǐliàowèijí unforeseen; dust storm example appropriate.
誓言 shìyán oath; 五星红旗 Vietnamese five-star red flag, not singular Vietnamese flag.
释怀 shìhuái let go; 温暖 wēnnuǎn not wēnxīn.
收敛 shōuliǎn restrain/converge; 干部 gànbù corrected.
收益率 shōuyìlǜ return rate; risk/yield comparison aligned.
手工业 shǒugōngyè handicrafts; embroidery/ceramics/bamboo crafts correct.
守恒 shǒuhéng conserved; remove duplicated 凭空凭白, accurate isolated-system wording.
殊荣 shūróng special honor; scientist national decoration aligned.
熟练度 shúliàndù proficiency; 高精尖 gāojīngjiān correct, accumulated skill example aligned.
曙光 shǔguāng dawn/hope; 靶向 bǎxiàng valid, medical research metaphor coherent.
树立 shùlì establish; ideals/worldview example correct.
束缚 shùfù restrict; 框框 kuàngkuàng not kāngkāng; include noun for constraints.
衰竭 shuāijié fail/exhaustion; medical failure nominal sense add noun.
双赢 shuāngyíng win-win; cooperation example aligned.
爽朗 shuǎnglǎng cheerful/open; veteran personality example correct.
水利工程 shuǐlìgōngchéng water conservancy; 三峡 multipurpose project aligned.
顺延 shùnyán postpone; inconsistent holiday/disaster condition repaired; not necessarily next day.
说服力 shuōfúlì persuasiveness; empirical report argument aligned.
司法解释 sīfǎjiěshì judicial interpretation; intellectual property cases example coherent.
死心塌地 sǐxīntādì unswervingly devoted; remove unnatural literal Vietnamese gloss.
伺机 sìjī bide time; correct sì reading in ambush context.
松弛 sōngchí relaxed; after fieldwork rest natural.
怂恿 sǒngyǒng instigate; túng dũng attested, resisting instigation aligned.
搜集 sōují gather; 高质量 gāozhìliàng not gāopǐnzhì. Stable head identities/level retained.
""", [
 (6,"贍 thiệm.",{"sino_vietnamese":"thiệm dưỡng"}),
 (12,"Broad acquaintance not deep mastery for 涉猎.",{"example":{"vietnamese":r[11].examples[0].vietnamese.replace("đọc rộng tìm hiểu sâu sắc","đọc rộng, tìm hiểu khái quát")}}),
 (14,"判决 pànjué.",py(14,"pàanjué","pànjué")),
 (15,"Repair contradictory/redundant modifiers.",{"example":{"simplified":"数字技术正在逐步渗透到传统制造业的各个环节。","pinyin":"Shùzì jìshù zhèngzài zhúbù shèntòu dào chuántǒng zhìzàoyè de gè ge huánjié.","vietnamese":"Công nghệ số đang dần thâm nhập vào từng khâu của ngành chế tạo truyền thống."}}),
 (18,"Consumer products can fall out of favor.",{"example":{"simplified":"随着环保意识增强，高耗能产品逐渐在市场上失宠。","pinyin":"Suízhe huánbǎo yìshí zēngqiáng, gāo hàonéng chǎnpǐn zhújiàn zài shìchǎng shang shīchǒng.","vietnamese":"Khi ý thức bảo vệ môi trường tăng lên, các sản phẩm tiêu hao nhiều năng lượng dần không còn được thị trường ưa chuộng."}}),
 (19,"Simple accurate disrupted-routine example.",{"example":{"simplified":"连续熬夜使他的生活节奏严重失调。","pinyin":"Liánxù áoyè shǐ tā de shēnghuó jiézòu yánzhòng shītiáo.","vietnamese":"Thức khuya liên tục khiến nhịp sinh hoạt của anh ấy rối loạn nghiêm trọng."}}),
 (22,"Affordable adjective and tangible-benefit noun.",{"part_of_speech":"adjective, noun","english_meanings":["affordable","good value","tangible benefit"]}),
 (28,"Chinese five-star flag translated accurately.",{"example":{"vietnamese":r[27].examples[0].vietnamese.replace("lá cờ đỏ sao vàng","lá cờ đỏ năm sao")}}),
 (29,"温暖 wēnnuǎn.",py(29,"wēnxīn","wēnnuǎn")),
 (30,"干部 gànbù.",py(30,"gàngbù","gànbù")),
 (33,"Remove duplicated adverbs; clear conservation statement.",{"part_of_speech":"verb, adjective","example":{"simplified":"在孤立系统中，总能量始终守恒。","pinyin":"Zài gūlì xìtǒng zhōng, zǒng néngliàng shǐzhōng shǒuhéng.","vietnamese":"Trong hệ cô lập, tổng năng lượng luôn được bảo toàn."}}),
 (38,"框 kuàng and nominal constraints.",dict(py(38,"tiáotiaokāngkāng","tiáotiaokuàngkuàng"),part_of_speech="verb, noun")),
 (39,"Nominal failure too.",{"part_of_speech":"verb, noun"}),
 (43,"Postponement does not guarantee next day; coherent condition.",{"vietnamese_meanings":["hoãn lại theo thứ tự","dời thời hạn về sau"],"example":{"simplified":"因暴雨影响，原定今天举行的考试将顺延两天。","pinyin":"Yīn bàoyǔ yǐngxiǎng, yuándìng jīntiān jǔxíng de kǎoshì jiāng shùnyán liǎng tiān.","vietnamese":"Do ảnh hưởng của mưa lớn, kỳ thi vốn dự kiến tổ chức hôm nay sẽ lùi lại hai ngày."}}),
 (46,"Remove unnatural literal gloss.",{"vietnamese_meanings":["một lòng một dạ","quyết tâm không thay đổi"]}),
 (50,"高质量 gāozhìliàng.",py(50,"gāo pǐnzhì","gāo zhìliàng")),
], sources=["https://hvdic.thivien.net/whv/%E8%B4%8D","https://hvdic.thivien.net/whv/%E6%BB%B2","https://hvdic.thivien.net/whv/%E6%85%AB"])

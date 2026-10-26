"""Actual L5-B020 review and rechecked content repairs."""
from record_batch import record, rows
r=rows("L5-B020")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B020", """
余地 yúdì leeway; negotiation flexibility appropriate.
渔业 yúyè fishery; remove doubled smart modifier; marine ranch not seagrass meadow.
予人口实 yǔrénkǒushí give critics grounds; administrative conduct example aligned.
雨后春笋 yǔhòuchūnsǔn rapid emergence; 笋 duẩn not vernacular măng; restore missing example syllables.
语音学 yǔyīnxué phonetics; speech production/tone/sandhi appropriate.
舆论监督 yúlùnjiāndū public scrutiny; 机关 jīguān correct.
宇宙飞船 yǔzhòufēichuán spacecraft; launch noise/flames modifier garbled, replace clear docking example.
原动力 yuándònglì driving force; 高质量 gāozhìliàng correct.
渊源 yuānyuán origins; 跨流域 kuàliúyù correct.
原子弹 yuánzǐdàn atomic bomb; historical scientific program example aligned.
远近闻名 yuǎnjìnwénmíng famous; traditional tea-making village appropriate.
约束力 yuēshùlì binding force; agreement obligations linguistically aligned.
蕴藏 yùncáng hold in store; remove doubled 极其.
赞叹 zàntàn admire; 巍峨 wēi'é not wéi'é.
糟粕 zāopò dregs; cultural essence versus dross example aligned.
责无旁贷 zéwúpángdài duty unshirkable; child protection example appropriate.
展台 zhǎntái display stand; machine exhibit appropriate.
占优势 zhànyōushì have advantage; intervening 绝对 is valid separable grammar.
张扬 zhāngyáng publicize; avoiding boastful publicity correct.
招募 zhāomù recruit; sporting volunteers example aligned.
兆头 zhàotou omen; not inherently lucky; repair extra 场 and overgrown sentence.
折中 zhézhōng compromise; development/environment balanced plan aligned.
针锋相对 zhēnfēngxiāngduì sharply opposed; remove unnatural literal Vietnamese kim găm từng mũi.
震惊 zhènjīng shocked; 科考 kēkǎo and 海沟最深底处 transcription repaired naturally.
蒸发 zhēngfā evaporate; 湖泊 húpō not húbō.
正轨 zhèngguǐ right track; restructuring troubled business coherent.
证据链 zhèngjùliàn evidence chain; 机关 jīguān and 轨迹 guǐjì corrected.
支柱产业 zhīzhùchǎnyè pillar industry; 高质量 gāozhìliàng correct.
直截了当 zhíjiéliǎodàng direct; tiệt not tiếp for 截.
指挥部 zhǐhuībù command center; flood response aligned.
指手画脚 zhǐshǒuhuàjiǎo point fingers; diplomatic interference example appropriate.
至关重要 zhìguānzhòngyào crucial; strategic supply-chain autonomy coherent.
治本 zhìběn address roots; simplify awkward tying-institutional-cage construction.
治理体系 zhìlǐtǐxì governance system; institutional modernization aligned.
忠贞不渝 zhōngzhēnbùyú unswervingly loyal; Vietnamese 先烈 liệt sĩ.
重塑 chóngsù reshape; AI changing production/life aligned.
主流媒体 zhǔliúméitǐ mainstream media; 媒 môi not mĩ.
注射剂 zhùshèjì injectable medicine; sterile production inspection aligned.
着眼点 zhuóyǎndiǎn focus; strategic research planning appropriate.
资料库 zīliàokù repository; historical document images aligned.
总揽全局 zǒnglǎnquánjú overall control; 协调 xiétiáo and 流域 liúyù corrected.
纵横捭阖 zònghéngbǎihé political maneuver; Warring States diplomats appropriate.
自力更生 zìlìgēngshēng self-reliance; historical construction example aligned.
自始至终 zìshǐzhìzhōng throughout; decades at remote station appropriate.
纵深 zòngshēn depth; domestic-market strategic depth metaphor aligned.
阻力 zǔlì resistance; aerodynamic train design example correct.
组建 zǔjiàn establish; research innovation team aligned.
遵纪守法 zūnjìshǒufǎ law-abiding; civic conduct appropriate.
遵循 zūnxún follow; 高质量 gāozhìliàng correct.
做作 zuòzuo affected; natural performance contrast appropriate. Stable head keys and level retained.
""", [
 (2,"Remove smart repetition; marine ranch translation.",{"example":{"simplified":r[1].examples[0].simplified.replace("智能智能化","智能化"),"pinyin":r[1].examples[0].pinyin.replace("zhìnéng zhìnénghuà","zhìnénghuà"),"vietnamese":r[1].examples[0].vietnamese.replace("đồng cỏ biển","trang trại nuôi trồng trên biển")}}),
 (4,"笋 duẩn; restore 春笋 chūnsǔn.",dict(py(4,"rúyǔ-hòuchǔn","rú yǔhòu-chūnsǔn"),sino_vietnamese="vũ hậu xuân duẩn")),
 (6,"机关 jīguān.",py(6,"jīgī","jīguān")),
 (7,"Clear spacecraft docking sentence.",{"example":{"simplified":"这艘载人宇宙飞船成功与空间站对接。","pinyin":"Zhè sōu zàirén yǔzhòu fēichuán chénggōng yǔ kōngjiānzhàn duìjiē.","vietnamese":"Tàu vũ trụ có người lái này đã ghép nối thành công với trạm vũ trụ."}}),
 (8,"高质量 exact transcription.",py(8,"gāo pǐnzhì","gāo zhìliàng")),
 (9,"流域 liúyù.",py(9,"kuàliùyù","kuàliúyù")),
 (13,"Remove doubled 极其.",{"example":{"simplified":r[12].examples[0].simplified.replace("极其极其","极其"),"pinyin":r[12].examples[0].pinyin.replace("jíqí jíqí","jíqí")}}),
 (14,"巍 wēi.",py(14,"wéi'é","wēi'é")),
 (21,"Omen can be good or bad; clear example.",{"vietnamese_meanings":["điềm báo","dấu hiệu báo trước"],"example":{"simplified":"人们把这场瑞雪看作来年丰收的好兆头。","pinyin":"Rénmen bǎ zhè chǎng ruìxuě kànzuò láinián fēngshōu de hǎo zhàotou.","vietnamese":"Mọi người coi trận tuyết lành này là điềm báo tốt cho vụ mùa bội thu năm tới."}}),
 (23,"Natural opposed-response gloss.",{"vietnamese_meanings":["đối đầu gay gắt","đáp trả không nhượng bộ"],"example":{"vietnamese":r[22].examples[0].vietnamese.replace(" kim găm từng mũi","")}}),
 (24,"Clear discovery/shock sentence with accurate 科考.",{"part_of_speech":"verb, adjective","example":{"simplified":"深海科考队的新发现令研究人员十分震惊。","pinyin":"Shēnhǎi kēkǎoduì de xīn fāxiàn lìng yánjiū rényuán shífēn zhènjīng.","vietnamese":"Phát hiện mới của đội khảo sát khoa học biển sâu khiến các nhà nghiên cứu hết sức kinh ngạc."}}),
 (25,"泊 pō in lake.",py(25,"húbō","húpō")),
 (27,"机关 and 轨迹.",{"example":{"pinyin":r[26].examples[0].pinyin.replace("jīgī","jīguān").replace("guìjī","guǐjì")}}),
 (28,"高质量 exact transcription.",py(28,"gāo pǐnzhì","gāo zhìliàng")),
 (29,"截 tiệt.",{"sino_vietnamese":"trực tiệt liễu đương"}),
 (33,"Natural root-cause example.",{"example":{"simplified":"解决这个问题不能只治标，还要从制度上治本。","pinyin":"Jiějué zhè ge wèntí bù néng zhǐ zhìbiāo, hái yào cóng zhìdù shang zhìběn.","vietnamese":"Giải quyết vấn đề này không thể chỉ chữa phần ngọn, mà còn phải xử lý tận gốc về mặt thể chế."}}),
 (35,"先烈 martyrs.",{"example":{"vietnamese":r[34].examples[0].vietnamese.replace("các bậc tiền liệt","các bậc liệt sĩ")}}),
 (37,"媒 môi.",{"sino_vietnamese":"chủ lưu môi thể"}),
 (41,"协调 and 流域.",{"example":{"pinyin":r[40].examples[0].pinyin.replace("xiétáo","xiétiáo").replace("kuàliùyù","kuàliúyù")}}),
 (49,"高质量 exact transcription.",py(49,"gāo pǐnzhì","gāo zhìliàng")),
])

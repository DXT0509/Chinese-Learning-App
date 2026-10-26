"""Actual L5-B017 decisions and corrected-result recheck."""
from record_batch import record, rows
r=rows("L5-B017")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B017", """
苏醒 sūxǐng wake; spring landscape metaphor coherent.
诉讼 sùsòng litigation; mediation/arbitration lowering dispute costs aligned.
溯源 sùyuán trace source; food traceability platform aligned.
随心所欲 suíxīnsuǒyù do as pleased; legal boundaries contrast correct.
索赔 suǒpéi claim compensation; nominal insurance claim also add noun.
坍塌 tāntā collapse; rain-soaked slope example aligned.
贪婪 tānlán greedy; temptation/moral restraint correct.
弹劾 tánhé impeach; 有权 yǒuquán not yǒuhuán.
探寻 tànxún search; 孜孜不倦 bújuàn not bújiàn.
瘫痪 tānhuàn paralyzed; infrastructure shutdown metaphor aligned.
淘汰赛 táotàisài knockout; 力克 not necessarily overwhelming win in Vietnamese.
套用 tàoyòng mechanically apply; uncritical industrial model copying example aligned.
特意 tèyì specially; school equipment donations natural.
梯队 tīduì echelon; tiered research-talent development aligned.
体魄 tǐpò physique; exercise and quoted educational maxim aligned.
体验感 tǐyàngǎn experience; digital public-service convenience correct.
天花板 tiānhuābǎn ceiling; athletic upper-limit metaphor aligned.
天理 tiānlǐ moral justice; 天理不容 not a kind of punishment, repair construction.
田野调查 tiányědiàochá fieldwork; anthropology and folklore, not ethnology, translate 民俗学 accurately.
挑拨 tiǎobō sow dissension; regional relationships example aligned.
调控 tiáokòng regulate; macro policy controls aligned.
通晓 tōngxiǎo thoroughly know; multilingual treaty expert example correct.
同理心 tónglǐxīn empathy; 温暖 wēnnuǎn not wēnxīn.
同舟共济 tóngzhōugòngjì pull together; flood relief appropriate.
统筹兼顾 tǒngchóujiāngù overall planning; 高质量 and 协调 pinyin mismatches repaired.
投产 tóuchǎn start production; remove doubled 超级.
投机倒把 tóujīdǎobǎ profiteer; emergency hoarding example aligned.
图腾 túténg totem; rock art symbolic animals coherent.
徒劳 túláo futile; failed divisive intentions example aligned.
唾弃 tuòqì spurn; 叛变 pànbiàn malformed pàanbiàn repaired.
妥当 tuǒdang proper; conference arrangements correct; simultaneous interpreting clearer Vietnamese.
瓦解 wǎjiě disintegrate; remove doubled 特大.
歪曲 wāiqū distort; 捏造事实 fabricate facts, not manufacture actual truth, Vietnamese repaired.
外汇储备 wàihuìchǔbèi reserves; financial-shock buffer example aligned.
玩忽职守 wánhūzhíshǒu neglect duty; public-official prosecution example coherent.
挽救 wǎnjiù save; emergency treatment narrative aligned.
惋惜 wǎnxī regret; remove 年轻青年 duplication.
万古长青 wàngǔchángqīng everlasting; friendship tree appropriate.
网联 wǎnglián networked; võng not vọng.
妄图 wàngtú vainly attempt; source uses verb as awkward noun and 打压 wrong pinyin, repair actual verb sentence.
微观 wēiguān microscopic; 分辨 fēnbiàn and 构象 gòuxiàng not 构相, repair transcription.
微不足道 wēibùzúdào negligible; aggregate small contributions natural.
畏缩 wèisuō flinch; 不可避免 bùkěbìmiǎn not bùkěbiǎanmiǎn.
慰问 wèiwèn sympathy visit; 干部 gànbù corrected.
紊乱 wěnluàn disordered; Sino-Vietnamese vấn not vận.
无动于衷 wúdòngyúzhōng indifferent; public grievances example aligned.
无微不至 wúwēibúzhì meticulous; recorded spoken 不 sandhi valid, teacher care appropriate.
无与伦比 wúyǔlúnbǐ incomparable; palace architecture aligned.
稀罕 xīhan rare; watch classifier 块 not 台, replace with clear example.
悉心 xīxīn devotedly; remove doubled 特大. Advanced level and stable head identities retained.
""", [
 (5,"Nominal claim.",{"part_of_speech":"verb, noun"}),
 (8,"权 quán.",py(8,"yǒuhuán","yǒuquán")),
 (9,"倦 juàn.",py(9,"bújiàn","bújuàn")),
 (11,"力克 hard-fought win not necessarily crushing.",{"example":{"vietnamese":r[10].examples[0].vietnamese.replace("thắng áp đảo đối thủ","nỗ lực đánh bại đối thủ")}}),
 (18,"Natural 天理不容 construction.",{"example":{"simplified":"这种残害无辜的行为天理不容。","pinyin":"Zhè zhǒng cánhài wúgū de xíngwéi tiānlǐ bù róng.","vietnamese":"Hành vi làm hại người vô tội như thế này là điều trời đất không dung."}}),
 (19,"Folklore not ethnology.",{"example":{"vietnamese":r[18].examples[0].vietnamese.replace("dân tộc học","nghiên cứu văn hóa dân gian")}}),
 (23,"温暖 wēnnuǎn.",py(23,"wēnxīn","wēnnuǎn")),
 (25,"高质量 and 协调 exact transcription.",{"example":{"pinyin":r[24].examples[0].pinyin.replace("gāo pǐnzhì xiétóng","gāo zhìliàng xiétiáo")}}),
 (26,"Remove doubled 超级.",{"example":{"simplified":r[25].examples[0].simplified.replace("超级超级","超级"),"pinyin":r[25].examples[0].pinyin.replace("chāojí chāojí","chāojí")}}),
 (30,"叛 pàn.",py(30,"pàanbiàn","pànbiàn")),
 (31,"同传 simultaneous interpretation.",{"example":{"vietnamese":r[30].examples[0].vietnamese.replace("dịch song song","phiên dịch đồng thời")}}),
 (32,"Remove doubled 特大.",{"example":{"simplified":r[31].examples[0].simplified.replace("特大特大","特大"),"pinyin":r[31].examples[0].pinyin.replace("tèdà tèdà","tèdà")}}),
 (33,"Fabricating facts translation.",{"example":{"vietnamese":r[32].examples[0].vietnamese.replace("cố ý nặn ra sự thật","cố ý bịa đặt sự việc")}}),
 (37,"Remove duplicated young modifier.",{"example":{"simplified":r[36].examples[0].simplified.replace("年轻青年","青年"),"pinyin":r[36].examples[0].pinyin.replace("niánqīng qīngnián","qīngnián")}}),
 (39,"網 võng.",{"sino_vietnamese":"võng liên"}),
 (40,"Use 妄图 as verb naturally.",{"example":{"simplified":"他妄图用谎言掩盖事实，最终却被揭穿。","pinyin":"Tā wàngtú yòng huǎngyán yǎngài shìshí, zuìzhōng què bèi jiēchuān.","vietnamese":"Anh ta mưu toan dùng lời nói dối che đậy sự thật, nhưng cuối cùng đã bị vạch trần."}}),
 (41,"分辨 and 构象 transcription.",{"example":{"pinyin":r[40].examples[0].pinyin.replace("fēnbian","fēnbiàn").replace("gòuxiàng","gòuxiàng")}}),
 (43,"避免 bìmiǎn.",py(43,"biǎanmiǎn","bìmiǎn")),
 (44,"干部 gànbù.",py(44,"gàngbù","gànbù")),
 (45,"紊 vấn.",{"sino_vietnamese":"vấn loạn"}),
 (49,"Proper watch classifier.",{"example":{"simplified":"在那个物资匮乏的年代，拥有一块名牌手表是很稀罕的事。","pinyin":"Zài nà ge wùzī kuìfá de niándài, yōngyǒu yí kuài míngpái shǒubiǎo shì hěn xīhan de shì.","vietnamese":"Trong thời vật tư khan hiếm ấy, sở hữu một chiếc đồng hồ đeo tay có thương hiệu là chuyện rất hiếm."}}),
 (50,"Remove doubled 特大.",{"example":{"simplified":r[49].examples[0].simplified.replace("特大特大","特大"),"pinyin":r[49].examples[0].pinyin.replace("tèdà tèdà","tèdà")}}),
], sources=["https://hvdic.thivien.net/whv/%E7%B4%8A","https://hvdic.thivien.net/whv/%E7%B6%B2"])

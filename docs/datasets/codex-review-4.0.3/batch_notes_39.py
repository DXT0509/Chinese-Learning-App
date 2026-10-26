"""L5-B019 actual linguistic review and corrected-result recheck."""
from record_batch import record, rows
r=rows("L5-B019")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B019", """
言简意赅 yánjiǎnyìgāi concise; 高质量 gāozhìliàng, neutral on-point Vietnamese.
言外之意 yánwàizhīyì implication; diplomatic wording interpretation aligned.
岩石 yánshí rock; 科考 kēkǎo not kěkǎo.
沿袭 yánxí follow tradition; Bai building form/customs aligned.
掩蔽 yǎnbì conceal; Sino-Vietnamese yểm tế not yểm bế.
掩埋 yǎnmái bury; mudslide search example correct.
眼界 yǎnjiè outlook; academic visit broadening vision appropriate.
谚语 yànyǔ proverb; agricultural weather wisdom aligned.
样板 yàngbǎn model; 高质量 gāozhìliàng correct.
瑶池 Yáochí mythical Jade Pool; 宛若 wǎnruò correct.
咬文嚼字 yǎowénjiáozì pedantic wording; tước not trước, replace ambiguous drafting example with direct conversation example.
野蛮 yěmán barbaric; dã man not dã manh.
野心 yěxīn ambition; ambition defeated rather than itself dying, repair awkward source.
夜幕 yèmù nightfall; 宛若 wǎnruò correct.
一目了然 yīmùliǎorán clear at glance; 流域 liúyù not liùyù.
一帆风顺 yīfānfēngshùn smooth; valid 一 sandhi yì in example.
一鼓作气 yīgǔzuòqì one sustained effort; tunnel breakthrough not traffic opening, Vietnamese refined.
一脉相承 yīmàixiāngchéng same lineage; replace malformed 将...一脉相承 predicate.
一诺千金 yīnuòqiānjīn keep promise; long-lived trusted brand example appropriate.
一窍不通 yīqiàobùtōng know nothing; 悉心 xīxīn not xīnxīn.
依恋 yīliàn attachment; nominal emotional attachment add noun POS.
依托 yītuō rely on; 粮食 grain not rice-only, 抗逆 stress-tolerant not pest-only.
依法行政 yīfǎxíngzhèng administer lawfully; 机关 jīguān correct.
遗留 yíliú leave behind; industrial contaminated land example aligned.
遗产税 yíchǎnshuì inheritance tax; Vietnamese tax-system not specifically income-tax system.
疑心 yíxīn suspicion; open commercial cooperation contrast aligned.
倚仗 yǐzhàng rely upon; family privilege example correct.
毅然 yìrán resolutely; remove tripled disaster degree modifiers.
意识形态 yìshíxíngtài ideology; 深刻 shēnkè not shēndù.
议案 yì'àn motion/bill; representatives submitting law proposal aligned.
异想天开 yìxiǎngtiānkāi wild fantasy; untested deployment example coherent.
意气用事 yìqìyòngshì impulsive; 协调 xiétiáo and 干部 gànbù corrected.
音节 yīnjié syllable; source conflates meaning unit with sound unit, replace with valid two-syllable example.
引咎辞职 yǐnjiùcízhí resign taking responsibility; safety official example aligned.
饮水思源 yǐnshuǐsīyuán gratitude to origins; remove doubled 民营.
印证 yìnzhèng corroborate; archaeological and documentary evidence aligned.
隐蔽 yǐnbì concealed; Sino-Vietnamese ẩn tế not ẩn bế.
隐瞒 yǐnmán conceal; 干部 and 诚实 transcription corrected.
硬币 yìngbì coin; 纪念 jìniàn malformed jìnìan repaired.
应酬 yìngchou social engagement; 机构 jīgòu not jīgī.
应届 yīngjiè current graduation year; remove doubled 吸纳.
盈利 yínglì profit; research startup reaching profitability aligned.
荧光 yíngguāng fluorescence; probe tracking animal cells coherent.
优势互补 yōushìhùbǔ complementary strengths; 互 hỗ not tương, remove duplicated coordination modifier.
悠久 yōujiǔ long-standing; 流域 liúyù correct.
油漆 yóuqī paint; 科考 kēkǎo correct.
友好往来 yǒuhǎowǎnglái friendly exchanges; Silk Road contact aligned.
右倾 yòuqīng right-leaning; political compromise description aligned.
幼稚 yòuzhì naive; 干部 gànbù corrected.
迂回 yūhuí circuitous approach; flanking maneuver example aligned. Stable identities/level retained.
""", [
 (1,"高质量 exact transcription and neutral relevance.",{"example":{"pinyin":r[0].examples[0].pinyin.replace("gāo pǐnzhì","gāo zhìliàng"),"vietnamese":r[0].examples[0].vietnamese.replace("trúng tim đen","đúng trọng tâm")}}),
 (3,"科考 kēkǎo.",py(3,"kěkǎo","kēkǎo")),
 (5,"蔽 tế.",{"sino_vietnamese":"yểm tế"}),
 (9,"高质量 exact transcription.",py(9,"gāo pǐnzhì","gāo zhìliàng")),
 (10,"若 ruò.",py(10,"wǎnrùo","wǎnruò")),
 (11,"嚼 tước and natural pedantry usage.",{"sino_vietnamese":"giảo văn tước tự","example":{"simplified":"讨论问题时不要过分咬文嚼字，而应关注实际意思。","pinyin":"Tǎolùn wèntí shí bú yào guòfèn yǎowén-jiáozì, ér yīng guānzhù shíjì yìsi.","vietnamese":"Khi thảo luận vấn đề, đừng quá câu nệ từng câu chữ mà nên chú ý đến ý nghĩa thực tế."}}),
 (12,"蛮 man.",{"sino_vietnamese":"dã man"}),
 (13,"Natural ambition collapse predicate.",{"example":{"simplified":"他企图独占市场的野心最终落空了。","pinyin":"Tā qǐtú dúzhàn shìchǎng de yěxīn zuìzhōng luòkōng le.","vietnamese":"Dã tâm độc chiếm thị trường của anh ta cuối cùng đã thất bại."}}),
 (14,"若 ruò.",py(14,"wǎnrùo","wǎnruò")),
 (15,"流域 liúyù.",py(15,"liùyù","liúyù")),
 (17,"Tunnel breakthrough not opening to traffic.",{"example":{"vietnamese":r[16].examples[0].vietnamese.replace("thông xe toàn tuyến","đào thông toàn tuyến").replace("thông xe hai chiều","đào thông từ hai hướng")}}),
 (18,"Clear inherited-lineage predicate.",{"example":{"simplified":"这两种地方戏曲在表演风格上一脉相承。","pinyin":"Zhè liǎng zhǒng dìfāng xìqǔ zài biǎoyǎn fēnggé shang yīmài-xiāngchéng.","vietnamese":"Hai loại hình hí kịch địa phương này kế thừa cùng một dòng về phong cách biểu diễn."}}),
 (20,"悉心 xīxīn.",py(20,"xīnxīn","xīxīn")),
 (21,"Nominal attachment.",{"part_of_speech":"verb, noun"}),
 (22,"Grain and adversity tolerance broader than rice/pests.",{"example":{"vietnamese":r[21].examples[0].vietnamese.replace("giống lúa mới phẩm chất tốt kháng sâu bệnh chịu hạn","giống cây lương thực mới có phẩm chất tốt, chịu điều kiện bất lợi và chịu hạn,")}}),
 (23,"机关 jīguān.",py(23,"jīgī","jīguān")),
 (25,"Tax not specifically income tax.",{"example":{"vietnamese":r[24].examples[0].vietnamese.replace("thuế thu nhập kinh tế","thuế kinh tế")}}),
 (28,"Remove redundant disaster modifiers.",{"example":{"simplified":"面对突发山火，消防战士毅然冲向救援一线。","pinyin":"Miànduì tūfā shānhuǒ, xiāofáng zhànshì yìrán chōngxiàng jiùyuán yīxiàn.","vietnamese":"Trước vụ cháy rừng bất ngờ, các chiến sĩ cứu hỏa kiên quyết lao tới tuyến đầu cứu hộ."}}),
 (29,"深刻 shēnkè.",py(29,"shēndù yǎnbiàn","shēnkè yǎnbiàn")),
 (32,"协调 and 干部.",{"example":{"pinyin":r[31].examples[0].pinyin.replace("xiétáo","xiétiáo").replace("gàngbù","gànbù")}}),
 (33,"Syllable sound unit, not mandatory meaning unit.",{"example":{"simplified":"普通话中的“学校”这个词有两个音节。","pinyin":"Pǔtōnghuà zhōng de “xuéxiào” zhè ge cí yǒu liǎng ge yīnjié.","vietnamese":"Từ “xuéxiào” trong tiếng Phổ thông có hai âm tiết."}}),
 (35,"Remove doubled 民营.",{"example":{"simplified":r[34].examples[0].simplified.replace("民营民营","民营"),"pinyin":r[34].examples[0].pinyin.replace("mínyíng mínyíng","mínyíng")}}),
 (37,"蔽 tế.",{"sino_vietnamese":"ẩn tế"}),
 (38,"干部 and 诚实.",{"example":{"pinyin":r[37].examples[0].pinyin.replace("gàngbù","gànbù").replace("chéngxìn shǒuxìn","chéngshí shǒuxìn")}}),
 (39,"纪念 jìniàn.",py(39,"jìnìan","jìniàn")),
 (40,"机构 jīgòu.",py(40,"jīgī","jīgòu")),
 (41,"Remove doubled 吸纳.",{"example":{"simplified":r[40].examples[0].simplified.replace("吸纳吸纳","吸纳"),"pinyin":r[40].examples[0].pinyin.replace("xīnà xīnà","xīnà")}}),
 (44,"互 hỗ; remove redundant 协调 beside 协同.",{"sino_vietnamese":"ưu thế hỗ bổ","example":{"simplified":r[43].examples[0].simplified.replace("协调协同","协同"),"pinyin":r[43].examples[0].pinyin.replace("xiétóng xiétóng","xiétóng")}}),
 (45,"流域 liúyù.",py(45,"liùyù","liúyù")),
 (46,"科考 kēkǎo.",py(46,"kěkǎo","kēkǎo")),
 (49,"干部 gànbù.",py(49,"gàngbù","gànbù")),
], sources=["https://hvdic.thivien.net/whv/%E8%94%BD","https://hvdic.thivien.net/whv/%E5%9A%BC"])

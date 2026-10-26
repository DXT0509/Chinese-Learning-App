"""Actual L5-B018 linguistic review and rechecked repairs."""
from record_batch import record, rows
r=rows("L5-B018")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B018", """
媳妇 xífu daughter-in-law/wife; fix corrupted 婆婆 transcription and unsupported children in Vietnamese.
喜闻乐见 xǐwénlèjiàn popular; 易懂 yìdǒng, local opera not Beijing opera; acrobatics not magic.
狭窄 xiázhǎi narrow; hiệp trách not mixed Sino-Vietnamese/vernacular hiệp hẹp.
下工夫 xiàgōngfu put in effort; research painstaking work example aligned.
夏令营 xiàlìngyíng summer camp; tangled repeated college/science-camp title repaired.
先决条件 xiānjuétiáojiàn prerequisite; social stability example aligned.
先例 xiānlì precedent; 判决 pànjué malformed source corrected.
闲暇 xiánxiá leisure; reading on weekend correct.
显而易见 xiǎnéryìjiàn evident; innovation strategic role aligned.
宪章 xiànzhāng charter; UN Charter principles linguistically aligned.
相提并论 xiāngtíbìnglùn compare equally; not blanket condemnation vơ đũa cả nắm, remove duplicated 自主.
向往 xiàngwǎng yearn; nominal aspiration requires noun too.
消除 xiāochú eliminate; poverty problem removal aligned.
消遣 xiāoqiǎn pastime; leisure tea/chess natural.
硝烟 xiāoyān gun smoke; 英雄 yīngxióng not yīngyǒng; Vietnamese 先烈 liệt sĩ.
协调员 xiétiáoyuán coordinator; 资金 zījīn not 基金 jījīn.
心甘情愿 xīngānqíngyuàn willingly; 成千上万 chéngqiānshàngwàn repaired.
心力交瘁 xīnlìjiāocuì exhausted; epidemic workers example coherent.
心满意足 xīnmǎnyìzú content; harvest smile example aligned.
心愿 xīnyuàn wish; aircraft engine flying metonymy acceptable.
新颖 xīnyǐng novel; smart bamboo-design idea aligned.
薪火相传 xīnhuǒxiāngchuán pass torch; cultural transmission example correct.
芯片 xīnpiàn chip; tâm phiến not hinh; 难题 nántí correct.
信念感 xìnniàngǎn conviction; acting belief in role, not religious faith, refine Vietnamese.
性能 xìngnéng performance; malformed synthesize-material-properties and duplicated composite repaired.
凶悍 xiōnghàn fierce; arresting armed drug trafficker aligned.
凶兆 xiōngzhào bad omen; rejecting astronomical superstition appropriate.
胸襟 xiōngjīn breadth of mind; mentor generosity aligned.
雄厚 xiónghòu substantial; replace untranslated 一流 in Vietnamese.
修正案 xiūzhèng'àn amendment; 表决 biǎojué not biàojué.
修剪 xiūjiǎn prune; streetside trees/hedges aligned.
虚无缥缈 xūwúpiāomiǎo illusory; ideal versus fantasy coherent.
许诺 xǔnuò promise; keeping business commitments aligned.
叙事学 xùshìxué narratology; novel discourse study accurate.
絮叨 xùdao nagging; 絮 nhứ not tự, naturalize duplicated Vietnamese dặn dò.
蓄水池 xùshuǐchí reservoir; 梯级 tījí not tījī.
轩然大波 xuānrándàbō uproar; algorithm scandal example aligned.
旋律 xuánlǜ melody; orchestral suite appropriate.
选用 xuǎnyòng choose for use; 壳体 kétǐ not kètǐ.
炫耀 xuànyào flaunt; modest scholar contrast natural.
雪中送炭 xuězhōngsòngtàn timely help; emergency winter supplies appropriate.
血气方刚 xuèqìfānggāng youthful vigor; generation cannot be period, repair subject/predicate.
循规蹈矩 xúnguīdǎojǔ conform; fix English dociley spelling.
压倒一切 yādǎoyīqiè overriding; example 一 sandhi yí valid.
压抑 yāyì suppress/depressed; add adjective POS for emotional state.
严寒 yánhán bitter cold; railway winter inspections aligned.
严厉 yánlì stern; replace unnatural nghiêm trị sắc bén gloss.
延期 yánqī postpone; hearing delay application coherent.
延续 yánxù continue; cultural continuity example aligned.
言传身教 yánchuánshēnjiào teach by word/example; principal influencing pupils appropriate. Stable keys and advanced level retained.
""", [
 (1,"婆婆 transcription and elderly-only respect.",{"example":{"pinyin":r[0].examples[0].pinyin.replace("pópom","pópo"),"vietnamese":r[0].examples[0].vietnamese.replace("kính già yêu trẻ","kính trọng người cao tuổi")}}),
 (2,"易懂 and faithful performance types.",{"example":{"pinyin":r[1].examples[0].pinyin.replace("yǐdǒng","yìdǒng"),"vietnamese":r[1].examples[0].vietnamese.replace("kinh kịch địa phương, xiếc ảo thuật","hí kịch địa phương, xiếc")}}),
 (3,"窄 trách.",{"sino_vietnamese":"hiệp trách"}),
 (5,"Untangle repeated camp title.",{"example":{"simplified":"这次科技夏令营吸引了全国各地的高中生参观重点大学和实验室。","pinyin":"Zhè cì kējì xiàlìngyíng xīyǐn le quánguó gèdì de gāozhōngshēng cānguān zhòngdiǎn dàxué hé shíyànshì.","vietnamese":"Trại hè khoa học công nghệ lần này thu hút học sinh trung học phổ thông khắp cả nước đến tham quan các đại học trọng điểm và phòng thí nghiệm."}}),
 (7,"判 pàn.",py(7,"pàanjué","pànjué")),
 (11,"Comparison not indiscriminate condemnation; remove repeated 自主.",{"vietnamese_meanings":["đặt ngang hàng để so sánh","đem ra bàn luận như tương đương"],"example":{"simplified":r[10].examples[0].simplified.replace("自主核心自主知识产权","自主核心知识产权"),"pinyin":r[10].examples[0].pinyin.replace("zìzhǔ héxīn zìzhǔ zhīshi","zìzhǔ héxīn zhīshi")}}),
 (12,"Nominal yearning.",{"part_of_speech":"verb, noun"}),
 (15,"英雄 transcription; Vietnamese martyrs.",{"example":{"pinyin":r[14].examples[0].pinyin.replace("de yīngyǒng tǔdì","de yīngxióng tǔdì"),"vietnamese":r[14].examples[0].vietnamese.replace("các bậc tiền liệt","các bậc liệt sĩ")}}),
 (16,"资金 zījīn.",py(16,"jiùzāi jījīn","jiùzāi zījīn")),
 (17,"成千上万 exact syllables.",py(17,"chéngqiān-wàngbiàn","chéngqiān-shàngwàn")),
 (23,"芯 tâm and 难题 tí.",dict(py(23,"nándí","nántí"),sino_vietnamese="tâm phiến")),
 (24,"Acting conviction not religious belief.",{"vietnamese_meanings":["cảm giác tin tưởng vững chắc","sự xác tín vào điều mình thể hiện"],"example":{"vietnamese":"Khi xây dựng nhân vật kinh điển, một nghệ sĩ kịch sân khấu giỏi cần có niềm tin vững chắc vào vai diễn, tập trung cao độ và hoàn toàn hòa mình vào thế giới nội tâm của nhân vật."}}),
 (25,"Synthesize material, evaluate performance.",{"example":{"simplified":"研究团队合成了一种新型复合材料，其耐磨和导热性能十分出色。","pinyin":"Yánjiū tuánduì héchéng le yì zhǒng xīnxíng fùhé cáiliào, qí nàimó hé dǎorè xìngnéng shífēn chūsè.","vietnamese":"Nhóm nghiên cứu đã tổng hợp một loại vật liệu composite mới có tính năng chịu mài mòn và dẫn nhiệt rất tốt."}}),
 (29,"Translate 一流.",{"example":{"vietnamese":r[28].examples[0].vietnamese.replace("trọng điểm一流","trọng điểm hàng đầu")}}),
 (30,"表 biǎo.",py(30,"biàojué","biǎojué")),
 (35,"絮 nhứ and Vietnamese duplication.",{"sino_vietnamese":"nhứ thao","example":{"vietnamese":r[34].examples[0].vietnamese.replace("dặn dò dặn dò","dặn dò")}}),
 (36,"级 jí.",py(36,"tījī","tījí")),
 (39,"壳 ké in 壳体.",py(39,"kètǐ","kétǐ")),
 (42,"Youth at vigorous age, not generation equals period.",{"example":{"simplified":"这些血气方刚的年轻人充满了奋斗的热情。","pinyin":"Zhèxiē xuèqì-fānggāng de niánqīngrén chōngmǎn le fèndòu de rèqíng.","vietnamese":"Những người trẻ tràn đầy sức sống này mang trong mình nhiệt huyết phấn đấu."}}),
 (43,"English spelling.",{"english_meanings":["to follow rules obediently","to conform to convention"]}),
 (45,"Depressed/oppressed adjective state.",{"part_of_speech":"verb, adjective"}),
 (47,"Natural stern/severe Vietnamese gloss.",{"vietnamese_meanings":["nghiêm khắc","nghiêm nghị","gay gắt"]}),
], sources=["https://hvdic.thivien.net/whv/%E8%8A%AF","https://hvdic.thivien.net/whv/%E7%AA%84","https://hvdic.thivien.net/whv/%E7%B5%AE"])

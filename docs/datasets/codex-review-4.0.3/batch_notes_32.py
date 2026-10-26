"""Actual L5-B012 review and corrections recheck."""
from record_batch import record, rows
r=rows("L5-B012")
def py(i,a,b):
    p=r[i-1].examples[0].pinyin
    assert a in p
    return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B012", """
联名 liánmíng jointly sign; joint research-fund petition aligned.
联姻 liányīn marriage/alliance; cross-sector pharmaceutical collaboration natural metaphor.
连带 liándài joint responsibility; liability example linguistically coherent.
廉政 liánzhèng clean government; 机关 jīguān not jīgī, correct.
链条 liàntiáo chain; remove duplicated modern-industry phrase.
梁柱 liángzhù beams/pillars; remove repeated 平凡 and 栋梁梁柱, correct cột quân gloss.
两全其美 liǎngquánqíměi both benefits; heritage preservation/living conditions aligned.
良知 liángzhī conscience; 诚实 chéngshí not chéngxìn in example.
谅解 liàngjiě understanding; include noun for 达成谅解.
辽阔 liáokuò vast; mountain panorama aligned.
猎取 lièqǔ hunt/acquire by pursuit; illegal hunting context does not make verb inherently poaching.
邻邦 línbāng neighboring country; diplomatic cooperation aligned.
临近 línjìn approach; holiday homebound travelers natural.
琳琅满目 línlángmǎnmù dazzling array; crafts exhibition correct.
伶俐 línglì quick-witted/articulate; children's poetry recital aligned.
灵敏 língmǐn sensitive; 传感器 chuángǎnqì must chuángǎn? Correct to chuángǎn? Mandarin 传 chuán, source chuán is correct; retain.
凌厉 línglì fierce; football offensive example aligned.
领土 lǐngtǔ territory; sovereignty wording linguistically coherent.
领航 lǐngháng pilot; replace awkward transitive 领航货轮编队 with 为...领航.
流连忘返 liúliánwàngfǎn linger; literal Hán-Việt lưu liên, correct malformed wǎnrùo to wǎnruò.
流浪者 liúlàngzhě wanderer; cold-weather homeless assistance aligned.
浏览量 liúlǎnliàng page views; correct extra a in liúlǎanliàng.
柳絮 liǔxù willow catkins; nhứ not thứ; remove 满天漫天 duplication.
龙舟 lóngzhōu dragon boat; festival racing example aligned.
隆重 lóngzhòng solemn/grand; awards ceremony aligned.
漏税 lòushuì omit tax payment; source gloss overequates deliberate 偷税, clarify tax omission/evasion context.
露天 lùtiān open-air; community movie screening aligned.
炉火纯青 lúhuǒchúnqīng consummate skill; teapot artisan example appropriate.
陆地 lùdì land; 九百六十 jiǔbǎiliùshí not jiǐbǎiliùshí.
路标 lùbiāo road sign; 反光 reflective rather than self-luminous in Vietnamese.
录用 lùyòng employ; written exam/interview recruitment coherent.
乱象 luànxiàng disorder; remove doubled 网络 absent from pinyin.
略微 lüèwēi slightly; temperature decrease example correct.
掠夺 lüèduó plunder; colonial resource exploitation aligned.
轮廓 lúnkuò contour; khuếch attested, mist bó not colloquial báo reading.
论坛 lùntán forum; international closed financial discussion aligned.
论证 lùnzhèng demonstrate/appraise; engineering assessment nominal noun also used.
麻木 mámù numb; 双手 shuāngshǒu not shǒushǒu, repair.
埋怨 mányuàn blame; correct special mán reading retained.
埋伏 máifu ambush; neutral fu conventional, guerrilla example aligned.
脉络 màiluò thread/development; research-history account aligned.
漫长 màncháng very long; development journey correct.
忙碌 mánglù busy; holiday shopping crowds aligned.
冒犯 màofàn offend; cross-cultural respect example correct.
盲目 mángmù blindly; investment expansion example aligned.
茅塞顿开 máosèdùnkāi suddenly understand; teacher insight correct, Vietnamese trúng tim đen inappropriate negative nuance.
茂盛 màoshèng lush; Vietnamese spelling sum suê, vegetation example aligned.
冒险 màoxiǎn take risk; prohibiting small fishing boats before storm natural.
美满 měimǎn blissful; newlywed life example correct.
蒙蔽 méngbì deceive; false online pricing example aligned. All head identities and level retained.
""", [
 (4,"机关 jīguān.",py(4,"jīgī","jīguān")),
 (5,"Remove redundant industry chain modifiers.",{"example":{"simplified":"我国制造业拥有门类齐全、规模庞大的现代工业链条。","pinyin":"Wǒguó zhìzàoyè yōngyǒu ménlèi qíquán, guīmó pángdà de xiàndài gōngyè liàntiáo.","vietnamese":"Ngành chế tạo nước ta có chuỗi công nghiệp hiện đại quy mô lớn và đầy đủ các ngành."}}),
 (6,"Repair repeated text and mistranslated beam/pillar.",{"vietnamese_meanings":["dầm và cột","rường cột","trụ cột"],"example":{"simplified":"这些默默奉献的青年劳动者是国家建设的梁柱。","pinyin":"Zhèxiē mòmò fèngxiàn de qīngnián láodòngzhě shì guójiā jiànshè de liángzhù.","vietnamese":"Những người lao động trẻ âm thầm cống hiến này là trụ cột của công cuộc xây dựng đất nước."}}),
 (8,"诚实 chéngshí.",py(8,"chéngxìn","chéngshí")),
 (9,"Nominal understanding.",{"part_of_speech":"verb, noun"}),
 (11,"Hunt is not inherently illegal.",{"vietnamese_meanings":["săn bắt","tìm kiếm để giành lấy"]}),
 (19,"Natural pilot construction.",{"example":{"simplified":"大雾中，海巡艇在前方为货轮编队领航。","pinyin":"Dàwù zhōng, hǎixúntǐng zài qiánfāng wèi huòlún biānduì lǐngháng.","vietnamese":"Trong sương mù dày đặc, tàu tuần tra biển dẫn đường phía trước cho đoàn tàu hàng."}}),
 (20,"连 liên; 宛若 wǎnruò.",dict(py(20,"wǎnrùo","wǎnruò"),sino_vietnamese="lưu liên vong phản")),
 (22,"览 lǎn one a.",py(22,"liúlǎanliàng","liúlǎnliàng")),
 (23,"絮 nhứ; remove duplicated sky phrase.",{"sino_vietnamese":"liễu nhứ","example":{"simplified":r[22].examples[0].simplified.replace("满天漫天","漫天"),"pinyin":r[22].examples[0].pinyin.replace("mǎntiān màntiān","màntiān")}}),
 (26,"漏税 tax omission distinguished from intentional 偷税.",{"vietnamese_meanings":["bỏ sót việc nộp thuế","không nộp đủ thuế"],"english_meanings":["to fail to pay tax due","to underpay taxes"]}),
 (29,"九 jiǔ.",py(29,"jiǐbǎiliùshí","jiǔbǎiliùshí")),
 (30,"Reflective sign, not self luminous.",{"example":{"vietnamese":"Trên tuyến đường thảo nguyên mênh mông phủ băng tuyết, các biển chỉ đường phản quang rõ nét, dễ thấy cách nhau vài cây số chỉ hướng cho tài xế xe tải đường dài đi trong gió tuyết."}}),
 (32,"Remove duplicated 网络.",{"example":{"simplified":r[31].examples[0].simplified.replace("网络网络","网络")}}),
 (35,"Formal 薄雾 bó.",py(35,"báowù","bówù")),
 (37,"Nominal technical appraisal.",{"part_of_speech":"verb, noun"}),
 (38,"双手 shuāngshǒu.",py(38,"shǒushǒu","shuāngshǒu")),
 (46,"切中要害 insight without negative expose-secret nuance.",{"example":{"vietnamese":"Nghe lời gợi mở sâu sắc, trúng trọng tâm và có tầm nhìn bao quát của thầy hướng dẫn, anh ấy, vốn bấy lâu mắc kẹt trong nghiên cứu học thuật, lập tức cảm thấy bừng sáng trí óc."}}),
 (47,"Vietnamese sum suê spelling.",{"vietnamese_meanings":["tươi tốt","sum suê","rậm rạp"],"example":{"vietnamese":r[46].examples[0].vietnamese.replace("xum xuê","sum suê")}}),
], sources=["https://hvdic.thivien.net/whv/%E7%B5%AE","https://hvdic.thivien.net/whv/%E5%BB%93"])

"""L5-B011 actual linguistic findings and rechecked corrections."""
from record_batch import record, rows
r = rows("L5-B011")
def py(i, a, b):
    value = r[i-1].examples[0].pinyin
    assert a in value
    return {"example": {"pinyin": value.replace(a,b)}}
record("L5-B011", """
开辟 kāipì open up; Sino-Vietnamese khai tịch, not bích. Research pathway example aligned.
开拓者 kāituòzhě pioneer; spaceport founding example correct.
开源 kāiyuán open-source/open revenue sources; add verb POS for second sense.
刊物 kānwù periodical; academic indexing example aligned.
勘探 kāntàn prospect; khám thám dictionary-attested, drilling example correct.
坎坷 kǎnkě rough/troubled; translator's resilient life example aligned.
慷慨 kāngkǎi generous; scholarship donations correct.
扛旗 kángqí carry banner/lead; tackling core research example aligned.
考据 kǎojù textual research; nominal use and ungrammatical English infinitive corrected.
苛刻 kēkè exacting; aerospace bearing operating conditions accurate.
颗粒 kēlì particle; khỏa not khóa; particle not molecule, clarify Vietnamese.
科教 kējiào science/education; development strategy example aligned.
客流 kèliú passenger flow; Spring Festival rail peak example correct.
空前 kōngqián unprecedented; major sporting event aligned.
口径 kǒujìng caliber/uniform reporting criteria; accounting not audit in Vietnamese.
扣留 kòuliú detain; source splits key across 查扣留置, replace with genuine target verb.
枯竭 kūjié exhausted; remove duplicated clean-energy adjective.
跨越式 kuàyuèshì leapfrogging; remove duplicated 历史性历史 and misleading milestone gloss.
款待 kuǎndài entertain guests; rural meal for visiting painters aligned.
筐 kuāng basket; 时节 shíjié not shíjī in example.
框定 kuàngdìng delineate; urban boundary planning aligned.
狂热 kuángrè fanatical; football crowd natural.
亏损 kuīsǔn loss; operating-loss reversal aligned.
昆虫学 kūnchóngxué entomology; beetle species expedition accurate.
捆绑 kǔnbǎng bind; figurative business restrictions aligned.
阔绰 kuòchuo lavish/well-off; Vietnamese not generic generosity, repair example rendering.
扩充 kuòchōng expand; Sino-Vietnamese khuếch sung rather than khoát, library resources aligned.
拉拢 lālong win over; correct English infinitive and 干部 gànbù; toned example variant retained.
来源 láiyuán source; isotope tracing of pollution aligned.
赖以生存 làiyǐshēngcún depend for survival; protecting Earth example coherent.
蓝图 lántú blueprint; 高能级 means high-capacity/high-level here, not physical energy grade.
滥用 lànyòng abuse; international sanctions example linguistically aligned.
牢固 láogù firm; correct 干部 gànbù.
牢骚 láosāo complaint; neutral sao in example conventional variant.
老迈 lǎomài elderly/frail; mental agility does not contradict physical aging.
乐善好施 lèshànhàoshī charitable; doctor offering free medicine aligned.
擂台 lèitái arena; milling technicians' contest correct.
累积 lěijī accumulate; awkward practice-knowledge phrase replaced with natural accumulation sentence.
冷落 lěngluò cold-shoulder/desolate; include adjective POS for market example.
愣 lèng stunned; unexpected award example aligned.
礼仪 lǐyí etiquette; international manners example coherent.
理智 lǐzhì rational; maintaining composure example correct.
理念 lǐniàn concept/philosophy; sustainable development example aligned.
立法 lìfǎ legislation; legal process example correct.
里程碑 lǐchéngbēi milestone; 达到/标志着 a milestone, not 取得里程碑, repair.
力所能及 lìsuǒnéngjí within ability; voluntary community contribution coherent.
历届 lìjiè successive past terms; alumni exhibition aligned.
立足点 lìzúdiǎn standpoint; remove malformed 落脚立足点 chain.
廉洁 liánjié incorruptible; correct 干部 gànbù.
联络 liánluò contact; alumni networks example aligned. Advanced level and stable identities retained.
""", [
 (1,"辟 in 开辟: tịch.",{"sino_vietnamese":"khai tịch"}),
 (3,"Revenue-source sense is verbal.",{"part_of_speech":"adjective, verb"}),
 (9,"Nominal textual research and grammatical English.",{"part_of_speech":"verb, noun","english_meanings":["to conduct textual research","to verify from documentary evidence"]}),
 (11,"颗 khỏa, particle not molecule.",{"sino_vietnamese":"khỏa lạp","vietnamese_meanings":["hạt","tiểu hạt"]}),
 (15,"核算 calculation not audit.",{"example":{"vietnamese":"Trong quá trình tính toán dữ liệu tổng điều tra kinh tế toàn quốc, cơ quan thống kê áp dụng nghiêm ngặt tiêu chí phân loại chỉ tiêu thống nhất toàn quốc, bảo đảm dữ liệu chân thực, khách quan và chính xác."}}),
 (16,"Use intact target verb naturally.",{"example":{"simplified":"海关依法扣留了这批缺少报关单据的货物。","pinyin":"Hǎiguān yīfǎ kòuliú le zhè pī quēshǎo bàoguān dānjù de huòwù.","vietnamese":"Hải quan đã tạm giữ theo luật lô hàng thiếu chứng từ khai báo hải quan này."}}),
 (17,"Remove duplicated 清洁.",{"example":{"simplified":r[16].examples[0].simplified.replace("清洁低碳可再生清洁能源","清洁低碳可再生能源"),"pinyin":r[16].examples[0].pinyin.replace("qīngjié dītàn kězàishēng qīngjié néngyuán","qīngjié dītàn kězàishēng néngyuán")}}),
 (18,"Remove historical duplication and noun gloss.",{"english_meanings":["leapfrogging","developing by leaps and bounds"],"example":{"simplified":r[17].examples[0].simplified.replace("历史性历史窗口","历史窗口"),"pinyin":r[17].examples[0].pinyin.replace("lìshǐxìng lìshǐ chuāngkǒu","lìshǐ chuāngkǒu")}}),
 (20,"时节 jié.",py(20,"shíjī","shíjié")),
 (26,"Distinguish lavish spending from generosity.",{"vietnamese_meanings":["sung túc","tiêu xài rộng rãi","xa hoa"],"example":{"vietnamese":"Vị giáo sư già sống hết sức giản dị này cả đời không màng danh lợi, không theo đuổi hưởng thụ vật chất xa hoa, nhưng lại dốc toàn bộ tiền tiết kiệm để tài trợ sinh viên nghèo."}}),
 (27,"擴 khuếch attested.",{"sino_vietnamese":"khuếch sung"}),
 (28,"English infinitive and 干部.",dict(py(28,"gàngbù","gànbù"),english_meanings=["to rope in","to win over"])),
 (31,"Contextual high-level development rendering.",{"example":{"vietnamese":"Hội nghị toàn thể Thành ủy đã phác họa kế hoạch phát triển lớn cho năm năm tới: xây dựng một thành phố mới hiện đại, có năng lực tổng hợp cao, sinh thái, đổi mới sáng tạo và đáng sống."}}),
 (33,"干部 gànbù.",py(33,"gàngbù","gànbù")),
 (38,"Natural accumulation syntax.",{"example":{"simplified":"知识需要通过长期阅读和实践逐步累积。","pinyin":"Zhīshi xūyào tōngguò chángqī yuèdú hé shíjiàn zhúbù lěijī.","vietnamese":"Kiến thức cần được tích lũy dần qua việc đọc và thực hành lâu dài."}}),
 (39,"Desolate adjective sense used.",{"part_of_speech":"verb, adjective"}),
 (45,"Natural milestone collocation.",{"example":{"simplified":"空间站进入长期在轨运营阶段，标志着载人航天事业迎来了新的里程碑。","pinyin":"Kōngjiānzhàn jìnrù chángqī zàiguǐ yùnyíng jiēduàn, biāozhì zhe zàirén hángtiān shìyè yínglái le xīn de lǐchéngbēi.","vietnamese":"Trạm vũ trụ bước vào giai đoạn vận hành lâu dài trên quỹ đạo, đánh dấu một cột mốc mới của sự nghiệp du hành vũ trụ có người lái."}}),
 (48,"Remove mixed standpoint phrase.",{"example":{"simplified":r[47].examples[0].simplified.replace("落脚立足点","立足点"),"pinyin":r[47].examples[0].pinyin.replace("luòjiǎo lìzúdiǎn","lìzúdiǎn")}}),
 (49,"干部 gànbù.",py(49,"gàngbù","gànbù")),
], sources=["https://hvdic.thivien.net/whv/%E8%BE%9F","https://hvdic.thivien.net/whv/%E5%8B%98","https://hvdic.thivien.net/whv/%E6%93%B4","https://hvdic.thivien.net/whv/%E9%A1%86"])

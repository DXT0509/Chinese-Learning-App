"""Actual L5-B014 all-field decisions and rechecked repairs."""
from record_batch import record, rows
r=rows("L5-B014")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B014", """
蓬勃 péngbó vigorous; innovation park vitality aligned.
批复 pīfù official reply; railway feasibility approval aligned.
批示 pīshì written instructions; nominal 作出批示 requires noun too.
疲惫 píbèi exhausted; bì bại not bì bãi, flood rescuers example aligned.
皮革 pígé leather; vegetable tanning and briefcase example correct.
偏见 piānjiàn prejudice; intercultural dialogue aligned.
偏僻 piānpì remote; Vietnamese high-mountain tea not specifically shan tuyết.
贫困 pínkùn poor; 难题 nántí not nándí.
品德 pǐndé moral character; 诚实守信 chéngshíshǒuxìn not chéngxìnshǒuxìn.
平息 píngxī subside; resolving online rumors aligned.
平面 píngmiàn plane; architectural floorplan aligned.
凭空 píngkōng without foundation; evidence-based research contrast correct.
破例 pòlì make exception; 潜质 qiánzhì not qiánzhǐ? Source qiánzhì correct, retain.
剖析 pōuxī analyze; phẫu not phẩu; 演变 yǎnbiàn not yǎnjiàn.
普及率 pǔjílǜ penetration rate; remove repeated percentage syllables.
欺骗 qīpiàn deceive; false investment schemes aligned.
齐心协力 qíxīnxiélì concerted effort; joint flood defense correct.
齐全 qíquán complete; source example only uses 一应俱全, replace with actual target.
旗下 qíxià under banner; group subsidiaries example accurate.
旗帜 qízhì banner; 前仆后继 qiánpūhòujì valid heroic falling pronunciation.
起草 qǐcǎo draft; 送审稿 sòngshěngǎo not sòngshěnggǎo.
启示 qǐshì inspiration; historical governance lessons aligned.
契机 qìjī opportunity; sporting event infrastructure example correct.
气魄 qìpò bold spirit; remove repeated 世纪 and Vietnamese duplication.
牵连 qiānlián implicate; 机关 jīguān correct.
谦虚 qiānxū modest; scientific success and humility aligned.
前夕 qiánxī eve; anniversary preparations aligned.
欠缺 qiànquē deficiency; 仿真 fǎngzhēn not fāngzhēn.
枪支 qiāngzhī firearms; gloss excludes ammunition itself, amend.
强硬 qiángyìng tough; 予以 yǔyǐ not jǐyǔ.
悄悄 qiāoqiāo quietly; entering laboratory respectfully natural.
桥梁 qiáoliáng bridge/link; language-cultural connection aligned.
技巧性 jìqiǎoxìng skillfulness; awkward superlative technique phrase replaced with clear gymnastics sentence.
亲密 qīnmì close; long collaboration and friendship coherent.
侵害 qīnhài infringe; remove duplicate 合法 absent in transcription.
钦佩 qīnpèi admire; corrupted 无自由衷 and repeated sentiment repaired.
轻视 qīngshì underestimate; neglecting core research example aligned.
倾向 qīngxiàng inclination; electric vehicle purchasing preferences correct.
清晰度 qīngxīdù clarity; correct 分辨率, 传输, 地面 transcription errors.
情操 qíngcāo moral sentiments; malformed 广泛优秀阅读 repaired.
情绪化 qíngxùhuà emotional; 干部 gànbù correct.
晴朗 qínglǎng clear; Great Wall against blue sky natural.
请求 qǐngqiú request; include noun for 提出正式请求.
庆祝会 qìngzhùhuì celebration; 干部 gànbù correct.
琼浆玉液 qióngjiāngyùyè fine wine; 宛若 wǎnruò, Vietnamese no place marker chốn.
秋收 qiūshōu autumn harvest; combine harvesters example aligned.
驱逐 qūzhú expel; warning and expulsion example aligned.
取舍 qǔshě choice; malformed 权衡利弊长远 repaired to longer-term decision sentence.
全盛 quánshèng most prosperous; adjective rather than heyday noun, modify gloss/POS.
权势 quánshì power/influence; equality before law example aligned. Stable keys and advanced level retained.
""", [
 (3,"Nominal instructions.",{"part_of_speech":"verb, noun"}),
 (4,"憊 bại.",{"sino_vietnamese":"bì bại"}),
 (7,"Do not infer specific tea cultivar.",{"example":{"vietnamese":"Dù là thôn núi hẻo lánh giữa núi non trùng điệp, giao thông vô cùng khó khăn, công trình đường nông thôn đến từng thôn của quốc gia đã mở thông tuyến tiêu thụ chè núi cao và đặc sản miền núi, giúp địa phương làm giàu."}}),
 (8,"难题 tí.",py(8,"nándí","nántí")),
 (9,"诚实 shí.",py(9,"chéngxìn-shǒuxìn","chéngshí-shǒuxìn")),
 (14,"剖 phẫu and 演变 biàn.",dict(py(14,"yǎnjiàn","yǎnbiàn"),sino_vietnamese="phẫu tích")),
 (15,"百分之百 single percent construction.",py(15,"bǎifēnzhī bǎifēnbǎi","bǎifēnzhī bǎi")),
 (18,"Example must demonstrate target 齐全.",{"example":{"simplified":"这座应急储备中心的救援设备十分齐全。","pinyin":"Zhè zuò yìngjí chǔbèi zhōngxīn de jiùyuán shèbèi shífēn qíquán.","vietnamese":"Thiết bị cứu hộ của trung tâm dự trữ khẩn cấp này rất đầy đủ."}}),
 (21,"审 shěn, no extra g.",py(21,"sòngshěnggǎo","sòngshěngǎo")),
 (24,"Remove repeated 世纪.",{"example":{"simplified":r[23].examples[0].simplified.replace("世纪超级调水世纪工程","世纪超级调水工程"),"pinyin":r[23].examples[0].pinyin.replace("shìjì chāojí diàoshuǐ shìjì gōngchéng","shìjì chāojí diàoshuǐ gōngchéng"),"vietnamese":r[23].examples[0].vietnamese.replace("siêu chuyển nước thế kỷ","siêu chuyển nước")}}),
 (25,"机关 jīguān.",py(25,"jīgī","jīguān")),
 (28,"仿 fǎng.",py(28,"fāngzhēn","fǎngzhēn")),
 (29,"Firearms not ammunition.",{"vietnamese_meanings":["súng ống","các loại súng"]}),
 (30,"予以 yǔyǐ.",py(30,"jǐyǔ","yǔyǐ")),
 (33,"Natural technique construction.",{"example":{"simplified":"这套体操动作的技巧性很强，对运动员的协调能力要求很高。","pinyin":"Zhè tào tǐcāo dòngzuò de jìqiǎoxìng hěn qiáng, duì yùndòngyuán de xiétiáo nénglì yāoqiú hěn gāo.","vietnamese":"Bài động tác thể dục này có tính kỹ thuật cao, đòi hỏi vận động viên có khả năng phối hợp tốt."}}),
 (35,"Remove doubled 合法.",{"example":{"simplified":r[34].examples[0].simplified.replace("合法合法","合法")}}),
 (36,"Repair corrupted text and repeated admiration.",{"example":{"simplified":"前辈坚贞不屈的精神令大家由衷钦佩。","pinyin":"Qiánbèi jiānzhēn-bùqū de jīngshén lìng dàjiā yóuzhōng qīnpèi.","vietnamese":"Tinh thần kiên trung bất khuất của bậc tiền bối khiến mọi người hết lòng khâm phục."}}),
 (39,"Correct several mismatched syllables.",{"example":{"pinyin":r[38].examples[0].pinyin.replace("gāofēnbànlǜ","gāofēnbiànlǜ").replace("chuānshū","chuánshū").replace("dīmiàn","dìmiàn")}}),
 (40,"Natural reading subject/modifiers.",{"example":{"simplified":"阅读优秀文学作品、亲近大自然，有助于陶冶情操。","pinyin":"Yuèdú yōuxiù wénxué zuòpǐn, qīnjìn dàzìrán, yǒuzhùyú táoyě qíngcāo.","vietnamese":"Đọc tác phẩm văn học hay và gần gũi thiên nhiên giúp bồi dưỡng tâm hồn, tình cảm cao đẹp."}}),
 (41,"干部 gànbù.",py(41,"gàngbù","gànbù")),
 (43,"Nominal request.",{"part_of_speech":"verb, noun"}),
 (44,"干部 gànbù.",py(44,"gàngbù","gànbù")),
 (45,"若 ruò and fine wine not a place.",{"example":{"pinyin":r[44].examples[0].pinyin.replace("wǎnrùo","wǎnruò"),"vietnamese":r[44].examples[0].vietnamese.replace("tựa chốn quỳnh","tựa quỳnh")}}),
 (48,"Natural weighing long-term consequences.",{"example":{"simplified":"选择研究方向时，应当权衡利弊，作出明智的取舍。","pinyin":"Xuǎnzé yánjiū fāngxiàng shí, yīngdāng quánhéng lìbì, zuòchū míngzhì de qǔshě.","vietnamese":"Khi chọn hướng nghiên cứu, cần cân nhắc lợi hại và đưa ra lựa chọn sáng suốt."}}),
 (49,"全盛 adjective at zenith.",{"part_of_speech":"adjective","vietnamese_meanings":["cực thịnh","hưng thịnh nhất"],"english_meanings":["at its zenith","most prosperous"]}),
], sources=["https://hvdic.thivien.net/whv/%E6%86%8A","https://hvdic.thivien.net/whv/%E5%89%96"])

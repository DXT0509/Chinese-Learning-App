"""Actual L5-B024 review; all corrected results re-read."""
from record_batch import record, rows
r=rows("L5-B024")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B024", """
百家争鸣 bǎijiāzhēngmíng competing schools; historical philosophical diversity aligned.
文质彬彬 wénzhìbīnbīn refined; 彬 bân not tân.
出神入化 chūshénrùhuà superb; erhu mastery appropriate.
独树一帜 dúshùyīzhì distinctive style; 写意 xiěyì not xièyì.
返璞归真 fǎnpúguīzhēn simplicity; writer rural retreat aligned.
凤毛麟角 fèngmáolínjiǎo rarity; ancient manuscripts appropriate.
高山仰止 gāoshānyǎngzhǐ admiration; replace uncertain quoted 景行 readings with unambiguous moral-example sentence.
海纳百川 hǎinàbǎichuān inclusive; cultural openness metaphor aligned.
翰墨 hànmò literary brush/ink; seal society writing gathering appropriate.
铺陈 pūchén detailed elaboration; 排比 rhetorical parallelism not word repetition in Vietnamese.
匠心独运 jiàngxīndúyùn ingenuity; 漏窗 patterned openwork window translation refined.
举一反三 jǔyīfǎnsān infer by analogy; mathematical teaching appropriate.
开卷有益 kāijuànyǒuyì beneficial reading; knowledge/moral enrichment aligned.
刻骨铭心 kègǔmíngxīn unforgettable; sacrifice memory appropriate.
口传心授 kǒuchuánxīnshòu oral/personal instruction; naturalize Vietnamese instead of dạy lòng.
妙笔生花 miàobǐshēnghuā gifted writing; Jiangnan prose appropriate.
耐人寻味 nàirénxúnwèi thought-provoking; ethical drama meaning aligned.
拍案叫绝 pāiànjiàojué applaud enthusiastically; 非遗 Vietnamese intangible heritage not phi di vật.
气韵 qìyùn artistic vitality; 写意 xiěyì not xièyì.
融通 róngtōng integrate; philosophical resource integration aligned.
入木三分 rùmùsānfēn penetrating; remove spurious precise inch conversion.
润物无声 rùnwùwúshēng nurture quietly; 莘莘 numerous pupils, not specifically excellent pupils.
深邃 shēnsuì profound; night sky/philosophical reflection appropriate.
生花妙笔 shēnghuāmiàobǐ gifted pen; 流域 liúyù corrected.
天衣无缝 tiānyīwúfèng flawless; coordinated spacecraft tracking aligned.
微言大义 wēiyándàyì concise deep meaning; Spring/Autumn chronicle interpretation appropriate.
文以载道 wényǐzàidào literature conveys moral principles; scholarship purpose aligned.
蔚为大观 wèiwéidàguān magnificent spectacle; Danxia rock formations appropriate.
文字学 wénzìxué character studies; evolution of Chinese scripts aligned.
唯美 wéiměi aesthetic; visual animation style appropriate.
文风 wénfēng writing style; corrupted repetitive sentence replaced with concise actual illustration.
瑕不掩瑜 xiábùyǎnyú flaws do not outweigh virtues; language-model example aligned.
薪火 xīnhuǒ cultural torch; intergenerational spirit appropriate.
虚实相生 xūshíxiāngshēng interplay real/empty; 几张一桌二椅 malformed, 写意 corrected in new clear stage example.
雅俗共赏 yǎsúgòngshǎng broad aesthetic appeal; dance drama example aligned.
仰止 yǎngzhǐ revere; moral predecessors appropriate.
一览无余 yìlǎnwúyú see entire scene; spoken 一 tone valid, observation tower appropriate.
意境 yìjìng artistic mood; separate painting 色设 from clashing 青绿/浅绛 style specifics with clear landscape example.
音律 yīnlǜ musical tuning; ancient pitch generation context aligned.
游刃有余 yóurènyǒuyú handle expertly; experienced microsurgeon appropriate.
寓情于景 yùqíngyújǐng emotion in scenery; 柳宗元 writing appropriate.
源远流长 yuányuǎnliúcháng long history; cultural continuity appropriate.
再接再厉 zàijiēzàilì persist further; scientific team encouragement aligned.
造诣 zàoyì attainment; 潜心 qiánxīn not qiǎnxīn.
章法 zhāngfǎ composition; cursive calligraphy structure appropriate.
真知灼见 zhēnzhīzhuójiàn insight; strategic expert discussion aligned.
珠联璧合 zhūliánbìhé brilliant combination; music/digital stage art appropriate.
主旋律 zhǔxuánlǜ main melody/theme; 脉搏 màibó not 脉络 màiluò.
追本溯源 zhuīběnsùyuán trace origin; 机构 jīgòu not jīgī.
卓尔不群 zhuóěrbùqún outstanding; scientist learning/personality appropriate. Keys and advanced level retained.
""", [
 (2,"彬 bân.",{"sino_vietnamese":"văn chất bân bân"}),
 (4,"写 xiě in painting style.",py(4,"xièyì","xiěyì")),
 (7,"Unambiguous admiration sentence.",{"example":{"simplified":"这位学者高尚的品格令人高山仰止。","pinyin":"Zhè wèi xuézhě gāoshàng de pǐngé lìngrén gāoshān-yǎngzhǐ.","vietnamese":"Phẩm cách cao thượng của học giả này khiến mọi người hết lòng kính ngưỡng."}}),
 (10,"Parallelism not reduplication.",{"example":{"vietnamese":r[9].examples[0].vietnamese.replace("điệp từ điệp ngữ","phép song hành")}}),
 (11,"Openwork window.",{"example":{"vietnamese":r[10].examples[0].vietnamese.replace("hoa cửa sổ","cửa sổ hoa văn rỗng")}}),
 (15,"Natural oral/personal teaching Vietnamese.",{"vietnamese_meanings":["truyền dạy trực tiếp bằng lời nói","tận tình chỉ bảo trực tiếp"],"example":{"vietnamese":"Nhiều tuyệt kỹ thủ công truyền thống thuộc di sản văn hóa phi vật thể dân gian có nguy cơ mai một được bảo tồn qua nhiều thế hệ nhờ nghệ nhân lão thành trực tiếp truyền miệng, tận tình chỉ bảo và cầm tay chỉ việc cho học trò."}}),
 (18,"Intangible heritage wording.",{"example":{"vietnamese":r[17].examples[0].vietnamese.replace("phi di vật","di sản phi vật thể")}}),
 (19,"写 xiě.",py(19,"xièyìhuà","xiěyìhuà")),
 (21,"Avoid inaccurate modern inch conversion.",{"english_meanings":["penetrating","profound","incisive"]}),
 (22,"Numerous pupils not excellent pupils.",{"example":{"vietnamese":r[21].examples[0].vietnamese.replace("muôn vàn học sinh trò giỏi","đông đảo học trò")}}),
 (24,"流域 liúyù.",py(24,"liùyù","liúyù")),
 (31,"Repair malformed duplicated bureaucratic phrasing.",{"example":{"simplified":"这篇报告文风简洁，内容充实，没有空话套话。","pinyin":"Zhè piān bàogào wénfēng jiǎnjié, nèiróng chōngshí, méiyǒu kōnghuà tàohuà.","vietnamese":"Báo cáo này có văn phong ngắn gọn, nội dung đầy đủ, không có lời sáo rỗng."}}),
 (34,"Coherent one-table-two-chairs stage symbolism.",{"example":{"simplified":"传统戏曲用一桌二椅和演员的动作营造虚实相生的舞台空间。","pinyin":"Chuántǒng xìqǔ yòng yī zhuō èr yǐ hé yǎnyuán de dòngzuò yíngzào xūshí-xiāngshēng de wǔtái kōngjiān.","vietnamese":"Hí kịch truyền thống dùng một bàn, hai ghế và động tác của diễn viên để tạo nên không gian sân khấu hư thực hòa quyện."}}),
 (38,"Clear landscape artistic mood without conflating painting styles.",{"example":{"simplified":"画家通过留白和淡雅的色彩营造出悠远的意境。","pinyin":"Huàjiā tōngguò liúbái hé dànyǎ de sècǎi yíngzào chū yōuyuǎn de yìjìng.","vietnamese":"Họa sĩ dùng khoảng trống và màu sắc thanh nhã để tạo nên ý cảnh xa xăm."}}),
 (44,"潜 qián.",py(44,"qiǎnxīn","qiánxīn")),
 (48,"脉搏 màibó.",py(48,"màiluò","màibó")),
 (49,"机构 jīgòu.",py(49,"jīgī","jīgòu")),
])

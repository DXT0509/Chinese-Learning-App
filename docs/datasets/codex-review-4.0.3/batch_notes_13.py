"""Actual full L4-B005 review and corrected-content recheck."""
from record_batch import record

record("L4-B005", """
紧迫 jǐnpò urgent; disaster relief supplies example and SV khẩn bách correct.
敬礼 jìnglǐ salute; flag salute is trang nghiêm, not chào cẩn thận, correct translation.
经济 jīngjì economy; real-economy steady growth sentence aligned.
经历 jīnglì experience; youthful hardships and 磨难 mónàn sound.
经营 jīngyíng operate; family-run century-old business example coherent.
京剧 jīngjù Beijing opera; traditional-performance interest example and Vietnamese accurate.
警告 jǐnggào warn; replace blue-alert terminology with unambiguous teacher warning example.
竞争 jìngzhēng compete/competition; add noun POS, commercial-market competition aligned.
竟然 jìngrán unexpectedly; quiet pupil taking first place correctly conveys surprise.
究竟 jiūjìng after all; discussion followed by emphatic how-to-handle question sound.
举 jǔ raise; classroom hand-raising question example correct.
举办 jǔbàn host; school international cultural festival aligned.
拒绝 jùjué refuse; restore missing zhèng tone in 不正当 example.
距离 jùlí distance; rail shortening travel distance/time coherent.
聚会 jùhuì gathering; junior-high classmates' warm reunion aligned.
开玩笑 kāiwánxiào joke; don't take casual joke seriously, 当真 dàngzhēn correct.
开心 kāixīn happy; family Lunar-New-Year reunion correctly translated.
看法 kànfǎ viewpoint; differing opinions about plan natural.
考虑 kǎolǜ consider; parents' valuable advice example and umlaut correct.
烤鸭 kǎoyā roast duck; Beijing authentic-food example coherent.
科学 kēxué science; 陈规 is chénguī not chéngguī, correct transcription.
颗 kē round-object/star classifier; dictionary 顆 supports khỏa, correct khóa; Polaris example aligned.
咳嗽 késou cough; cold dry winter inducing cough, neutral sou and SV valid.
可怜 kělián pitiful; shivering stray kitten example correct.
可是 kěshì but with 虽然; traffic-jam delay accurately contrasted.
可惜 kěxī regrettable; 球赛 means ball match, avoid adding unsupported football specificity in VI.
客厅 kètīng living room; family watching televised gala aligned.
肯定 kěndìng definitely; shared effort guaranteeing on-time completion coherent.
空 kōng empty; empty box example, distinct from kòng free-time sense.
空间 kōngjiān space; room reserved for bookshelf correctly expressed.
恐怕 kǒngpà afraid/perhaps; anticipated evening storm shows uncertain prediction.
苦恼 kǔnǎo distressed; thesis-topic difficulty and 找不到 pronunciation aligned.
矿泉水 kuàngquánshuǐ mineral water; insert 在 before backpack locative and align full example.
枯燥 kūzào dull; teacher making theory lively, passive 被 construction sound.
困难 kùnnan difficulties; neutral nan accepted, temporary setbacks and no retreat example sound.
垃圾桶 lājītǒng bin; dictionary 圾 is sắc here, correct lạp cơ dũng to lạp sắc dũng; simplify environment collocation.
拉 lā pull; opening curtains to let sunshine in, directional complement correct.
蜡烛 làzhú candle; birthday cake colorful candles, pinyin and SV aligned.
来不及 láibu jí not enough time; flight departing in half-hour, neutral bu valid.
来得及 láidejí enough time; two hours before train leaves, neutral de valid.
来自 láizì come from; international volunteers' origins coherent.
懒 lǎn lazy; repair awkward 习惯太懒散 subject construction and align translation.
浪费 làngfèi waste; valuable food not to be wasted, all fields sound.
浪漫 làngmàn romantic; add necessary beach-walking locative using a clear natural example.
老虎 lǎohǔ tiger; Northeast wild tiger figuratively king of forest, correct pinyin.
冷静 lěngjìng calm; emergency no-panic example and Vietnamese accurate.
离婚 líhūn divorce; replace clumsy long-term-personality syntax with natural incompatibility/divorce-procedure example.
礼貌 lǐmào politeness; respectful greeting demonstrates manners accurately.
理发 lǐfà haircut; place 重要 before 外事会议 and align pinyin, preserve hair fà identity.
理解 lǐjiě understand; close friend understanding hardship, correct. All 50 Level 4 identities retained; no new ambiguity unresolved.
""", [
 (2,"Saluting flag is not greeting carefully.",{"example":{"vietnamese":"Các đội viên Đội Thiếu niên Tiền phong hướng về quốc kỳ, trang nghiêm chào cờ."}}),
 (7,"Use natural 警告 example without conflating official 预警 labels.",{"example":{"simplified":"老师警告学生不要在走廊里奔跑。","pinyin":"Lǎoshī jǐnggào xuésheng bú yào zài zǒuláng lǐ bēnpǎo.","vietnamese":"Thầy giáo cảnh báo học sinh không được chạy trong hành lang."}}),
 (8,"Competition noun already present.",{"part_of_speech":"verb, noun"}),
 (13,"Missing fourth tone on 正.",{"example":{"pinyin":"Miànduì wéifǎ-luànjì de bú zhèngdàng yāoqiú, wǒmen bìxū jiānjué jùjué."}}),
 (21,"陈规 chénguī, no ng coda on 陈.",{"example":{"pinyin":"Wǒmen yào xiāngxìn kēxué, pòchú chénguī-jiùsú yǔ míxìn."}}),
 (22,"顆 dictionary lists khoả/khoã, not khóa.",{"sino_vietnamese":"khỏa"}),
 (26,"球赛 does not specify football.",{"example":{"vietnamese":"Trận đấu bóng này vô cùng đặc sắc, bạn không đến tận nơi xem thì thật đáng tiếc."}}),
 (33,"Backpack is a locative requiring 在 in this construction.",{"example":{"simplified":"长途登山徒步旅行时别忘了在随身背包里备上一瓶矿泉水。","pinyin":"Chángtú dēngshān túbù lǚxíng shí bié wàng le zài suíshēn bēibāo lǐ bèi shang yì píng kuàngquánshuǐ."}}),
 (36,"Correct 圾 SV and use natural keep-environment-clean phrase.",{"sino_vietnamese":"lạp sắc dũng","example":{"simplified":"公园里设有分类垃圾桶，方便市民保持环境清洁。","pinyin":"Gōngyuán lǐ shèyǒu fēnlèi lājītǒng, fāngbiàn shìmín bǎochí huánjìng qīngjié.","vietnamese":"Trong công viên có thùng rác phân loại, giúp người dân thuận tiện giữ gìn môi trường sạch sẽ."}}),
 (42,"Remove malformed lazy-habit predication.",{"example":{"simplified":"他平时很懒散，房间总是乱七八糟，也不肯动手收拾。","pinyin":"Tā píngshí hěn lǎnsǎn, fángjiān zǒngshì luànqībāzāo, yě bù kěn dòngshǒu shōushi.","vietnamese":"Anh ấy thường rất lười nhác, phòng lúc nào cũng bừa bộn mà anh ấy cũng không chịu dọn dẹp."}}),
 (44,"Supply beach locative in natural walking example.",{"example":{"simplified":"在夏夜的海滩上漫步是一件很浪漫的事。","pinyin":"Zài xiàyè de hǎitān shang mànbù shì yí jiàn hěn làngmàn de shì.","vietnamese":"Dạo bước trên bãi biển vào đêm hè là một việc rất lãng mạn."}}),
 (47,"Natural incompatibility and divorce-procedure phrasing.",{"example":{"simplified":"他们因为性格不合，最终协商办理了离婚手续。","pinyin":"Tāmen yīnwèi xìnggé bùhé, zuìzhōng xiéshāng bànlǐ le líhūn shǒuxù.","vietnamese":"Vì tính cách không hợp, cuối cùng họ đã thỏa thuận làm thủ tục ly hôn."}}),
 (49,"Natural modifier order for important foreign-affairs meeting.",{"example":{"simplified":"明天要去参加重要外事会议，他下午抽空去理发店理发。","pinyin":"Míngtiān yào qù cānjiā zhòngyào wàishì huìyì, tā xiàwǔ chōukòng qù lǐfàdiàn lǐfà."}}),
], sources=["https://hvdic.thivien.net/whv/%E9%A1%86","https://hvdic.thivien.net/whv/%E5%9C%BE","https://hvdic.thivien.net/whv/%E6%A1%B6"])

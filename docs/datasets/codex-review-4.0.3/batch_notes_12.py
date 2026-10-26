"""L4-B004 actual all-field linguistic review; edits re-read before checkpointing."""
from record_batch import record

record("L4-B004", """
结账 jiézhàng pay bill; correct SV trượng to trướng; restaurant example otherwise aligned.
猴子 hóuzi monkey; mischievous monkeys swinging on branches, neutral zi valid.
厚 hòu thick/deep affection; winter padded coat example correct.
后悔 hòuhuǐ regret; future regret after wasting time accurately expressed.
后来 hòulái later; temporal noun can function adverbially, friendship example coherent.
忽然 hūrán suddenly; storm example sound, remove duplicated Vietnamese trút phrasing.
护士 hùshi nurse; weak second syllable acceptable colloquially, night-duty nursing example aligned.
结实 jiēshi sturdy, not jiéshí fruit-bearing; solid wooden desk example correct.
怀疑 huáiyí suspect; premeditated-case possibility and pinyin agree.
回忆 huíyì recall/memory; add noun POS and replace unnatural 无限回忆 sentence.
活动 huódòng activity; student environmental tree-planting event accurately translated.
结合 jiéhé combine; linking theory with practical operation natural and aligned.
火 huǒ fire/anger; replace awkward 红火 with clear fire noun example and recheck all fields.
基础 jīchǔ foundation; foreign-language pronunciation/grammar foundations sentence sound.
激动 jīdòng excited; national-team victory example coherent, mark 得 in 夺得 as dé.
积极 jījí positive/active; optimistic youth facing setbacks coherent and correctly translated.
积累 jīlěi accumulate/accumulation; add noun POS for existing nominal sense; reading-literature example correct.
及时 jíshí in time/timely; timely emergency aid example aligns, add adjective POS for timely sense.
即使 jíshǐ even if with 也; obstacles-to-success sentence and sandhi correct.
寄信 jìxìn mail letter; replace duplicated 把家信寄信投递 construction with natural standalone 寄信 example.
计划 jìhuà plan; executing revision plan correctly expressed and translated.
技术 jìshù technology/skill; advanced automated production technology example coherent.
既然 jìrán since; Chinese pattern 那就 sound, repair unnatural Vietnamese introductory word order.
继续 jìxù continue; 教室 must jiàoshì, not jiàoxuéshì; complete shortened sentence rechecked.
寄托 jìtuō entrust hopes/feelings; nostalgic lyric poem example and 游子 yóuzǐ correct.
结论 jiélùn conclusion; expert reasoning then conclusion naturally aligned.
加油站 jiāyóuzhàn petrol station; fill tank before motorway journey, complete pinyin/VI correct.
家具 jiājù furniture; 特地 is tèdì, not tēdì, otherwise Scandinavian furnishing example sound.
假 jiǎ false; fake-news example, not jià holiday; pinyin/sense aligned.
价格 jiàgé price; affordable organic produce example and 物美价廉 correct.
坚持 jiānchí persevere; habitual early running and robust physique accurately translated.
减肥 jiǎnféi lose weight; 均衡 must jūnhéng, not jìnhéng; corrected full example transcription rechecked.
减少 jiǎnshǎo reduce; low-carbon transport reducing tailpipe pollution aligned.
建议 jiànyì suggest/proposal; add noun POS matching proposal; weak-foundation pupils study advice coherent.
将来 jiānglái future; replace clumsy 学好专业课本领 with mastering professional skills; all example fields aligned.
奖金 jiǎngjīn bonus; year-end reward after diligent effort natural and correct.
降低 jiàngdī reduce; energy-saving process reducing consumption, SV hàng đê valid.
降落 jiàngluò land; replace odd 问候音乐 with 欢迎音乐 and update translation/pinyin.
交 jiāo hand in/make friends; representative collecting and submitting homework sound.
交流 jiāoliú exchange; international cultural exchange enhancing understanding coherent.
交通 jiāotōng transport; well-developed metro/bus network example correct.
郊区 jiāoqū suburbs; 清新 is qīngxīn, not xīnxīan; simplify near-suburb phrase and align example.
解释 jiěshì explain; request to explain word meaning accurate, yíxià sandhi valid.
尽管 jǐnguǎn although; despite snow soldiers remain at posts, all fields aligned.
教授 jiàoshòu professor; advanced algebra taught to graduate students, pinyin and SV sound.
教育 jiàoyù education; strategic priority education example coherent with matching Vietnamese.
接受 jiēshòu accept; 中肯 zhòngkěn and 不断 búduàn correct, constructive criticism sentence sound.
接着 jiēzhe then; detailed-report followed by execution discussion matches sequence.
节 jié classifier lessons/sections/carriages; two grammar periods example correctly aligned.
节约 jiéyuē economize; electricity/water saving example and sandhi correct. Level 4 placements and stable identities remain reasonable.
""", [
 (1,"账/帳 is trướng, not trượng.",{"sino_vietnamese":"kết trướng"}),
 (6,"Remove duplicated Vietnamese downpour expression.",{"example":{"vietnamese":"Trên bầu trời chớp giật sấm rền, bỗng nhiên mưa lớn đổ xuống như trút nước."}}),
 (10,"Recall/memory noun missing; repair unnatural unlimited-recall collocation.",{"part_of_speech":"verb, noun","example":{"simplified":"走在故乡的老街上，我回忆起了童年的往事。","pinyin":"Zǒu zài gùxiāng de lǎojiē shang, wǒ huíyì qǐ le tóngnián de wǎngshì.","vietnamese":"Đi trên con phố cổ ở quê nhà, tôi nhớ lại những chuyện thời thơ ấu."}}),
 (13,"Use an unambiguous fire noun rather than 红火 collocation.",{"example":{"simplified":"冬天，壁炉里燃烧着明亮的火焰。","pinyin":"Dōngtiān, bìlú lǐ ránshāo zhe míngliàng de huǒyàn.","vietnamese":"Vào mùa đông, những ngọn lửa sáng bùng cháy trong lò sưởi."}}),
 (15,"得 in 夺得 pronounced dé.",{"example":{"pinyin":"Dāng tīngdào zǔguóduì duódé guànjūn xǐxùn shí, suǒyǒu qiúmí dōu jīdòng de tiào le qǐlai."}}),
 (17,"Accumulation nominal sense already present.",{"part_of_speech":"verb, noun"}),
 (18,"Include timely adjectival sense.",{"part_of_speech":"adverb, adjective"}),
 (20,"Avoid duplicated letter object inside 把 construction.",{"example":{"simplified":"我顺便去邮局帮室友寄信。","pinyin":"Wǒ shùnbiàn qù yóujú bāng shìyǒu jìxìn.","vietnamese":"Tôi tiện thể đến bưu điện gửi thư giúp bạn cùng phòng."}}),
 (23,"Natural Vietnamese since/then construction.",{"example":{"vietnamese":"Mọi người đã nhất trí tán thành đề xuất này thì chúng ta hãy lập tức bắt tay vào tổ chức thực hiện."}}),
 (24,"教室 jiàoshì has two syllables; improve rest-duration syntax.",{"example":{"simplified":"课间休息十分钟之后，大家回到教室继续听讲。","pinyin":"Kèjiān xiūxi shí fēnzhōng zhīhòu, dàjiā huídào jiàoshì jìxù tīngjiǎng.","vietnamese":"Sau mười phút giải lao giữa giờ, mọi người trở lại lớp học tiếp tục nghe giảng."}}),
 (28,"特地 tèdì fourth tone.",{"example":{"pinyin":"Xīn bānjìn gōngyù hòu tāmen tèdì gòuzhì le yí tào xiàndài běi'ōu fēnggé de jiǎnyuē jiājù."}}),
 (32,"均衡 jūnhéng correct onset/vowel/tone.",{"example":{"pinyin":"Kēxué hélǐ de jiǎnféi xūyào jūnhéng kòngzhì yǐnshí bìng pèihé chízhīyǐhéng de yǒuyǎng yùndòng."}}),
 (34,"Proposal noun already in English.",{"part_of_speech":"verb, noun"}),
 (35,"Skills are mastered, not studied as 课本领.",{"example":{"simplified":"努力掌握专业技能，将来才能实现自己的抱负。","pinyin":"Nǔlì zhǎngwò zhuānyè jìnéng, jiānglái cáinéng shíxiàn zìjǐ de bàofù.","vietnamese":"Nỗ lực nắm vững kỹ năng chuyên môn thì sau này mới có thể thực hiện hoài bão của mình."}}),
 (38,"Welcome music is 欢迎音乐, not greeting music 问候音乐.",{"example":{"simplified":"飞机平稳降落在跑道上，机舱里响起了欢迎音乐。","pinyin":"Fēijī píngwěn jiàngluò zài pǎodào shang, jīcāng lǐ xiǎngqǐ le huānyíng yīnyuè.","vietnamese":"Máy bay hạ cánh êm ái xuống đường băng, trong khoang vang lên tiếng nhạc chào đón."}}),
 (42,"Repair 清新 transcription and redundant near-suburb phrasing.",{"example":{"simplified":"周末不少市民喜欢自驾前往空气清新的郊区踏青游玩。","pinyin":"Zhōumò bùshǎo shìmín xǐhuan zìjià qiánwǎng kōngqì qīngxīn de jiāoqū tàqīng yóuwán.","vietnamese":"Cuối tuần không ít người dân thích tự lái xe đến vùng ngoại ô có không khí trong lành để du xuân ngắm cảnh."}}),
])

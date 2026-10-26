"""Actual L4-B010 full-content review with rechecked corrections."""
from record_batch import record

record("L4-B010", """
友好 yǒuhǎo friendly; arts festival building friendship, accurate.
友谊 yǒuyì friendship; friendly sports tournament and 新篇章 aligned.
有趣 yǒuqù interesting; engaging physical experiments arousing curiosity correct.
语法 yǔfǎ grammar; vocabulary plus grammatical-rule learning accurate.
语言 yǔyán language; communication and civilization bridge metaphor coherent.
羽毛球 yǔmáoqiú badminton; young school staff at weekend gym, correct.
预习 yùxí preview lessons; preparing textbook before class, pinyin/VI sound.
原谅 yuánliàng forgive; admission and correction of faults before pardon coherent.
原则 yuánzé principle; principled right/wrong stance, complete pinyin correct.
约会 yuēhuì date/appointment; add noun POS for café date example.
阅读 yuèdú read; daily classics reading and 陶冶 táoyě correct.
允许 yǔnxǔ permit; dictionary verifies duẫn variant, retain; laboratory authorization example sound.
杂志 zázhì magazine; research journal example slightly repetitive but grammatical and aligned.
咱们 zánmen inclusive we; dictionary supports ta for 咱, correct thảm môn to ta môn.
暂时 zànshí temporarily; roadworks diversion and VI accurate.
责任 zérèn responsibility; protecting children, 茁壮 is zhuózhuàng, correct.
增加 zēngjiā increase; peak holiday train frequency increase, correct.
增长 zēngzhǎng growth; 赋能 here enables rather than transfers authority, correct Vietnamese.
招聘 zhāopìn recruit; algorithm engineer recruitment, SV chiêu phính correct.
真正 zhēnzhèng genuine; enduring comradeship after hardship, correct.
正常 zhèngcháng normal; restored power operation and 调试 tiáoshì correct.
正式 zhèngshì official; emblem release announcement aligned.
证明 zhèngmíng prove/certificate; add noun POS and Vietnamese certificate sense; artifact evidence example coherent.
支持 zhīchí support; tax measures supporting small firms, all fields sound.
知识 zhīshi knowledge; acquiring scientific/cultural knowledge, neutral shi valid.
直接 zhíjiē direct; 疲劳驾驶 means fatigued driving, does not necessarily mean falling asleep, correct translation.
值得 zhíde worth; documentary worth seeing, neutral de and 一看 yí kàn correct.
职业 zhíyè occupation; dedicated work producing achievement, accurate.
植物 zhíwù plants; improve awkward plants dwelling/breeding with clear rainforest plant-variety example.
指导 zhǐdǎo guide; senior engineer guiding young technicians coherent.
只好 zhǐhǎo have no choice; storm-bound expedition waiting at camp accurate.
制造 zhìzào manufacture; domestically developed passenger plane example aligned.
质量 zhìliàng quality/mass; both senses valid, product inspection example sound.
忠实 zhōngshí faithful; 如 is rú not rù in thirty-year loyal subscription example.
重视 zhòngshì value; fostering independent thought/practical skill aligned.
周围 zhōuwéi surroundings; scenic new campus location, correct.
逐渐 zhújiàn gradually; 沉睡 is chénshuì not chénsùi, correct transcription.
主动 zhǔdòng proactive; volunteering for hard tasks without counting personal gains accurate.
主张 zhǔzhāng advocate; peaceful international dispute resolution, all fields sound.
主意 zhǔyi idea; brainstorming workable new plan, weak yi valid.
祝贺 zhùhè congratulate; mathematics competition gold medal, correct.
著名 zhùmíng famous; rare species is 珍稀 not 珍惜; correct written typo and preserve intended meaning.
专门 zhuānmén specially/specialized; correct Vietnamese meanings and home-visit medical-service example without invented free charge.
专业 zhuānyè specialty; computer-science undergraduate going into software development correct.
赚 zhuàn earn; dictionary verifies trám, not khoán; entrepreneurial profits example aligned.
准确 zhǔnquè accurate; weather-map track prediction example linguistically aligned.
准时 zhǔnshí on time; eight-thirty meeting sign-in instruction correct.
资源 zīyuán resources; renewable sun/wind utilization accurately expressed.
姿势 zīshì posture; example Chinese 坐姿 requires zuòzī, not substituted zīshì, correct pinyin.
资金 zījīn capital; construction funding raised, all fields aligned. Level 4 classification and all identities preserved.
""", [
 (10,"Appointment/date nominal use already present.",{"part_of_speech":"verb, noun"}),
 (14,"咱 dictionary supports ta, not thảm.",{"sino_vietnamese":"ta môn"}),
 (18,"赋能 in digital transformation means enabling, not granting authority.",{"example":{"vietnamese":"Nhờ sự hỗ trợ của chuyển đổi số, tổng giá trị sản lượng của các doanh nghiệp công nghệ cao trong quý này đã tăng trưởng nhanh chóng và ổn định."}}),
 (23,"Certificate noun missing from Vietnamese/POS.",{"part_of_speech":"verb, noun","vietnamese_meanings":["chứng minh","xác nhận","giấy chứng nhận"]}),
 (26,"Fatigue is not necessarily falling asleep.",{"example":{"vietnamese":"Nguyên nhân trực tiếp của vụ tai nạn giao thông này là tài xế điều khiển xe trong tình trạng mệt mỏi và thao tác không đúng."}}),
 (29,"Avoid attributing dwelling behavior to plants.",{"example":{"simplified":"热带雨林中生长着许多珍稀的野生植物。","pinyin":"Rèdài yǔlín zhōng shēngzhǎng zhe xǔduō zhēnxī de yěshēng zhíwù.","vietnamese":"Trong rừng mưa nhiệt đới có nhiều loài thực vật hoang dã quý hiếm sinh trưởng."}}),
 (34,"如 is rú, second tone.",{"example":{"pinyin":"Tā shì zhè jiā lìshǐ yōujiǔ de wénxué zázhì sānshí nián rú yí rì de zhōngshí dìngyuè dúzhě."}}),
 (37,"沉睡 chénshuì requires sh onset.",{"example":{"pinyin":"Suízhe chūnhuí-dàdì qìwēn zhuǎnnuǎn, chénshuì le yì dōng de xiǎoxī bīngxuě zhújiàn xiāoróng."}}),
 (42,"Rare species is 珍稀, not cherish 珍惜; same pinyin but different characters/meaning.",{"example":{"simplified":"这位享誉海内外的著名生物学家一生致力于珍稀濒危植物的保护与育种。"}}),
 (43,"Translate specially/specialized and correct home medical visit collocation; no claim of free service.",{"part_of_speech":"adverb, adjective","vietnamese_meanings":["chuyên, riêng","đặc biệt","chuyên biệt"],"example":{"simplified":"社区卫生服务中心专门为行动不便的老人提供上门诊疗服务。","pinyin":"Shèqū wèishēng fúwù zhōngxīn zhuānmén wèi xíngdòng búbiàn de lǎorén tígōng shàngmén zhěnliáo fúwù.","vietnamese":"Trung tâm dịch vụ y tế cộng đồng cung cấp riêng dịch vụ khám chữa bệnh tại nhà cho người cao tuổi đi lại khó khăn."}}),
 (45,"賺 dictionary reading trám.",{"sino_vietnamese":"trám"}),
 (49,"坐姿 in Chinese must correspond to zuòzī.",{"example":{"pinyin":"Zài rìcháng fú'àn dúxiě guòchéng zhōng bǎochí zhèngquè de zuòzī yǔ shìjù nénggòu yǒuxiào bǎohù shìlì jiànkāng."}}),
], sources=["https://hvdic.thivien.net/whv/%E8%B3%BA","https://hvdic.thivien.net/whv/%E5%92%B1","https://hvdic.thivien.net/whv/%E5%85%81"])

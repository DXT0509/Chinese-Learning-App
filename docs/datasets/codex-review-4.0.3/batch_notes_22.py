"""Actual L5-B002 full-content review and corrected example recheck."""
from record_batch import record

record("L5-B002", """
查询 cháxún inquire/search; 询 SV tuân, correct tra tầm to tra tuân; rail app inquiry accurate.
差别 chābié disparity; urban/rural teacher and equipment gap, correct.
查明 chámíng ascertain; technical/CCTV investigation finding fire cause aligned.
产物 chǎnwù product/outcome; internet as technical/civilizational product, correct.
阐明 chǎnmíng clarify; trade-system values explained, accurate.
长久 chángjiǔ long-lasting; sustainable lasting prosperity, correct.
偿还 chánghuán repay; bank infrastructure loan repaid fully and punctually, correct.
常年 chángnián year round/normal year; add noun POS and normal-year VI sense already in English.
昌盛 chāngshèng prosperous; wishes for national prosperity and peace aligned.
常理 chánglǐ common sense; replace unnatural thông lý with đạo lý thông thường, suspect's unusual behavior example sound.
倡议 chàngyì initiative; add noun POS matching 发出倡议 in example.
超越性 chāoyuèxìng transcendence; philosophical work transcending time/space, correct.
沉淀 chéndiàn settle/precipitation; add noun POS for precipitation, figurative wisdom settling after trials coherent.
沉着 chénzhuó calm; ship captain responding calmly to storm, correct not particle zhe.
沉闷 chénmèn oppressive; storm-before-air mèn and 闷热 mēnrè distinction correctly rendered.
沉沦 chénlún degenerate; refusing despair after setbacks, correct.
陈列室 chénlièshì exhibition room; school historical photographs displayed, sound.
晨练 chénliàn morning exercise; elders exercising in fresh park air aligned.
成效 chéngxiào achieved effect; river conservation work results accurate.
澄清 chéngqīng clarify; 机关 is jīguān not jīgòu, correct transcription.
呈现 chéngxiàn show; technology clusters and vigorous development correct.
沉思 chénsī ponder; add noun POS for 陷入沉思, mathematician's contemplation aligned.
称霸 chēngbà dominate; diplomatic stance example linguistically coherent, no contemporary event verification claimed.
成分 chéngfèn ingredient; labels with additive composition amounts aligned.
成见 chéngjiàn prejudice; cross-cultural communication removing historical preconceptions correct.
承载 chéngzài carry; old bridge bearing shared memory, correct.
乘务员 chéngwùyuán attendant; high-speed train passenger service accurate.
惩罚 chéngfá punish; add noun POS for 受到惩罚, environmental-law example sound linguistically.
成败 chéngbài success/failure; precision aerospace assembly details matter, correct.
城镇化 chéngzhènhuà urbanization; central/western development coherent.
澄清度 chéngqīngdù clarity; use straightforward measured water-sample clarity rather than muddled industrial drinking-water criterion.
称呼 chēnghu address; use direct target-word example rather than synonym-only honorific statement.
诚恳 chéngkěn sincere; honest self-reflection at meeting aligned.
盛产 shèngchǎn abound; productive fertile subtropical fruit plain, correct.
乘机 chéngjī seize opportunity; replace unnatural 乘机而上 with taking opportunity to ask professor.
成千上万 chéngqiānshàngwàn thousands; remove duplicated 海内外中外 while retaining tourist example.
承诺 chéngnuò promise; conference carbon commitments example pinyin/VI aligned.
崇敬 chóngjìng revere; 干部 is gànbù not gàngbù, correct.
充沛 chōngpèi vigorous; 难题 is nántí not nándí; energy supporting research breakthrough sound.
崇尚 chóngshàng uphold; valuing labor and knowledge, correct.
冲突 chōngtū conflict; peaceful regional dispute resolution, correct.
充足 chōngzú sufficient; sleep/nutrition sufficiency example and 均衡 jūnhéng correct.
抽空 chōukòng find time; mayor visiting housing-repair site, correct kòng.
抽象 chōuxiàng abstract; calculus taught accessibly, passive example aligned.
抽查 chōuchá spot-check; supermarket quality inspections, correct.
筹备 chóubèi prepare; forum preparations orderly, correct.
稠密 chóumì dense; fire safety in densely populated historic district coherent.
筹划 chóuhuà plan; cultural tourism route planning, accurate.
初衷 chūzhōng original intention; charity school offering access to education, correct.
出道 chūdào debut; replace unnatural 天赋青年 adjective stack with natural singer-debut example. Level 5 technical/abstract vocabulary and stable identities retained.
""", [
 (1,"询/詢 is tuân, not tầm.",{"sino_vietnamese":"tra tuân"}),
 (8,"Normal/average year noun sense already in English.",{"part_of_speech":"adverb, noun","vietnamese_meanings":["quanh năm","thường niên","năm bình thường"]}),
 (10,"Natural Vietnamese common-sense gloss.",{"vietnamese_meanings":["lẽ thường","đạo lý thông thường"]}),
 (11,"Initiative noun used after 发出.",{"part_of_speech":"verb, noun"}),
 (13,"Precipitation nominal sense already present.",{"part_of_speech":"verb, noun"}),
 (20,"机关 jīguān must match Chinese characters.",{"example":{"pinyin":"Zhēnduì jìnqī wǎngluò shang liúchuán de xūjiǎ yáoyán, gōng'ān jīguān zài guānfāng píngtái dì-yī shíjiān fābù tōngbào chéngqīng shìshí."}}),
 (22,"Deep thought nominal use after 陷入.",{"part_of_speech":"verb, noun"}),
 (28,"Punishment nominal use after 受到.",{"part_of_speech":"verb, noun"}),
 (31,"Clarity measurement example without conflating clarity and drinkability.",{"example":{"simplified":"工作人员用仪器测量水样的澄清度。","pinyin":"Gōngzuò rényuán yòng yíqì cèliáng shuǐyàng de chéngqīngdù.","vietnamese":"Nhân viên dùng thiết bị đo độ trong của mẫu nước."}}),
 (32,"Direct natural use of target 称呼.",{"example":{"simplified":"在正式场合，应该礼貌地称呼对方。","pinyin":"Zài zhèngshì chǎnghé, yīnggāi lǐmào de chēnghu duìfāng.","vietnamese":"Trong những dịp trang trọng, nên xưng hô lịch sự với người đối diện."}}),
 (35,"Avoid conflation with 乘势而上 phrase.",{"example":{"simplified":"会议结束后，他乘机向教授请教了一个问题。","pinyin":"Huìyì jiéshù hòu, tā chéngjī xiàng jiàoshòu qǐngjiào le yí ge wèntí.","vietnamese":"Sau khi hội nghị kết thúc, anh ấy nhân cơ hội hỏi giáo sư một vấn đề."}}),
 (36,"Remove duplicated domestic/foreign modifiers.",{"example":{"simplified":"每逢中秋国庆长假，成千上万的游客慕名涌向风景如画的历史古都。","pinyin":"Měiféng Zhōngqiū Guóqìng chángjià, chéngqiān-shàngwàn de yóukè mùmíng yǒngxiàng fēngguāng-rúhuà de lìshǐ gǔdū."}}),
 (38,"干部 gànbù, not gàngbù.",{"example":{"pinyin":"Guǎngdà qīngnián gànbù qúnzhòng huái zhe wúbǐ chóngjìng de xīnqíng shēnqiè miǎnhuái wèi mínzú dúlì jiěfàng yīngyǒng xīshēng de gémìng xiānliè."}}),
 (39,"题 second-tone tí, not dí.",{"example":{"pinyin":"Niánqīng kēyán tuánduì píngjiè chōngpèi de jīnglì hé búxiè de tànsuǒ zhuīqiú, gōngguān ná xià le héxīn jìshù nántí."}}),
 (50,"Natural talented-singer debut phrasing.",{"example":{"simplified":"这位年轻歌手在音乐比赛中夺冠后正式出道。","pinyin":"Zhè wèi niánqīng gēshǒu zài yīnyuè bǐsài zhōng duóguàn hòu zhèngshì chūdào.","vietnamese":"Ca sĩ trẻ này chính thức bước vào nghề sau khi giành chức vô địch trong cuộc thi âm nhạc."}}),
])

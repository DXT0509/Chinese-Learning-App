"""Actual L5-B007 review, corrected examples rechecked; one stable-key issue held."""
from record_batch import record

record("L5-B007", """
古董 gǔdǒng antique; 监督 jiāndū not jiānguǎn in source example, correct.
骨干 gǔgàn backbone; taking heavy responsibility 挑起大梁 tiǎoqǐ not tiāoqǐ, correct.
鼓动 gǔdòng instigate; rumor-driven troublemaking example coherent.
顾虑 gùlǜ misgiving; 干部 gànbù not gàngbù, correct.
顾问 gùwèn adviser; city planning/environment experts consulting, correct.
故乡 gùxiāng hometown; nostalgia of distant traveler aligned.
关联 guānlián relation; add noun POS for 内在关联 in economic-indicator example.
关照 guānzhào look after; train attendant helping blind traveler, correct.
官僚 guānliáo bureaucratic; 干部 gànbù not gàngbù, correct.
关税 guānshuì tariff; illustrative bilateral trade reduction, correct pinyin/senses.
贯彻 must guànchè but stable key guan1 che4 has wrong first tone; hold for explicit identity repair, also remove duplicate 全面.
惯例 guànlì customary practice; business-contract example linguistically aligned.
灌溉 guàngài irrigate; canal bringing water to downstream farmland, correct.
光辉 guānghuī radiance; 磨灭 mómiè not mómoi, correct, add adjective POS for shining life.
光芒 guāngmáng rays; golden sunrise through layered cloud, correct.
广阔 guǎngkuò broad; digital/AI prospects, accurate.
归还 guīhuán return; repair active inanimate-material subject with explicit 被归还给原主.
归纳 guīnà infer/summarize; clinical data symptom pattern analysis, correct.
规避 guībì circumvent; correct Vietnamese néng tránh typo to né tránh.
规范化 guīfànhuà standardized; streamlined public approvals, all fields aligned.
规矩 guīju rule; traditional no-rules-no-square-circle idiom accurate, neutral ju valid.
规模化 guīmóhuà large-scale; consolidated tea plantation operation, correct.
规划图 guīhuàtú planning map; city transport map explanation at model exhibit, correct.
轨道 guǐdào orbit/track; satellite in planned orbit, correct.
贵族 guìzú aristocrat; 阶级 jiējí not jiēcéng, correct.
国家级 guójiājí national-level; remove redundant 常绿 repeated in forest description.
过滤 guòlǜ filter; multilayer adsorption removing suspended particles aligned.
过失 guòshī negligence; faulty operation causing machine stoppage, correct.
过度 guòdù excessive; 血管 xuèguǎn not xiěguǎn in compound, correct pinyin.
过渡 guòdù transition; bridging old/new curriculum, distinct written key retained.
海底 hǎidǐ seabed; deep submersible collecting sediment, pinyin/VI aligned.
海关 hǎiguān customs; port inspection of travelers/goods, correct.
海洋学 hǎiyángxué oceanography; 海洋大学 means ocean studies university, not maritime navigation school, clarify VI.
含糊 hánhu vague; 含糊其辞 requires qící not qíwèi, correct.
含义 hányì meaning; couplet's philosophical connotations, correct.
行情 hángqíng market quotation; soybean/corn futures settlements, not xíng reading.
航海 hánghǎi seafaring; Zheng He's voyages illustrative historical example, correct.
航空母舰 hángkōngmǔjiàn aircraft carrier; catapult-capable ship example, correct.
豪迈 háomài bold; revolutionary optimism on long march, aligned.
毫米 háomǐ millimeter; 0.01 mm precision example accurate.
好恶 hàowù likes/dislikes; both fourth tones correct, judicial impartiality example aligned.
浩劫 hàojié catastrophe; world-war devastation, correct.
合并 hébìng merge; university merger, correct.
合成 héchéng synthesize; simplify overstacked experimental-material example without unsupported superconductivity property.
合伙 héhuǒ partnership; three returning doctors founding biotech firm, correct.
合身 héshēn well-fitting; custom-tailored suit and liángshēn reading valid.
合影 héyǐng group photo; add verb POS for taking group photo in example.
合算 hésuàn worthwhile; 年度 is annual, not monthly pass, correct Vietnamese.
合情合理 héqínghélǐ reasonable; balanced arbitration decision, correct.
和睦 hémù harmonious; helpful neighbors and family harmony, correct. Level 5 classification retained; 贯彻 identity remains genuinely blocked by stable-key constraint.
""", [
 (1,"监督 jiāndū differs from 监管 jiānguǎn.",{"example":{"pinyin":"Guójiā tèxǔ wénwù pāimài jīgòu zài yángé fǎzhì shěnchá jiāndū xià gōngkāi pāimài le yì pī liúshī hǎiwài duō nián de zhēnguì gǔdài tóngqì gǔdǒng."}}),
 (2,"挑起 responsibility is tiǎoqǐ.",{"example":{"pinyin":"Gāi gāokējì kēyán chuàngxīn tuánduì zhōng sānshíwǔ suì yǐxià de yōuxiù qīngnián jìshù zhuānjiā yǐjīng tiǎoqǐ dàliáng chéngzhǎng wéi yánfā zhōngjiān gǔgàn."}}),
 (4,"干部 gànbù not gàngbù.",{"example":{"pinyin":"Lǐngdǎo gànbù zài shēnrù jīcéng tīngqǔ qúnzhòng pīpíng yìjiàn shí yīngdāng xūhuái-ruògǔ, chèdǐ dǎxiāo guǎngdà lǎobǎixìng gǎn jiǎng zhēnhuà de xīnlǐ gùlǜ."}}),
 (7,"Relation nominal use.",{"part_of_speech":"verb, noun"}),
 (9,"干部 gànbù not gàngbù.",{"example":{"pinyin":"Lǐngdǎo gànbù bìxū jiānjué kèfú tuōlí-shíjì gāogāo-zàishàng de guānliáo-zhǔyì zuòfēng, shǐzhōng tóng rénmín qúnzhòng zuò zài yì tiáo bǎndèng shang."}}),
 (11,"Remove duplicated 全面; correct example's actual guànchè while keeping mismatching head identity on hold.",{"example":{"simplified":"各级党委政府必须全面准确贯彻创新、协调、绿色、开放、共享的新发展理念。","pinyin":"Gè jí dǎngwěi zhèngfǔ bìxū quánmiàn zhǔnquè guànchè chuàngxīn, xiétiáo, lǜsè, kāifàng, gòngxiǎng de xīn fāzhǎn lǐniàn."}}),
 (14,"磨灭 mómiè needs valid final/tone; shining adjective used in example.",{"part_of_speech":"noun, adjective","example":{"pinyin":"Wěidà gémìng lǐngxiù yòng qí guānghuī de yìshēng wèi guójiā fùqiáng rénmín xìngfú jiànlì le yǒng bù mómiè de bùxiǔ lìshǐ gōngxūn."}}),
 (17,"Use proper passive with returned documents as subject.",{"example":{"simplified":"这批族谱资料在学术研究结束后，已被完整归还给原主。","pinyin":"Zhè pī zúpǔ zīliào zài xuéshù yánjiū jiéshù hòu, yǐ bèi wánzhěng guīhuán gěi yuánzhǔ.","vietnamese":"Sau khi nghiên cứu học thuật kết thúc, số tài liệu gia phả này đã được trả lại nguyên vẹn cho chủ cũ."}}),
 (19,"Vietnamese né tránh spelling.",{"vietnamese_meanings":["né tránh","phòng tránh (rủi ro)"]}),
 (25,"阶级 jiējí, not 阶层 jiēcéng.",{"example":{"pinyin":"Lìshǐ tícái diànshìjù shēnkè jiēlù le fēngjiàn jiù shídài fǔxiǔ mòluò de dà dìzhǔ guìzú jiējí huīhuò-wúdù de shēmí jìshēng shēnghuó."}}),
 (26,"Remove duplicated evergreen descriptor.",{"example":{"simplified":"这片保存完好的亚热带原始常绿阔叶林被国务院正式批准设立为国家级自然保护区。","pinyin":"Zhè piàn bǎocún wánhǎo de yàrèdài yuánshǐ chánglǜ kuòyèlín bèi Guówùyuàn zhèngshì pīzhǔn shèlì wéi guójiājí zìrán bǎohùqū."}}),
 (29,"血管 xuèguǎn standard compound reading.",{"example":{"pinyin":"Chángqī chǔyú guòdù píláo yǔ jīngshén gāodù jǐnbēng de gāoyā gōngzuò zhuàngtài zhōng jíyì yòufā xīn-nǎoxuèguǎn tūfā jíbìng."}}),
 (33,"Oceanographic university rather than maritime navigation university.",{"example":{"vietnamese":"Trường đại học hải dương hiện đại cấp quốc gia đã xây dựng ngành hải dương học tổng hợp hàng đầu, bao quát vật lý biển, sinh vật biển và thăm dò biển sâu, vùng cực."}}),
 (34,"辞 cí, not 谓 wèi.",{"example":{"pinyin":"Zài shèjí gōngsī zhòngdà tóuzī cáiwù juécè de fǎlǜ quánzé jièdìng shang, hétong yòngcí bìxū jīngzhǔn yánmì, jué bù néng hánhu-qící."}}),
 (44,"Clear synthesis example without modifier stack/speculative property.",{"example":{"simplified":"科研团队在实验室中合成了一种新型晶体材料。","pinyin":"Kēyán tuánduì zài shíyànshì zhōng héchéng le yì zhǒng xīnxíng jīngtǐ cáiliào.","vietnamese":"Nhóm nghiên cứu khoa học đã tổng hợp một loại vật liệu tinh thể mới trong phòng thí nghiệm."}}),
 (47,"Taking a group photo is verbal in example.",{"part_of_speech":"noun, verb"}),
 (48,"年度 annual, not monthly.",{"example":{"vietnamese":"Đối với người thường xuyên đi công tác đường dài liên tỉnh, mua một vé thông hành thương mại liên kết cả năm của đường sắt cao tốc toàn quốc là rất có lợi."}}),
], pending={11:{"reason":"Standard guan4 che4 conflicts with source stable lexical identity guan1 che4. Example repaired, but headword requires explicit identity repair rather than silent renaming.","linguistic_uncertainty":True}})

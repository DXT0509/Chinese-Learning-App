"""Actual L4-B012 full linguistic review and corrected-result recheck."""
from record_batch import record

record("L4-B012", """
编写 biānxiě compile; experts coauthoring Chinese textbook over three years, correct.
辩论 biànlùn debate; add noun POS for 展开辩论, AI ethics debate aligned.
辩解 biànjiě justify; add noun POS for 作辩解, admitting dereliction without excuses correct.
标本 biāoběn specimen; museum fossil displays and pinyin aligned.
标志 biāozhì landmark/symbol; completed rail hub marks city modernization correct.
表决 biǎojué vote; anonymous ballot passing draft charter, correct.
表态 biǎotài declare stance; department heads expressing support coherent.
表彰 biǎozhāng commend; civic courage award ceremony, all fields aligned.
别扭 bièniu awkward; meeting after misunderstanding, weak niu valid.
冰雹 bīngbáo hail; hail hitting orchards, 不要 mistaken bào reading avoided.
播送 bōsòng broadcast; morning radio news to listeners correct.
播放 bōfàng play; repeated Silk Road documentary in multimedia classroom correct.
波浪 bōlàng waves; golden ripples on lake, accurate.
波动 bōdòng fluctuate; add noun POS for 出现波动, commodity-market example aligned.
搏斗 bódòu struggle; rescuers battling rough seas, 殊死 shūsǐ correct.
补偿 bǔcháng compensate; land-acquisition compensation sentence linguistically correct.
补救 bǔjiù remedy; emergency algorithm bug mitigation coherent.
补贴 bǔtiē subsidy; agricultural production support, correct.
捕捞 bǔlāo fish/catch; dictionary 撈 lao, correct bộ thao to bộ lao; fishing season example sound.
不得已 bùdéyǐ no alternative; canceled flight and overnight hotel, aligned.
不顾 bùgù disregard; búgù in connected speech correct, soldier ignoring personal risk coherent.
不禁 bùjīn cannot help; moved to tears by veteran professor's account, jīn not jìn correct.
不免 bùmiǎn inevitably; lonely student homesickness at New Year, sound.
不由得 bùyóude involuntarily; comic mime causing laughter, correctly translated.
裁缝 cáifeng tailor; liángshēn measurement reading supported by MOE; retain rather than invent tone error.
裁判 cáipàn referee; football officiating impartially, full example aligned.
采纳 cǎinà adopt; experts approving energy-saving building design, correct.
彩票 cǎipiào lottery ticket; public-welfare funding example linguistically aligned.
餐巾 cānjīn napkin; correct SV xán to xan, remove tablecloth sense, 丝质 must sīzhì not sījī.
残疾 cánjí disability; accessible facilities/social inclusion example correct.
残酷 cánkù cruel; historical war depiction, correct.
仓库 cāngkù warehouse; automated temperature-controlled emergency storage coherent.
操场 cāochǎng school sports field; school exercise assembly, correct tones and meaning.
操劳 cāoláo toil; parents' lifelong effort raising children, correct.
草案 cǎo'àn draft; legislation working group submits draft regulation, apostrophe correct.
草率 cǎoshuài careless/hasty; warning against hasty public decisions aligned.
策划 cèhuà plan; online heritage promotion campaign, correct.
测量 cèliáng measure; replace misattached high-precision team modifier with clear geology measurement example.
阐述 chǎnshù expound; accessible explanation of low-carbon development, accurate.
常识 chángshí general knowledge; disaster escape/self-help knowledge, correct.
常态 chángtài usual state; correct 干部 gànbù, not gàngbù, in routine outreach example.
畅通 chàngtōng unblocked; holiday motorway traffic maintained, correct.
倡导 chàngdǎo advocate; volunteers promoting green lifestyle, aligned.
钞票 chāopiào banknotes; digital payments reducing cash use, correct.
超越 chāoyuè surpass; researchers exceeding limits, correct.
车厢 chēxiāng carriage; climate-controlled passenger compartments, all syllables aligned.
扯 chě pull/chat; 东拉西扯 by winter fire illustrates chatting, accurate.
彻底 chèdǐ thorough; pollution eradication example sound.
沉默 chénmò silent; respectful memorial silence, correct.
沉重 chénzhòng heavy; remove duplicated 沉重繁重 modifiers in economic-burden example. All Level 4 records read, stable keys retained, no genuine new uncertainty left.
""", [
 (2,"Debate noun used in 展开辩论.",{"part_of_speech":"verb, noun"}),
 (3,"Excuse/justification noun used in example.",{"part_of_speech":"verb, noun"}),
 (14,"Fluctuation nominal use after 出现.",{"part_of_speech":"verb, noun"}),
 (19,"撈 dictionary lao, not thao.",{"sino_vietnamese":"bộ lao"}),
 (29,"餐 xan; napkin not tablecloth; silk material 质 zhì.",{"sino_vietnamese":"xan cân","vietnamese_meanings":["khăn ăn"],"example":{"pinyin":"Fúwùyuán zài yànhuì kāixí zhīqián xìzhì de zài měi ge cānwèi qián zhěngqí zhédié bǎifàng hǎo le jiébái de sīzhì cānjīn."}}),
 (38,"Precision describes measurement rather than team.",{"example":{"simplified":"地质勘探队使用现代仪器对溶洞地貌进行了精确测量。","pinyin":"Dìzhì kāntànduì shǐyòng xiàndài yíqì duì róngdòng dìmào jìnxíng le jīngquè cèliáng.","vietnamese":"Đội khảo sát địa chất dùng thiết bị hiện đại để đo đạc chính xác địa mạo hang động đá vôi."}}),
 (41,"干部 gànbù has no ng coda in 干.",{"example":{"pinyin":"Bǎ diàochá-yánjiū yǔ zǒufǎng jīcéng qúnzhòng zhuǎnhuà wéi guǎngdà dǎngyuán gànbù kāizhǎn gè xiàng rìcháng xíngzhèng gōngzuò de yì zhǒng zìjué chángtài."}}),
 (50,"Remove duplicated heavy adjectives.",{"example":{"simplified":"突如其来的自然灾害给当地基础设施建设与群众正常生产生活带来了极其沉重的经济负担。","pinyin":"Tūrúqílái de zìrán zāihài gěi dāngdì jīchǔ shèshī jiànshè yǔ qúnzhòng zhèngcháng shēngchǎn shēnghuó dàilái le jíqí chénzhòng de jīngjì fùdān."}}),
], sources=["https://hvdic.thivien.net/whv/%E6%92%88","https://hvdic.thivien.net/whv/%E9%A4%90","https://dict.mini.moe.edu.tw/SearchIndex/word_detail?breadcrumbs=Search_%E9%87%8F_one&dictSearchField=%E9%87%8F&wordID=D0000770"])

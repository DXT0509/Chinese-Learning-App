"""Explicit notes for Level 3 batches 2 and 3 read in full."""

from checkpoint import save

save(
    "L3-B002",
    {
        1: "着急 zhao2 ji2 is anxious/in a hurry, with zháo rather than particle zhe; calming request and Vietnamese are aligned.",
        2: "生气 sheng1 qi4 denotes anger; reason-for-being-angry example and Vietnamese agree.",
        3: "奇怪 qi2 guai4, kỳ quái, is strange; evaluative sentence and Vietnamese match.",
        4: "热情 re4 qing2, nhiệt tình, is warm/enthusiastic; guest-hospitality sentence is grammatical and accurately translated.",
        5: "认真 ren4 zhen1, nhận chân, means earnest/conscientious; earnest-study example and Vietnamese are appropriate.",
        6: "聪明 cong1 ming5 is intelligent; neutral ming is common and the boy example agrees.",
        7: "努力 nu3 li4 includes strive as well as hardworking; added verb POS for the existing striving sense and conditional example.",
        8: "新鲜 xin1 xian1, tân tiên, means fresh; fresh-morning-air example and Vietnamese are valid.",
        9: "安静 an1 jing4, an tĩnh, is quiet; library example and Vietnamese match.",
        10: "热闹 re4 nao5, nhiệt náo, is lively/bustling; neutral nao and night-market example are aligned.",
        11: "舒服 shu1 fu5, thư phục, is comfortable; the chair-use construction is natural and accurately translated.",
        12: "方便 fang1 bian4, phương tiện, means convenient in Chinese; metro-travel example correctly uses Vietnamese thuận tiện rather than noun phương tiện.",
        13: "安全 an1 quan2 means safe/safety. Added noun POS and nominal meaning for 注意安全 in the existing example.",
        14: "危险 wei1 xian3, nguy hiểm, means dangerous; road-playing example is semantically and grammatically aligned.",
        15: "重要 zhong4 yao4, trọng yếu, means important; comparison of health and money is natural.",
        16: "主要 zhu3 yao4, chủ yếu, means main/primary; main-content example and Vietnamese match.",
        17: "特别 te4 bie2, đặc biệt, means special; distinctive dish-taste example correctly selects that sense.",
        18: "一般 yi4 ban1 uses attested spoken sandhi but needs the same citation identity policy decision as 一直. Also restored omitted 很 in example Pinyin.",
        19: "简单 jian3 dan1, giản đơn, means simple; problem-evaluation example and Vietnamese align.",
        20: "复杂 fu4 za2, phức tạp, is complex; situation example and Vietnamese agree.",
        21: "满意 man3 yi4, mãn ý, means satisfied; customer's service evaluation and Vietnamese are correct.",
        22: "有名 you3 ming2, hữu danh, means famous; well-known-university sentence is natural.",
        23: "调皮 tiao2 pi2 means mischievous; tiáo is the correct reading here, and younger-brother example aligns.",
        24: "诚实 cheng2 shi2, thành thực, means honest; person-description sentence and Vietnamese are correct.",
        25: "小心 xiao3 xin1, tiểu tâm, means careful; slippery-road warning and Vietnamese match.",
        26: "马虎 ma3 hu5, mã hổ, means careless; neutral hu and exam warning are appropriate.",
        27: "暖和 nuan3 huo5, noãn hòa, is warm; huo5 is appropriate in this word and spring-weather change aligns.",
        28: "凉快 liang2 kuai5, lương khoái, is pleasantly cool; autumn-weather example and Vietnamese match.",
        29: "勇敢 yong3 gan3, dũng cảm, is brave; soldier description and Vietnamese align.",
        30: "幽默 you1 mo4, u mặc, is humorous; teacher's humorous presentation and Vietnamese agree.",
        31: "害羞 hai4 xiu1, hại tu, means shy; reaction to strangers and Vietnamese are correct.",
        32: "瘦 shou4, sấu, means thin/lose weight; post-illness change and Vietnamese align.",
        33: "胖 pang4, bạng, means fat. Original sweet-food advice had unclear causal ellipsis; replaced it with an explicit excessive-sweets -> gain-weight sentence.",
        34: "健康 jian4 kang1, kiện khang, means healthy; health-wishing formula and Vietnamese are natural.",
        35: "年轻 nian2 qing1, niên khinh, is young; learning-new-knowledge advice is aligned and Level 3 appropriate.",
        36: "严格 yan2 ge2, nghiêm cách, is strict; teacher's requirements sentence and Vietnamese are correct.",
        37: "活泼 huo2 po5 is supplied with neutral po, whereas standard teaching sources normally give huópō. Retain key and hold for documented neutral-tone variant/citation verification.",
        38: "亲切 qin1 qie4, thân thiết, means kind/cordial; aunt's manner and Vietnamese are appropriate.",
        39: "丰富 feng1 fu4, phong phú, means rich/abundant; book-content example and Vietnamese match.",
        40: "顺利 shun4 li4, thuận lợi, means smooth/successful; work-wishing formula and Vietnamese are natural.",
        41: "苦 ku3, khổ, includes bitter/difficult; medicine taste selects bitter. The sentence is an illustrative language example, not identification of a treatment.",
        42: "精彩 jing1 cai3, tinh thải, means excellent/wonderful; evening-performance example and Vietnamese align.",
        43: "困 kun4, khốn, means sleepy or constrained; sleep-deprived example selects sleepiness and Vietnamese matches.",
        44: "疼 teng2, đông, means painful/sore; headache sentence and Vietnamese are accurate.",
        45: "久 jiu3, cửu, is long duration; 好久不见 and long-time-no-see greeting align.",
        46: "差 cha4, sai, means poor/bad in quality, distinguished from chai1 business-trip reading; eyesight example is valid.",
        47: "低 di1, đê, means low, distinguished from stature 矮; temperature example and Vietnamese align.",
        48: "优秀 you1 xiu4, ưu tú, means excellent; teacher description and Vietnamese agree.",
        49: "粗心 cu1 xin1, thô tâm, means careless; task-solving warning and Vietnamese align.",
        50: "骄傲 jiao1 ao4 covers proud/arrogant, retaining both legitimate senses; proverb selects arrogance and uses the correct apostrophe in jiāo'ào.",
    },
    corrections={
        7: {
            "changes": {"part_of_speech": "adjective; verb"},
            "reason": "Preserve hardworking adjective and strive verb senses already represented in meanings/example.",
        },
        13: {
            "changes": {
                "part_of_speech": "adjective; noun",
                "vietnamese_meanings": ["an toàn", "sự an toàn"],
                "english_meanings": ["safe", "secure", "safety"],
            },
            "reason": "注意安全 in the existing sentence uses nominal safety, which the adjective-only entry did not represent.",
        },
        18: {
            "changes": {
                "examples": [
                    {
                        "simplified": "这家餐馆的味道很一般。",
                        "pinyin": "Zhè jiā cānguǎn de wèidao hěn yìbān.",
                        "vietnamese": "Vị đồ ăn ở quán này rất bình thường.",
                    }
                ]
            },
            "reason": "Restore omitted 很 as hěn; the yi4 citation/sandhi identity question remains unresolved.",
        },
        33: {
            "changes": {
                "examples": [
                    {
                        "simplified": "甜食吃多了容易发胖。",
                        "pinyin": "Tiánshí chī duō le róngyì fāpàng.",
                        "vietnamese": "Ăn nhiều đồ ngọt dễ béo.",
                    }
                ]
            },
            "reason": "Make excessive eating, not eating less, the explicit cause of gaining weight; new Chinese/Pinyin/Vietnamese were re-read together.",
        },
    },
    pending={
        18: {
            "linguistic_uncertainty": True,
            "reason": "Need a consistent lexical citation-vs-spoken-sandhi policy for 一般|yi4 ban1 without silent key replacement.",
        },
        37: {
            "linguistic_uncertainty": True,
            "reason": "Verify whether neutral po5 is an accepted teaching variant or requires a different canonical pronunciation identity.",
        },
    },
)

save(
    "L3-B003",
    {
        1: "客人 ke4 ren5 is guest/customer; example's full rén differed from selected neutral ren. Aligned to kèren without declaring full-tone variation invalid.",
        2: "邻居 lin2 ju1, lân cư, means neighbor; good-neighbor-relations sentence and Vietnamese match.",
        3: "校长 xiao4 zhang3, hiệu trưởng, is principal; speech-at-school-assembly example and Pinyin are aligned.",
        4: "司机 si1 ji1, ty cơ, is driver; taxi-driver sentence and Vietnamese are correct.",
        5: "同事 tong2 shi4, đồng sự, means coworker; 相处 uses chǔ correctly and the getting-along sentence is aligned.",
        6: "阿姨 a1 yi2, a di, is aunt/parent-generation woman as address; surname-plus-aunt example and Vietnamese are appropriate.",
        7: "叔叔 shu1 shu5, thúc thúc, is uncle/parent-generation male address; book-gift example is aligned.",
        8: "爷爷 ye2 ye5, gia gia, specifically denotes paternal grandfather here; eighty-year-old example and ông nội match.",
        9: "奶奶 nai3 nai5, nãi nãi, is paternal grandmother; food-taste example and bà nội translation are aligned.",
        10: "外婆 wai4 po2, ngoại bà, is maternal grandmother; summer-visit example and bà ngoại are correct.",
        11: "孙子 sun1 zi5 is grandson rather than nephew. Qualified ambiguous Vietnamese cháu trai with generation/default paternal relation; example remains valid.",
        12: "顾客 gu4 ke4, cố khách, is customer; shopping-center example and Vietnamese align.",
        13: "观众 guan1 zhong4, quan chúng, is audience; applauding an actor's performance is natural and accurately translated.",
        14: "记者 ji4 zhe3, ký giả, is journalist; scientist-interview example and Vietnamese match.",
        15: "导游 dao3 you2, đạo du, is tour guide; Great Wall history introduction and Vietnamese are correct. Lower-case place-name Pinyin is a nonblocking capitalization inconsistency.",
        16: "律师 lü4 shi1, luật sư, means lawyer; sentence and translation are aligned illustrative language, not legal advice.",
        17: "警察 jing3 cha2, cảnh sát, means police officer; directing road traffic and Vietnamese agree.",
        18: "经理 jing1 li3, kinh lý, is manager; Zhang-manager location sentence and Vietnamese giám đốc/quản lý are contextually valid.",
        19: "作者 zuo4 zhe3, tác giả, is author; young-author example and Vietnamese match.",
        20: "演员 yan3 yuan2, diễn viên, is actor of either sex; movie-actor example is accurate.",
        21: "歌手 ge1 shou3, ca thủ, means singer; singer's pleasant voice and Vietnamese are aligned.",
        22: "社会 she4 hui4, xã hội, is society; every-person-lives-in-society sentence is grammatical.",
        23: "国家 guo2 jia1, quốc gia, is country/nation; long-history description and Vietnamese align.",
        24: "世界 shi4 jie4, thế giới, is world; travel-around-world desire and Vietnamese are correct.",
        25: "城市 cheng2 shi4, thành thị, is city; 一座 is the right classifier and the modern-city description aligns.",
        26: "农村 nong2 cun1, nông thôn, is countryside; grandfather's residence preference and Vietnamese match.",
        27: "街道 jie1 dao4, nhai đạo, means street; trees on both sides and zhòng planting reading are correct.",
        28: "公园 gong1 yuan2, công viên, is park; older people's morning walk sentence and Vietnamese align.",
        29: "银行 yin2 hang2, ngân hàng, is bank; háng not xíng is correct, and card-application example is natural.",
        30: "邮局 you2 ju2, bưu cục, is post office; school-opposite location and Vietnamese match.",
        31: "超市 chao1 shi4, siêu thị, means supermarket; grocery-shopping-after-work example aligns.",
        32: "市场 shi4 chang3, thị trường, is market; farm-market morning scene and Vietnamese chợ are accurate.",
        33: "图书馆 tu2 shu1 guan3, đồ thư quán, is library; afternoon book-borrowing example is correct.",
        34: "体育馆 ti3 yu4 guan3 is an indoor gym/sports hall; replaced overly broad stadium English with indoor sports arena. Friday ball-game example and Vietnamese are accurate.",
        35: "博物馆 bo2 wu4 guan3, bác vật quán, is museum; weekend history-museum visits and Vietnamese agree.",
        36: "电影院 dian4 ying3 yuan4 is movie theater, distinct from 电影 film; new-film outing example and Vietnamese align.",
        37: "剧场 ju4 chang3, kịch trường, is theater; 京剧 uses jīngjù correctly and evening-performance translation matches.",
        38: "大使馆 da4 shi3 guan3 means embassy. Recast visa sentence as one speaker's plan rather than a universal rule that every visa requires an embassy visit.",
        39: "海边 hai3 bian1, hải biên, means seaside; summer-holiday sentence and Vietnamese align.",
        40: "动物园 dong4 wu4 yuan2 is zoo; father-and-panda outing sentence and Vietnamese are accurate.",
        41: "植物园 zhi2 wu4 yuan2 is botanical garden; unusual-flora idiom and Vietnamese hoa thơm cỏ lạ correspond naturally.",
        42: "办公室 ban4 gong1 shi4, biện công thất, is office; teacher marking homework and Vietnamese agree.",
        43: "会议室 hui4 yi4 shi4 is meeting room; second-floor gathering request and Vietnamese are correct.",
        44: "厨房 chu2 fang2, trù phòng, is kitchen; mother's dinner preparation and Vietnamese align.",
        45: "阳台 yang2 tai2, dương đài, is balcony; flower-planting sentence and Vietnamese match.",
        46: "电梯 dian4 ti1, điện thang, means elevator; going to floor eight and Vietnamese are accurate.",
        47: "楼梯 lou2 ti1, lâu thang, means stairs; exercise-by-taking-stairs sentence distinguishes it from 电梯.",
        48: "院子 yuan4 zi5, viện tử, is courtyard; children playing there and Vietnamese are aligned.",
        49: "邻里 lin2 li3, lân lý, concerns neighborhood/neighbors as a community rather than simply an individual 邻居; mutual-help example is valid.",
        50: "社会学 she4 hui4 xue2, xã hội học, is sociology; university major example and Vietnamese agree. Example sentence is at the upper end of this app's Level 3 but interpretable with the gloss.",
    },
    corrections={
        1: {
            "changes": {
                "examples": [
                    {
                        "simplified": "今天家里来了一位客人。",
                        "pinyin": "Jīntiān jiā li lái le yí wèi kèren.",
                        "vietnamese": "Hôm nay nhà có một vị khách đến.",
                    }
                ]
            },
            "reason": "Align example with selected neutral ren5, preserving the valid guest sentence and meaning.",
        },
        11: {
            "changes": {
                "vietnamese_meanings": ["cháu trai (thế hệ cháu của ông bà; thường chỉ cháu nội)"]
            },
            "reason": "Disambiguate grandson from nephew in Vietnamese without conflating 孙子 with the mother's-side 外孙 default.",
        },
        34: {
            "changes": {"english_meanings": ["gymnasium", "indoor sports arena"]},
            "reason": "Clarify indoor sports hall rather than teaching an unqualified stadium synonym; Vietnamese nhà thi đấu is retained.",
        },
        38: {
            "changes": {
                "examples": [
                    {
                        "simplified": "我明天去大使馆办签证。",
                        "pinyin": "Wǒ míngtiān qù dàshǐguǎn bàn qiānzhèng.",
                        "vietnamese": "Ngày mai tôi đến đại sứ quán làm thủ tục xin thị thực.",
                    }
                ]
            },
            "reason": "Use a specific illustrative plan instead of an overgeneralized visa-procedure claim; retain the embassy learning target.",
        },
    },
)

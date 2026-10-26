"""Explicit Level 2 batch 2/3 notes after reading all records and examples."""

from checkpoint import save

save(
    "L2-B002",
    {
        1: "眼睛 yan3 jing5, nhãn tinh, means eyes; neutral jing and large-eyes example match.",
        2: "头发 tou2 fa5, đầu phát, means hair; neutral fa distinguishes the word from isolated 发 readings, and long-hair example aligns.",
        3: "脸 lian3, kiểm, is face; washing-face sentence and Vietnamese are natural.",
        4: "手 shou3, thủ, is hand; washing before eating and Vietnamese agree.",
        5: "腿 tui3, thoái, is leg rather than foot; the gloss makes this distinction and pain example is correct.",
        6: "脚 jiao3, cước, is foot; tired-feet-after-walking sentence and Vietnamese are aligned.",
        7: "哥哥 ge1 ge5, ca ca, is elder brother; university-study example and neutral second syllable are correct.",
        8: "姐姐 jie3 jie5, tỷ tỷ, is elder sister; working-hard example and Vietnamese match.",
        9: "弟弟 di4 di5, đệ đệ, is younger brother; watching-TV progressive is natural.",
        10: "妹妹 mei4 mei5, muội muội, is younger sister; dancing preference and Vietnamese align.",
        11: "丈夫 zhang4 fu5, trượng phu, is husband with neutral fu; doctor example is accurate.",
        12: "妻子 qi1 zi5, thê tử, is wife; living-in-Shanghai example is aligned.",
        13: "男人 nan2 ren2, nam nhân, is adult man; a full-tone ren is valid careful pronunciation beside common weak ren. Uncle-identification example is correct.",
        14: "女人 nü3 ren2, nữ nhân, means woman; full-tone ren in the selected reading and ability sentence are valid.",
        15: "孩子 hai2 zi5, hài tử, means child/children; three-children sentence and Vietnamese agree.",
        16: "服务员 fu2 wu4 yuan2 is service staff/waiter; Chinese bill request is natural. Replaced the stilted Vietnamese vocative with a natural polite request.",
        17: "手机 shou3 ji1, thủ cơ, is mobile phone; table-location sentence and Vietnamese match.",
        18: "手表 shou3 biao3, thủ biểu, is wristwatch; 只 classifier and pretty-watch sentence are appropriate.",
        19: "报纸 bao4 zhi3, báo chỉ, is newspaper; grandfather's morning reading and Vietnamese align.",
        20: "铅笔 qian1 bi3, duyên bút, means pencil; instrument construction 用铅笔写字 and Vietnamese agree.",
        21: "颜色 yan2 se4 means color; nhan sắc is a character-reading aid and not the meaning in this entry. Preferred-color question and màu sắc gloss are correct.",
        22: "红 hong2, hồng, is red; red-garment example and Vietnamese match.",
        23: "白 bai2, bạch, is white; snow-color sentence and translation align.",
        24: "黑 hei1, hắc, is black; 黑车 can also mean an unlicensed taxi. Made the color meaning explicit with 黑色的车 rather than leaving the collocation ambiguous.",
        25: "蓝 lan2, lam, is blue, distinguished from green 绿; sky example and Vietnamese agree.",
        26: "绿 lü4, lục, is green; spring leaves and Vietnamese xanh refer correctly to leaf color.",
        27: "黄 huang2, hoàng, means yellow; Chinese banana-color sentence and tones are correct. Fixed the Vietnamese typo Quối chuối to Quả chuối.",
        28: "件 jian4, kiện, counts garments/events; overcoat example and Vietnamese are sound.",
        29: "张 zhang1, trương, counts flat objects; a sheet of paper is a clear beginner example.",
        30: "只 zhi1, chích, is the animal/one-of-a-pair classifier; a small bird is correctly counted. Distinct from adverb 只 zhi3.",
        31: "条 tiao2, điều, counts elongated items including trousers; suitable-fit sentence and Vietnamese align.",
        32: "双 shuang1, song, counts a pair; new-pair-of-shoes example and Vietnamese match.",
        33: "次 ci4, thứ, counts occurrences; 第一次来中国 means first time visiting, with ordinal 一 retaining yī.",
        34: "下次 xia4 ci4 means next time; future shared-meal invitation and Vietnamese align.",
        35: "上次 shang4 ci4 means last time; past Beijing visit and Vietnamese match.",
        36: "去年 qu4 nian2, khứ niên, means last year; past-trip example is accurate.",
        37: "明年 ming2 nian2, minh niên, means next year; study-abroad intention and Vietnamese are aligned.",
        38: "早上 zao3 shang5, tảo thượng, means early morning; six-o'clock waking example is appropriate.",
        39: "过去 is supplied as guo4 qu5 but labeled the past noun; example uses full qù for past and neutral qu for passing away. Hold for citation/neutral and sense-identity reconciliation rather than silently renaming its key.",
        40: "小时 xiao3 shi2, tiểu thời, means hour/duration; two-hour study example and Vietnamese align.",
        41: "已经 yi3 jing1, dĩ kinh, marks already; return-home example and đã...rồi translation match.",
        42: "正在 zheng4 zai4 marks an action in progress; dinner sentence and Vietnamese đang agree.",
        43: "马上 ma3 shang4 means immediately here, not literally on a horse; coming-right-away example supports that sense.",
        44: "一直 yìzhí is a real contextual pronunciation in teaching materials, but the catalog's citation-vs-sandhi identity policy is inconsistent with yi1 elsewhere. Preserve key and hold this policy uncertainty; clarify the uninterrupted-action Vietnamese example.",
        45: "常常 chang2 chang2, thường thường, means often; habitual bookshop visits and Vietnamese match.",
        46: "再 zai4, tái, means again for a subsequent action; repetition request is natural and does not conflate 已经发生的又.",
        47: "就 jiu4, tựu, can mean then/immediately; conditional telling-after-thinking sentence and Vietnamese are appropriate.",
        48: "别 bie2, biệt, is the prohibitive don't; smoking injunction and Vietnamese are accurate.",
        49: "真 zhen1, chân, intensifies an evaluation; nice-weather example and Vietnamese thật are aligned.",
        50: "非常 fei1 chang2 means very/extremely; song-preference sentence is grammatical, with Chinese-song context rather than a claim of a specific song's language provenance.",
    },
    corrections={
        16: {
            "changes": {
                "examples": [
                    {
                        "simplified": "服务员，请结账。",
                        "pinyin": "Fúwùyuán, qǐng jiézhàng.",
                        "vietnamese": "Anh/chị phục vụ ơi, cho tôi thanh toán.",
                    }
                ]
            },
            "reason": "Use a natural Vietnamese address and bill request rather than the literal vocative Phục vụ viên.",
        },
        24: {
            "changes": {
                "examples": [
                    {
                        "simplified": "他买了一辆黑色的车。",
                        "pinyin": "Tā mǎi le yí liàng hēisè de chē.",
                        "vietnamese": "Anh ấy đã mua một chiếc xe màu đen.",
                    }
                ]
            },
            "reason": "Disambiguate literal black from the lexicalized illegal-taxi meaning of 黑车, preserving the intended color lesson.",
        },
        27: {
            "changes": {
                "examples": [
                    {
                        "simplified": "香蕉是黄的。",
                        "pinyin": "Xiāngjiāo shì huáng de.",
                        "vietnamese": "Quả chuối có màu vàng.",
                    }
                ]
            },
            "reason": "Fix nonsensical Vietnamese typo Quối chuối; Chinese and pronunciation remain unchanged.",
        },
        44: {
            "changes": {
                "vietnamese_meanings": ["suốt", "liên tục", "luôn luôn", "thẳng"],
                "examples": [
                    {
                        "simplified": "他一直在看书。",
                        "pinyin": "Tā yìzhí zài kàn shū.",
                        "vietnamese": "Anh ấy vẫn đang đọc sách suốt từ nãy đến giờ.",
                    }
                ],
            },
            "reason": "Clarify uninterrupted ongoing action and natural Vietnamese while retaining all valid original senses; phonological identity policy remains pending.",
        },
    },
    pending={
        39: {
            "linguistic_uncertainty": True,
            "reason": "Neutral qu5 lexical identity vs full-tone past-noun reading and mixed-sense example need resolution without changing an imported lexical key.",
        },
        44: {
            "linguistic_uncertainty": True,
            "reason": "Contextual yi4 is attested, but citation identity policy and yi1/yi4 distinction need explicit reconciliation; do not rename automatically.",
        },
    },
    sources=[
        "https://www.cheng-tsui.com/sites/default/files/gfc_3_tb_fm-l1.pdf",
        "https://www.ncdc.go.ug/wp-content/uploads/2024/02/CHINESE_SYLLABUS_compressed.pdf",
    ],
)

save(
    "L2-B003",
    {
        1: "因为 yin1 wei4, nhân vi, introduces a cause; paired 所以 sentence and Vietnamese vì...nên are correct.",
        2: "所以 suo3 yi3, sở dĩ, is therefore/so in Chinese; provided Vietnamese cho nên avoids the different modern Vietnamese use of sở dĩ.",
        3: "但是 dan4 shi4, đãn thị, means but; wish-versus-time contrast and Vietnamese match.",
        4: "虽然 sui1 ran2, tuy nhiên, means although in Chinese; provided mặc dù correctly avoids translating it as Vietnamese however.",
        5: "如果 ru2 guo3, như quả, means if; conditional rain sentence and Vietnamese agree, with contextual bú qù.",
        6: "左边 zuo3 bian5, tả biên, is left; bank-left-of-supermarket relation is accurate.",
        7: "右边 you4 bian5, hữu biên, is right; bookshop-right-of-school relation and Vietnamese match.",
        8: "旁边 pang2 bian5 is beside; changed example's full biān to selected neutral bian. Subject-neighbor relation and Vietnamese remain correct.",
        9: "外面 wai4 mian5 is outside; aligned example's mian with the selected neutral reading. Cold-outside invitation and Vietnamese are valid.",
        10: "中间 zhong1 jian1, trung gian, means middle/between; position between two people and Vietnamese agree.",
        11: "往 wang3, vãng, is toward; forward-direction instruction and Vietnamese are natural, with contextual 一直 yìzhí.",
        12: "向 xiang4, hướng, is toward/to; right-turn direction and Vietnamese are correct.",
        13: "离 li2, ly, measures distance from; house-near-company example matches Vietnamese cách.",
        14: "从 cong2, tùng, denotes from; coming-from-Vietnam sentence and Vietnamese align.",
        15: "比 bi3, tỷ, is comparative than in this entry, not the infinitive to compare. Corrected English gloss; brother-height comparison and Vietnamese remain correct.",
        16: "关 guan1, quan, means close/turn off; leaving-home light-switch instruction and Vietnamese match.",
        17: "洗澡 xi3 zao3, tẩy tảo, is bathe/shower; going-to-bathe-first sentence is natural.",
        18: "洗手间 xi3 shou3 jian1 means restroom; a polite synonym of 厕所, not a duplicate lexical identity to merge. Location question is aligned.",
        19: "刷牙 shua1 ya2, loát nha, is brush teeth; after-waking instruction and Vietnamese agree.",
        20: "起床 qi3 chuang2, khởi sàng, is get up; seven-every-morning example and Vietnamese are correct.",
        21: "散步 san4 bu4, tản bộ, is stroll/walk; park-after-dinner example is natural.",
        22: "累 lei4 means tired. Luy/lụy are attested Sino-Vietnamese variants rather than an automatic typo; work-all-day fatigue and Vietnamese are aligned.",
        23: "饱 bao3, bão, is satiated/full; 吃饱了 and ăn no rồi are equivalent.",
        24: "饿 e4, ngạ, is hungry; afternoon-walking example and idiomatic đói meo are aligned.",
        25: "渴 ke3, khát, means thirsty; drink-water suggestion and Vietnamese are natural.",
        26: "干净 gan1 jing4, can tịnh, means clean; cleaned-room result complement and Vietnamese match.",
        27: "脏 zang1, tang, means dirty, distinguished from zang4 internal-organ reading; laundry sentence and Vietnamese are accurate.",
        28: "忙 mang2, mang, means busy; recent-workload example and Vietnamese agree.",
        29: "容易 rong2 yi4, dung dịch, means easy; Vietnamese dễ is correct and the reading aid must not be used as the modern Vietnamese chemical-solution meaning.",
        30: "难 nan2, nan, means difficult; question-hard-to-answer sentence and Vietnamese align.",
        31: "正确 zheng4 que4, chính xác, means correct; answer-evaluation sentence and Vietnamese match.",
        32: "清楚 qing1 chu5 means clear/understand clearly; writing-legibly instruction supports the selected sense.",
        33: "甜 tian2, điềm, means sweet; watermelon taste and Vietnamese are accurate.",
        34: "咸 xian2, hàm, means salty; dish-a-little-salty example and Vietnamese align.",
        35: "辣 la4, lạt, means spicy; Sichuan-cuisine example and Vietnamese cay are correct despite the misleading modern Vietnamese homophone lạt.",
        36: "酸 suan1, toan, means sour; apple taste and Vietnamese are aligned.",
        37: "汤 tang1, thang, means soup/broth; a hot bowl and Vietnamese canh/súp are appropriate.",
        38: "菜单 cai4 dan1, thái đơn, means menu; request to server and Vietnamese thực đơn match.",
        39: "筷子 kuai4 zi5, khoái tử, is chopsticks; customary utensil-use sentence and Vietnamese align.",
        40: "勺子 shao2 zi5, chước tử, is spoon; 一把勺子 is an acceptable classifier construction.",
        41: "碗 wan3, oản, is bowl; a bowl of noodles and Vietnamese quantity match.",
        42: "果汁 guo3 zhi1, quả trấp, is fruit juice; apple-juice question and Vietnamese are aligned.",
        43: "啤酒 pi2 jiu3 means beer. Ty tửu is an attested variant of bì/ti tửu, not a reason to invent a replacement reading; negative drinking sentence is valid.",
        44: "蛋糕 dan4 gao1, đản cao, is cake; birthday example and Vietnamese bánh kem are appropriate.",
        45: "糖 tang2, đường, includes sugar/candy; coffee example selects sugar correctly.",
        46: "包子 bao1 zi5, bao tử, is stuffed steamed bun; gloss bánh bao avoids confusing the character reading with Vietnamese stomach.",
        47: "饺子 jiao3 zi5, giảo tử, is dumpling; northern New-Year custom example is natural in the Chinese context.",
        48: "面条 mian4 tiao2, miến điều, is noodles; lunch beef-noodle example and Vietnamese align.",
        49: "问题 wen4 ti2, vấn đề, includes question/problem; asking a teacher about an unclear issue is appropriate.",
        50: "事情 shi4 qing5, sự tình, is matter/affair; many-things-to-do sentence and Vietnamese match.",
    },
    corrections={
        8: {
            "changes": {
                "examples": [
                    {
                        "simplified": "他就坐在我旁边。",
                        "pinyin": "Tā jiù zuò zài wǒ pángbian.",
                        "vietnamese": "Anh ấy ngồi ngay bên cạnh tôi.",
                    }
                ]
            },
            "reason": "Use the lexical record's selected neutral bian5 consistently in the example; full-tone variation is not rejected as universally invalid.",
        },
        9: {
            "changes": {
                "examples": [
                    {
                        "simplified": "外面很冷，快进来吧。",
                        "pinyin": "Wàimian hěn lěng, kuài jìnlái ba.",
                        "vietnamese": "Bên ngoài rất lạnh, mau vào trong đi.",
                    }
                ]
            },
            "reason": "Align example with selected neutral mian5; retain the valid Chinese sentence and translation.",
        },
        15: {
            "changes": {"english_meanings": ["than", "compared with"]},
            "reason": "Prepositional comparative 比 is than/compared with in this scoped entry, not infinitival to compare.",
        },
    },
    sources=[
        "https://hvdic.thivien.net/hv/b%C3%AC%20t%E1%BB%ADu",
        "https://res.vnjp.org/kanji/han-viet/LUY",
        "https://dictionary.zim.vn/trung-viet/%E7%B4%AF",
    ],
)

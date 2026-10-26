"""Explicit Level 3 batch 6 notes, including genuine errors and unresolved identities."""

from checkpoint import save

save(
    "L3-B006",
    {
        1: "意思 yi4 si5, ý tứ, is meaning/idea; neutral si and word-meaning question are aligned.",
        2: "意见 yi4 jian4 means opinion and, in 有意见, objection/disagreement; decision-comment question and Vietnamese match.",
        3: "办法 ban4 fa3, biện pháp, is method/way; good-solution question and Vietnamese are accurate.",
        4: "机会 ji1 hui4, cơ hội, means opportunity; learning-opportunity example and Vietnamese agree.",
        5: "水平 shui3 ping2 means level/standard; corrected Vietnamese typo mực độ to mức độ. Language-level improvement example is valid.",
        6: "成绩 cheng2 ji4, thành tích, is results/grades; excellent-exam-results example and Vietnamese match.",
        7: "经验 jing1 yan4, kinh nghiệm, is experience; teaching-experience sentence and Vietnamese are aligned.",
        8: "要求 yao1 qiu2, yêu cầu, is requirement here, with yāo not yào; strict-requirement sentence and Vietnamese agree.",
        9: "关系 guan1 xi5, quan hệ, is relationship; neutral xi and collegial-relations sentence are correct.",
        10: "新闻 xin1 wen2, tân văn, is news; grandfather's seven-o'clock viewing habit and Vietnamese align.",
        11: "故事 gu4 shi5, cố sự, is story; neutral shi and bedtime-story sentence are natural.",
        12: "历史 li4 shi3, lịch sử, is history; university-history interest example and Vietnamese match.",
        13: "文化 wen2 hua4, văn hóa, is culture; traditional-culture experience example is aligned.",
        14: "节目 jie2 mu4, tiết mục, is program/show; evening TV-show sentence and Vietnamese are understandable and valid.",
        15: "比赛 bi3 sai4, tỷ tái, is competition/match; football-match sentence and Vietnamese agree.",
        16: "音乐 yin1 yue4, âm nhạc, is music; yuè is correct rather than lè, and light-music example aligns.",
        17: "声音 sheng1 yin1, thanh âm, is sound/voice; clear pleasant teacher's voice and Vietnamese match.",
        18: "词典 ci2 dian3, từ điển, is dictionary; frequent-lookup language-learning sentence is aligned.",
        19: "句子 ju4 zi5, cú tử, is sentence; neutral zi and sentence-construction instruction are correct.",
        20: "段落 duan4 luo4, đoạn lạc, is paragraph; made the ordinal construction explicit with 第一个段落, retaining the target compound and matching Vietnamese.",
        21: "信誉 xin4 yu4, tín dự, is reputation/credit standing; established-shop example and Vietnamese uy tín are aligned.",
        22: "作用 zuo4 yong4, tác dụng, is effect/function; regular-exercise example and Vietnamese match as language content.",
        23: "原因 yuan2 yin1, nguyên nhân, is cause/reason; accident-investigation sentence and Vietnamese align.",
        24: "结果 jie2 guo3, kết quả, is result, distinct from fruit-bearing jiēguǒ; revision/exam example is appropriate.",
        25: "目的 mu4 di4, mục đích, is purpose; dì is correct, not de particle, and study-medicine purpose sentence aligns.",
        26: "重点 zhong4 dian3, trọng điểm, is key point; revision-focus instruction and Vietnamese match.",
        27: "特点 te4 dian3, đặc điểm, is characteristic; building's old-fashioned style example and Vietnamese agree.",
        28: "优点 you1 dian3, ưu điểm, is strength/merit; everyone's-strengths sentence and Vietnamese align.",
        29: "缺点 que1 dian3, khuyết điểm, is weakness/flaw; improvement instruction and Vietnamese are correct.",
        30: "方式 fang1 shi4, phương thức, is way/method; reading as a knowledge-acquisition method and Vietnamese match.",
        31: "其实 qi2 shi2, kỳ thực, means actually; question-not-as-hard-as-imagined example and Vietnamese align.",
        32: "尤其 you2 qi2 means especially; corrected Sino-Vietnamese ưu kỳ to vưu kỳ, since 尤 is vưu, not 優 ưu.",
        33: "几乎 ji1 hu1 means almost; original ki ha is erroneous. Corrected to attested Sino-Vietnamese cơ hồ; emotional-speech example remains valid.",
        34: "一共 yi2 gong4 is normal spoken yígòng but needs catalog citation-vs-sandhi identity reconciliation. Corrected currency translation without renaming its key; hold remains.",
        35: "互相 hu4 xiang1, hỗ tương, means mutually; classmates' mutual-support sentence and Vietnamese agree.",
        36: "经常 jing1 chang2, kinh thường, means often/regularly; after-dinner neighborhood walking and Vietnamese align.",
        37: "突然 tu1 ran2, đột nhiên, means suddenly; abrupt rain and Vietnamese are aligned. hǎohāo is an attested colloquial 好好 realization.",
        38: "偶尔 ou3 er3, ngẫu nhĩ, means occasionally; apostrophe in ǒu'ěr is correct and fishing example aligns.",
        39: "先 xian1, tiên, means first/before; first grocery stop after work and Vietnamese agree.",
        40: "终于 zhong1 yu2, chung vu, means finally; passing-after-long-effort example and Vietnamese match.",
        41: "另外 ling4 wai4, lệnh ngoại, means besides/in addition; extra-pen purchase example and Vietnamese are natural.",
        42: "或者 huo4 zhe3, hoặc giả, is or; book-reading/music alternatives are aligned.",
        43: "不但 bu2 dan4 is normal contextual búdàn, but its lexical key encodes sandhi contrary to citation treatment elsewhere. Preserve key and hold pending explicit policy, not automatic renaming.",
        44: "而且 er2 qie3, nhi thả, links an additional positive property; taste-and-price restaurant example and Vietnamese match.",
        45: "只要 zhi3 yao4 is as long as; corrected translation of 大幅 from very quickly to considerably, preserving the conditional practice example.",
        46: "只有 zhi3 you3 is only if in the supplied 只有...才 construction; dream-achievement condition and Vietnamese agree.",
        47: "为了 wei4 le5 introduces purpose; neutral le and physical-fitness motivation example are aligned.",
        48: "除了 chu2 le5 means except/besides; Sunday exception and Vietnamese ngoại trừ match.",
        49: "根据 gen1 ju4 means according to/based on; medical-result example and Vietnamese are aligned illustrative language rather than medical instructions.",
        50: "关于 guan1 yu2 is about/regarding; event-organization discussion sentence and Vietnamese match, with correct apostrophe in fāng'àn.",
    },
    corrections={
        5: {
            "changes": {"vietnamese_meanings": ["trình độ", "mức độ"]},
            "reason": "Fix Vietnamese spelling mực độ to mức độ, preserving the level/standard sense.",
        },
        20: {
            "changes": {
                "examples": [
                    {
                        "simplified": "请朗读课文的第一个段落。",
                        "pinyin": "Qǐng lǎngdú kèwén de dì-yī ge duànluò.",
                        "vietnamese": "Xin hãy đọc to đoạn văn đầu tiên của bài học.",
                    }
                ]
            },
            "reason": "Use an explicit, natural ordinal classifier construction for the compound paragraph noun.",
        },
        32: {
            "changes": {"sino_vietnamese": "vưu kỳ"},
            "reason": "Correct 尤 vưu versus 優 ưu; 尤其 is not written 优其.",
        },
        33: {
            "changes": {"sino_vietnamese": "cơ hồ"},
            "reason": "Replace ki ha with documented Sino-Vietnamese 幾乎/几乎 cơ hồ; lexical meaning and pronunciation stay unchanged.",
        },
        34: {
            "changes": {
                "examples": [
                    {
                        "simplified": "这些书买下来一共需要一百块钱。",
                        "pinyin": "Zhèxiē shū mǎi xiàlai yígòng xūyào yì bǎi kuài qián.",
                        "vietnamese": "Mua hết chỗ sách này tổng cộng cần một trăm tệ.",
                    }
                ]
            },
            "reason": "Chinese price unit is yuan, not Vietnamese đồng; citation/sandhi identity policy remains pending.",
        },
        45: {
            "changes": {
                "examples": [
                    {
                        "simplified": "只要坚持练习，口语就能大幅提升。",
                        "pinyin": "Zhǐyào jiānchí liànxí, kǒuyǔ jiù néng dàfú tíshēng.",
                        "vietnamese": "Chỉ cần kiên trì luyện tập, kỹ năng nói sẽ được cải thiện đáng kể.",
                    }
                ]
            },
            "reason": "大幅 expresses substantial degree, not necessarily speed; align the Vietnamese translation accordingly.",
        },
    },
    pending={
        34: {
            "linguistic_uncertainty": True,
            "reason": "Need an explicit yi1 citation vs yi2 spoken-sandhi lexical identity policy for 一共.",
        },
        43: {
            "linguistic_uncertainty": True,
            "reason": "Need an explicit bu4 citation vs bu2 contextual-sandhi lexical identity policy for 不但.",
        },
    },
    sources=[
        "https://hvdic.thivien.net/py/t/ji1",
        "https://en.wiktionary.org/wiki/%E5%B9%BE%E4%B9%8E",
    ],
)

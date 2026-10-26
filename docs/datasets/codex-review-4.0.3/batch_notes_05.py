"""Explicit Level 3 batch 1 notes after reading all records and examples."""

from checkpoint import save

save(
    "L3-B001",
    {
        1: "打算 da3 suan4 means plan/intend. Weak suan is also possible in speech; aligned example to this record's selected full-tone suan4.",
        2: "决定 jue2 ding4, quyết định, means decide; completed study-abroad decision and Vietnamese align.",
        3: "解决 jie3 jue2, giải quyết, is solve/resolve; difficult-problem sentence and Vietnamese are natural.",
        4: "选择 xuan3 ze2, tuyển trạch, is choose/select; choosing a major carefully and Vietnamese match.",
        5: "同意 tong2 yi4 means agree; collective agreement with an idea is correctly expressed and translated.",
        6: "习惯 xi2 guan4 has verb be used to and noun habit senses; added noun POS to preserve the provided thói quen sense.",
        7: "愿意 yuan4 yi4 means willing; helping-someone-with-a-favor example and Vietnamese align.",
        8: "照顾 zhao4 gu5, chiếu cố, is look after; neutral gu and child-care example are accurate.",
        9: "相信 xiang1 xin4, tương tín, is believe/trust; ability reassurance and Vietnamese match.",
        10: "发现 fa1 xian4 means discover; wallet-missing sentence and Vietnamese are aligned, with contextual bú before jiàn.",
        11: "记得 ji4 de5, ký đắc, is remember; neutral de and remembering-a-name question are correct.",
        12: "忘记 wang4 ji4, vong ký, means forget; forgetting to bring a phone and Vietnamese match.",
        13: "影响 ying3 xiang3, ảnh hưởng, means influence/affect; late-night-habit example and Vietnamese are aligned.",
        14: "比较 bi3 jiao4 is compare as verb or relatively as adverb; added adverb POS for the supplied sense and actual cold-weather example. Tỷ giác is an attested reading aid.",
        15: "提高 ti2 gao1, đề cao, means raise/improve; language-level improvement and Vietnamese are correct.",
        16: "迟到 chi2 dao4 means arrive late; morning tardiness example and Vietnamese are understandable and valid.",
        17: "搬 ban1 means move/carry; next-month moving-home sentence and Vietnamese align.",
        18: "换 huan4, hoán, means change/exchange; currency-exchange example is natural and accurately translated.",
        19: "带 dai4, đới, includes bring/carry/lead; umbrella reminder and Vietnamese match.",
        20: "拿 na2, nã, means take/hold; holding a bag briefly and Vietnamese align.",
        21: "放 fang4, phóng, means put/place/release; book-on-table placement sentence is grammatical.",
        22: "留 liu2, lưu, means stay/retain; staying in China for work and Vietnamese are correct.",
        23: "碰 peng4 means bump/touch/encounter. Corrected unattested bành to documented Sino-Vietnamese bính; accidental meeting example and meanings remain.",
        24: "掉 diao4, điệu, means fall/drop; keys-on-ground example and Vietnamese align.",
        25: "挂 gua4, quải, includes hang and hang up a phone; wall-map example correctly uses hang.",
        26: "贴 tie1, thiếp, means stick/paste; red-paper-on-door example and Vietnamese agree.",
        27: "抽 chou1, trừu, covers draw out and smoke; cigarette-smoking example selects the listed sense correctly.",
        28: "算 suan4, toán, includes calculate/count and consider/reckon. Added consider sense because 算完 in the existing example is not arithmetic.",
        29: "查 cha2, tra, means check/look up; dictionary lookup request and Vietnamese align.",
        30: "画 hua4, họa, is draw/paint; 画画儿 has correct erhua in the object noun, with a natural preference sentence.",
        31: "爬 pa2, ba, is climb/crawl; weekend mountain-climbing invitation is natural.",
        32: "讲 jiang3, giảng, is speak/explain/teach; giving a lesson to students and Vietnamese align.",
        33: "聊 liao2, liêu, means chat; online-chatting example and Vietnamese match.",
        34: "接 jie1, tiếp, covers receive/pick up; airport collection of a friend is a valid example.",
        35: "寄 ji4, ký, is mail/send; letter-home sentence, letter classifier and Vietnamese are appropriate.",
        36: "检查 jian3 cha2, kiểm tra, is inspect/check; medical body-check example is naturally translated khám sức khỏe.",
        37: "练习 lian4 xi2 is practice or an exercise; added noun POS for the existing bài tập meaning, without removing the valid practice example.",
        38: "遇到 yu4 dao4, ngộ đáo, is encounter; difficulty-reassurance sentence and contextual bú yào are correct.",
        39: "出现 chu1 xian4 means appear; computer-screen error sentence and Vietnamese align.",
        40: "变化 bian4 hua4 is change as verb/noun; actual sentence 这座城市的变化 uses a noun. Added noun POS and explicit nominal gloss.",
        41: "完成 wan2 cheng2 means complete/finish; task-completion sentence and Vietnamese are accurate.",
        42: "了解 liao3 jie3, liễu giải, means understand/get to know; liǎo reading is correct, not le particle; culture example aligns.",
        43: "关心 guan1 xin1, quan tâm, is care/be concerned; parents and children's lives example is accurate.",
        44: "放心 fang4 xin1 means be reassured; self-care promise and Vietnamese yên tâm are natural.",
        45: "担心 dan1 xin1 means worry; original example Pinyin omitted 很. Restored hěn so every Chinese word is represented.",
        46: "敢 gan3, cảm, means dare; fear of walking alone at night and Vietnamese match.",
        47: "生发 sheng1 fa1 conflates sprouting/arising with hair-growing, which calls for the fa4 hair reading. Retain identity and both valid meanings pending pronunciation-specific sense separation; do not silently delete hair or add an unreviewed key.",
        48: "结束 jie2 shu4, kết thúc, is end/finish; film ends at ten and Vietnamese agree.",
        49: "祝 zhu4, chúc, expresses good wishes; birthday greeting is idiomatic and correctly translated.",
        50: "难过 nan2 guo4 means sad/distressed; bad-news reaction and Vietnamese are aligned.",
    },
    corrections={
        1: {
            "changes": {
                "examples": [
                    {
                        "simplified": "明天你打算做什么？",
                        "pinyin": "Míngtiān nǐ dǎsuàn zuò shénme?",
                        "vietnamese": "Ngày mai bạn dự định làm gì?",
                    }
                ]
            },
            "reason": "Align example with selected full-tone suan4 while acknowledging weak-syllable usage elsewhere.",
        },
        6: {
            "changes": {"part_of_speech": "verb; noun"},
            "reason": "Preserve both accustomed-to verb and habit noun senses already present.",
        },
        14: {
            "changes": {"part_of_speech": "verb; adverb"},
            "reason": "Existing example and relatively sense require adverb POS in addition to compare verb.",
        },
        23: {
            "changes": {"sino_vietnamese": "bính"},
            "reason": "Hán Nôm reference lists binh, bánh, bính for 碰; bành is not the supplied character's documented reading.",
        },
        28: {
            "changes": {
                "vietnamese_meanings": ["tính", "tính toán", "coi là", "xem là"],
                "english_meanings": ["to calculate", "to count", "to consider", "to reckon"],
            },
            "reason": "Existing example means consider the matter finished; add this genuine sense rather than labeling the sentence arithmetic.",
        },
        37: {
            "changes": {"part_of_speech": "verb; noun"},
            "reason": "Verb practice and noun exercise are both already present in the meanings.",
        },
        40: {
            "changes": {
                "part_of_speech": "verb; noun",
                "vietnamese_meanings": ["thay đổi", "biến đổi", "sự thay đổi"],
            },
            "reason": "The existing example's possessive nominal construction requires noun coverage alongside the verb.",
        },
        45: {
            "changes": {
                "examples": [
                    {
                        "simplified": "别担心，事情很快会好起来的。",
                        "pinyin": "Bié dānxīn, shìqing hěn kuài huì hǎo qǐlai de.",
                        "vietnamese": "Đừng lo lắng, mọi chuyện sẽ sớm tốt lên thôi.",
                    }
                ]
            },
            "reason": "Pinyin omitted 很 from the actual Chinese sentence; add hěn and recheck the full aligned sentence.",
        },
    },
    pending={
        47: {
            "linguistic_uncertainty": True,
            "reason": "Mixed fa1 sprouting vs fa4 hair sense cannot be resolved while silently preserving a single pronunciation key; editorial sense/identity decision required.",
        }
    },
    sources=[
        "https://hvdic.thivien.net/whv/%E7%A2%B0",
        "https://vnjpdict.com/tuvung/%E6%AF%94%E8%BC%83",
    ],
)

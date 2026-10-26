"""Explicit Level 3 batch 4/5 content review; original sources remain unchanged."""

from checkpoint import save

save(
    "L3-B004",
    {
        1: "伞 san3, tản, is umbrella; rain-and-reminder example and Vietnamese align.",
        2: "包 bao1, bao, is bag/package; keys-in-bag example and Vietnamese are correct.",
        3: "钱包 qian2 bao1, tiền bao, means wallet; 落 là is the leave-behind reading, not luò, and taxi example matches.",
        4: "箱子 xiang1 zi5, tương tử, covers box/trunk/suitcase; travel context correctly selects suitcase.",
        5: "行李 xing2 li5, hành lý, means luggage; xíng and neutral li are right, and security-machine instruction aligns.",
        6: "地图 di4 tu2, địa đồ, is map; route-finding suggestion and Vietnamese are accurate.",
        7: "照片 zhao4 pian4, chiếu phiến, is photograph; Great Wall relative-clause example and Vietnamese match.",
        8: "照相机 zhao4 xiang4 ji1 is camera; classifier 台, purchase sentence and Vietnamese are correct. Supplied chiếu tương cơ is a character-reading aid, not the actual Vietnamese definition.",
        9: "信 xin4, tín, is letter/mail in this entry; receiving a friend's letter is aligned.",
        10: "信封 xin4 feng1, tín phong, is envelope; address-writing instruction and Vietnamese match.",
        11: "邮票 you2 piao4, bưu phiếu, is postage stamp; attaching a stamp to an envelope is natural.",
        12: "包裹 bao1 guo3, bao khỏa, is parcel; afternoon pickup and Vietnamese are aligned.",
        13: "瓶子 ping2 zi5, bình tử, means bottle; milk-bottle example and Vietnamese are valid, with generic container rather than a distinct flower-vase teaching target.",
        14: "盒子 he2 zi5, hạp tử, is box/case; putting a small knife in a box and Vietnamese match.",
        15: "镜子 jing4 zi5, kính tử, is mirror; 面 classifier and hanging-on-wall sentence align.",
        16: "钥匙 yao4 shi5 is key. Original 找不到了大门的钥匙 put final 了 before the object and stressed potential 不 incorrectly. Moved 了 to the end and used neutral bu.",
        17: "锁 suo3, tỏa, is lock; checking the door lock before leaving is aligned.",
        18: "灯 deng1, đăng, is light/lamp; dark-room switch-on suggestion and Vietnamese agree.",
        19: "空调 kong1 tiao2, không điều, is air conditioner; cooling-in-summer example and Vietnamese are correct.",
        20: "冰箱 bing1 xiang1, băng tương, is refrigerator; putting milk inside and Vietnamese match.",
        21: "洗衣机 xi3 yi1 ji1, tẩy y cơ, is washing machine; easy-to-use example and Vietnamese align.",
        22: "微波炉 wei1 bo1 lu2, vi ba lô, is microwave; reheating-rice sentence and Vietnamese are correct.",
        23: "电风扇 dian4 feng1 shan4, điện phong phiến, is electric fan; shàn reading and hot-weather instruction align.",
        24: "被子 bei4 zi5, bị tử, means quilt/blanket, not passive 被; thick-cover suggestion and Vietnamese match.",
        25: "床单 chuang2 dan1, sàng đơn, is bedsheet; changing a dirty sheet and Vietnamese align.",
        26: "枕头 zhen3 tou5, chẩm đầu, is pillow. Recast the example to explicitly sleep USING the pillow, avoiding the awkward 枕头睡得 subject/complement construction.",
        27: "毛巾 mao2 jin1, mao cân, is towel; face-drying instruction and Vietnamese are aligned.",
        28: "牙刷 ya2 shua1, nha loát, is toothbrush; monthly-replacement sentence is grammatical illustrative content, not a clinical instruction to the user.",
        29: "牙膏 ya2 gao1, nha cao, is toothpaste; tube classifier 支 and nearly-used-up example are correct.",
        30: "肥皂 fei2 zao4 is soap; corrected Sino-Vietnamese phì táo to phì tạo because 皂 is tạo.",
        31: "梳子 shu1 zi5, sơ tử, is comb; combing hair with it and Vietnamese align.",
        32: "帽子 mao4 zi5, mạo tử, is hat; 戴 rather than 穿 is correct and reminder translation matches.",
        33: "裤子 ku4 zi5, khố tử, is trousers; length-fits sentence, 条 classifier and Vietnamese align.",
        34: "裙子 qun2 zi5, quần tử, means skirt/dress, not Vietnamese trousers; source Vietnamese váy correctly avoids that false friend.",
        35: "鞋 xie2, hài, is shoes; removing shoes before entering and Vietnamese agree.",
        36: "袜子 wa4 zi5 means socks; original ngoạt tử is unsupported. Corrected to miệt tử based on 襪, retaining the warm-socks example.",
        37: "眼镜 yan3 jing4 means spectacles, distinct from 眼睛 yan3 jing5 eyes; newspaper-reading example and Vietnamese align.",
        38: "墨镜 mo4 jing4, mặc kính, means sunglasses; outdoor-summer example and Vietnamese match.",
        39: "雨伞 yu3 san3 specifies rain umbrella; 伞 is a broader related word rather than a duplicate to delete. Reminder sentence is aligned.",
        40: "皮鞋 pi2 xie2, bì hài, is leather shoes; one pair, father's outfit and Vietnamese are correct.",
        41: "衬衫 chen4 shan1, sấn sam, is shirt; white clean shirt sentence and Vietnamese align.",
        42: "外套 wai4 tao4, ngoại sáo, is coat/jacket; cold-weather dressing suggestion and Vietnamese are natural.",
        43: "大衣 da4 yi1, đại y, is overcoat; black winter-overcoat example and Vietnamese match.",
        44: "领带 ling3 dai4, lĩnh đới, is necktie; 系 jì is correct for tying and work-outfit sentence aligns.",
        45: "皮带 pi2 dai4, bì đới, is belt; quality-evaluation sentence and Vietnamese are accurate.",
        46: "手表带 shou3 biao3 dai4 is watch strap, a transparent but valid compound distinct from 手表; wear/age sentence and Vietnamese match.",
        47: "围巾 wei2 jin1, vi cân, is scarf; wearing a scarf for warmth and Vietnamese align.",
        48: "手套 shou3 tao4, thủ sáo, is gloves; wearing them while riding and Vietnamese match.",
        49: "雨衣 yu3 yi1, vũ y, is raincoat; heavy-rain convenience example and Vietnamese are accurate.",
        50: "泳衣 yong3 yi1 means swimsuit; corrected dũng y to vịnh y, consistent with the earlier 泳 correction. Swimming-at-seaside example is valid.",
    },
    corrections={
        16: {
            "changes": {
                "examples": [
                    {
                        "simplified": "我找不到大门的钥匙了。",
                        "pinyin": "Wǒ zhǎobudào dàmén de yàoshi le.",
                        "vietnamese": "Tôi không tìm thấy chìa khóa cổng lớn nữa.",
                    }
                ]
            },
            "reason": "Move sentence-final 了 after the object and render potential-complement 不 as neutral bu; re-read all three aligned fields.",
        },
        26: {
            "changes": {
                "examples": [
                    {
                        "simplified": "用这个枕头睡觉很舒服。",
                        "pinyin": "Yòng zhège zhěntou shuìjiào hěn shūfu.",
                        "vietnamese": "Nằm ngủ với chiếc gối này rất thoải mái.",
                    }
                ]
            },
            "reason": "Make the pillow an explicit instrument rather than the apparent sleeper, using a natural beginner sentence.",
        },
        30: {
            "changes": {"sino_vietnamese": "phì tạo"},
            "reason": "皂 has the documented Sino-Vietnamese reading tạo, not táo.",
        },
        36: {
            "changes": {"sino_vietnamese": "miệt tử"},
            "reason": "襪/袜 has miệt/mạt/vạt readings; ngoạt is not appropriate here. Select documented miệt.",
        },
        50: {
            "changes": {"sino_vietnamese": "vịnh y"},
            "reason": "泳 is vịnh; correct recurring dũng substitution while preserving swimsuit meaning and example.",
        },
    },
    sources=[
        "https://hvdic.thivien.net/whv/%E7%9A%82",
        "https://hvdic.thivien.net/whv/%E8%A5%AA",
        "https://xiehanzi.com/han-tu/%E6%B3%B3/",
    ],
)

save(
    "L3-B005",
    {
        1: "季节 ji4 jie2, quý tiết, is season; four-seasons sentence and Vietnamese agree.",
        2: "春天 chun1 tian1 means spring; 花儿 huār erhua and flower-blooming sentence are aligned.",
        3: "夏天 xia4 tian1 means summer; hot-weather description and Vietnamese match.",
        4: "秋天 qiu1 tian1 means autumn; Beijing autumn description and Vietnamese are valid.",
        5: "冬天 dong1 tian1 means winter; snowy-weather example and Vietnamese align as an illustrative cold-climate context.",
        6: "太阳 tai4 yang2, thái dương, is sun; eastern sunrise sentence and Vietnamese agree.",
        7: "月亮 yue4 liang5, nguyệt lượng, is moon; neutral liang and big-round description match.",
        8: "星星 xing1 xing5, tinh tinh, is stars; neutral second xing and bright-night-sky example align.",
        9: "风 feng1, phong, is wind; strong-wind warning and Vietnamese are correct.",
        10: "雪 xue3, tuyết, is snow; white-ground scene and Vietnamese are aligned.",
        11: "云 yun2, vân, is cloud; 朵 classifier and white-cloud sentence match.",
        12: "空气 kong1 qi4, không khí, is air; fresh-forest-air example and Vietnamese are accurate.",
        13: "环境 huan2 jing4 means environment; hoàn cảnh is a reading aid while môi trường is the correct current Chinese sense. Environmental-protection sentence aligns.",
        14: "草 cao3, thảo, is grass; courtyard-growth sentence uses zhǎng correctly and Vietnamese agrees.",
        15: "树 shu4, thụ, means tree; 棵 classifier and hundred-year history sentence align.",
        16: "花 hua1, hoa, is flower in this noun entry; fragrant-garden example and Vietnamese match.",
        17: "叶子 ye4 zi5, diệp tử, is leaf; neutral zi and autumn color change are accurate.",
        18: "河 he2, hà, is river; clear-water sentence and Vietnamese align.",
        19: "湖 hu2, hồ, is lake; lakeside walking sentence and Vietnamese match.",
        20: "海 hai3, hải, is sea; seaside-landscape example and Vietnamese are correct.",
        21: "山 shan1, sơn, is mountain; snow-covered peak scene and Vietnamese align. 终年 is zhōngnián in this context.",
        22: "森林 sen1 lin2, sâm lâm, is forest; animal-habitat example and Vietnamese match.",
        23: "动物 dong4 wu4, động vật, is animal; caring-for-small-animals example is aligned.",
        24: "鸟 niao3, điểu, is bird; singing-in-branches scene and Vietnamese hót are natural.",
        25: "马 ma3, mã, is horse; 匹 classifier and grassland example match.",
        26: "牛 niu2, ngưu, covers cattle and in wider compounds buffalo; cattle-herding example and Vietnamese bò are correct.",
        27: "羊 yang2, dương, covers sheep/goats; 绵羊 in the example selects sheep explicitly and Vietnamese cừu matches.",
        28: "熊猫 xiong2 mao1, hùng miêu, is giant panda; national-treasure statement and Vietnamese are aligned.",
        29: "气候 qi4 hou4, khí hậu, is climate; pleasant-climate example and Vietnamese are correct.",
        30: "自然 zi4 ran2 has nature noun and natural adjective senses already present; added adjective POS, preserving the nature example.",
        31: "温度 wen1 du4, ôn độ, means temperature; pool-temperature sentence is grammatical. Replaced awkward Vietnamese vừa vặn with vừa phải.",
        32: "气温 qi4 wen1, khí ôn, specifies air temperature, distinct from generic 温度; forecast example and Vietnamese match.",
        33: "度 du4, độ, is degree for temperature/angle; thirty-degree air-temperature sentence is aligned.",
        34: "米 mi3, mễ, is meter in this measure entry, distinct from rice sense; hundred-meter field example and Vietnamese match.",
        35: "千克 qian1 ke4, thiên khắc, is kilogram; two-kilogram apple-weighing request and Vietnamese are correct.",
        36: "斤 jin1 is the Mainland 500-g catty, not a Vietnamese kilogram. Kept the explicit unit definition and clarified the example's 500 g and yuan price.",
        37: "克 ke4, khắc, is gram; hundred-gram tea package and Vietnamese align.",
        38: "公里 gong1 li3, công lý, is kilometer; correct Vietnamese cây số avoids the reading-aid false friend justice.",
        39: "段 duan4, đoạn, counts sections; hard-to-walk road section and Vietnamese are aligned.",
        40: "层 ceng2, tầng, counts floors/layers; third-floor location and Vietnamese match.",
        41: "页 ye4, diệp, counts pages; tenth-page instruction and Vietnamese are correct.",
        42: "套 tao4, sáo, counts sets/suites; a new suit example and Vietnamese bộ are aligned.",
        43: "位 wei4, vị, politely counts people; identity question and courteous Vietnamese are natural.",
        44: "把 ba3, bả, counts handled objects including chairs; one-chair example and Vietnamese match, without conflating 把 disposal construction.",
        45: "头 tou2, đầu, counts large livestock; aligned the example's weak tou with this record's selected full-tone tóu.",
        46: "匹 pi3, thất, counts horses/cloth bolts; fine-horse-running example and Vietnamese are correct.",
        47: "棵 ke1 counts trees; corrected khóa to documented Sino-Vietnamese khỏa. Two peach trees and Vietnamese align.",
        48: "辆 liang4, lượng, counts vehicles; one-new-car example and Vietnamese match.",
        49: "封 feng1, phong, counts letters; received-letter example and Vietnamese are aligned.",
        50: "场 chang3 for events is mixed with rain-spell sense normally taught as chang2. Keep the lexical key and valid meanings, but hold for pronunciation-specific sense reconciliation instead of silently changing the key.",
    },
    corrections={
        30: {
            "changes": {"part_of_speech": "noun; adjective"},
            "reason": "Preserve both nature noun and natural adjective senses already represented in meanings.",
        },
        31: {
            "changes": {
                "examples": [
                    {
                        "simplified": "今天水池的温度刚刚好。",
                        "pinyin": "Jīntiān shuǐchí de wēndù gānggāng hǎo.",
                        "vietnamese": "Hôm nay nhiệt độ nước trong hồ vừa phải.",
                    }
                ]
            },
            "reason": "Use natural Vietnamese for a suitable water temperature rather than clothing-fit word vừa vặn.",
        },
        36: {
            "changes": {
                "examples": [
                    {
                        "simplified": "这斤香蕉五块钱。",
                        "pinyin": "Zhè jīn xiāngjiāo wǔ kuài qián.",
                        "vietnamese": "500 gam chuối này giá năm tệ.",
                    }
                ]
            },
            "reason": "Make Mainland jin=500 g explicit and avoid confusing Chinese yuan with Vietnamese đồng in the price.",
        },
        45: {
            "changes": {
                "examples": [
                    {
                        "simplified": "农场里养着二十头牛。",
                        "pinyin": "Nóngchǎng lǐ yǎng zhe èrshí tóu niú.",
                        "vietnamese": "Trong trang trại nuôi hai mươi con bò.",
                    }
                ]
            },
            "reason": "Align the classifier example with the selected full-tone tou2 lexical record.",
        },
        47: {
            "changes": {"sino_vietnamese": "khỏa"},
            "reason": "棵 is documented as khoả/khoã, normalized here to khỏa, not khóa.",
        },
    },
    pending={
        50: {
            "linguistic_uncertainty": True,
            "reason": "Record chang3 event senses and rain example need explicit chang2/chang3 lexical-sense decision; no silent key rewrite or sense removal.",
        }
    },
    sources=[
        "https://hvdic.thivien.net/whv/%E6%A3%B5",
        "https://www.buli.page/view/zidian/entry/b7674f31-9b0c-45c5-860d-02609e056d56/",
    ],
)

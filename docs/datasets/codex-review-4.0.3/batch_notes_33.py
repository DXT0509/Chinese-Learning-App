"""L5-B013 actual review and corrected-result recheck."""
from record_batch import record, rows
r=rows("L5-B013")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B013", """
猛烈 měngliè fierce; typhoon wind/waves aligned.
弥补 míbǔ remedy; separate 弥补短板 from 填补空白 collocation.
密谋 mìmóu plot; 机关 jīguān not jīgī.
勉励 miǎnlì encourage; senior scientist addressing young researchers natural.
勉强 miǎnqiǎng forced/barely; source adjective example requires expanded POS and glosses.
面貌 miànmào appearance; renewed rural environment aligned.
苗头 miáotou early sign; spotting safety problems aligned.
名副其实 míngfùqíshí true to name; smart farm example appropriate.
明朗 mínglǎng clear/bright; technology-zone prospects aligned.
命题 mìngtí proposition/problem; environmental development question aligned.
摸索 mōsuǒ explore; weak suo example variant valid, welding technique research aligned.
模仿 mófǎng imitate; artist developing own style natural.
模式 móshì pattern/model; clean energy/desert restoration integrated approach aligned.
摩擦力 mócālì frictional force; brake example coherent.
墨守成规 mòshǒuchéngguī cling to convention; innovation contrast appropriate.
谋求 móuqiú seek; peaceful shared prosperity example aligned.
母语 mǔyǔ mother tongue; source mastery activity wrongly called communication tool, repair subject.
沐浴 mùyù bathe; mountain sunlight metaphor correct but 整座崇山峻岭 awkward, repair.
目睹 mùdǔ witness; national achievements example aligned.
目光 mùguāng gaze/outlook; remove repeated 战略 absent from transcription.
纳米 nàmǐ nanometer; 薄膜 bómó in formal scientific term.
难堪 nánkān embarrassed; 赤 chì not cì in 面红耳赤.
难能可贵 nánnéngkěguì difficult and commendable; traditional quality craft example aligned.
逆境 nìjìng adversity; resilience idioms coherent.
年度 niándù year/reporting period; annual bulletin usage correct.
念头 niàntou thought; source 从未动摇过念头 contradicts intended never contemplated giving up, repair.
凝聚力 níngjùlì cohesion; team activities building cohesion aligned.
凝固 nínggù solidify; diesel inside pipe solidifies, pipe itself does not, repair.
拧 nǐng screw tight; valve bolt tightening supports third-tone identity.
农林牧渔 nónglínmùyú four industries; remove malformed deepwater agriculture list, 流域 liúyù corrected.
奴隶 núlì slave; historical social system example aligned.
虐待 nüèdài abuse; vulnerable people example linguistically coherent.
挪用 nuóyòng misappropriate; relief resources example aligned.
诺言 nuòyán promise; solemn commitment example correct.
欧亚 Ōuyà Eurasia; rail freight land bridge appropriate.
殴打 ōudǎ assault; 机关 jīguān correct example.
偶像 ǒuxiàng idol; 功勋卓著 zhuózhù not zhuózhe.
排斥 páichì exclude; open academic exchange example correct.
排放量 páifàngliàng emission amount; reduction example aligned.
派生 pàishēng derive; 合规 héguī tone mark on u, repair.
攀登 pāndēng climb; 珠穆朗玛 extra rǎng syllable removed.
盘旋 pánxuán circle; helicopter searching sea natural.
畔 pàn bank/side; wetland lakeshore path correct.
庞大 pángdà enormous; supercomputing node cluster aligned.
抛弃 pāoqì discard; abandoning unpopular practices coherent.
泡沫 pàomò foam/bubble; financial inflated-price metaphor aligned.
配给 pèijǐ ration; relief-water allocation correct jǐ reading.
培训班 péixùnbān training class; accurately translate Chinese agency rather than replace by Vietnamese ministry title.
佩服 pèifu admire; 极度 jídù not jíduān, remove unsupported weapons from Vietnamese.
盆地 péndì basin; Sichuan topography example coherent. Advanced level and stable keys retained.
""", [
 (2,"弥补短板 versus 填补空白.",{"example":{"simplified":r[1].examples[0].simplified.replace("短板空白","短板"),"pinyin":r[1].examples[0].pinyin.replace("duǎnbǎn kòngbái","duǎnbǎn"),"vietnamese":"Nhờ đổi mới tự chủ phối hợp liên ngành trong lĩnh vực thuật toán phần mềm cơ sở, đội ngũ nghiên cứu nước ta đã khắc phục hiệu quả các điểm yếu về công nghệ then chốt."}}),
 (3,"机关 jīguān.",py(3,"jīgī","jīguān")),
 (5,"Forced adjective and barely adverb.",{"part_of_speech":"verb, adjective, adverb","english_meanings":["to force someone","strained or forced","reluctantly","barely"],"vietnamese_meanings":["gượng ép","miễn cưỡng","vừa đủ; miễn cưỡng đạt được"]}),
 (17,"Language is tool, mastery is activity.",{"example":{"simplified":"母语是交流思想、传承文化的重要工具。","pinyin":"Mǔyǔ shì jiāoliú sīxiǎng, chuánchéng wénhuà de zhòngyào gōngjù.","vietnamese":"Tiếng mẹ đẻ là công cụ quan trọng để trao đổi tư tưởng và lưu truyền văn hóa."}}),
 (18,"Natural mountain-sunlight subject.",{"example":{"simplified":"清晨，层峦叠嶂的群山沐浴在金色的阳光中。","pinyin":"Qīngchén, céngluán-diézhàng de qúnshān mùyù zài jīnsè de yángguāng zhōng.","vietnamese":"Sáng sớm, những dãy núi trùng điệp đắm mình trong ánh nắng vàng."}}),
 (20,"Remove repeated 战略.",{"example":{"simplified":r[19].examples[0].simplified.replace("战略战略","战略")}}),
 (21,"Formal 薄膜 bó.",py(21,"báomó","bómó")),
 (22,"赤 chì.",py(22,"ěrcì","ěrchì")),
 (26,"Never entertain giving-up thought, not never waver that thought.",{"example":{"simplified":"面对科研中的重重困难，他从未动过放弃的念头。","pinyin":"Miànduì kēyán zhōng de chóngchóng kùnnan, tā cóngwèi dòngguo fàngqì de niàntou.","vietnamese":"Trước muôn vàn khó khăn trong nghiên cứu, anh ấy chưa từng có ý nghĩ từ bỏ."}}),
 (28,"Fuel solidifies rather than pipe material.",{"example":{"simplified":"在严寒地区，需要防止油管中的柴油凝固。","pinyin":"Zài yánhán dìqū, xūyào fángzhǐ yóuguǎn zhōng de cháiyóu nínggù.","vietnamese":"Ở vùng giá rét, cần ngăn dầu diesel trong đường ống đông đặc."}}),
 (30,"Clear four-industry example; remove malformed list.",{"example":{"simplified":"当地通过科技创新推动农林牧渔各产业高质量发展。","pinyin":"Dāngdì tōngguò kējì chuàngxīn tuīdòng nóng-lín-mù-yú gè chǎnyè gāo zhìliàng fāzhǎn.","vietnamese":"Địa phương thúc đẩy phát triển chất lượng cao các ngành nông nghiệp, lâm nghiệp, chăn nuôi và thủy sản thông qua đổi mới khoa học công nghệ."}}),
 (36,"机关 jīguān.",py(36,"jīgī","jīguān")),
 (37,"卓著 zhù.",py(37,"zhuózhe","zhuózhù")),
 (40,"规 guī.",py(40,"hégūi","héguī")),
 (41,"珠穆朗玛 proper name without extra syllable.",py(41,"Zhūmùlǎngrǎngmǎ","Zhūmùlǎngmǎ")),
 (48,"Translate agency accurately.",{"example":{"vietnamese":"Cơ quan Nhân lực và An sinh xã hội thành phố đã tổ chức miễn phí nhiều lớp tập huấn kỹ năng chuyên đề về vận hành phát trực tiếp thương mại điện tử nông thôn và tiếp thị thương hiệu đặc sắc, dành riêng cho thanh niên về quê khởi nghiệp."}}),
 (49,"极度 jídù and major national technology not necessarily weapon.",{"example":{"pinyin":r[48].examples[0].pinyin.replace("jíduān","jídù"),"vietnamese":"Trước tinh thần cống hiến cao cả của thế hệ nhà khoa học đi trước, tự lực cánh sinh, âm thầm nghiên cứu chế tạo những thiết bị chiến lược của quốc gia trong điều kiện vô cùng gian khổ, toàn thể cán bộ nghiên cứu trẻ đều hết lòng khâm phục."}}),
])

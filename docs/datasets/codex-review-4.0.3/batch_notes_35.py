"""L5-B015 actual review and re-read corrected content."""
from record_batch import record, rows
r=rows("L5-B015")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B015", """
情调 qíngdiào mood; atmospheric café lighting/music coherent.
情节 qíngjié plot; doubled 故事 removed.
请教 qǐngjiào consult; 前辈 qiánbèi not diànbèi.
穷尽 qióngjìn exhaust; finite knowledge of nature example aligned.
丘陵 qiūlíng hills; red-soil tea/citrus development aligned.
渠道 qúdào channel; direct farm-retail distribution aligned.
驱使 qūshǐ prompt; optical/radio conflation removed with clear curiosity example.
曲折 qūzhé winding; mountain trail description aligned.
趋势 qūshì trend; clean energy development example correct.
权威性 quánwēixìng authority; 机构 jīgòu and 校准 jiàozhǔn corrected.
全国性 quánguóxìng nationwide; vocational contest aligned.
权利 quánlì rights; not necessarily privilege, English refined.
权衡 quánhéng weigh; investment risks and returns correct.
券 quàn voucher; 节假日 jiéjiàrì not jiérìrì.
劝阻 quànzǔ dissuade; malformed 国家森林级 protected-area description repaired.
缺乏症 quēfázhèng deficiency disorder; iodine context aligned.
缺口 quēkǒu shortfall; shortage of skilled workers aligned.
群体 qúntǐ group; social support example correct.
群众性 qúnzhòngxìng mass; remove repeated 群众 modifier.
染色体 rǎnsètǐ chromosome; chromosome not itself a DNA double helix, replace inaccurate biological explanation.
嚷 rǎng shout; rāngrang reduplicated verb variant valid.
扰乱 rǎoluàn disrupt; 机关 jīguān corrected.
热爱 rè'ài love; teacher dedication example aligned.
热潮 rècháo upsurge; source 和 hé transcribed yǔ, correct.
热带雨林 rèdàiyǔlín tropical rainforest; ecosystem preservation aligned.
人道主义 réndàozhǔyì humanitarianism; remove doubled 特大, Vietnamese humanitarian adjective naturalized.
人格 réngé character; scholar integrity example aligned.
人才流失 réncáiliúshī brain drain; retention incentive example accurate.
人力资源 rénlìzīyuán human resources; labor market example correct.
人事 rénshì personnel; 干部 gànbù corrected.
人情味 rénqíngwèi human warmth; neighborhood mutual assistance correct.
认同感 rèntónggǎn identification/belonging; school cultural activities aligned.
韧性 rènxìng resilience; economic adaptability aligned.
日程表 rìchéngbiǎo timetable; meeting secretariat schedule correct.
日益 rìyì increasingly; automation productivity example aligned.
日新月异 rìxīnyuèyì rapid change; digital-city development appropriate.
融入 róngrù integrate; overseas students' campus adaptation aligned.
柔韧 róurèn supple/tough; artificial ligament material example aligned.
容纳 róngnà accommodate; distinguish athletics events from football matches.
冗余 rǒngyú redundancy; hardware backup design aligned.
如饥似渴 rújīsìkě eagerly; students reading classics correct.
锐利 ruìlì sharp; remove clairvoyance-like gloss, translate 切中要害 neutrally.
润滑 rùnhuá lubricate; gearbox oil example coherent.
若无其事 ruòwúqíshì as though nothing happened; experienced dispatcher apparent composure aligned.
弱势群体 ruòshìqúntǐ vulnerable groups; social protection example correct.
撒谎 sāhuǎng lie; honesty example natural.
塞外 sàiwài beyond frontier; correct sài reading and nomadic contacts.
三言两语 sānyánliǎngyǔ few words; 难题 nántí not nándí.
散漫 sǎnmàn undisciplined; 伊始 yīshǐ not yīshǐ? Source yīshǐ is correct, retained.
桑梓 sāngzǐ native place; 完全中学 includes junior and senior secondary, translate accurately. Keys/level retained.
""", [
 (2,"Remove doubled 故事.",{"example":{"simplified":r[1].examples[0].simplified.replace("故事故事","故事")}}),
 (3,"前辈 qiánbèi.",py(3,"lǎodiànbèi","lǎoqiánbèi")),
 (7,"Avoid conflating optical and radio telescopes.",{"example":{"simplified":"强烈的求知欲驱使他不断探索宇宙的奥秘。","pinyin":"Qiángliè de qiúzhīyù qūshǐ tā búduàn tànsuǒ yǔzhòu de àomì.","vietnamese":"Lòng ham hiểu biết mãnh liệt thôi thúc anh ấy không ngừng khám phá bí ẩn của vũ trụ."}}),
 (10,"机构 and 校准 pronunciation.",{"example":{"pinyin":r[9].examples[0].pinyin.replace("jīgī","jīgòu").replace("xiàozhǔn","jiàozhǔn")}}),
 (12,"Rights rather than special privilege.",{"english_meanings":["right","entitlement"]}),
 (14,"节假日 jiéjiàrì.",py(14,"jiérìrì","jiéjiàrì")),
 (15,"Repair malformed protected-area classification.",{"example":{"simplified":"在森林保护区内，巡护人员及时劝阻了游客生火的危险行为。","pinyin":"Zài sēnlín bǎohùqū nèi, xúnhù rényuán jíshí quànzǔ le yóukè shēnghuǒ de wēixiǎn xíngwéi.","vietnamese":"Trong khu bảo tồn rừng, nhân viên tuần tra đã kịp thời can ngăn hành vi đốt lửa nguy hiểm của du khách."}}),
 (19,"Remove repeated crowd modifier.",{"example":{"simplified":r[18].examples[0].simplified.replace("群众性群众合唱","群众性合唱"),"pinyin":r[18].examples[0].pinyin.replace("qúnzhòngxìng qúnzhòng héchàng","qúnzhòngxìng héchàng")}}),
 (20,"Accurate relation between chromosome and genetic information.",{"example":{"simplified":"染色体携带着生物的遗传信息。","pinyin":"Rǎnsètǐ xiédài zhe shēngwù de yíchuán xìnxī.","vietnamese":"Nhiễm sắc thể mang thông tin di truyền của sinh vật."}}),
 (22,"机关 jīguān.",py(22,"jīgī","jīguān")),
 (24,"和 hé.",py(24,"qīng-shàonián yǔ shìmín","qīng-shàonián hé shìmín")),
 (26,"Remove doubled 特大 and literal Vietnamese label.",{"example":{"simplified":r[25].examples[0].simplified.replace("特大特大","特大"),"pinyin":r[25].examples[0].pinyin.replace("tèdà tèdà","tèdà"),"vietnamese":r[25].examples[0].vietnamese.replace("cứu trợ chủ nghĩa nhân đạo","cứu trợ nhân đạo")}}),
 (30,"干部 gànbù.",py(30,"gàngbù","gànbù")),
 (39,"Athletics and football separate events.",{"example":{"simplified":"这座体育场能容纳八万名观众观看田径比赛或足球赛。","pinyin":"Zhè zuò tǐyùchǎng néng róngnà bāwàn míng guānzhòng guānkàn tiánjìng bǐsài huò zúqiúsài.","vietnamese":"Sân vận động này có thể chứa tám vạn khán giả xem thi đấu điền kinh hoặc bóng đá."}}),
 (42,"Sharp/keen, not clairvoyance; neutral hits-the-point translation.",{"vietnamese_meanings":["sắc bén","sắc nhọn","nhạy bén"],"example":{"vietnamese":r[41].examples[0].vietnamese.replace("đánh trúng tim đen","đi đúng trọng tâm")}}),
 (48,"难题 tí.",py(48,"nándí","nántí")),
 (50,"Complete secondary school includes both stages.",{"example":{"vietnamese":r[49].examples[0].vietnamese.replace("trường cấp ba","trường trung học cơ sở và trung học phổ thông liên cấp")}}),
])

"""Actual L5-B021 review and corrected-result recheck."""
from record_batch import record, rows
r=rows("L5-B021")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B021", """
沧海一粟 cānghǎiyīsù drop in ocean; cosmic insignificance example appropriate.
博古通今 bógǔtōngjīn erudite across time; scholar example aligned.
厚积薄发 hòujībófā accumulate and judiciously express; 潜心 qiánxīn, malformed English repaired.
精益求精 jīngyìqiújīng improve continually; artisans not necessarily multiple great countries in Vietnamese.
革故鼎新 gégùdǐngxīn innovate; institutional reform aligned.
继往开来 jìwǎngkāilái carry past forward; remove doubled 历史.
循序渐进 xúnxùjiànjìn gradual progress; educational cognition example correct.
潜移默化 qiányímòhuà subtle influence; 律己 lǜjǐ not lùjǐ.
推陈出新 tuīchénchūxīn renew tradition; 戏曲 generic traditional opera not Beijing opera.
未雨绸缪 wèiyǔchóumóu prepare ahead; remove doubled 金融.
防患未然 fánghuànwèirán prevent trouble; chemical-plant safety aligned.
卧薪尝胆 wòxīnchángdǎn endure hardship; Hán-Việt thường not vernacular nếm; 打压 dǎyā.
任重道远 rènzhòngdàoyuǎn heavy duty/long road; modernization task coherent.
脚踏实地 jiǎotàshídì practical; 干部 gànbù and 难题 nántí corrected.
风雨同舟 fēngyǔtóngzhōu share adversity; political solidarity example aligned.
标新立异 biāoxīnlìyì original; design originality/usability balance appropriate.
别出心裁 biéchūxīncái ingenious; architectural design example aligned.
不屈不挠 bùqūbùnáo unyielding; resistance under hardship appropriate.
持之以恒 chízhīyǐhéng persevere; learning skills gradually aligned.
粗制滥造 cūzhìlànzào shoddy manufacture; need not imply counterfeit, gloss refined.
大公无私 dàgōngwúsī impartial; both 干部 occurrences gànbù.
见义勇为 jiànyìyǒngwéi brave just act; child rescue appropriate.
举世瞩目 jǔshìzhǔmù worldwide attention; historic development example aligned.
空前绝后 kōngqiánjuéhòu unprecedented/unrepeatable; event hyperbole appropriate.
理所当然 lǐsuǒdāngrán natural/right; 诚实 chéngshí corrected.
络绎不绝 luòyìbùjué endless stream; remove doubled 黄金.
名列前茅 mínglièqiánmáo among best; city ranking example aligned.
莫名其妙 mòmíngqímiào inexplicable; 高精度 gāojīngdù not 高精密 in transcription.
迫不及待 pòbùjídài cannot wait; athlete reunion appropriate.
千方百计 qiānfāngbǎijì every means; emergency water relief aligned.
前所未有 qiánsuǒwèiyǒu unprecedented; digital opportunities aligned.
勤能补拙 qínnéngbǔzhuō diligence compensates weakness; refine English overstatement stupidity.
情不自禁 qíngbùzìjīn cannot restrain emotion; flag/anthem conflation repaired.
日积月累 rìjīyuèlěi accumulated over time; technical craftsmanship aligned.
融会贯通 rónghuìguàntōng integrate mastery; interdisciplinary study appropriate.
深谋远虑 shēnmóuyuǎnlǜ foresight; energy strategic planning aligned.
世外桃源 shìwàitáoyuán peaceful haven; 宛若 wǎnruò corrected.
适得其反 shìdéqífǎn counterproductive; inappropriate wetland cultivation aligned.
谈笑风生 tánxiàofēngshēng cheerful talk; 科考 kēkǎo corrected.
提心吊胆 tíxīndiàodǎn anxious; 陡峭 dǒuqiào correct tone placement.
天伦之乐 tiānlúnzhīlè family bliss; Mid-Autumn not year-end dinner, repair.
脱颖而出 tuōyǐngérchū stand out; winning innovation contest appropriate.
喜出望外 xǐchūwàngwài unexpectedly joyful; material certification news aligned.
闲情逸致 xiánqíngyìzhì leisurely mood; tea/poetry interlude appropriate.
想方设法 xiǎngfāngshèfǎ try every way; remove doubled 生命.
言行一致 yánxíngyīzhì words/actions consistent; 干部 gànbù corrected.
因地制宜 yīndìzhìyí adapt locally; differentiated rural industries aligned.
迎刃而解 yíngrènérjiě readily resolved; 难题 nántí corrected.
斩钉截铁 zhǎndīngjiétiě decisive; stern public statement example aligned.
知足常乐 zhīzúchánglè contentment; elderly philanthropist example coherent. Keys/level retained.
""", [
 (3,"潜 qián and accurate concise English.",dict(py(3,"qiǎnxīn","qiánxīn"),english_meanings=["to accumulate deeply and express judiciously","to build a strong foundation before achievement"])),
 (4,"Contextual artisans translation.",{"example":{"vietnamese":r[3].examples[0].vietnamese.replace("Những người thợ thủ công của các nước lớn đương đại","Những nghệ nhân bậc thầy đương đại")}}),
 (6,"Remove doubled 历史.",{"example":{"simplified":r[5].examples[0].simplified.replace("历史历史","历史"),"pinyin":r[5].examples[0].pinyin.replace("lìshǐ lìshǐ","lìshǐ")}}),
 (8,"律 lǜ.",py(8,"yányúlùjǐ","yányúlǜjǐ")),
 (9,"Generic opera not Beijing opera.",{"example":{"vietnamese":r[8].examples[0].vietnamese.replace("kinh kịch truyền thống","hí kịch truyền thống")}}),
 (10,"Remove doubled 金融.",{"example":{"simplified":r[9].examples[0].simplified.replace("金融金融","金融"),"pinyin":r[9].examples[0].pinyin.replace("jīnróng jīnróng","jīnróng")}}),
 (12,"尝 thường; 打压 dǎyā.",dict(py(12,"dǎyī","dǎyā"),sino_vietnamese="ngọa tân thường đảm")),
 (14,"干部 and 难题.",{"example":{"pinyin":r[13].examples[0].pinyin.replace("gàngbù","gànbù").replace("nándí","nántí")}}),
 (20,"Shoddy manufacture need not counterfeit.",{"vietnamese_meanings":["sản xuất ẩu tả","làm dối làm ẩu","làm ra hàng kém chất lượng"]}),
 (21,"干部 gànbù twice.",py(21,"gàngbù","gànbù")),
 (25,"诚实 chéngshí.",py(25,"chéngxìn-shǒuxìn","chéngshí-shǒuxìn")),
 (26,"Remove doubled 黄金.",{"example":{"simplified":r[25].examples[0].simplified.replace("黄金黄金","黄金"),"pinyin":r[25].examples[0].pinyin.replace("huángjīn huángjīn","huángjīn")}}),
 (28,"高精度 exact transcription.",py(28,"gāo jīngmì","gāo jīngdù")),
 (32,"Natural diligence gloss.",{"english_meanings":["diligence compensates for lack of natural ability","hard work makes up for clumsiness"]}),
 (33,"Anthem is sound, flag is not.",{"example":{"simplified":"听到国歌在领奖台上方响起，观众情不自禁地流下了热泪。","pinyin":"Tīngdào guógē zài lǐngjiǎngtái shàngfāng xiǎngqǐ, guānzhòng qíngbùzìjīn de liúxià le rèlèi.","vietnamese":"Nghe quốc ca vang lên trên bục nhận giải, khán giả không kìm được những giọt nước mắt xúc động."}}),
 (37,"若 ruò.",py(37,"wǎnrùo","wǎnruò")),
 (39,"科考 kēkǎo.",py(39,"kěkǎo","kēkǎo")),
 (40,"峭 qiào.",py(40,"dǒuqìao","dǒuqiào")),
 (41,"Mid-Autumn reunion dinner not New Year eve dinner.",{"example":{"simplified":r[40].examples[0].simplified.replace("年夜饭","团圆饭"),"pinyin":r[40].examples[0].pinyin.replace("niányèfàn","tuányuánfàn"),"vietnamese":r[40].examples[0].vietnamese.replace("cơm tất niên","cơm đoàn viên")}}),
 (45,"Remove doubled 生命.",{"example":{"simplified":r[44].examples[0].simplified.replace("生命生命线","生命线"),"pinyin":r[44].examples[0].pinyin.replace("shēngmìng shēngmìngxiàn","shēngmìngxiàn")}}),
 (46,"干部 gànbù.",py(46,"gàngbù","gànbù")),
 (48,"难题 tí.",py(48,"nándí","nántí")),
])

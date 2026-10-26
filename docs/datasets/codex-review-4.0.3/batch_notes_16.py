"""Actual L4-B008 all-field review, with explicit corrections and recheck."""
from record_batch import record

record("L4-B008", """
数量 shùliàng quantity; sufficient order quantity and precision instruments coherent.
数字 shùzì digit; accurate experimental figures sentence correct.
帅 shuài handsome; young man in formal suit, neutral qi in 帅气 valid.
顺便 shùnbiàn incidentally; buying eggs on way home natural.
硕士 shuòshì master's degree; engineering degree after study aligned.
顺序 shùnxù sequence; ticket inspection in queue-number order sound.
说明 shuōmíng explain; research-proposal background request accurate.
死 sǐ die/rigid; add adjective POS matching rigid; frozen orchids example correct.
速度 sùdù speed; higher intercity train speeds and pinyin aligned.
塑料袋 sùliàodài plastic bag; 袋 SV đại, not đới; reusable cloth-bag example correct.
随时 suíshí anytime; contacting customer service in case of problems natural.
所谓 suǒwèi so-called; skepticism about online expert remedies correctly translated.
随便 suíbiàn casual/as one pleases; feeling at home with friends accurate.
随着 suízhe along with; social/economic progress clause and neutral zhe valid.
所有 suǒyǒu all; silence phones before concert, complete pinyin/VI correct.
台 tái machine classifier; precision electronic measurement device example aligned.
抬 tái lift/carry; two men carrying sofa upstairs, correct distinct identity from 台.
态度 tàidu weak du colloquial reading; friendly service attitude example coherent; retain pronunciation key.
谈 tán discuss; professor/graduate students discussing research frontier correctly expressed.
谈判 tánpàn negotiation; add noun POS for 举行谈判 example.
趟 tàng trip classifier; dictionary verifies thảng, correct erroneous thướng; three trips example accurate.
躺 tǎng lie down; exhausted worker falling asleep, 睡着 shuìzháo correct.
特殊 tèshū special; replace awkward due-to-reason-this-situation structure with natural weather diversion example.
讨论 tǎolùn discussion/discuss; add noun POS for 展开讨论, AI ethics example aligned.
讨厌 tǎoyàn dislike/annoying; remove gibberish hòuh kě and align natural mosquito example; add adjective POS; yểm attested SV variant.
提纲 tígāng outline; outlining long report before writing, correct.
提 tí carry/mention; net bag of apples example correct.
提供 tígōng provide; library supplying large document database free, first-tone gōng correct.
提前 tíqián ahead of time; leave early to avoid Monday traffic, accurate.
提醒 tíxǐng remind; train attendant reminding passengers about luggage aligned.
填空 tiánkòng fill blanks; correct fourth-tone kòng empty slot, exam questions coherent.
条件 tiáojiàn conditions; school infrastructure and educational conditions correct.
停止 tíngzhǐ stop; blizzard suspending rail services, all fields aligned.
挺 tǐng quite; pleasant outdoor walk in light breeze, natural emphasis.
通过 tōngguò pass/through; add preposition POS for through sense, exam-passing example sound.
通知 tōngzhī notify/notice; add noun POS for formal notice, opening ceremony example accurate.
同情 tóngqíng sympathy/sympathize; add noun POS, SV đồng tình not confused with Vietnamese agreeing meaning.
推 tuī push/postpone; weather-delayed sports meet demonstrates postponement through 推迟, correct.
推迟 tuīchí postpone; delayed flight forcing meeting postponement, correct.
脱 tuō remove clothes/shoes; reading-room shoe-change instruction aligned.
袜 wà sock in compounds; 襪 SV miệt, correct ngoạt; baby's socks example accurate.
完全 wánquán completely; feasible engineering proposal after analysis, correct.
网球 wǎngqiú tennis; 塑胶 court surface is synthetic, not necessarily carpet; correct Vietnamese.
网站 wǎngzhàn website; university course-schedule publication correctly translated.
往返 wǎngfǎn round trip; Beijing-Tianjin commuting example and SV correct.
危机 wēijī crisis; company public-relations crisis response coherent.
卫生间 wèishēngjiān bathroom; ensuite room facilities aligned.
味道 wèidao flavor; replace redundant 香味味道 with natural pastry taste example.
吻合 wěnhé coincide; measured versus calculated data matching, correct.
文章 wénzhāng article; scholarly literary journal publication accurate. All Level 4 placements retained and no duplicate keys introduced.
""", [
 (8,"Include rigid adjectival sense already present.",{"part_of_speech":"verb, adjective"}),
 (10,"袋 is đại, whereas đới belongs to 帶.",{"sino_vietnamese":"tố liệu đại"}),
 (20,"Negotiation noun used in 举行谈判.",{"part_of_speech":"verb, noun"}),
 (21,"Dictionary verifies trip classifier SV thảng.",{"sino_vietnamese":"thảng"}),
 (23,"Natural exceptional-weather construction.",{"example":{"simplified":"由于特殊天气情况，航班不得不改降邻近机场。","pinyin":"Yóuyú tèshū tiānqì qíngkuàng, hángbān bùdébù gǎijiàng línjìn jīchǎng.","vietnamese":"Do tình hình thời tiết đặc biệt, chuyến bay buộc phải chuyển sang hạ cánh ở sân bay lân cận."}}),
 (24,"Discussion noun in example.",{"part_of_speech":"verb, noun"}),
 (25,"Remove non-Pinyin hòuh kě and awkward biting modifier; include annoying adjective.",{"part_of_speech":"verb, adjective","example":{"simplified":"夏天下雨过后，草丛里常有许多讨厌的蚊子。","pinyin":"Xiàtiān xià yǔ guòhòu, cǎocóng lǐ cháng yǒu xǔduō tǎoyàn de wénzi.","vietnamese":"Vào mùa hè sau những cơn mưa, trong bụi cỏ thường có nhiều muỗi đáng ghét."}}),
 (35,"Through sense is prepositional.",{"part_of_speech":"verb, preposition"}),
 (36,"Notice noun already present.",{"part_of_speech":"verb, noun"}),
 (37,"Sympathy nominal sense in example.",{"part_of_speech":"verb, noun"}),
 (41,"袜/襪 standard SV miệt for sock.",{"sino_vietnamese":"miệt"}),
 (43,"塑胶 means synthetic/polymer surface rather than carpet.",{"example":{"vietnamese":"Sân quần vợt mặt sân tổng hợp mới xây của trường chiều nào cũng đông kín học sinh yêu thể thao."}}),
 (48,"Remove duplicated aroma/flavor noun construction.",{"example":{"simplified":"那家老店的手工糕点味道香甜，很受欢迎。","pinyin":"Nà jiā lǎodiàn de shǒugōng gāodiǎn wèidao xiāngtián, hěn shòu huānyíng.","vietnamese":"Bánh thủ công của cửa tiệm lâu năm ấy có hương vị thơm ngọt, rất được yêu thích."}}),
], sources=["https://hvdic.thivien.net/whv/%E8%B6%9F","https://hvdic.thivien.net/whv/%E8%A5%AA","https://hvdic.thivien.net/whv/%E5%8E%AD"])

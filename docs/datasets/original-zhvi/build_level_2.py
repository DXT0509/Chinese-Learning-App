"""Author, validate and register Level 2 vocabulary (150 items across 3 batches)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generator_core import save_batch

# Batch 1: 50 items
BATCH_001_ITEMS = """
帮助|bang1 zhu4|bang trợ|verb|giúp đỡ; hỗ trợ|to help; to assist|谢谢你的帮助。|Xièxie nǐ de bāngzhù.|Cảm ơn sự giúp đỡ của bạn.
准备|zhun3 bei4|chuẩn bị|verb|chuẩn bị|to prepare|我准备去考试。|Wǒ zhǔnbèi qù kǎoshì.|Tôi chuẩn bị đi thi.
开始|kai1 shi3|khai thủy|verb|bắt đầu|to begin; to start|会议九点开始。|Huìyì jiǔ diǎn kāishǐ.|Cuộc họp bắt đầu lúc chín giờ.
介绍|jie4 shao4|giới thiệu|verb|giới thiệu|to introduce|我给你介绍一位新朋友。|Wǒ gěi nǐ jièshào yí wèi xīn péngyou.|Tôi giới thiệu với bạn một người bạn mới.
希望|xi1 wang4|hy vọng|verb|hy vọng; mong muốn|to hope; to wish|我希望明天天气好。|Wǒ xīwàng míngtiān tiānqì hǎo.|Tôi hy vọng ngày mai thời tiết đẹp.
欢迎|huan1 ying2|hoan nghênh|verb|hoan nghênh; chào đón|to welcome|欢迎你们来我家。|Huānyíng nǐmen lái wǒ jiā.|Chào mừng các bạn đến nhà tôi.
回答|hui2 da2|hồi đáp|verb|trả lời; giải đáp|to answer; to reply|请回答我的问题。|Qǐng huídá wǒ de wèntí.|Xin vui lòng trả lời câu hỏi của tôi.
告诉|gao4 su5|cáo tố|verb|nói cho biết; bảo|to tell|请告诉我你的名字。|Qǐng gàosu wǒ nǐ de míngzi.|Xin hãy cho tôi biết tên của bạn.
等|deng3|đẳng|verb|chờ; đợi|to wait|请在门口等我。|Qǐng zài ménkǒu děng wǒ.|Xin hãy đợi tôi ở cửa.
送|song4|tống|verb|tặng; tiễn|to give as a gift; to see off|爸爸送我一本书。|Bàba sòng wǒ yì běn shū.|Bố tặng tôi một cuốn sách.
玩|wan2|ngoạn|verb|chơi; vui chơi|to play; to have fun|孩子们在外面玩。|Háizimen zài wàimiàn wán.|Lũ trẻ đang chơi ở bên ngoài.
笑|xiao4|tiếu|verb|cười|to smile; to laugh|她笑得很开心。|Tā xiào de hěn kāixīn.|Cô ấy cười rất vui vẻ.
哭|ku1|khốc|verb|khóc|to cry|小孩子哭了。|Xiǎoháizi kū le.|Đứa bé khóc rồi.
借|jie4|tá|verb|mượn; vay|to borrow; to lend|我想借一本书。|Wǒ xiǎng jiè yì běn shū.|Tôi muốn mượn một cuốn sách.
还|huan2|hoàn|verb|trả lại (đồ, tiền)|to return (something)|我明天还你钱。|Wǒ míngtiān huán nǐ qián.|Ngày mai tôi trả tiền bạn.
知道|zhi1 dao5|tri đạo|verb|biết; hiểu rõ|to know|我不知道他在哪里。|Wǒ bù zhīdào tā zài nǎli.|Tôi không biết anh ấy ở đâu.
觉得|jue2 de5|giác đắc|verb|cảm thấy; thấy rằng|to feel; to think|我觉得今天很冷。|Wǒ juéde jīntiān hěn lěng.|Tôi thấy hôm nay rất lạnh.
认为|ren4 wei2|nhận vi|verb|cho rằng; nghĩ rằng|to think; to consider|我认为这个方法很好。|Wǒ rènwéi zhège fāngfǎ hěn hǎo.|Tôi cho rằng cách này rất tốt.
离开|li2 kai1|ly khai|verb|rời khỏi; rời xa|to leave; to depart|他已经离开北京了。|Tā yǐjīng líkāi Běijīng le.|Anh ấy đã rời khỏi Bắc Kinh rồi.
经过|jing1 guo4|kinh qua|verb|đi qua; trải qua|to pass by; to go through|去学校要经过一个公园。|Qù xuéxiào yào jīngguò yí ge gōngyuán.|Đến trường phải đi qua một công viên.
参加|can1 jia1|tham gia|verb|tham gia; dự|to participate; to attend|我想参加这个活动。|Wǒ xiǎng cānjiā zhège huódòng.|Tôi muốn tham gia hoạt động này.
考试|kao3 shi4|khảo thí|noun|kỳ thi; thi cử|exam; test|明天我们有汉语考试。|Míngtiān wǒmen yǒu hànyǔ kǎoshì.|Ngày mai chúng tôi có bài thi tiếng Trung.
完|wan2|hoàn|verb|xong; hết; hoàn thành|to finish; to run out|我看完了这本书。|Wǒ kànwán le zhè běn shū.|Tôi đã đọc xong cuốn sách này.
错|cuo4|thác|adjective|sai; nhầm|wrong; incorrect|这道题你做错了。|Zhè dào tí nǐ zuòcuò le.|Câu này bạn làm sai rồi.
对|dui4|đối|adjective|đúng; chính xác|right; correct|你说得很对。|Nǐ shuō de hěn duì.|Bạn nói rất đúng.
明白|ming2 bai5|minh bạch|verb|hiểu; rõ ràng|to understand; clear|老师说的话你明白吗？|Lǎoshī shuō de huà nǐ míngbai ma?|Lời thầy giáo nói bạn có hiểu không?
跳|tiao4|khiêu|verb|nhảy|to jump|猫跳到了桌子上。|Māo tiào dào le zhuōzi shang.|Con mèo nhảy lên bàn.
骑|qi2|kỵ|verb|cưỡi; đi (xe đạp, xe máy)|to ride|我骑自行车去上学。|Wǒ qí zìxíngchē qù shàngxué.|Tôi đi xe đạp đến trường.
自行车|zi4 xing2 che1|tự hành xa|noun|xe đạp|bicycle|这是我新买的自行车。|Zhè shì wǒ xīn mǎi de zìxíngchē.|Đây là chiếc xe đạp mới mua của tôi.
公共汽车|gong1 gong4 qi4 che1|công cộng khí xa|noun|xe buýt; xe công cộng|bus|坐公共汽车很便宜。|Zuò gōnggòng qìchē hěn piányi.|Đi xe buýt rất rẻ.
船|chuan2|thuyền|noun|thuyền; tàu thủy|boat; ship|他们坐船去旅游。|Tāmen zuò chuán qù lǚyóu.|Họ đi tàu thủy đi du lịch.
票|piao4|phiếu|noun|vé|ticket|我买了两张火车票。|Wǒ mǎi le liǎng zhāng huǒchēpiào.|Tôi đã mua hai vé tàu hỏa.
路|lu4|lộ|noun|đường; tuyến đường|road; path|这条路上车很多。|Zhè tiáo lù shang chē hěn duō.|Trên con đường này có rất nhiều xe.
机场|ji1 chang3|cơ trường|noun|sân bay|airport|我们开车去机场。|Wǒmen kāichē qù jīchǎng.|Chúng tôi lái xe đến sân bay.
门|men2|môn|noun|cửa; cổng|door; gate|请把门关上。|Qǐng bǎ mén guānshang.|Xin hãy đóng cửa lại.
教室|jiao4 shi4|giáo thất|noun|phòng học; lớp học|classroom|同学们都在教室里。|Tóngxuémen dōu zài jiàoshì lǐ.|Các bạn học đều ở trong lớp học.
房间|fang2 jian1|phòng gian|noun|căn phòng; phòng|room|这个房间很干净。|Zhège fángjiān hěn gānjìng.|Căn phòng này rất sạch sẽ.
宾馆|bin1 guan3|tân quán|noun|khách sạn|hotel|我们在宾馆住了一天。|Wǒmen zài bīnguǎn zhù le yì tiān.|Chúng tôi đã ở khách sạn một ngày.
便宜|pian2 yi5|tiện nghi|adjective|rẻ; giá rẻ|cheap; inexpensive|这家店的东西很便宜。|Zhè jiā diàn de dōngxi hěn piányi.|Đồ của tiệm này rất rẻ.
贵|gui4|quý|adjective|đắt; quý|expensive; noble|这件衣服太贵了。|Zhè jiàn yīfu tài guì le.|Bộ quần áo này đắt quá.
新|xin1|tân|adjective|mới|new|这是我的新电脑。|Zhè shì wǒ de xīn diànnǎo.|Đây là máy tính mới của tôi.
旧|jiu4|cựu|adjective|cũ|old; used|这本词典太旧了。|Zhè běn cídiǎn tài jiù le.|Cuốn từ điển này cũ quá rồi.
长|chang2|trường|adjective|dài|long|这条河很长。|Zhè tiáo hé hěn cháng.|Con sông này rất dài.
短|duan3|đoản|adjective|ngắn|short|这件衣服有点儿短。|Zhè jiàn yīfu yǒudiǎnr duǎn.|Bộ quần áo này hơi ngắn.
高|gao1|cao|adjective|cao|tall; high|他长得很高。|Tā zhǎng de hěn gāo.|Anh ấy trông rất cao.
矮|ai3|oải|adjective|thấp; lùn|short; low|弟弟比我矮一点儿。|Dìdi bǐ wǒ ǎi yìdiǎnr.|Em trai thấp hơn tôi một chút.
快|kuai4|khoái|adjective|nhanh|fast; quick|他跑得真快。|Tā pǎo de zhēn kuài.|Anh ấy chạy thật là nhanh.
慢|man4|mạn|adjective|chậm|slow|请你说慢一点儿。|Qǐng nǐ shuō màn yìdiǎnr.|Xin bạn hãy nói chậm một chút.
晴|qing2|tình|adjective|nắng; trời quang|sunny; clear|今天是一个晴天。|Jīntiān shì yí ge qíngtiān.|Hôm nay là một ngày trời nắng.
阴|yin1|âm|adjective|âm u; râm trời|cloudy; overcast|今天阴天，可能要下雨。|Jīntiān yīntiān, kěnéng yào xiàyǔ.|Hôm nay trời râm, có thể sắp mưa.
"""

# Batch 2: 50 items
BATCH_002_ITEMS = """
眼睛|yan3 jing5|nhãn tinh|noun|mắt; đôi mắt|eye|她的眼睛很大。|Tā de yǎnjing hěn dà.|Mắt của cô ấy rất to.
头发|tou2 fa5|đầu phát|noun|tóc|hair|妈妈的头发很长。|Māma de tóufa hěn cháng.|Tóc của mẹ rất dài.
脸|lian3|kiểm|noun|mặt; khuôn mặt|face|洗脸后觉得很舒服。|Xǐliǎn hòu juéde hěn shūfu.|Sau khi rửa mặt cảm thấy rất dễ chịu.
手|shou3|thủ|noun|tay; bàn tay|hand|饭前请洗手。|Fàn qián qǐng xǐshǒu.|Trước khi ăn cơm xin hãy rửa tay.
腿|tui3|thoái|noun|chân (từ đùi trở xuống)|leg|我的腿有点儿疼。|Wǒ de tuǐ yǒudiǎnr téng.|Chân tôi hơi đau một chút.
脚|jiao3|cước|noun|bàn chân|foot|走了很久，我的脚累了。|Zǒu le hěn jiǔ, wǒ de jiǎo lèi le.|Đi bộ rất lâu, chân tôi mỏi rồi.
哥哥|ge1 ge5|ca ca|noun|anh trai|elder brother|我哥哥在大学读书。|Wǒ gēge zài dàxué dúshū.|Anh trai tôi học ở trường đại học.
姐姐|jie3 jie5|tỷ tỷ|noun|chị gái|elder sister|姐姐工作很努力。|Jiějie gōngzuò hěn nǔlì.|Chị gái làm việc rất chăm chỉ.
弟弟|di4 di5|đệ đệ|noun|em trai|younger brother|弟弟正在看电视。|Dìdi zhèngzài kàn diànshì.|Em trai đang xem ti vi.
妹妹|mei4 mei5|muội muội|noun|em gái|younger sister|我妹妹喜欢跳舞。|Wǒ mèimei xǐhuan tiàowǔ.|Em gái tôi thích khiêu vũ.
丈夫|zhang4 fu5|trượng phu|noun|chồng|husband|她的丈夫是医生。|Tā de zhàngfu shì yīshēng.|Chồng của cô ấy là bác sĩ.
妻子|qi1 zi5|thê tử|noun|vợ|wife|他和妻子住在上海。|Tā hé qīzi zhù zài Shànghǎi.|Anh ấy và vợ sống ở Thượng Hải.
男人|nan2 ren2|nam nhân|noun|đàn ông; người nam|man; male|那位男人是我叔叔。|Nà wèi nánrén shì wǒ shūshu.|Người đàn ông kia là chú của tôi.
女人|nü3 ren2|nữ nhân|noun|phụ nữ; người nữ|woman; female|她是很有能力的女人。|Tā shì hěn yǒu nénglì de nǚrén.|Cô ấy là một người phụ nữ rất có năng lực.
孩子|hai2 zi5|hài tử|noun|trẻ con; con cái|child; children|房间里有三个孩子。|Fángjiān lǐ yǒu sān ge háizi.|Trong phòng có ba đứa trẻ.
服务员|fu2 wu4 yuan2|phục vụ viên|noun|nhân viên phục vụ|waiter; attendant|服务员，请结账。|Fúwùyuán, qǐng jiézhàng.|Phục vụ viên, xin thanh toán.
手机|shou3 ji1|thủ cơ|noun|điện thoại di động|mobile phone|我的手机在桌子上。|Wǒ de shǒujī zài zhuōzi shang.|Điện thoại của tôi ở trên bàn.
手表|shou3 biao3|thủ biểu|noun|đồng hồ đeo tay|wrist watch|这只手表很漂亮。|Zhè zhī shǒubiǎo hěn piàoliang.|Chiếc đồng hồ này rất đẹp.
报纸|bao4 zhi3|báo chỉ|noun|báo; tờ báo|newspaper|爷爷每天早上看报纸。|Yéye měitiān zǎoshang kàn bàozhǐ.|Ông nội mỗi sáng đều đọc báo.
铅笔|qian1 bi3|duyên bút|noun|bút chì|pencil|我用铅笔写字。|Wǒ yòng qiānbǐ xiězì.|Tôi dùng bút chì viết chữ.
颜色|yan2 se4|nhan sắc|noun|màu sắc|color|你喜欢什么颜色？|Nǐ xǐhuan shénme yánsè?|Bạn thích màu gì?
红|hong2|hồng|adjective|đỏ|red|她穿了一件红衣服。|Tā chuān le yí jiàn hóng yīfu.|Cô ấy mặc một chiếc áo đỏ.
白|bai2|bạch|adjective|trắng|white|雪是白的。|Xuě shì bái de.|Tuyết màu trắng.
黑|hei1|hắc|adjective|đen|black|他买了一辆黑车。|Tā mǎi le yí liàng hēi chē.|Anh ấy đã mua một chiếc xe màu đen.
蓝|lan2|lam|adjective|xanh lam; xanh da trời|blue|今天的天空很蓝。|Jīntiān de tiānkōng hěn lán.|Bầu trời hôm nay rất xanh.
绿|lü4|lục|adjective|xanh lá cây; lục|green|春天树叶很绿。|Chūntiān shùyè hěn lǜ.|Mùa xuân lá cây rất xanh.
黄|huang2|hoàng|adjective|vàng|yellow|香蕉是黄的。|Xiāngjiāo shì huáng de.|Quối chuối có màu vàng.
件|jian4|kiện|classifier|chiếc; cái (áo, việc)|classifier for clothes or events|我买了一件大衣。|Wǒ mǎi le yí jiàn dàyī.|Tôi đã mua một chiếc áo khoác.
张|zhang1|trương|classifier|tờ; tấm; bức (mặt phẳng)|classifier for flat objects|桌上有一张纸。|Zhuō shang yǒu yì zhāng zhǐ.|Trên bàn có một tờ giấy.
只|zhi1|chích|classifier|con (động vật); chiếc (trong đôi)|classifier for birds and animals|树上有一只小鸟。|Shù shang yǒu yì zhī xiǎoniǎo.|Trên cây có một con chim nhỏ.
条|tiao2|điều|classifier|con; cái; sợi (vật dài hẹp)|classifier for long thin things|这条裤子很合适。|Zhè tiáo kùzi hěn héshì.|Chiếc quần này rất vừa vặn.
双|shuang1|song|classifier|đôi; cặp|pair|我想买一双新鞋。|Wǒ xiǎng mǎi yì shuāng xīn xié.|Tôi muốn mua một đôi giày mới.
次|ci4|thứ|classifier|lần; lượt|time; occurrence|这是我第一次来中国。|Zhè shì wǒ dì-yī cì lái Zhōngguó.|Đây là lần đầu tiên tôi đến Trung Quốc.
下次|xia4 ci4|hạ thứ|noun|lần sau|next time|下次我们再一起吃饭。|Xiàcì wǒmen zài yìqǐ chīfàn.|Lần sau chúng ta lại cùng nhau ăn cơm.
上次|shang4 ci4|thượng thứ|noun|lần trước|last time|上次去北京我很开心。|Shàngcì qù Běijīng wǒ hěn kāixīn.|Lần trước đi Bắc Kinh tôi rất vui vẻ.
去年|qu4 nian2|khứ niên|noun|năm ngoái; năm trước|last year|去年我去了北京。|Qùnián wǒ qù le Běijīng.|Năm ngoái tôi đã đi Bắc Kinh.
明年|ming2 nian2|minh niên|noun|năm sau; sang năm|next year|明年我打算去留学。|Míngnián wǒ dǎsuàn qù liúxué.|Năm sau tôi dự định đi du học.
早上|zao3 shang5|tảo thượng|noun|buổi sáng sớm; sáng|early morning|我早上六点起床。|Wǒ zǎoshang liù diǎn qǐchuáng.|Buổi sáng tôi thức dậy lúc sáu giờ.
过去|guo4 qu5|quá khứ|noun|quá khứ; trước đây|past|过去的事情就让它过去吧。|Guòqù de shìqing jiù ràng tā guòqu ba.|Chuyện trong quá khứ hãy để nó qua đi.
小时|xiao3 shi2|tiểu thời|noun|giờ; tiếng đồng hồ|hour|我们学了两个小时。|Wǒmen xué le liǎng ge xiǎoshí.|Chúng tôi đã học hai tiếng đồng hồ.
已经|yi3 jing1|dĩ kinh|adverb|đã; rồi|already|他已经回家了。|Tā yǐjīng huí jiā le.|Anh ấy đã về nhà rồi.
正在|zheng4 zai4|chính tại|adverb|đang (tiến hành)|in the middle of|我正在吃晚饭。|Wǒ zhèngzài chī wǎnfàn.|Tôi đang ăn cơm tối.
马上|ma3 shang4|mã thượng|adverb|ngay lập tức; liền|immediately; at once|我马上就来。|Wǒ mǎshàng jiù lái.|Tôi sẽ đến ngay đây.
一直|yi4 zhi2|nhất trực|adverb|luôn luôn; thẳng|straight; all along|他一直在看书。|Tā yìzhí zài kàn shū.|Anh ấy vẫn luôn đang đọc sách.
常常|chang2 chang2|thường thường|adverb|thường; thường xuyên|often; frequently|我们常常去那家书店。|Wǒmen chángcháng qù nà jiā shūdiàn.|Chúng tôi thường đến hiệu sách đó.
再|zai4|tái|adverb|lại; nữa (hành động tương lai)|again; once more|请再说一遍。|Qǐng zài shuō yí biàn.|Xin hãy nói lại một lần nữa.
就|jiu4|tựu|adverb|ngay; liền; thì|then; right away|我想清楚了就告诉你。|Wǒ xiǎng qīngchu le jiù gàosu nǐ.|Tôi nghĩ thông suốt rồi sẽ bảo bạn ngay.
别|bie2|biệt|adverb|đừng; chớ|do not|别抽烟，对身体不好。|Bié chōuyān, duì shēntǐ bù hǎo.|Đừng hút thuốc, không tốt cho sức khỏe.
真|zhen1|chân|adverb|thật; thực sự|really; truly|今天天气真好。|Jīntiān tiānqì zhēn hǎo.|Hôm nay thời tiết thật là đẹp.
非常|fei1 chang2|phi thường|adverb|vô cùng; rất|very; extremely|我非常喜欢这首中国歌。|Wǒ fēicháng xǐhuan zhè shǒu zhōngguó gē.|Tôi vô cùng thích bài hát tiếng Trung này.
"""

# Batch 3: 50 items
BATCH_003_ITEMS = """
因为|yin1 wei4|nhân vi|conjunction|bởi vì; vì|because|因为下雨，所以我们没去。|Yīnwèi xià yǔ, suǒyǐ wǒmen méi qù.|Vì trời mưa nên chúng tôi không đi.
所以|suo3 yi3|sở dĩ|conjunction|cho nên; vì vậy|therefore; so|他生病了，所以请假。|Tā shēngbìng le, suǒyǐ qǐngjià.|Anh ấy bị ốm cho nên xin nghỉ.
但是|dan4 shi4|đãn thị|conjunction|nhưng mà; nhưng|but; however|我很想去，但是没时间。|Wǒ hěn xiǎng qù, dànshì méi shíjiān.|Tôi rất muốn đi, nhưng không có thời gian.
虽然|sui1 ran2|tuy nhiên|conjunction|mặc dù; tuy rằng|although; even though|虽然天气冷，但他还是去跑步。|Suīrán tiānqì lěng, dàn tā háishì qù pǎobù.|Mặc dù trời lạnh nhưng anh ấy vẫn đi chạy bộ.
如果|ru2 guo3|như quả|conjunction|nếu; nếu như|if; in case|如果明天下雨，我们就不去。|Rúguǒ míngtiān xià yǔ, wǒmen jiù bú qù.|Nếu ngày mai trời mưa, chúng mình sẽ không đi.
左边|zuo3 bian5|tả biên|noun|bên trái; phía bên trái|left; left side|银行在超市的左边。|Yínháng zài chāoshì de zuǒbian.|Ngân hàng ở bên trái siêu thị.
右边|you4 bian5|hữu biên|noun|bên phải; phía bên phải|right; right side|书店在学校右边。|Shūdiàn zài xuéxiào yòubian.|Hiệu sách ở bên phải trường học.
旁边|pang2 bian5|bàng biên|noun|bên cạnh|beside; side|他就坐在我旁边。|Tā jiù zuò zài wǒ pángbiān.|Anh ấy ngồi ngay bên cạnh tôi.
外面|wai4 mian5|ngoại diện|noun|bên ngoài; phía ngoài|outside|外面很冷，快进来吧。|Wàimiàn hěn lěng, kuài jìnlái ba.|Bên ngoài rất lạnh, mau vào trong đi.
中间|zhong1 jian1|trung gian|noun|ở giữa; chính giữa|middle; between|他在我们两个人中间。|Tā zài wǒmen liǎng ge rén zhōngjiān.|Anh ấy ở giữa hai người chúng tôi.
往|wang3|vãng|preposition|hướng về; về phía|toward; to|一直往前走就是地铁站。|Yìzhí wǎng qián zǒu jiù shì dìtiězhàn.|Đi thẳng về phía trước chính là ga tàu điện ngầm.
向|xiang4|hướng|preposition|hướng về; về phía; đối với|towards; to|请向右转。|Qǐng xiàng yòu zhuǎn.|Xin vui lòng rẽ về bên phải.
离|li2|ly|preposition|cách (khoảng cách)|away from|我家离公司很近。|Wǒ jiā lí gōngsī hěn jìn.|Nhà tôi cách công ty rất gần.
从|cong2|tùng|preposition|từ (nơi chốn, thời gian)|from|我从越南来。|Wǒ cóng Yuènán lái.|Tôi đến từ Việt Nam.
比|bi3|tỷ|preposition|so với (so sánh)|to compare|弟弟比哥哥高。|Dìdi bǐ gēge gāo.|Em trai cao hơn anh trai.
关|guan1|quan|verb|đóng; tắt (đèn, máy)|to close; to turn off|请出门前关灯。|Qǐng chūmén qián guān dēng.|Xin hãy tắt đèn trước khi ra ngoài.
洗澡|xi3 zao3|tẩy tảo|verb|tắm; tắm rửa|to take a bath; to shower|我先去洗澡。|Wǒ xiān qù xǐzǎo.|Tôi đi tắm trước.
洗手间|xi3 shou3 jian1|tẩy thủ gian|noun|nhà vệ sinh; toa-lét|restroom; toilet|请问洗手间在哪里？|Qǐngwèn xǐshǒujiān zài nǎli?|Xin hỏi nhà vệ sinh ở đâu?
刷牙|shua1 ya2|loát nha|verb|đánh răng|to brush teeth|早上起床后要刷牙。|Zǎoshang qǐchuáng hòu yào shuāyá.|Buổi sáng sau khi thức dậy phải đánh răng.
起床|qi3 chuang2|khởi sàng|verb|thức dậy; dậy|to get up|我每天早上七点起床。|Wǒ měitiān zǎoshang qī diǎn qǐchuáng.|Tôi thức dậy lúc bảy giờ mỗi sáng.
散步|san4 bu4|tản bộ|verb|đi dạo; tản bộ|to take a walk|晚饭后我们去公园散步。|Wǎnfàn hòu wǒmen qù gōngyuán sànbù.|Sau bữa tối chúng tôi đi công viên dạo bộ.
累|lei4|luy|adjective|mệt; mệt mỏi|tired|工作了一天，我很累。|Gōngzuò le yì tiān, wǒ hěn lèi.|Làm việc cả ngày, tôi rất mệt.
饱|bao3|bão|adjective|no (bụng)|full (not hungry)|我吃饱了。|Wǒ chībǎo le.|Tôi ăn no rồi.
饿|e4|ngạ|adjective|đói|hungry|走了一下午，肚子很饿。|Zǒu le yí xiàwǔ, dùzi hěn è.|Đi cả buổi chiều, bụng đói meo.
渴|ke3|khát|adjective|khát (nước)|thirsty|口渴了，喝点水吧。|Kǒukě le, hē diǎn shuǐ ba.|Khát nước rồi, uống chút nước đi.
干净|gan1 jing4|can tịnh|adjective|sạch sẽ|clean|这间屋子打扫得很干净。|Zhè jiān wūzi dǎsǎo de hěn gānjìng.|Căn phòng này dọn dẹp rất sạch sẽ.
脏|zang1|tang|adjective|bẩn; dơ|dirty|衣服脏了，需要洗。|Yīfu zāng le, xūyào xǐ.|Quần áo bẩn rồi, cần phải giặt.
忙|mang2|mang|adjective|bận; bận rộn|busy|最近工作非常忙。|Zuìjìn gōngzuò fēicháng máng.|Dạo gần đây công việc rất bận rộn.
容易|rong2 yi4|dung dịch|adjective|dễ; dễ dàng|easy|学中文不太容易。|Xué zhōngwén bú tài róngyì.|Học tiếng Trung không dễ lắm.
难|nan2|nan|adjective|khó; nan giải|difficult; hard|这个问题很难回答。|Zhège wèntí hěn nán huídá.|Câu hỏi này rất khó trả lời.
正确|zheng4 que4|chính xác|adjective|chính xác; đúng đắn|correct; right|你的答案是正确的。|Nǐ de dá'àn shì zhèngquè de.|Đáp án của bạn là chính xác.
清楚|qing1 chu5|thanh sở|adjective|rõ ràng; hiểu rõ|clear; distinct|请把字写清楚。|Qǐng bǎ zì xiě qīngchu.|Xin hãy viết chữ cho rõ ràng.
甜|tian2|điềm|adjective|ngọt|sweet|这个西瓜真甜。|Zhège xīguā zhēn tián.|Quả dưa hấu này ngọt thật.
咸|xian2|hàm|adjective|mặn|salty|这道菜有点儿咸。|Zhè dào cài yǒudiǎnr xián.|Món này hơi mặn một chút.
辣|la4|lạt|adjective|cay|spicy; hot|四川菜很辣。|Sìchuān cài hěn là.|Món ăn Tứ Xuyên rất cay.
酸|suan1|toan|adjective|chua|sour|这个苹果有点儿酸。|Zhège píngguǒ yǒudiǎnr suān.|Quả táo này hơi chua một chút.
汤|tang1|thang|noun|canh; súp|soup|先喝一碗热汤吧。|Xiān hē yì wǎn rè tāng ba.|Trước tiên hãy uống một bát canh nóng đi.
菜单|cai4 dan1|thái đơn|noun|thực đơn; menu|menu|服务员，请给我们菜单。|Fúwùyuán, qǐng gěi wǒmen càidān.|Phục vụ viên, xin cho chúng tôi xem thực đơn.
筷子|kuai4 zi5|khoái tử|noun|đôi đũa; đũa|chopsticks|中国人习惯用筷子吃饭。|Zhōngguórén xíguàn yòng kuàizi chīfàn.|Người Trung Quốc quen dùng đũa ăn cơm.
勺子|shao2 zi5|chước tử|noun|cái thìa; muỗng|spoon|请给我一把勺子。|Qǐng gěi wǒ yì bǎ sháozi.|Xin hãy cho tôi một chiếc thìa.
碗|wan3|oản|noun|bát; cái chén|bowl|我吃了一碗面条。|Wǒ chī le yì wǎn miàntiáo.|Tôi đã ăn một bát mì sợi.
果汁|guo3 zhi1|quả trấp|noun|nước ép hoa quả; nước trái cây|fruit juice|你想喝苹果汁吗？|Nǐ xiǎng hē píngguǒzhī ma?|Bạn có muốn uống nước ép táo không?
啤酒|pi2 jiu3|ty tửu|noun|bia|beer|他不喝啤酒。|Tā bù hē píjiǔ.|Anh ấy không uống bia.
蛋糕|dan4 gao1|đản cao|noun|bánh ngọt; bánh kem|cake|生日那天我吃了蛋糕。|Shēngrì nà tiān wǒ chī le dàngāo.|Vào ngày sinh nhật tôi đã ăn bánh kem.
糖|tang2|đường|noun|đường; kẹo|sugar; candy|喝咖啡时我加一点儿糖。|Hē kāfēi shí wǒ jiā yìdiǎnr táng.|Khi uống cà phê tôi cho thêm một chút đường.
包子|bao1 zi5|bao tử|noun|bánh bao|steamed stuffed bun|这家店的包子很好吃。|Zhè jiā diàn de bāozi hěn hǎochī.|Bánh bao của quán này rất ngon.
饺子|jiao3 zi5|giảo tử|noun|sủi cảo; bánh chẻo|dumpling|过年时北方人吃饺子。|Guònián shí běifāngrén chī jiǎozi.|Vào dịp Tết người miền Bắc ăn sủi cảo.
面条|mian4 tiao2|miến điều|noun|mì sợi; mì|noodles|中午我们去吃牛肉面条。|Zhōngwǔ wǒmen qù chī niúròu miàntiáo.|Buổi trưa chúng mình đi ăn mì bò nhé.
问题|wen4 ti2|vấn đề|noun|câu hỏi; vấn đề|question; problem|你有不懂的问题可以问老师。|Nǐ yǒu bù dǒng de wèntí kěyǐ wèn lǎoshī.|Bạn có vấn đề chưa hiểu có thể hỏi thầy giáo.
事情|shi4 qing5|sự tình|noun|sự việc; việc; chuyện|matter; affair|今天我有很多事情要做。|Jīntiān wǒ yǒu hěn duō shìqing yào zuò.|Hôm nay tôi có rất nhiều việc phải làm.
"""


def main():
    b1 = [line.strip() for line in BATCH_001_ITEMS.strip().splitlines() if line.strip()]
    b2 = [line.strip() for line in BATCH_002_ITEMS.strip().splitlines() if line.strip()]
    b3 = [line.strip() for line in BATCH_003_ITEMS.strip().splitlines() if line.strip()]

    print("Building and validating Level 2 Batch 001...")
    save_batch(level=2, batch_num=1, raw_lines=b1)

    print("Building and validating Level 2 Batch 002...")
    save_batch(level=2, batch_num=2, raw_lines=b2)

    print("Building and validating Level 2 Batch 003...")
    save_batch(level=2, batch_num=3, raw_lines=b3)

    print("Level 2 complete! Total 150 items across 3 batches.")


if __name__ == "__main__":
    main()

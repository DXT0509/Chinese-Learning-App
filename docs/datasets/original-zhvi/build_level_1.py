"""Author, validate and register Level 1 vocabulary (100 items in 2 batches)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generator_core import save_batch

# Batch 1 (50 items)
BATCH_001_ITEMS = """
苹果|ping2 guo3|bình quả|noun|quả táo; táo|apple|我吃苹果。|Wǒ chī píngguǒ.|Tôi ăn táo.
杯子|bei1 zi5|bôi tử|noun|cốc; ly; tách|cup; glass|桌子上有一个杯子。|Zhuōzi shang yǒu yí ge bēizi.|Trên bàn có một cái cốc.
衣服|yi1 fu5|y phục|noun|quần áo|clothes|我想买衣服。|Wǒ xiǎng mǎi yīfu.|Tôi muốn mua quần áo.
飞机|fei1 ji1|phi cơ|noun|máy bay|airplane|我坐飞机去北京。|Wǒ zuò fēijī qù Běijīng.|Tôi đi máy bay đến Bắc Kinh.
出租车|chu1 zu1 che1|xuất tô xa|noun|xe taxi; taxi|taxi|我们坐出租车去学校。|Wǒmen zuò chūzūchē qù xuéxiào.|Chúng tôi đi taxi đến trường học.
电视|dian4 shi4|điện thị|noun|ti vi; truyền hình|television|我看电视。|Wǒ kàn diànshì.|Tôi xem ti vi.
电脑|dian4 nao3|điện não|noun|máy tính|computer|他在用电脑。|Tā zài yòng diànnǎo.|Anh ấy đang dùng máy tính.
电影|dian4 ying3|điện ảnh|noun|phim; điện ảnh|movie; film|今天晚上我看电影。|Jīntiān wǎnshang wǒ kàn diànyǐng.|Tối nay tôi xem phim.
天气|tian1 qi4|thiên khí|noun|thời tiết|weather|今天天气很好。|Jīntiān tiānqì hěn hǎo.|Hôm nay thời tiết rất đẹp.
猫|mao1|miêu|noun|con mèo; mèo|cat|我家有一只猫。|Wǒ jiā yǒu yì zhī māo.|Nhà tôi có một con mèo.
狗|gou3|cẩu|noun|con chó; chó|dog|那是一只狗。|Nà shì yì zhī gǒu.|Kia là một con chó.
东西|dong1 xi5|đông tây|noun|đồ đạc; thứ; đồ vật|thing; stuff|你想买什么东西？|Nǐ xiǎng mǎi shénme dōngxi?|Bạn muốn mua đồ gì?
桌子|zhuo1 zi5|trác tử|noun|cái bàn; bàn|table; desk|这是我的桌子。|Zhè shì wǒ de zhuōzi.|Đây là bàn của tôi.
椅子|yi3 zi5|ỷ tử|noun|cái ghế; ghế|chair|请坐在椅子上。|Qǐng zuò zài yǐzi shang.|Xin mời ngồi trên ghế.
医生|yi1 sheng1|y sinh|noun|bác sĩ|doctor|他是医生。|Tā shì yīshēng.|Anh ấy là bác sĩ.
医院|yi1 yuan4|y viện|noun|bệnh viện|hospital|我妈妈在医院工作。|Wǒ māma zài yīyuàn gōngzuò.|Mẹ tôi làm việc ở bệnh viện.
饭店|fan4 dian4|phạn điếm|noun|nhà hàng; khách sạn; quán ăn|restaurant; hotel|我们去饭店吃米饭。|Wǒmen qù fàndiàn chī mǐfàn.|Chúng tôi đến nhà hàng ăn cơm.
商店|shang1 dian4|thương điếm|noun|cửa hàng; tiệm|shop; store|我去商店买水。|Wǒ qù shāngdiàn mǎi shuǐ.|Tôi đến cửa hàng mua nước.
火车站|huo3 che1 zhan4|hỏa xa trạm|noun|ga xe lửa; ga tàu hỏa|train station|火车站很远。|Huǒchēzhàn hěn yuǎn.|Ga tàu hỏa rất xa.
北京|bei3 jing1|Bắc Kinh|noun|Bắc Kinh|Beijing|他住在北京。|Tā zhù zài Běijīng.|Anh ấy sống ở Bắc Kinh.
中国|zhong1 guo2|Trung Quốc|noun|Trung Quốc|China|我喜欢中国。|Wǒ xǐhuan Zhōngguó.|Tôi thích Trung Quốc.
上|shang4|thượng|noun|phía trên; bên trên; lên|on; above; to go up|书在桌子上。|Shū zài zhuōzi shang.|Sách ở trên bàn.
下|xia4|hạ|noun|phía dưới; bên dưới; xuống|under; below; to go down|小猫在椅子下。|Xiǎomāo zài yǐzi xià.|Con mèo con ở dưới ghế.
前面|qian2 mian5|tiền diện|noun|phía trước; đằng trước|front; ahead|学校在前面。|Xuéxiào zài qiánmian.|Trường học ở phía trước.
后面|hou4 mian5|hậu diện|noun|phía sau; đằng sau|back; behind|医院在商店后面。|Yīyuàn zài shāngdiàn hòumian.|Bệnh viện ở phía sau cửa hàng.
里面|li3 mian5|lý diện|noun|bên trong; phía trong|inside|学校里面有很多人。|Xuéxiào lǐmian yǒu hěn duō rén.|Bên trong trường học có rất nhiều người.
上午|shang4 wu3|thượng ngọ|noun|buổi sáng (nửa đầu ngày)|morning|我上午去学校。|Wǒ shàngwǔ qù xuéxiào.|Buổi sáng tôi đến trường học.
中午|zhong1 wu3|trung ngọ|noun|buổi trưa|noon|中午我吃米饭。|Zhōngwǔ wǒ chī mǐfàn.|Buổi trưa tôi ăn cơm.
下午|xia4 wu3|hạ ngọ|noun|buổi chiều|afternoon|下午我们喝茶。|Xiàwǔ wǒmen hē chá.|Buổi chiều chúng tôi uống trà.
晚上|wan3 shang5|vãn thượng|noun|buổi tối; ban đêm|evening; night|晚上我在家看书。|Wǎnshang wǒ zài jiā kàn shū.|Buổi tối tôi ở nhà đọc sách.
现在|xian4 zai4|hiện tại|noun|bây giờ; hiện tại|now|现在是上午十点。|Xiànzài shì shàngwǔ shí diǎn.|Bây giờ là mười giờ sáng.
时候|shi2 hou5|thời hậu|noun|lúc; khi; thời điểm|time; moment|你什么时候去北京？|Nǐ shénme shíhou qù Běijīng?|Khi nào bạn đi Bắc Kinh?
分钟|fen1 zhong1|phân chung|noun|phút (thời gian)|minute|请等五分钟。|Qǐng děng wǔ fēnzhōng.|Xin vui lòng đợi năm phút.
星期|xing1 qi1|tinh kỳ|noun|tuần; thứ|week|今天是星期一。|Jīntiān shì xīngqīyī.|Hôm nay là thứ hai.
岁|sui4|tuế|classifier|tuổi|years old|我今年二十岁。|Wǒ jīnnián èrshí suì.|Năm nay tôi hai mươi tuổi.
块|kuai4|khối|classifier|đồng; tệ (tiền tệ); miếng|piece; yuan (currency)|这本书三十块。|Zhè běn shū sānshí kuài.|Cuốn sách này giá ba mươi đồng.
个|ge4|cá|classifier|cái; chiếc; con; người (lượng từ chung)|general classifier|我有一个朋友。|Wǒ yǒu yí ge péngyou.|Tôi có một người bạn.
本|ben3|bản|classifier|cuốn; quyển (sách, vở)|classifier for books|我买了一本书。|Wǒ mǎi le yì běn shū.|Tôi đã mua một cuốn sách.
些|xie1|tia|classifier|vài; một số; một ít|some; a few|这些是我的书。|Zhèxiē shì wǒ de shū.|Những cuốn này là sách của tôi.
做|zuo4|tác|verb|làm; chế tạo|to do; to make|你想做什么？|Nǐ xiǎng zuò shénme?|Bạn muốn làm gì?
睡觉|shui4 jiao4|thụy giác|verb|ngủ|to sleep|我想睡觉。|Wǒ xiǎng shuìjiào.|Tôi muốn đi ngủ.
打电话|da3 dian4 hua4|đả điện thoại|phrase|gọi điện thoại|to make a phone call|他在打电话。|Tā zài dǎ diànhuà.|Anh ấy đang gọi điện thoại.
回|hui2|hồi|verb|về; quay về|to return; to go back|我们回家吧。|Wǒmen huí jiā ba.|Chúng mình về nhà đi.
下雨|xia4 yu3|hạ vũ|verb|mưa; trời mưa|to rain|今天下雨了。|Jīntiān xià yǔ le.|Hôm nay trời mưa rồi.
冷|leng3|lãnh|adjective|lạnh|cold|今天天气很冷。|Jīntiān tiānqì hěn lěng.|Hôm nay thời tiết rất lạnh.
热|re4|nhiệt|adjective|nóng|hot|水太热了。|Shuǐ tài rè le.|Nước nóng quá rồi.
高兴|gao1 xing4|cao hưng|adjective|vui vẻ; phấn khởi|happy; glad|认识你很高兴。|Rènshi nǐ hěn gāoxìng.|Rất vui được quen biết bạn.
漂亮|piao4 liang5|phiêu lượng|adjective|đẹp; xinh xắn|pretty; beautiful|这件衣服很漂亮。|Zhè jiàn yīfu hěn piàoliang.|Bộ quần áo này rất đẹp.
喂|wei4||interjection|a-lô (chào khi nghe điện thoại); này|hello (on the phone)|喂，你在哪儿？|Wèi, nǐ zài nǎr?|A-lô, bạn đang ở đâu?
和|he2|hòa|conjunction|và; cùng; với|and; with|我和你去。|Wǒ hé nǐ qù.|Tôi và bạn cùng đi.
"""

# Batch 2 (50 items)
BATCH_002_ITEMS = """
怎么样|zen3 me5 yang4||pronoun|thế nào; ra sao|how about; how is it|这本书怎么样？|Zhè běn shū zěnmeyàng?|Cuốn sách này thế nào?
同学|tong2 xue2|đồng học|noun|bạn học; bạn cùng lớp|classmate|他是我的同学。|Tā shì wǒ de tóngxué.|Anh ấy là bạn học của tôi.
小姐|xiao3 jie5|tiểu thư|noun|cô; tiểu thư (cách xưng hô lịch sự)|miss; young lady|王小姐在学校。|Wáng xiǎojiě zài xuéxiào.|Cô Vương đang ở trường học.
先生|xian1 sheng5|tiên sinh|noun|ông; ngài; thầy (cách xưng hô)|Mr.; gentleman|李先生很忙。|Lǐ xiānsheng hěn máng.|Ông Lý rất bận.
名字|ming2 zi5|danh tự|noun|tên; tên gọi|name|你的名字叫什么？|Nǐ de míngzi jiào shénme?|Tên của bạn là gì?
汉语|han4 yu3|Hán ngữ|noun|tiếng Hán; tiếng Trung|Chinese language|我学汉语。|Wǒ xué hànyǔ.|Tôi học tiếng Trung.
字|zi4|tự|noun|chữ; chữ viết|character; word|这个字怎么读？|Zhège zì zěnme dú?|Chữ này đọc thế nào?
点|dian3|điểm|classifier|giờ (thời gian); điểm|o'clock; point|现在是八点。|Xiànzài shì bā diǎn.|Bây giờ là tám giờ.
说话|shuo1 hua4|thuyết thoại|verb|nói chuyện; phát biểu|to speak; to talk|请不要说话。|Qǐng bú yào shuōhuà.|Xin đừng nói chuyện.
看见|kan4 jian4|khán kiến|verb|nhìn thấy; thấy|to see; to catch sight of|我看见他了。|Wǒ kànjiàn tā le.|Tôi nhìn thấy anh ấy rồi.
没|mei2|một|adverb|chưa; không (phủ định hành động)|not; have not|我没去学校。|Wǒ méi qù xuéxiào.|Tôi chưa đến trường học.
哪个|na3 ge4||pronoun|cái nào; người nào|which one|你想买哪个？|Nǐ xiǎng mǎi nǎge?|Bạn muốn mua cái nào?
为什么|wei4 shen2 me5|vi thập ma|pronoun|tại sao; vì sao|why|你为什么不吃米饭？|Nǐ wèishénme bù chī mǐfàn?|Tại sao bạn không ăn cơm?
茶馆|cha2 guan3|trà quán|noun|quán trà|teahouse|我们去茶馆喝茶。|Wǒmen qù cháguǎn hē chá.|Chúng tôi đến quán trà uống trà.
开车|kai1 che1|khai xa|verb|lái xe|to drive a car|他会开车。|Tā huì kāichē.|Anh ấy biết lái xe.
面包|mian4 bao1|miến bao|noun|bánh mì|bread|我早饭吃面包。|Wǒ zǎofàn chī miànbāo.|Bữa sáng tôi ăn bánh mì.
牛奶|niu2 nai3|ngưu nãi|noun|sữa bò; sữa|milk|我每天喝牛奶。|Wǒ měitiān hē niúnǎi.|Mỗi ngày tôi đều uống sữa.
鸡蛋|ji1 dan4|kê đản|noun|trứng gà|egg|我想吃鸡蛋。|Wǒ xiǎng chī jīdàn.|Tôi muốn ăn trứng gà.
鱼|yu2|ngư|noun|con cá; cá|fish|猫喜欢吃鱼。|Māo xǐhuan chī yú.|Mèo thích ăn cá.
羊肉|yang2 rou4|dương nhục|noun|thịt cừu|mutton; lamb|我不吃羊肉。|Wǒ bù chī yángròu.|Tôi không ăn thịt cừu.
西瓜|xi1 gua1|tây qua|noun|dưa hấu|watermelon|夏天的西瓜很甜。|Xiàtiān de xīguā hěn tián.|Dưa hấu mùa hè rất ngọt.
咖啡|ka1 fei1|cà phê|noun|cà phê|coffee|你想喝咖啡吗？|Nǐ xiǎng hē kāfēi ma?|Bạn có muốn uống cà phê không?
跑步|pao3 bu4|bào bộ|verb|chạy bộ|to run; to jog|他喜欢早晨跑步。|Tā xǐhuan zǎochen pǎobù.|Anh ấy thích chạy bộ buổi sáng.
游泳|you2 yong3|du dũng|verb|bơi lội; bơi|to swim|星期天我去游泳。|Xīngqītiān wǒ qù yóuyǒng.|Chủ nhật tôi đi bơi.
踢足球|ti1 zu2 qiu2|thích túc cầu|phrase|đá bóng; đá banh|to play football|我们去踢足球吧。|Wǒmen qù tī zúqiú ba.|Chúng mình đi đá bóng đi.
打篮球|da3 lan2 qiu2|đả lam cầu|phrase|chơi bóng rổ|to play basketball|下午我们打篮球。|Xiàwǔ wǒmen dǎ lánqiú.|Buổi chiều chúng tôi chơi bóng rổ.
唱歌|chang4 ge1|xướng ca|verb|ca hát; hát|to sing|她唱歌唱得很好。|Tā chànggē chàng de hěn hǎo.|Cô ấy hát rất hay.
跳舞|tiao4 wu3|khiêu vũ|verb|nhảy múa; khiêu vũ|to dance|我喜欢跳舞。|Wǒ xǐhuan tiàowǔ.|Tôi thích khiêu vũ.
旅游|lü3 you2|lữ du|verb|du lịch; đi chơi|to travel|我们去中国旅游。|Wǒmen qù Zhōngguó lǚyóu.|Chúng tôi đi Trung Quốc du lịch.
上班|shang4 ban1|thượng ban|verb|đi làm|to go to work|我爸爸八点上班。|Wǒ bàba bā diǎn shàngbān.|Bố tôi tám giờ đi làm.
下班|xia4 ban1|hạ ban|verb|tan làm; tan sở|to get off work|他下午五点下班。|Tā xiàwǔ wǔ diǎn xiàbān.|Anh ấy tan làm lúc năm giờ chiều.
运动|yun4 dong4|vận động|noun|thể thao; vận động|sports; exercise|多做运动对身体好。|Duō zuò yùndòng duì shēntǐ hǎo.|Vận động nhiều tốt cho sức khỏe.
身体|shen1 ti3|thân thể|noun|sức khỏe; thân thể|body; health|你身体好吗？|Nǐ shēntǐ hǎo ma?|Sức khỏe của bạn tốt không?
生病|sheng1 bing4|sinh bệnh|verb|bị bệnh; ốm|to fall ill|他生病了，没来学校。|Tā shēngbìng le, méi lái xuéxiào.|Anh ấy bị ốm rồi, không đến trường học.
药|yao4|dược|noun|thuốc|medicine|你吃药了吗？|Nǐ chī yào le ma?|Bạn đã uống thuốc chưa?
休息|xiu1 xi5|hưu tức|verb|nghỉ ngơi|to rest|请好好休息。|Qǐng hǎohāo xiūxi.|Xin hãy nghỉ ngơi thật tốt.
出门|chu1 men2|xuất môn|verb|ra ngoài; rời nhà|to go out|他出门了。|Tā chūmén le.|Anh ấy ra ngoài rồi.
进|jin4|tiến|verb|vào; tiến vào|to enter; to come in|请进。|Qǐng jìn.|Xin mời vào.
出|chu1|xuất|verb|ra; đi ra|to go out; to exit|他走出教室。|Tā zǒuchū jiàoshì.|Anh ấy bước ra khỏi phòng học.
穿|chuan1|xuyên|verb|mặc (quần áo); đi (giày dép)|to wear; to put on|今天很冷，多穿衣服。|Jīntiān hěn lěng, duō chuān yīfu.|Hôm nay rất lạnh, mặc nhiều quần áo vào.
洗|xi3|tẩy|verb|rửa; giặt|to wash|我先洗手。|Wǒ xiān xǐshǒu.|Tôi rửa tay trước.
给|gei3|cấp|verb|cho; tặng; đưa cho|to give|这是给你的水。|Zhè shì gěi nǐ de shuǐ.|Đây là nước cho bạn.
找|zhao3|trảo|verb|tìm kiếm; trả lại tiền thừa|to look for; to give change|你在找什么？|Nǐ zài zhǎo shénme?|Bạn đang tìm cái gì?
懂|dong3|đổng|verb|hiểu; biết rõ|to understand|这句话你懂吗？|Zhè jù huà nǐ dǒng ma?|Câu này bạn có hiểu không?
问|wen4|vấn|verb|hỏi|to ask|我想问你一个问题。|Wǒ xiǎng wèn nǐ yí ge wèntí.|Tôi muốn hỏi bạn một câu hỏi.
走|zou3|tẩu|verb|đi; bước đi|to walk; to leave|我们走吧。|Wǒmen zǒu ba.|Chúng mình đi thôi.
跑|pao3|bào|verb|chạy|to run|他跑得很慢。|Tā pǎo de hěn màn.|Anh ấy chạy rất chậm.
到|dao4|đáo|verb|đến; tới; đạt tới|to arrive; to reach|我到家了。|Wǒ dào jiā le.|Tôi về đến nhà rồi.
远|yuan3|viễn|adjective|xa|far; distant|我家离学校很远。|Wǒ jiā lí xuéxiào hěn yuǎn.|Nhà tôi cách trường rất xa.
近|jin4|cận|adjective|gần|near; close|商店离这里很近。|Shāngdiàn lí zhèli hěn jìn.|Cửa hàng cách đây rất gần.
"""


def main():
    lines_b1 = [line.strip() for line in BATCH_001_ITEMS.strip().splitlines() if line.strip()]
    lines_b2 = [line.strip() for line in BATCH_002_ITEMS.strip().splitlines() if line.strip()]

    print("Building and validating Level 1 Batch 001...")
    save_batch(level=1, batch_num=1, raw_lines=lines_b1)

    print("Building and validating Level 1 Batch 002...")
    save_batch(level=1, batch_num=2, raw_lines=lines_b2)
    print("Level 1 complete! Total 100 items.")


if __name__ == "__main__":
    main()

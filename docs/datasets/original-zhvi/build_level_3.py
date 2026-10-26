"""Author, validate and register Level 3 vocabulary (300 items across 6 batches)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generator_core import save_batch

# Batch 1 (50 items): Actions, decisions, cognitive verbs
BATCH_001_ITEMS = """
打算|da3 suan4|đả toán|verb|dự định; tính toán|to plan; to intend|明天你打算做什么？|Míngtiān nǐ dǎsuan zuò shénme?|Ngày mai bạn dự định làm gì?
决定|jue2 ding4|quyết định|verb|quyết định|to decide|我已经决定去留学了。|Wǒ yǐjīng juédìng qù liúxué le.|Tôi đã quyết định đi du học rồi.
解决|jie3 jue2|giải quyết|verb|giải quyết (vấn đề)|to resolve; to solve|这个问题很难解决。|Zhège wèntí hěn nán jiějué.|Vấn đề này rất khó giải quyết.
选择|xuan3 ze2|tuyển trạch|verb|chọn lựa; lựa chọn|to choose; to select|你要认真选择你的专业。|Nǐ yào rènzhēn xuǎnzé nǐ de zhuānyè.|Bạn cần lựa chọn chuyên ngành cẩn thận.
同意|tong2 yi4|đồng ý|verb|đồng ý; tán thành|to agree|大家都同意这个想法。|Dàjiā dōu tóngyì zhège xiǎngfǎ.|Mọi người đều đồng ý với ý kiến này.
习惯|xi2 guan4|tập quán|verb|quen; thói quen|to be used to; habit|我已经习惯了这里的生活。|Wǒ yǐjīng xíguàn le zhèli de shēnghuó.|Tôi đã quen với cuộc sống ở đây rồi.
愿意|yuan4 yi4|nguyện ý|verb|bằng lòng; sẵn lòng|to be willing|你愿意帮我一个忙吗？|Nǐ yuànyì bāng wǒ yí ge máng ma?|Bạn có sẵn lòng giúp tôi một việc không?
照顾|zhao4 gu5|chiếu cố|verb|chăm sóc; trông nom|to look after; to take care of|姐姐很会照顾小孩子。|Jiějie hěn huì zhàogu xiǎoháizi.|Chị gái rất biết cách chăm sóc trẻ con.
相信|xiang1 xin4|tương tín|verb|tin tưởng; tin|to believe; to trust|我相信你一定能做到。|Wǒ xiāngxìn nǐ yídìng néng zuòdào.|Tôi tin rằng bạn nhất định có thể làm được.
发现|fa1 xian4|phát hiện|verb|phát hiện; nhận ra|to discover; to find out|我发现我的钱包不见了。|Wǒ fāxiàn wǒ de qiánbāo bújiàn le.|Tôi phát hiện ví tiền của mình bị mất rồi.
记得|ji4 de5|ký đắc|verb|nhớ; còn nhớ|to remember|你还记得他的名字吗？|Nǐ hái jìde tā de míngzi ma?|Bạn còn nhớ tên của anh ấy không?
忘记|wang4 ji4|vong ký|verb|quên; bỏ quên|to forget|我忘记带手机了。|Wǒ wàngjì dài shǒujī le.|Tôi quên mang theo điện thoại rồi.
影响|ying3 xiang3|ảnh hưởng|verb|ảnh hưởng; tác động|to influence; to affect|经常熬夜会影响健康。|Jīngcháng áoyè huì yǐngxiǎng jiànkāng.|Thường xuyên thức khuya sẽ ảnh hưởng sức khỏe.
比较|bi3 jiao4|tỷ giác|verb|so sánh; tương đối|to compare; relatively|今天比较冷，多穿件衣服。|Jīntiān bǐjiào lěng, duō chuān jiàn yīfu.|Hôm nay tương đối lạnh, mặc thêm áo vào.
提高|ti2 gao1|đề cao|verb|nâng cao; cải thiện|to improve; to raise|我想提高我的汉语水平。|Wǒ xiǎng tígāo wǒ de hànyǔ shuǐpíng.|Tôi muốn nâng cao trình độ tiếng Trung của mình.
迟到|chi2 dao4|trì đáo|verb|đến muộn; đi trễ|to arrive late|今天早上我迟到了。|Jīntiān zǎoshang wǒ chídào le.|Sáng nay tôi đã bị muộn.
搬|ban1|ban|verb|dọn; chuyển; bê|to move; to shift|我下个月要搬家。|Wǒ xià ge yuè yào bānjiā.|Tháng sau tôi phải chuyển nhà.
换|huan4|hoán|verb|đổi; thay|to change; to exchange|我想换一些人民币。|Wǒ xiǎng huàn yìxiē rénmínbì.|Tôi muốn đổi một ít đồng nhân dân tệ.
带|dai4|đới|verb|mang theo; dắt; dẫn|to bring; to carry|出门别忘了带雨伞。|Chūmén bié wàng le dài yǔsǎn.|Ra ngoài đừng quên mang theo ô.
拿|na2|nã|verb|cầm; nắm; lấy|to take; to hold|请帮我拿一下包。|Qǐng bāng wǒ ná yíxià bāo.|Xin giúp tôi cầm cái túi một lát.
放|fang4|phóng|verb|đặt; để; thả|to put; to place|把书放在桌子上。|Bǎ shū fàng zài zhuōzi shang.|Đặt cuốn sách lên trên bàn.
留|liu2|lưu|verb|ở lại; giữ lại; lưu lại|to stay; to remain|他决定留在中国工作。|Tā juédìng liú zài Zhōngguó gōngzuò.|Anh ấy quyết định ở lại Trung Quốc làm việc.
碰|peng4|bành|verb|chạm; va chạm; gặp|to touch; to bump; to meet|今天在路上碰到了老同学。|Jīntiān zài lù shang pèngdào le lǎo tóngxué.|Hôm nay trên đường tôi tình cờ gặp bạn học cũ.
掉|diao4|điệu|verb|rơi; rớt; tụt|to drop; to fall|钥匙掉在地上。|Yàoshi diào zài dì shang.|Chìa khóa rơi trên mặt đất.
挂|gua4|quải|verb|treo; mắc; cúp (máy)|to hang; to put up|墙上挂着一张世界地图。|Qiáng shang guà zhe yì zhāng shìjiè dìtú.|Trên tường có treo một tấm bản đồ thế giới.
贴|tie1|thiếp|verb|dán; dính|to stick; to paste|门上贴着一张红纸。|Mén shang tiē zhe yì zhāng hóng zhǐ.|Trên cửa có dán một tờ giấy đỏ.
抽|chou1|trừu|verb|rút ra; hút (thuốc)|to draw out; to smoke|抽烟对身体非常有害。|Chōuyān duì shēntǐ fēicháng yǒuhài.|Hút thuốc rất có hại cho sức khỏe.
算|suan4|toán|verb|tính; tính toán|to calculate; to count|这件事不能算完。|Zhè jiàn shì bù néng suàn wán.|Chuyện này không thể coi như xong.
查|cha2|tra|verb|tra cứu; kiểm tra|to check; to look up|请查一下字典。|Qǐng chá yíxià zìdiǎn.|Xin hãy tra từ điển một chút.
画|hua4|họa|verb|vẽ (tranh)|to draw; to paint|她很喜欢画画儿。|Tā hěn xǐhuan huà huàr.|Cô ấy rất thích vẽ tranh.
爬|pa2|ba|verb|leo; trèo; bò|to climb; to crawl|周末我们去爬山吧。|Zhōumò wǒmen qù páshān ba.|Cuối tuần chúng mình đi leo núi đi.
讲|jiang3|giảng|verb|nói; kể; giảng giải|to speak; to explain|老师正在给学生讲课。|Lǎoshī zhèngzài gěi xuésheng jiǎngkè.|Thầy giáo đang giảng bài cho học sinh.
聊|liao2|liêu|verb|nói chuyện; trò chuyện|to chat|我们经常在网上聊天。|Wǒmen jīngcháng zài wǎng shang liáotiān.|Chúng tôi thường trò chuyện trên mạng.
接|jie1|tiếp|verb|đón; nhận (điện thoại)|to receive; to pick up|我去机场接朋友。|Wǒ qù jīchǎng jiē péngyou.|Tôi đi sân bay đón bạn.
寄|ji4|ký|verb|gửi (thư, hàng)|to mail; to send|我想给家里寄一封信。|Wǒ xiǎng gěi jiā li jì yì fēng xìn.|Tôi muốn gửi một bức thư về nhà.
检查|jian3 cha2|kiểm tra|verb|kiểm tra; xem xét|to inspect; to check|医生正在给他检查身体。|Yīshēng zhèngzài gěi tā jiǎnchá shēntǐ.|Bác sĩ đang khám sức khỏe cho anh ấy.
练习|lian4 xi2|luyện tập|verb|luyện tập; bài tập|to practice; exercise|每天多练习说汉语。|Měitiān duō liànxí shuō hànyǔ.|Mỗi ngày hãy luyện nói tiếng Trung nhiều hơn.
遇到|yu4 dao4|ngộ đáo|verb|gặp phải; bắt gặp|to meet; to encounter|遇到困难不要害怕。|Yùdào kùnnan bú yào hàipà.|Gặp phải khó khăn đừng sợ hãi.
出现|chu1 xian4|xuất hiện|verb|xuất hiện; nảy sinh|to appear; to arise|电脑屏幕上出现了一个错误。|Diànnǎo píngmù shang chūxiàn le yí ge cuòwù.|Trên màn hình máy tính xuất hiện một lỗi.
变化|bian4 hua4|biến hóa|verb|thay đổi; biến đổi|to change; variation|这座城市的变化很大。|Zhè zuò chéngshì de biànhuà hěn dà.|Sự thay đổi của thành phố này rất lớn.
完成|wan2 cheng2|hoàn thành|verb|hoàn thành; làm xong|我终于完成了这项任务。|Wǒ zhōngyú wánchéng le zhè xiàng rènwu.|Tôi cuối cùng đã hoàn thành nhiệm vụ này.
了解|liao3 jie3|liễu giải|verb|hiểu rõ; tìm hiểu|to understand; to know well|我想了解中国文化。|Wǒ xiǎng liǎojiě zhōngguó wénhuà.|Tôi muốn tìm hiểu văn hóa Trung Quốc.
关心|guan1 xin1|quan tâm|verb|quan tâm; để ý|to care for; to be concerned|父母非常关心孩子的生活。|Fùmǔ fēicháng guānxīn háizi de shēnghuó.|Bố mẹ rất quan tâm đến cuộc sống của con cái.
放心|fang4 xin1|phóng tâm|verb|yên tâm; an lòng|to feel relieved|你放心，我会照顾好自己的。|Nǐ fàngxīn, wǒ huì zhàogu hǎo zìjǐ de.|Bạn yên tâm, tôi sẽ chăm sóc tốt cho bản thân.
担心|dan1 xin1|đam tâm|verb|lo lắng; lo âu|to worry; to be anxious|别担心，事情很快会好起来的。|Bié dānxīn, shìqing kuài huì hǎo qǐlai de.|Đừng lo lắng, mọi chuyện sẽ sớm tốt lên thôi.
生发|sheng1 fa1|sinh phát|verb|mọc tóc; phát sinh|to grow hair; to sprout|这种植物在春天生发。|Zhè zhǒng zhíwù zài chūntiān shēngfā.|Loại thực vật này đâm chồi vào mùa xuân.
生病|sheng1 bing4|sinh bệnh|verb|ốm; phát bệnh|to get sick|天气忽冷忽热容易生病。|Tiānqì hū lěng hū rè róngyì shēngbìng.|Thời tiết lúc nóng lúc lạnh rất dễ bị ốm.
同意|tong2 yi4|đồng ý|verb|đồng ý; nhất trí|to agree|老师同意了我的请求。|Lǎoshī tóngyì le wǒ de qǐngqiú.|Thầy giáo đã đồng ý lời thỉnh cầu của tôi.
敢|gan3|cảm|verb|dám|to dare|他不敢一个人走夜路。|Tā bù gǎn yí ge rén zǒu yèlù.|Anh ấy không dám đi đường đêm một mình.
打算|da3 suan4|đả toán|verb|dự tính; định làm|to plan; to consider|毕业后你打算做什么工作？|Bìyè hòu nǐ dǎsuan zuò shénme gōngzuò?|Sau khi tốt nghiệp bạn định làm công việc gì?
"""

# Let's fix duplicate items within batch 001 list before running:
# In BATCH_001_ITEMS: check duplicates: 同意, 打算, 生病 were entered twice.
# Let's clean and ensure 50 distinct items:
BATCH_001_CLEAN = """
打算|da3 suan4|đả toán|verb|dự định; tính toán|to plan; to intend|明天你打算做什么？|Míngtiān nǐ dǎsuan zuò shénme?|Ngày mai bạn dự định làm gì?
决定|jue2 ding4|quyết định|verb|quyết định|to decide|我已经决定去留学了。|Wǒ yǐjīng juédìng qù liúxué le.|Tôi đã quyết định đi du học rồi.
解决|jie3 jue2|giải quyết|verb|giải quyết (vấn đề)|to resolve; to solve|这个问题很难解决。|Zhège wèntí hěn nán jiějué.|Vấn đề này rất khó giải quyết.
选择|xuan3 ze2|tuyển trạch|verb|chọn lựa; lựa chọn|to choose; to select|你要认真选择你的专业。|Nǐ yào rènzhēn xuǎnzé nǐ de zhuānyè.|Bạn cần lựa chọn chuyên ngành cẩn thận.
同意|tong2 yi4|đồng ý|verb|đồng ý; tán thành|to agree|大家都同意这个想法。|Dàjiā dōu tóngyì zhège xiǎngfǎ.|Mọi người đều đồng ý với ý kiến này.
习惯|xi2 guan4|tập quán|verb|quen; thói quen|to be used to; habit|我已经习惯了这里的生活。|Wǒ yǐjīng xíguàn le zhèli de shēnghuó.|Tôi đã quen với cuộc sống ở đây rồi.
愿意|yuan4 yi4|nguyện ý|verb|bằng lòng; sẵn lòng|to be willing|你愿意帮我一个忙吗？|Nǐ yuànyì bāng wǒ yí ge máng ma?|Bạn có sẵn lòng giúp tôi một việc không?
照顾|zhao4 gu5|chiếu cố|verb|chăm sóc; trông nom|to look after; to take care of|姐姐很会照顾小孩子。|Jiějie hěn huì zhàogu xiǎoháizi.|Chị gái rất biết cách chăm sóc trẻ con.
相信|xiang1 xin4|tương tín|verb|tin tưởng; tin|to believe; to trust|我相信你一定能做到。|Wǒ xiāngxìn nǐ yídìng néng zuòdào.|Tôi tin rằng bạn nhất định có thể làm được.
发现|fa1 xian4|phát hiện|verb|phát hiện; nhận ra|to discover; to find out|我发现我的钱包不见了。|Wǒ fāxiàn wǒ de qiánbāo bújiàn le.|Tôi phát hiện ví tiền của mình bị mất rồi.
记得|ji4 de5|ký đắc|verb|nhớ; còn nhớ|to remember|你还记得他的名字吗？|Nǐ hái jìde tā de míngzi ma?|Bạn còn nhớ tên của anh ấy không?
忘记|wang4 ji4|vong ký|verb|quên; bỏ quên|to forget|我忘记带手机了。|Wǒ wàngjì dài shǒujī le.|Tôi quên mang theo điện thoại rồi.
影响|ying3 xiang3|ảnh hưởng|verb|ảnh hưởng; tác động|to influence; to affect|经常熬夜会影响健康。|Jīngcháng áoyè huì yǐngxiǎng jiànkāng.|Thường xuyên thức khuya sẽ ảnh hưởng sức khỏe.
比较|bi3 jiao4|tỷ giác|verb|so sánh; tương đối|to compare; relatively|今天比较冷，多穿件衣服。|Jīntiān bǐjiào lěng, duō chuān jiàn yīfu.|Hôm nay tương đối lạnh, mặc thêm áo vào.
提高|ti2 gao1|đề cao|verb|nâng cao; cải thiện|to improve; to raise|我想提高我的汉语水平。|Wǒ xiǎng tígāo wǒ de hànyǔ shuǐpíng.|Tôi muốn nâng cao trình độ tiếng Trung của mình.
迟到|chi2 dao4|trì đáo|verb|đến muộn; đi trễ|to arrive late|今天早上我迟到了。|Jīntiān zǎoshang wǒ chídào le.|Sáng nay tôi đã bị muộn.
搬|ban1|ban|verb|dọn; chuyển; bê|to move; to shift|我下个月要搬家。|Wǒ xià ge yuè yào bānjiā.|Tháng sau tôi phải chuyển nhà.
换|huan4|hoán|verb|đổi; thay|to change; to exchange|我想换一些人民币。|Wǒ xiǎng huàn yìxiē rénmínbì.|Tôi muốn đổi một ít đồng nhân dân tệ.
带|dai4|đới|verb|mang theo; dắt; dẫn|to bring; to carry|出门别忘了带雨伞。|Chūmén bié wàng le dài yǔsǎn.|Ra ngoài đừng quên mang theo ô.
拿|na2|nã|verb|cầm; nắm; lấy|to take; to hold|请帮我拿一下包。|Qǐng bāng wǒ ná yíxià bāo.|Xin giúp tôi cầm cái túi một lát.
放|fang4|phóng|verb|đặt; để; thả|to put; to place|把书放在桌子上。|Bǎ shū fàng zài zhuōzi shang.|Đặt cuốn sách lên trên bàn.
留|liu2|lưu|verb|ở lại; giữ lại; lưu lại|to stay; to remain|他决定留在中国工作。|Tā juédìng liú zài Zhōngguó gōngzuò.|Anh ấy quyết định ở lại Trung Quốc làm việc.
碰|peng4|bành|verb|chạm; va chạm; gặp|to touch; to bump; to meet|今天在路上碰到了老同学。|Jīntiān zài lù shang pèngdào le lǎo tóngxué.|Hôm nay trên đường tôi tình cờ gặp bạn học cũ.
掉|diao4|điệu|verb|rơi; rớt; tụt|to drop; to fall|钥匙掉在地上。|Yàoshi diào zài dì shang.|Chìa khóa rơi trên mặt đất.
挂|gua4|quải|verb|treo; mắc; cúp (máy)|to hang; to put up|墙上挂着一张世界地图。|Qiáng shang guà zhe yì zhāng shìjiè dìtú.|Trên tường có treo một tấm bản đồ thế giới.
贴|tie1|thiếp|verb|dán; dính|to stick; to paste|门上贴着一张红纸。|Mén shang tiē zhe yì zhāng hóng zhǐ.|Trên cửa có dán một tờ giấy đỏ.
抽|chou1|trừu|verb|rút ra; hút (thuốc)|to draw out; to smoke|抽烟对身体非常有害。|Chōuyān duì shēntǐ fēicháng yǒuhài.|Hút thuốc rất có hại cho sức khỏe.
算|suan4|toán|verb|tính; tính toán|to calculate; to count|这件事不能算完。|Zhè jiàn shì bù néng suàn wán.|Chuyện này không thể coi như xong.
查|cha2|tra|verb|tra cứu; kiểm tra|to check; to look up|请查一下字典。|Qǐng chá yíxià zìdiǎn.|Xin hãy tra từ điển một chút.
画|hua4|họa|verb|vẽ (tranh)|to draw; to paint|她很喜欢画画儿。|Tā hěn xǐhuan huà huàr.|Cô ấy rất thích vẽ tranh.
爬|pa2|ba|verb|leo; trèo; bò|to climb; to crawl|周末我们去爬山吧。|Zhōumò wǒmen qù páshān ba.|Cuối tuần chúng mình đi leo núi đi.
讲|jiang3|giảng|verb|nói; kể; giảng giải|to speak; to explain|老师正在给学生讲课。|Lǎoshī zhèngzài gěi xuésheng jiǎngkè.|Thầy giáo đang giảng bài cho học sinh.
聊|liao2|liêu|verb|nói chuyện; trò chuyện|to chat|我们经常在网上聊天。|Wǒmen jīngcháng zài wǎng shang liáotiān.|Chúng tôi thường trò chuyện trên mạng.
接|jie1|tiếp|verb|đón; nhận (điện thoại)|to receive; to pick up|我去机场接朋友。|Wǒ qù jīchǎng jiē péngyou.|Tôi đi sân bay đón bạn.
寄|ji4|ký|verb|gửi (thư, hàng)|to mail; to send|我想给家里寄一封信。|Wǒ xiǎng gěi jiā li jì yì fēng xìn.|Tôi muốn gửi một bức thư về nhà.
检查|jian3 cha2|kiểm tra|verb|kiểm tra; xem xét|to inspect; to check|医生正在给他检查身体。|Yīshēng zhèngzài gěi tā jiǎnchá shēntǐ.|Bác sĩ đang khám sức khỏe cho anh ấy.
练习|lian4 xi2|luyện tập|verb|luyện tập; bài tập|to practice; exercise|每天多练习说汉语。|Měitiān duō liànxí shuō hànyǔ.|Mỗi ngày hãy luyện nói tiếng Trung nhiều hơn.
遇到|yu4 dao4|ngộ đáo|verb|gặp phải; bắt gặp|to meet; to encounter|遇到困难不要害怕。|Yùdào kùnnan bú yào hàipà.|Gặp phải khó khăn đừng sợ hãi.
出现|chu1 xian4|xuất hiện|verb|xuất hiện; nảy sinh|to appear; to arise|电脑屏幕上出现了一个错误。|Diànnǎo píngmù shang chūxiàn le yí ge cuòwù.|Trên màn hình máy tính xuất hiện một lỗi.
变化|bian4 hua4|biến hóa|verb|thay đổi; biến đổi|to change; variation|这座城市的变化很大。|Zhè zuò chéngshì de biànhuà hěn dà.|Sự thay đổi của thành phố này rất lớn.
完成|wan2 cheng2|hoàn thành|verb|hoàn thành; làm xong|我终于完成了这项任务。|Wǒ zhōngyú wánchéng le zhè xiàng rènwu.|Tôi cuối cùng đã hoàn thành nhiệm vụ này.
了解|liao3 jie3|liễu giải|verb|hiểu rõ; tìm hiểu|to understand; to know well|我想了解中国文化。|Wǒ xiǎng liǎojiě zhōngguó wénhuà.|Tôi muốn tìm hiểu văn hóa Trung Quốc.
关心|guan1 xin1|quan tâm|verb|quan tâm; để ý|to care for; to be concerned|父母非常关心孩子的生活。|Fùmǔ fēicháng guānxīn háizi de shēnghuó.|Bố mẹ rất quan tâm đến cuộc sống của con cái.
放心|fang4 xin1|phóng tâm|verb|yên tâm; an lòng|to feel relieved|你放心，我会照顾好自己的。|Nǐ fàngxīn, wǒ huì zhàogu hǎo zìjǐ de.|Bạn yên tâm, tôi sẽ chăm sóc tốt cho bản thân.
担心|dan1 xin1|đam tâm|verb|lo lắng; lo âu|to worry; to be anxious|别担心，事情很快会好起来的。|Bié dānxīn, shìqing kuài huì hǎo qǐlai de.|Đừng lo lắng, mọi chuyện sẽ sớm tốt lên thôi.
敢|gan3|cảm|verb|dám|to dare|他不敢一个人走夜路。|Tā bù gǎn yí ge rén zǒu yèlù.|Anh ấy không dám đi đường đêm một mình.
生发|sheng1 fa1|sinh phát|verb|mọc tóc; phát sinh|to grow hair; to sprout|这种植物在春天生发。|Zhè zhǒng zhíwù zài chūntiān shēngfā.|Loại thực vật này đâm chồi vào mùa xuân.
愿意|yuan4 yi4|nguyện ý|verb|bằng lòng; ưng thuận|to be willing|我愿意和你一起努力。|Wǒ yuànyì hé nǐ yìqǐ nǔlì.|Tôi sẵn lòng cùng bạn cố gắng.
相信|xiang1 xin4|tương tín|verb|tin; tin tưởng|to believe|请相信我的话。|Qǐng xiāngxìn wǒ de huà.|Xin hãy tin lời tôi nói.
难过|nan2 guo4|nan quá|adjective|buồn rầu; đau lòng|sad; sorrowful|听到这个坏消息他很难过。|Tīngdào zhège huài xiāoxi tā hěn nánguò.|Nghe thấy tin xấu này anh ấy rất buồn.
"""

# Let's fix line 48 and 49 of BATCH_001_CLEAN (愿意 and 相信 are duplicated).
# Replace with: 祝 (zhu4), 发现 (already in), 借 (already in L2), 结束 (jie2 shu4), 迟到 (already in), 参加 (in L2), 保护 (bao3 hu4)
BATCH_001 = """
打算|da3 suan4|đả toán|verb|dự định; tính toán|to plan; to intend|明天你打算做什么？|Míngtiān nǐ dǎsuan zuò shénme?|Ngày mai bạn dự định làm gì?
决定|jue2 ding4|quyết định|verb|quyết định|to decide|我已经决定去留学了。|Wǒ yǐjīng juédìng qù liúxué le.|Tôi đã quyết định đi du học rồi.
解决|jie3 jue2|giải quyết|verb|giải quyết (vấn đề)|to resolve; to solve|这个问题很难解决。|Zhège wèntí hěn nán jiějué.|Vấn đề này rất khó giải quyết.
选择|xuan3 ze2|tuyển trạch|verb|chọn lựa; lựa chọn|to choose; to select|你要认真选择你的专业。|Nǐ yào rènzhēn xuǎnzé nǐ de zhuānyè.|Bạn cần lựa chọn chuyên ngành cẩn thận.
同意|tong2 yi4|đồng ý|verb|đồng ý; tán thành|to agree|大家都同意这个想法。|Dàjiā dōu tóngyì zhège xiǎngfǎ.|Mọi người đều đồng ý với ý kiến này.
习惯|xi2 guan4|tập quán|verb|quen; thói quen|to be used to; habit|我已经习惯了这里的生活。|Wǒ yǐjīng xíguàn le zhèli de shēnghuó.|Tôi đã quen với cuộc sống ở đây rồi.
愿意|yuan4 yi4|nguyện ý|verb|bằng lòng; sẵn lòng|to be willing|你愿意帮我一个忙吗？|Nǐ yuànyì bāng wǒ yí ge máng ma?|Bạn có sẵn lòng giúp tôi một việc không?
照顾|zhao4 gu5|chiếu cố|verb|chăm sóc; trông nom|to look after; to take care of|姐姐很会照顾小孩子。|Jiějie hěn huì zhàogu xiǎoháizi.|Chị gái rất biết cách chăm sóc trẻ con.
相信|xiang1 xin4|tương tín|verb|tin tưởng; tin|to believe; to trust|我相信你一定能做到。|Wǒ xiāngxìn nǐ yídìng néng zuòdào.|Tôi tin rằng bạn nhất định có thể làm được.
发现|fa1 xian4|phát hiện|verb|phát hiện; nhận ra|to discover; to find out|我发现我的钱包不见了。|Wǒ fāxiàn wǒ de qiánbāo bújiàn le.|Tôi phát hiện ví tiền của mình bị mất rồi.
记得|ji4 de5|ký đắc|verb|nhớ; còn nhớ|to remember|你还记得他的名字吗？|Nǐ hái jìde tā de míngzi ma?|Bạn còn nhớ tên của anh ấy không?
忘记|wang4 ji4|vong ký|verb|quên; bỏ quên|to forget|我忘记带手机了。|Wǒ wàngjì dài shǒujī le.|Tôi quên mang theo điện thoại rồi.
影响|ying3 xiang3|ảnh hưởng|verb|ảnh hưởng; tác động|to influence; to affect|经常熬夜会影响健康。|Jīngcháng áoyè huì yǐngxiǎng jiànkāng.|Thường xuyên thức khuya sẽ ảnh hưởng sức khỏe.
比较|bi3 jiao4|tỷ giác|verb|so sánh; tương đối|to compare; relatively|今天比较冷，多穿件衣服。|Jīntiān bǐjiào lěng, duō chuān jiàn yīfu.|Hôm nay tương đối lạnh, mặc thêm áo vào.
提高|ti2 gao1|đề cao|verb|nâng cao; cải thiện|to improve; to raise|我想提高我的汉语水平。|Wǒ xiǎng tígāo wǒ de hànyǔ shuǐpíng.|Tôi muốn nâng cao trình độ tiếng Trung của mình.
迟到|chi2 dao4|trì đáo|verb|đến muộn; đi trễ|to arrive late|今天早上我迟到了。|Jīntiān zǎoshang wǒ chídào le.|Sáng nay tôi đã bị muộn.
搬|ban1|ban|verb|dọn; chuyển; bê|to move; to shift|我下个月要搬家。|Wǒ xià ge yuè yào bānjiā.|Tháng sau tôi phải chuyển nhà.
换|huan4|hoán|verb|đổi; thay|to change; to exchange|我想换一些人民币。|Wǒ xiǎng huàn yìxiē rénmínbì.|Tôi muốn đổi một ít đồng nhân dân tệ.
带|dai4|đới|verb|mang theo; dắt; dẫn|to bring; to carry|出门别忘了带雨伞。|Chūmén bié wàng le dài yǔsǎn.|Ra ngoài đừng quên mang theo ô.
拿|na2|nã|verb|cầm; nắm; lấy|to take; to hold|请帮我拿一下包。|Qǐng bāng wǒ ná yíxià bāo.|Xin giúp tôi cầm cái túi một lát.
放|fang4|phóng|verb|đặt; để; thả|to put; to place|把书放在桌子上。|Bǎ shū fàng zài zhuōzi shang.|Đặt cuốn sách lên trên bàn.
留|liu2|lưu|verb|ở lại; giữ lại; lưu lại|to stay; to remain|他决定留在中国工作。|Tā juédìng liú zài Zhōngguó gōngzuò.|Anh ấy quyết định ở lại Trung Quốc làm việc.
碰|peng4|bành|verb|chạm; va chạm; gặp|to touch; to bump; to meet|今天在路上碰到了老同学。|Jīntiān zài lù shang pèngdào le lǎo tóngxué.|Hôm nay trên đường tôi tình cờ gặp bạn học cũ.
掉|diao4|điệu|verb|rơi; rớt; tụt|to drop; to fall|钥匙掉在地上。|Yàoshi diào zài dì shang.|Chìa khóa rơi trên mặt đất.
挂|gua4|quải|verb|treo; mắc; cúp (máy)|to hang; to put up|墙上挂着一张世界地图。|Qiáng shang guà zhe yì zhāng shìjiè dìtú.|Trên tường có treo một tấm bản đồ thế giới.
贴|tie1|thiếp|verb|dán; dính|to stick; to paste|门上贴着一张红纸。|Mén shang tiē zhe yì zhāng hóng zhǐ.|Trên cửa có dán một tờ giấy đỏ.
抽|chou1|trừu|verb|rút ra; hút (thuốc)|to draw out; to smoke|抽烟对身体非常有害。|Chōuyān duì shēntǐ fēicháng yǒuhài.|Hút thuốc rất có hại cho sức khỏe.
算|suan4|toán|verb|tính; tính toán|to calculate; to count|这件事不能算完。|Zhè jiàn shì bù néng suàn wán.|Chuyện này không thể coi như xong.
查|cha2|tra|verb|tra cứu; kiểm tra|to check; to look up|请查一下字典。|Qǐng chá yíxià zìdiǎn.|Xin hãy tra từ điển một chút.
画|hua4|họa|verb|vẽ (tranh)|to draw; to paint|她很喜欢画画儿。|Tā hěn xǐhuan huà huàr.|Cô ấy rất thích vẽ tranh.
爬|pa2|ba|verb|leo; trèo; bò|to climb; to crawl|周末我们去爬山吧。|Zhōumò wǒmen qù páshān ba.|Cuối tuần chúng mình đi leo núi đi.
讲|jiang3|giảng|verb|nói; kể; giảng giải|to speak; to explain|老师正在给学生讲课。|Lǎoshī zhèngzài gěi xuésheng jiǎngkè.|Thầy giáo đang giảng bài cho học sinh.
聊|liao2|liêu|verb|nói chuyện; trò chuyện|to chat|我们经常在网上聊天。|Wǒmen jīngcháng zài wǎng shang liáotiān.|Chúng tôi thường trò chuyện trên mạng.
接|jie1|tiếp|verb|đón; nhận (điện thoại)|to receive; to pick up|我去机场接朋友。|Wǒ qù jīchǎng jiē péngyou.|Tôi đi sân bay đón bạn.
寄|ji4|ký|verb|gửi (thư, hàng)|to mail; to send|我想给家里寄一封信。|Wǒ xiǎng gěi jiā li jì yì fēng xìn.|Tôi muốn gửi một bức thư về nhà.
检查|jian3 cha2|kiểm tra|verb|kiểm tra; xem xét|to inspect; to check|医生正在给他检查身体。|Yīshēng zhèngzài gěi tā jiǎnchá shēntǐ.|Bác sĩ đang khám sức khỏe cho anh ấy.
练习|lian4 xi2|luyện tập|verb|luyện tập; bài tập|to practice; exercise|每天多练习说汉语。|Měitiān duō liànxí shuō hànyǔ.|Mỗi ngày hãy luyện nói tiếng Trung nhiều hơn.
遇到|yu4 dao4|ngộ đáo|verb|gặp phải; bắt gặp|to meet; to encounter|遇到困难不要害怕。|Yùdào kùnnan bú yào hàipà.|Gặp phải khó khăn đừng sợ hãi.
出现|chu1 xian4|xuất hiện|verb|xuất hiện; nảy sinh|to appear; to arise|电脑屏幕上出现了一个错误。|Diànnǎo píngmù shang chūxiàn le yí ge cuòwù.|Trên màn hình máy tính xuất hiện một lỗi.
变化|bian4 hua4|biến hóa|verb|thay đổi; biến đổi|to change; variation|这座城市的变化很大。|Zhè zuò chéngshì de biànhuà hěn dà.|Sự thay đổi của thành phố này rất lớn.
完成|wan2 cheng2|hoàn thành|verb|hoàn thành; làm xong|to complete; to finish|我终于完成了这项任务。|Wǒ zhōngyú wánchéng le zhè xiàng rènwu.|Tôi cuối cùng đã hoàn thành nhiệm vụ này.
了解|liao3 jie3|liễu giải|verb|hiểu rõ; tìm hiểu|to understand; to know well|我想了解中国文化。|Wǒ xiǎng liǎojiě zhōngguó wénhuà.|Tôi muốn tìm hiểu văn hóa Trung Quốc.
关心|guan1 xin1|quan tâm|verb|quan tâm; để ý|to care for; to be concerned|父母非常关心孩子的生活。|Fùmǔ fēicháng guānxīn háizi de shēnghuó.|Bố mẹ rất quan tâm đến cuộc sống của con cái.
放心|fang4 xin1|phóng tâm|verb|yên tâm; an lòng|to feel relieved|你放心，我会照顾好自己的。|Nǐ fàngxīn, wǒ huì zhàogu hǎo zìjǐ de.|Bạn yên tâm, tôi sẽ chăm sóc tốt cho bản thân.
担心|dan1 xin1|đam tâm|verb|lo lắng; lo âu|to worry; to be anxious|别担心，事情很快会好起来的。|Bié dānxīn, shìqing kuài huì hǎo qǐlai de.|Đừng lo lắng, mọi chuyện sẽ sớm tốt lên thôi.
敢|gan3|cảm|verb|dám|to dare|他不敢一个人走夜路。|Tā bù gǎn yí ge rén zǒu yèlù.|Anh ấy không dám đi đường đêm một mình.
生发|sheng1 fa1|sinh phát|verb|mọc tóc; phát sinh|to grow hair; to sprout|这种植物在春天生发。|Zhè zhǒng zhíwù zài chūntiān shēngfā.|Loại thực vật này đâm chồi vào mùa xuân.
结束|jie2 shu4|kết thúc|verb|kết thúc; chấm dứt|to end; to finish|电影十点结束。|Diànyǐng shí diǎn jiéshù.|Bộ phim kết thúc lúc mười giờ.
祝|zhu4|chúc|verb|chúc; chúc mừng|to wish; to express good wishes|祝你生日快乐！|Zhù nǐ shēngrì kuàilè!|Chúc bạn sinh nhật vui vẻ!
难过|nan2 guo4|nan quá|adjective|buồn rầu; đau lòng|sad; sorrowful|听到这个坏消息他很难过。|Tīngdào zhège huài xiāoxi tā hěn nánguò.|Nghe thấy tin xấu này anh ấy rất buồn.
"""

# Batch 2 (50 items): States, descriptions, qualities, attitudes
BATCH_002 = """
着急|zhao2 ji2|trước cấp|adjective|sốt ruột; lo lắng; vội vàng|anxious; worried|别着急，慢慢说。|Bié zháojí, mànmàn shuō.|Đừng sốt ruột, hãy nói từ từ.
生气|sheng1 qi4|sinh khí|adjective|tức giận; giận dỗi|angry; mad|他因为这件事生气了。|Tā yīnwèi zhè jiàn shì shēngqì le.|Anh ấy tức giận vì chuyện này rồi.
奇怪|qi2 guai4|kỳ quái|adjective|kỳ lạ; quái lạ|strange; weird|这件事情很奇怪。|Zhè jiàn shìqing hěn qíguài.|Chuyện này rất kỳ lạ.
热情|re4 qing2|nhiệt tình|adjective|nhiệt tình; niềm nở|warm-hearted; enthusiastic|中国人对客人很热情。|Zhōngguórén duì kèrén hěn rèqíng.|Người Trung Quốc rất nhiệt tình với khách.
认真|ren4 zhen1|nhận chân|adjective|nghiêm túc; chăm chỉ|serious; earnest|他学习非常认真。|Tā xuéxí fēicháng rènzhēn.|Anh ấy học tập vô cùng chăm chỉ.
聪明|cong1 ming5|thông minh|adjective|thông minh; sáng dạ|clever; intelligent|这个小男孩很聪明。|Zhège xiǎo nánhái hěn cōngming.|Cậu bé này rất thông minh.
努力|nu3 li4|nỗ lực|adjective|nỗ lực; chăm chỉ|hardworking; to strive|只要努力就能成功。|Zhǐyào nǔlì jiù néng chénggōng.|Chỉ cần nỗ lực thì sẽ thành công.
新鲜|xin1 xian1|tân tiên|adjective|tươi mới; trong lành|fresh|早晨的空气很新鲜。|Zǎochen de kōngqì hěn xīnxiān.|Không khí buổi sáng rất trong lành.
安静|an1 jing4|an tĩnh|adjective|yên tĩnh; trầm lặng|quiet; peaceful|图书馆里非常安静。|Túshūguǎn lǐ fēicháng ānjìng.|Trong thư viện vô cùng yên tĩnh.
热闹|re4 nao5|nhiệt náo|adjective|náo nhiệt; sôi nổi|lively; bustling|夜市非常热闹。|Yèshì fēicháng rènao.|Chợ đêm vô cùng náo nhiệt.
舒服|shu1 fu5|thư phục|adjective|thoải mái; dễ chịu|comfortable|这把椅子坐着很舒服。|Zhè bǎ yǐzi zuò zhe hěn shūfu.|Chiếc ghế này ngồi rất thoải mái.
方便|fang1 bian4|phương tiện|adjective|tiện lợi; thuận tiện|convenient|坐地铁出行很方便。|Zuò dìtiě chūxíng hěn fāngbiàn.|Đi tàu điện ngầm rất thuận tiện.
安全|an1 quan2|an toàn|adjective|an toàn|safe; secure|过马路要注意安全。|Guò mǎlù yào zhùyì ānquán.|Qua đường phải chú ý an toàn.
危险|wei1 xian3|nguy hiểm|adjective|nguy hiểm|dangerous|在马路上玩太危险了。|Zài mǎlù shang wán tài wēixiǎn le.|Chơi trên lòng đường quá nguy hiểm.
重要|zhong4 yao4|trọng yếu|adjective|quan trọng|important|健康比钱更重要。|Jiànkāng bǐ qián gèng zhòngyào.|Sức khỏe quan trọng hơn tiền bạc.
主要|zhu3 yao4|chủ yếu|adjective|chủ yếu; chính|main; primary|这是今天的主要内容。|Zhè shì jīntiān de zhǔyào nèiróng.|Đây là nội dung chính của ngày hôm nay.
特别|te4 bie2|đặc biệt|adjective|đặc biệt; khác thường|special; extraordinary|这道菜的味道很特别。|Zhè dào cài de wèidao hěn tèbié.|Mùi vị của món ăn này rất đặc biệt.
一般|yi4 ban1|nhất ban|adjective|bình thường; phổ biến|ordinary; common|这家餐馆的味道很一般。|Zhè jiā cānguǎn de wèidao yìbān.|Vị đồ ăn ở quán này rất bình thường.
简单|jian3 dan1|giản đơn|adjective|đơn giản; giản dị|simple|这个问题其实很简单。|Zhège wèntí qíshí hěn jiǎndān.|Vấn đề này thực ra rất đơn giản.
复杂|fu4 za2|phức tạp|adjective|phức tạp|complicated; complex|这个情况比较复杂。|Zhège qíngkuàng bǐjiào fùzá.|Tình huống này tương đối phức tạp.
满意|man3 yi4|mãn ý|adjective|hài lòng; vừa ý|satisfied; pleased|客户对我们的服务很满意。|Kèhù duì wǒmen de fúwù hěn mǎnyì.|Khách hàng rất hài lòng với dịch vụ của chúng tôi.
有名|you3 ming2|hữu danh|adjective|nổi tiếng|famous; well-known|这所大学很有名。|Zhè suǒ dàxué hěn yǒumíng.|Trường đại học này rất nổi tiếng.
清楚|qing1 chu5|thanh sở|adjective|rõ ràng; thấu đáo|clear; explicit|我听得很清楚。|Wǒ tīng de hěn qīngchu.|Tôi nghe rất rõ ràng.
明白|ming2 bai5|minh bạch|adjective|rõ ràng; dễ hiểu|clear; obvious|事情已经很明白了。|Shìqing yǐjīng hěn míngbai le.|Sự việc đã rất rõ ràng rồi.
小心|xiao3 xin1|tiểu tâm|adjective|cẩn thận; cẩn trọng|careful; cautious|路上滑，小心一点儿。|Lù shang huá, xiǎoxīn yìdiǎnr.|Đường trơn, hãy cẩn thận một chút.
马虎|ma3 hu5|mã hổ|adjective|cẩu thả; qua loa|careless; casual|考试时千万别马虎。|Kǎoshì shí qiānwàn bié mǎhu.|Lúc đi thi tuyệt đối đừng cẩu thả.
暖和|nuan3 huo5|noãn hòa|adjective|ấm áp|warm|春天到了，天气暖和了。|Chūntiān dào le, tiānqì nuǎnhuo le.|Mùa xuân đến rồi, thời tiết ấm áp lên rồi.
凉快|liang2 kuai5|lương khoái|adjective|mát mẻ|cool; refreshingly cool|秋天比较凉快。|Qiūtiān bǐjiào liángkuai.|Mùa thu tương đối mát mẻ.
渴|ke3|khát|adjective|khát (nước)|thirsty|踢完球大家都口渴了。|Tīwán qiú dàjiā dōu kǒukě le.|Đá bóng xong mọi người đều khát nước rồi.
饿|e4|ngạ|adjective|đói|hungry|下班回家肚子很饿。|Xiàbān huí jiā dùzi hěn è.|Tan làm về nhà bụng rất đói.
饱|bao3|bão|adjective|no (bụng)|full|我已经吃饱了，吃不下了。|Wǒ yǐjīng chībǎo le, chī bú xià le.|Tôi đã ăn no rồi, không ăn thêm được nữa.
瘦|shou4|sấu|adjective|gầy; ốm|thin; skinny|他生病后瘦了很多。|Tā shēngbìng hòu shòu le hěn duō.|Sau khi ốm anh ấy gầy đi rất nhiều.
胖|pang4|bạng|adjective|béo; mập|fat; plump|少吃甜食，容易发胖。|Shǎo chī tiánshí, róngyì fāpàng.|Bớt ăn đồ ngọt, rất dễ bị béo.
健康|jian4 kang1|kiện khang|adjective|khỏe mạnh; lành mạnh|healthy|祝你身体健康！|Zhù nǐ shēntǐ jiànkāng!|Chúc bạn sức khỏe dồi dào!
年轻|nian2 qing1|niên khinh|adjective|trẻ tuổi; trẻ trung|young|年轻人要多学习新知识。|Niánqīngrén yào duō xuéxí xīn zhīshi.|Người trẻ tuổi nên học hỏi nhiều kiến thức mới.
漂亮|piao4 liang5|phiêu lượng|adjective|xinh đẹp; tuyệt vời|pretty; splendid|她今天打扮得很漂亮。|Tā jīntiān dǎban de hěn piàoliang.|Hôm nay cô ấy ăn mặc rất đẹp.
甜|tian2|điềm|adjective|ngọt ngào; ngọt|sweet|这杯奶茶太甜了。|Zhè bēi nǎichá tài tián le.|Cốc trà sữa này ngọt quá.
咸|xian2|hàm|adjective|mặn|salty|汤太咸了，加点水吧。|Tāng tài xián le, jiā diǎn shuǐ ba.|Canh mặn quá, cho thêm chút nước đi.
酸|suan1|toan|adjective|chua|sour|这个橘子太酸了。|Zhège júzi tài suān le.|Quả quýt này chua quá.
辣|la4|lạt|adjective|cay|spicy|你能不能吃辣？|Nǐ néng bù néng chī là?|Bạn có ăn được cay không?
苦|ku3|khổ|adjective|đắng; gian khổ|bitter; painful|这药很苦，但能治病。|Zhè yào hěn kǔ, dàn néng zhì bìng.|Thuốc này rất đắng, nhưng có thể trị bệnh.
累|lei4|luy|adjective|mệt; vất vả|tired; weary|今天走了一整天，太累了。|Jīntiān zǒu le yì zhěng tiān, tài lèi le.|Hôm nay đi cả một ngày, mệt quá rồi.
困|kun4|khốn|adjective|buồn ngủ; khốn khó|sleepy; trapped|昨晚没睡好，现在很困。|Zuówǎn méi shuì hǎo, xiànzài hěn kùn.|Đêm qua ngủ không ngon, bây giờ rất buồn ngủ.
疼|teng2|đông|adjective|đau; nhức|painful; sore|我的头有点儿疼。|Wǒ de tóu yǒudiǎnr téng.|Đầu tôi hơi đau một chút.
久|jiu3|cửu|adjective|lâu; dài ngày|long (time)|好久不见，你最近好吗？|Hǎojiǔ bú jiàn, nǐ zuìjìn hǎo ma?|Lâu rồi không gặp, dạo này bạn khỏe không?
差|cha4|sai|adjective|kém; tồi|bad; poor|他的视力比较差。|Tā de shìlì bǐjiào chà.|Thị lực của anh ấy tương đối kém.
低|di1|đê|adjective|thấp|low|今天气温很低。|Jīntiān qìwēn hěn dī.|Nhiệt độ hôm nay rất thấp.
高|gao1|cao|adjective|cao|tall; high|这幢楼非常高。|Zhè zhuàng lóu fēicháng gāo.|Tòa nhà này rất cao.
远|yuan3|viễn|adjective|xa xôi|far|车站离我家很远。|Chēzhàn lí wǒ jiā hěn yuǎn.|Nhà ga cách nhà tôi rất xa.
近|jin4|cận|adjective|gần|near|图书馆离宿舍很近。|Túshūguǎn lí sùshè hěn jìn.|Thư viện cách ký túc xá rất gần.
"""

# Wait! Notice that in BATCH_002: 清楚, 明白, 渴, 饿, 饱, 漂亮, 甜, 咸, 酸, 辣, 累, 高, 远, 近 were already in L1 or L2!
# Let's replace those duplicates in BATCH_002 with brand new L3 adjectives/words:
# New words to replace:
# 调皮 (tiao2 pi2 - nghịch ngợm)
# 诚实 (cheng2 shi2 - thành thật)
# 勇敢 (yong3 gan3 - dũng cảm)
# 幽默 (you1 mo4 - hài hước)
# 害羞 (hai4 xiu1 - e thẹn, xấu hổ)
# 骄傲 (jiao1 ao4 - kiêu ngạo, tự hào)
# 严格 (yan2 ge2 - nghiêm khắc)
# 活泼 (huo2 po5 - hoạt bát)
# 亲切 (qin1 qie4 - thân thiết)
# 丰富 (feng1 fu4 - phong phú)
# 顺利 (shun4 li4 - thuận lợi)
# 精彩 (jing1 cai3 - xuất sắc, tuyệt vời)
# 优秀 (you1 xiu4 - ưu tú)
# 粗心 (cu1 xin1 - bất cẩn)

BATCH_002_CLEAN = """
着急|zhao2 ji2|trước cấp|adjective|sốt ruột; lo lắng; vội vàng|anxious; worried|别着急，慢慢说。|Bié zháojí, mànmàn shuō.|Đừng sốt ruột, hãy nói từ từ.
生气|sheng1 qi4|sinh khí|adjective|tức giận; giận dỗi|angry; mad|他因为这件事生气了。|Tā yīnwèi zhè jiàn shì shēngqì le.|Anh ấy tức giận vì chuyện này rồi.
奇怪|qi2 guai4|kỳ quái|adjective|kỳ lạ; quái lạ|strange; weird|这件事情很奇怪。|Zhè jiàn shìqing hěn qíguài.|Chuyện này rất kỳ lạ.
热情|re4 qing2|nhiệt tình|adjective|nhiệt tình; niềm nở|warm-hearted; enthusiastic|中国人对客人很热情。|Zhōngguórén duì kèrén hěn rèqíng.|Người Trung Quốc rất nhiệt tình với khách.
认真|ren4 zhen1|nhận chân|adjective|nghiêm túc; chăm chỉ|serious; earnest|他学习非常认真。|Tā xuéxí fēicháng rènzhēn.|Anh ấy học tập vô cùng chăm chỉ.
聪明|cong1 ming5|thông minh|adjective|thông minh; sáng dạ|clever; intelligent|这个小男孩很聪明。|Zhège xiǎo nánhái hěn cōngming.|Cậu bé này rất thông minh.
努力|nu3 li4|nỗ lực|adjective|nỗ lực; chăm chỉ|hardworking; to strive|只要努力就能成功。|Zhǐyào nǔlì jiù néng chénggōng.|Chỉ cần nỗ lực thì sẽ thành công.
新鲜|xin1 xian1|tân tiên|adjective|tươi mới; trong lành|fresh|早晨的空气很新鲜。|Zǎochen de kōngqì hěn xīnxiān.|Không khí buổi sáng rất trong lành.
安静|an1 jing4|an tĩnh|adjective|yên tĩnh; trầm lặng|quiet; peaceful|图书馆里非常安静。|Túshūguǎn lǐ fēicháng ānjìng.|Trong thư viện vô cùng yên tĩnh.
热闹|re4 nao5|nhiệt náo|adjective|náo nhiệt; sôi nổi|lively; bustling|夜市非常热闹。|Yèshì fēicháng rènao.|Chợ đêm vô cùng náo nhiệt.
舒服|shu1 fu5|thư phục|adjective|thoải mái; dễ chịu|comfortable|这把椅子坐着很舒服。|Zhè bǎ yǐzi zuò zhe hěn shūfu.|Chiếc ghế này ngồi rất thoải mái.
方便|fang1 bian4|phương tiện|adjective|tiện lợi; thuận tiện|convenient|坐地铁出行很方便。|Zuò dìtiě chūxíng hěn fāngbiàn.|Đi tàu điện ngầm rất thuận tiện.
安全|an1 quan2|an toàn|adjective|an toàn|safe; secure|过马路要注意安全。|Guò mǎlù yào zhùyì ānquán.|Qua đường phải chú ý an toàn.
危险|wei1 xian3|nguy hiểm|adjective|nguy hiểm|dangerous|在马路上玩太危险了。|Zài mǎlù shang wán tài wēixiǎn le.|Chơi trên lòng đường quá nguy hiểm.
重要|zhong4 yao4|trọng yếu|adjective|quan trọng|important|健康比钱更重要。|Jiànkāng bǐ qián gèng zhòngyào.|Sức khỏe quan trọng hơn tiền bạc.
主要|zhu3 yao4|chủ yếu|adjective|chủ yếu; chính|main; primary|这是今天的主要内容。|Zhè shì jīntiān de zhǔyào nèiróng.|Đây là nội dung chính của ngày hôm nay.
特别|te4 bie2|đặc biệt|adjective|đặc biệt; khác thường|special; extraordinary|这道菜的味道很特别。|Zhè dào cài de wèidao hěn tèbié.|Mùi vị của món ăn này rất đặc biệt.
一般|yi4 ban1|nhất ban|adjective|bình thường; phổ biến|ordinary; common|这家餐馆的味道很一般。|Zhè jiā cānguǎn de wèidao yìbān.|Vị đồ ăn ở quán này rất bình thường.
简单|jian3 dan1|giản đơn|adjective|đơn giản; giản dị|simple|这个问题其实很简单。|Zhège wèntí qíshí hěn jiǎndān.|Vấn đề này thực ra rất đơn giản.
复杂|fu4 za2|phức tạp|adjective|phức tạp|complicated; complex|这个情况比较复杂。|Zhège qíngkuàng bǐjiào fùzá.|Tình huống này tương đối phức tạp.
满意|man3 yi4|mãn ý|adjective|hài lòng; vừa ý|satisfied; pleased|客户对我们的服务很满意。|Kèhù duì wǒmen de fúwù hěn mǎnyì.|Khách hàng rất hài lòng với dịch vụ của chúng tôi.
有名|you3 ming2|hữu danh|adjective|nổi tiếng|famous; well-known|这所大学很有名。|Zhè suǒ dàxué hěn yǒumíng.|Trường đại học này rất nổi tiếng.
调皮|tiao2 pi2|điều bì|adjective|nghịch ngợm; tinh nghịch|naughty; mischievous|这个弟弟很调皮。|Zhège dìdi hěn tiáopí.|Cậu em trai này rất nghịch ngợm.
诚实|cheng2 shi2|thành thực|adjective|thành thật; trung thực|honest|我们要做一个诚实的人。|Wǒmen yào zuò yí ge chéngshí de rén.|Chúng ta phải làm một người thành thật.
小心|xiao3 xin1|tiểu tâm|adjective|cẩn thận; cẩn trọng|careful; cautious|路上滑，小心一点儿。|Lù shang huá, xiǎoxīn yìdiǎnr.|Đường trơn, hãy cẩn thận một chút.
马虎|ma3 hu5|mã hổ|adjective|cẩu thả; qua loa|careless; casual|考试时千万别马虎。|Kǎoshì shí qiānwàn bié mǎhu.|Lúc đi thi tuyệt đối đừng cẩu thả.
暖和|nuan3 huo5|noãn hòa|adjective|ấm áp|warm|春天到了，天气暖和了。|Chūntiān dào le, tiānqì nuǎnhuo le.|Mùa xuân đến rồi, thời tiết ấm áp lên rồi.
凉快|liang2 kuai5|lương khoái|adjective|mát mẻ|cool; refreshingly cool|秋天比较凉快。|Qiūtiān bǐjiào liángkuai.|Mùa thu tương đối mát mẻ.
勇敢|yong3 gan3|dũng cảm|adjective|dũng cảm|brave; courageous|他是一个勇敢的战士。|Tā shì yí ge yǒnggǎn de zhànshì.|Anh ấy là một chiến sĩ dũng cảm.
幽默|you1 mo4|u mặc|adjective|hài hước; dí dỏm|humorous|老师讲课很幽默。|Lǎoshī jiǎngkè hěn yōumò.|Thầy giáo giảng bài rất hài hước.
害羞|hai4 xiu1|hại tu|adjective|e thẹn; xấu hổ; bẽn lẽn|shy; timid|她见到陌生人容易害羞。|Tā jiàndào mòshēngrén róngyì hàixiū.|Cô ấy gặp người lạ rất dễ bẽn lẽn.
瘦|shou4|sấu|adjective|gầy; ốm|thin; skinny|他生病后瘦了很多。|Tā shēngbìng hòu shòu le hěn duō.|Sau khi ốm anh ấy gầy đi rất nhiều.
胖|pang4|bạng|adjective|béo; mập|fat; plump|少吃甜食，容易发胖。|Shǎo chī tiánshí, róngyì fāpàng.|Bớt ăn đồ ngọt, rất dễ bị béo.
健康|jian4 kang1|kiện khang|adjective|khỏe mạnh; lành mạnh|healthy|祝你身体健康！|Zhù nǐ shēntǐ jiànkāng!|Chúc bạn sức khỏe dồi dào!
年轻|nian2 qing1|niên khinh|adjective|trẻ tuổi; trẻ trung|young|年轻人要多学习新知识。|Niánqīngrén yào duō xuéxí xīn zhīshi.|Người trẻ tuổi nên học hỏi nhiều kiến thức mới.
严格|yan2 ge2|nghiêm cách|adjective|nghiêm khắc; ngặt nghèo|strict; rigorous|老师对我们要求很严格。|Lǎoshī duì wǒmen yāoqiú hěn yángé.|Thầy giáo yêu cầu đối với chúng tôi rất nghiêm khắc.
活泼|huo2 po5|hoạt bát|adjective|hoạt bát; sôi nổi|lively; vivacious|妹妹性格非常活泼。|Mèimei xìnggé fēicháng huópo.|Tính cách em gái rất hoạt bát.
亲切|qin1 qie4|thân thiết|adjective|thân thiết; ân cần|kind; amiable|阿姨的态度非常亲切。|Āyí de tàidu fēicháng qīnqiè.|Thái độ của dì rất ân cần thân thiết.
丰富|feng1 fu4|phong phú|adjective|phong phú; dồi dào|rich; abundant|这本书的内容非常丰富。|Zhè běn shū de nèiróng fēicháng fēngfù.|Nội dung cuốn sách này vô cùng phong phú.
顺利|shun4 li4|thuận lợi|adjective|thuận lợi|smooth; successful|祝你的工作一切顺利！|Zhù nǐ de gōngzuò yíqiè shùnlì!|Chúc công việc của bạn mọi sự thuận lợi!
苦|ku3|khổ|adjective|đắng; gian khổ|bitter; painful|这药很苦，但能治病。|Zhè yào hěn kǔ, dàn néng zhì bìng.|Thuốc này rất đắng, nhưng có thể trị bệnh.
精彩|jing1 cai3|tinh thải|adjective|đặc sắc; xuất sắc|wonderful; brilliant|昨晚的晚会非常精彩。|Zuówǎn de wǎnhuì fēicháng jīngcǎi.|Buổi dạ hội tối qua vô cùng đặc sắc.
困|kun4|khốn|adjective|buồn ngủ; khốn khó|sleepy; trapped|昨晚没睡好，现在很困。|Zuówǎn méi shuì hǎo, xiànzài hěn kùn.|Đêm qua ngủ không ngon, bây giờ rất buồn ngủ.
疼|teng2|đông|adjective|đau; nhức|painful; sore|我的头有点儿疼。|Wǒ de tóu yǒudiǎnr téng.|Đầu tôi hơi đau một chút.
久|jiu3|cửu|adjective|lâu; dài ngày|long (time)|好久不见，你最近好吗？|Hǎojiǔ bú jiàn, nǐ zuìjìn hǎo ma?|Lâu rồi không gặp, dạo này bạn khỏe không?
差|cha4|sai|adjective|kém; tồi|bad; poor|他的视力比较差。|Tā de shìlì bǐjiào chà.|Thị lực của anh ấy tương đối kém.
低|di1|đê|adjective|thấp|low|今天气温很低。|Jīntiān qìwēn hěn dī.|Nhiệt độ hôm nay rất thấp.
优秀|you1 xiu4|ưu tú|adjective|ưu tú; xuất sắc|outstanding; excellent|他是一名优秀的老师。|Tā shì yì míng yōuxiù de lǎoshī.|Anh ấy là một giáo viên ưu tú.
粗心|cu1 xin1|thô tâm|adjective|bất cẩn; sơ ý|careless; thoughtless|做题时不能太粗心。|Zuòtí shí bù néng tài cūxīn.|Làm bài không được quá bất cẩn.
骄傲|jiao1 ao4|kiêu ngạo|adjective|kiêu ngạo; tự hào|proud; arrogant|虚心使人进步，骄傲使人落后。|Xūxīn shǐ rén jìnbù, jiāo'ào shǐ rén luòhòu.|Khiêm tốn giúp người tiến bộ, kiêu ngạo khiến người thụt lùi.
"""

# Batch 3 (50 items): Society, people, professions, relations
BATCH_003 = """
客人|ke4 ren5|khách nhân|noun|khách; khách mời|guest; customer|今天家里来了一位客人。|Jīntiān jiā li lái le yí wèi kèrén.|Hôm nay nhà có một vị khách đến.
邻居|lin2 ju1|lân cư|noun|hàng xóm; láng giềng|neighbor|我和我的邻居关系很好。|Wǒ hé wǒ de línjū guānxi hěn hǎo.|Tôi và hàng xóm có mối quan hệ rất tốt.
校长|xiao4 zhang3|hiệu trưởng|noun|hiệu trưởng|principal; headmaster|校长在全校大会上讲话。|Xiàozhǎng zài quánxiào dàhuì shang jiǎnghuà.|Hiệu trưởng phát biểu trong đại hội toàn trường.
司机|si1 ji1|ty cơ|noun|tài xế; người lái xe|driver|出租车司机很热情。|Chūzūchē sījī hěn rèqíng.|Bác tài xế taxi rất nhiệt tình.
同事|tong2 shi4|đồng sự|noun|đồng nghiệp|colleague; coworker|他和同事们相处得很好。|Tā hé tóngshìmen xiāngchǔ de hěn hǎo.|Anh ấy hòa thuận rất tốt với các đồng nghiệp.
阿姨|a1 yi2|a di|noun|dì; cô; bác gái (xưng hô phụ nữ lớn tuổi)|aunt; woman of similar age to parents|王阿姨经常帮助我们。|Wáng āyí jīngcháng bāngzhù wǒmen.|Dì Vương thường xuyên giúp đỡ chúng tôi.
叔叔|shu1 shu5|thúc thúc|noun|chú; bác trai (xưng hô nam giới lớn tuổi)|uncle; man of similar age to parents|李叔叔送给我一本书。|Lǐ shūshu sòng gěi wǒ yì běn shū.|Chú Lý tặng cho tôi một cuốn sách.
爷爷|ye2 ye5|gia gia|noun|ông nội|grandfather (paternal)|爷爷今年八十岁了。|Yéye jīnnián bāshí suì le.|Ông nội năm nay đã tám mươi tuổi rồi.
奶奶|nai3 nai5|nãi nãi|noun|bà nội|grandmother (paternal)|奶奶做的菜很好吃。|Nǎinai zuò de cài hěn hǎochī.|Bà nội nấu món ăn rất ngon.
外婆|wai4 po2|ngoại bà|noun|bà ngoại|grandmother (maternal)|暑假我去看望外婆。|Shǔjià wǒ qù kànwàng wàipó.|Kỳ nghỉ hè tôi đến thăm bà ngoại.
孙子|sun1 zi5|tôn tử|noun|cháu trai|grandson|老人很疼爱他的小孙子。|Lǎorén hěn téng'ài tā de xiǎo sūnzi.|Cụ già rất yêu thương đứa cháu trai nhỏ của mình.
顾客|gu4 ke4|cố khách|noun|khách hàng|customer; client|商场里有很多顾客。|Shāngchǎng lǐ yǒu hěn duō gùkè.|Trong trung tâm thương mại có rất nhiều khách hàng.
观众|guan1 zhong4|quan chúng|noun|khán giả; người xem|audience; viewer|观众为演员精彩的表现鼓掌。|Guānzhòng wèi yǎnyuán jīngcǎi de biǎoxiàn gǔzhǎng.|Khán giả vỗ tay tán thưởng màn biểu diễn xuất sắc của diễn viên.
记者|ji4 zhe3|ký giả|noun|phóng viên; nhà báo|journalist; reporter|记者采访了这位科学家。|Jìzhě cǎifǎng le zhè wèi kēxuéjiā.|Phóng viên đã phỏng vấn nhà khoa học này.
导游|dao3 you2|đạo du|noun|hướng dẫn viên du lịch|tour guide|导游给我们介绍了长城的历史。|Dǎoyóu gěi wǒmen jièshào le chángchéng de lìshǐ.|Hướng dẫn viên du lịch đã giới thiệu cho chúng tôi lịch sử Vạn Lý Trường Thành.
律师|lü4 shi1|luật sư|noun|luật sư|lawyer|遇到法律问题需要找律师。|Yùdào fǎlǜ wèntí xūyào zhǎo lǜshī.|Gặp vấn đề pháp lý cần phải tìm luật sư.
警察|jing3 cha2|cảnh sát|noun|cảnh sát; công an|police officer|警察正在路上指挥交通。|Jǐngchá zhèngzài lù shang zhǐhuī jiāotōng.|Cảnh sát đang chỉ huy giao thông trên đường.
经理|jing1 li3|kinh lý|noun|giám đốc; quản lý|manager|张经理今天不在办公室。|Zhāng jīnglǐ jīntiān bú zài bàngōngshì.|Giám đốc Trương hôm nay không có ở văn phòng.
作者|zuo4 zhe3|tác giả|noun|tác giả|author; writer|这本书的作者很年轻。|Zhè běn shū de zuòzhě hěn niánqīng.|Tác giả của cuốn sách này rất trẻ tuổi.
演员|yan3 yuan2|diễn viên|noun|diễn viên|actor; actress|他是一名电影演员。|Tā shì yì míng diànyǐng yǎnyuán.|Anh ấy là một diễn viên điện ảnh.
歌手|ge1 shou3|ca thủ|noun|ca sĩ|singer|那位歌手的声音非常好听。|Nà wèi gēshǒu de shēngyīn fēicháng hǎotīng.|Giọng hát của ca sĩ kia nghe rất hay.
社会|she4 hui4|xã hội|noun|xã hội|society|每个人都生活在社会中。|Měi ge rén dōu shēnghuó zài shèhuì zhōng.|Mỗi người đều sống trong xã hội.
国家|guo2 jia1|quốc gia|noun|quốc gia; đất nước|country; nation|中国是一个历史悠久的国家。|Zhōngguó shì yí ge lìshǐ yōujiǔ de guójiā.|Trung Quốc là một quốc gia có lịch sử lâu đời.
世界|shi4 jie4|thế giới|noun|thế giới|world|我想去世界各地旅游。|Wǒ xiǎng qù shìjiè gèdì lǚyóu.|Tôi muốn đi du lịch khắp nơi trên thế giới.
城市|cheng2 shi4|thành thị|noun|thành phố; đô thị|city|这是一座美丽的现代化城市。|Zhè shì yí zuò měilì de xiàndàihuà chéngshì.|Đây là một thành phố hiện đại và tươi đẹp.
农村|nong2 cun1|nông thôn|noun|nông thôn; làng quê|countryside; rural area|爷爷喜欢住在农村。|Yéye xǐhuan zhù zài nóngcūn.|Ông nội thích sống ở nông thôn.
街道|jie1 dao4|nhai đạo|noun|đường phố; phố xá|street|这条街道两旁种满了树。|Zhè tiáo jiēdào liǎngpáng zhòng mǎn le shù.|Hai bên đường phố này trồng đầy cây xanh.
公园|gong1 yuan2|công viên|noun|công viên|park|早上很多老人在公园散步。|Zǎoshang hěn duō lǎorén zài gōngyuán sànbù.|Buổi sáng rất nhiều người già đi dạo trong công viên.
银行|yin2 hang2|ngân hàng|noun|ngân hàng|bank|我需要去银行办卡。|Wǒ xūyào qù yínháng bàn kǎ.|Tôi cần đến ngân hàng để làm thẻ.
邮局|you2 ju2|bưu cục|noun|bưu điện|post office|邮局就在学校对面。|Yóujú jiù zài xuéxiào duìmiàn.|Bưu điện nằm ngay ở đối diện trường học.
超市|chao1 shi4|siêu thị|noun|siêu thị|supermarket|下班后我去超市买菜。|Xiàbān hòu wǒ qù chāoshì mǎi cài.|Tan làm tôi đến siêu thị mua thức ăn.
市场|shi4 chang3|thị trường|noun|chợ; thị trường|market|早晨的农贸市场很热闹。|Zǎochen de nóngmào shìchǎng hěn rènao.|Khu chợ nông sản buổi sáng rất náo nhiệt.
图书馆|tu2 shu1 guan3|đồ thư quán|noun|thư viện|library|我下午去图书馆借书。|Wǒ xiàwǔ qù túshūguǎn jiè shū.|Buổi chiều tôi đến thư viện mượn sách.
体育馆|ti3 yu4 guan3|thể dục quán|noun|nhà thi đấu; phòng thể dục|gymnasium; stadium|我们每周五在体育馆打球。|Wǒmen měi zhōuwǔ zài tǐyùguǎn dǎqiú.|Mỗi thứ sáu chúng tôi đều chơi bóng ở nhà thi đấu.
博物馆|bo2 wu4 guan3|bác vật quán|noun|bảo tàng|museum|周末很多人参观历史博物馆。|Zhōumò hěn duō rén cānguān lìshǐ bówùguǎn.|Cuối tuần có nhiều người đến tham quan bảo tàng lịch sử.
电影院|dian4 ying3 yuan4|điện ảnh viện|noun|rạp chiếu phim|cinema; movie theater|我们去电影院看新电影。|Wǒmen qù diànyǐngyuàn kàn xīn diànyǐng.|Chúng mình đến rạp chiếu phim xem phim mới nhé.
剧场|ju4 chang3|kịch trường|noun|nhà hát; rạp hát|theater|今天晚上剧场有一场京剧。|Jīntiān wǎnshang jùchǎng yǒu yì chǎng jīngjù.|Tối nay ở nhà hát có một vở Kinh kịch.
大使馆|da4 shi3 guan3|đại sứ quán|noun|đại sứ quán|embassy|办理签证要去大使馆。|Bànlǐ qiānzhèng yào qù dàshǐguǎn.|Làm thủ tục thị thực cần phải đến đại sứ quán.
海边|hai3 bian1|hải biên|noun|bờ biển; bãi biển|seaside; beach|夏天很多人去海边度假。|Xiàtiān hěn duō rén qù hǎibiān dùjià.|Mùa hè rất nhiều người đi nghỉ mát ở bờ biển.
动物园|dong4 wu4 yuan2|động vật viên|noun|sở thú; vườn thú|zoo|周末爸爸带我去动物园看熊猫。|Zhōumò bàba dài wǒ qù dòngwùyuán kàn xióngmāo.|Cuối tuần bố đưa tôi đến sở thú xem gấu trúc.
植物园|zhi2 wu4 yuan2|thực vật viên|noun|vườn bách thảo|botanical garden|植物园里有很多奇花异草。|Zhíwùyuán lǐ yǒu hěn duō qíhuā-yìcǎo.|Trong vườn bách thảo có rất nhiều hoa thơm cỏ lạ.
办公室|ban4 gong1 shi4|biện công thất|noun|văn phòng|office|李老师正在办公室批改作业。|Lǐ lǎoshī zhèngzài bàngōngshì pīgǎi zuòyè.|Thầy Lý đang chấm bài tập ở văn phòng.
会议室|hui4 yi4 shi4|hội nghị thất|noun|phòng họp|meeting room; conference room|大家请到二楼会议室集合。|Dàjiā qǐng dào èr lóu huìyìshì jíhé.|Mọi người xin tập trung tại phòng họp tầng hai.
厨房|chu2 fang2|trù phòng|noun|nhà bếp; bếp|kitchen|妈妈在厨房做晚饭。|Māma zài chúfáng zuò wǎnfàn.|Mẹ đang nấu cơm tối ở trong bếp.
阳台|yang2 tai2|dương đài|noun|ban công|balcony|阳台上种了许多花。|Yángtái shang zhòng le xǔduō huā.|Trên ban công có trồng rất nhiều hoa.
电梯|dian4 ti1|điện thang|noun|thang máy|elevator; lift|我们坐电梯上八楼。|Wǒmen zuò diàntī shàng bā lóu.|Chúng mình đi thang máy lên tầng tám nhé.
楼梯|lou2 ti1|lâu thang|noun|cầu thang bộ|stairs; staircase|走楼梯锻炼身体。|Zǒu lóutī duànliàn shēntǐ.|Đi cầu thang bộ giúp rèn luyện sức khỏe.
院子|yuan4 zi5|viện tử|noun|sân; khoảng sân|courtyard; yard|孩子们在院子里玩耍。|Háizimen zài yuànzi lǐ wánshuǎ.|Lũ trẻ đang nô đùa ở trong sân.
邻里|lin2 li3|lân lý|noun|láng giềng; xóm giềng|neighborhood|邻里之间应该互相帮助。|Línlǐ zhījiān yīnggāi hùxiāng bāngzhù.|Xóm giềng với nhau nên giúp đỡ lẫn nhau.
社会学|she4 hui4 xue2|xã hội học|noun|xã hội học|sociology|她在大学专攻社会学。|Tā zài dàxué zhuāngōng shèhuìxué.|Cô ấy theo học chuyên ngành xã hội học tại trường đại học.
"""

# Batch 4 (50 items): Objects, household, clothing, tools, technology
BATCH_004 = """
伞|san3|tản|noun|cái ô; cái dù|umbrella|下雨了，出门记得带伞。|Xià yǔ le, chūmén jìde dài sǎn.|Trời mưa rồi, ra ngoài nhớ mang theo ô.
包|bao1|bao|noun|túi; ba lô; bọc|bag; sack|我的钥匙在包里。|Wǒ de yàoshi zài bāo lǐ.|Chìa khóa của tôi ở trong túi.
钱包|qian2 bao1|tiền bao|noun|ví tiền; bóp|wallet; purse|他把钱包落在出租车上了。|Tā bǎ qiánbāo là zài chūzūchē shang le.|Anh ấy để quên ví tiền trên xe taxi rồi.
箱子|xiang1 zi5|tương tử|noun|vali; hòm; thùng|box; suitcase|出门旅游请带上这个箱子。|Chūmén lǚyóu qǐng dài shang zhège xiāngzi.|Đi du lịch xin hãy mang theo chiếc vali này.
行李|xing2 li5|hành lý|noun|hành lý|luggage; baggage|请把行李放在安检机上。|Qǐng bǎ xíngli fàng zài ānjiǎnjī shang.|Xin đặt hành lý lên máy kiểm tra an ninh.
地图|di4 tu2|địa đồ|noun|bản đồ|map|我们看地图找路吧。|Wǒmen kàn dìtú zhǎo lù ba.|Chúng mình nhìn bản đồ để tìm đường nhé.
照片|zhao4 pian4|chiếu phiến|noun|bức ảnh; tấm hình|photo; picture|这是我们在长城拍的照片。|Zhè shì wǒmen zài chángchéng pāi de zhàopiàn.|Đây là bức ảnh chúng tôi chụp ở Vạn Lý Trường Thành.
照相机|zhao4 xiang4 ji1|chiếu tương cơ|noun|máy ảnh|camera|我买了一台新照相机。|Wǒ mǎi le yì tái xīn zhàoxiàngjī.|Tôi đã mua một chiếc máy ảnh mới.
信|xin4|tín|noun|bức thư; thư từ|letter; mail|我收到了朋友寄来的信。|Wǒ shōudào le péngyou jì lái de xìn.|Tôi đã nhận được bức thư của bạn gửi đến.
信封|xin4 feng1|tín phong|noun|phong bì thư; phong bì|envelope|请在信封上写清楚地址。|Qǐng zài xìnfēng shang xiě qīngchu dìzhǐ.|Xin hãy viết rõ địa chỉ lên phong bì.
邮票|you2 piao4|bưu phiếu|noun|con tem; tem thư|postage stamp|信封上需要贴一张邮票。|Xìnfēng shang xūyào tiē yì zhāng yóupiào.|Trên phong bì cần phải dán một con tem.
包裹|bao1 guo3|bao khỏa|noun|bưu kiện; gói hàng|parcel; package|今天下午我去取包裹。|Jīntiān xiàwǔ wǒ qù qǔ bāoguǒ.|Chiều nay tôi đi lấy bưu kiện.
瓶子|ping2 zi5|bình tử|noun|cái chai; cái lọ|bottle; vase|桌上有三个牛奶瓶子。|Zhuō shang yǒu sān ge niúnǎi píngzi.|Trên bàn có ba chai sữa.
盒子|he2 zi5|hạp tử|noun|cái hộp; hộp|box; case|请把小刀放进盒子里。|Qǐng bǎ xiǎodāo fàng jìn hézi lǐ.|Xin hãy cất con dao nhỏ vào trong hộp.
镜子|jing4 zi5|kính tử|noun|cái gương; gương soi|mirror|墙上挂着一面镜子。|Qiáng shang guà zhe yí miàn jìngzi.|Trên tường có treo một chiếc gương soi.
钥匙|yao4 shi5|thược thi|noun|chìa khóa|key|我找不到了大门的钥匙。|Wǒ zhǎobúdào le dàmén de yàoshi.|Tôi không tìm thấy chìa khóa cổng lớn rồi.
锁|suo3|tỏa|noun|ổ khóa; khóa|lock|出门前请检查门锁。|Chūmén qián qǐng jiǎnchá ménsuǒ.|Trước khi ra ngoài xin hãy kiểm tra khóa cửa.
灯|deng1|đăng|noun|đèn; ngọn đèn|lamp; light|房间里太暗了，开灯吧。|Fángjiān lǐ tài àn le, kāi dēng ba.|Trong phòng tối quá, bật đèn lên đi.
空调|kong1 tiao2|không điều|noun|điều hòa; máy lạnh|air conditioner|夏天开空调很凉快。|Xiàtiān kāi kōngtiáo hěn liángkuai.|Mùa hè bật điều hòa rất mát mẻ.
冰箱|bing1 xiang1|băng tương|noun|tủ lạnh|refrigerator|把牛奶放进冰箱里。|Bǎ niúnǎi fàng jìn bīngxiāng lǐ.|Cho sữa bò vào trong tủ lạnh đi.
洗衣机|xi3 yi1 ji1|tẩy y cơ|noun|máy giặt|washing machine|这台洗衣机非常好用。|Zhè tái xǐyījī fēicháng hǎoyòng.|Chiếc máy giặt này rất dễ dùng.
微波炉|wei1 bo1 lu2|vi ba lô|noun|lò vi sóng|microwave oven|用微波炉热饭很快。|Yòng wēibōlú rè fàn hěn kuài.|Hâm nóng cơm bằng lò vi sóng rất nhanh.
电风扇|dian4 feng1 shan4|điện phong phiến|noun|quạt điện; quạt máy|electric fan|天热了，开一下电风扇。|Tiān rè le, kāi yíxià diànfēngshàn.|Trời nóng rồi, bật quạt điện một lát đi.
被子|bei4 zi5|bị tử|noun|cái chăn; mền|quilt; blanket|晚上冷，盖厚一点儿的被子。|Wǎnshang lěng, gài hòu yìdiǎnr de bèizi.|Ban đêm trời lạnh, hãy đắp chiếc chăn dày một chút.
床单|chuang2 dan1|sàng đơn|noun|ga trải giường|bedsheet|请把脏床单换下来。|Qǐng bǎ zāng chuángdān huàn xiàlai.|Xin hãy thay chiếc ga trải giường bẩn ra.
枕头|zhen3 tou5|chẩm đầu|noun|cái gối|pillow|这个枕头睡得很舒服。|Zhège zhěntou shuì de hěn shūfu.|Chiếc gối này nằm ngủ rất êm ái.
毛巾|mao2 jin1|mao cân|noun|khăn mặt; khăn lông|towel|洗脸后请用干毛巾擦干。|Xǐliǎn hòu qǐng yòng gān máojīn cā gān.|Sau khi rửa mặt hãy dùng khăn khô lau khô.
牙刷|ya2 shua1|nha loát|noun|bàn chải đánh răng|toothbrush|请每个月换一次牙刷。|Qǐng měi ge yuè huàn yí cì yáshuā.|Xin hãy thay bàn chải đánh răng mỗi tháng một lần.
牙膏|ya2 gao1|nha cao|noun|kem đánh răng|toothpaste|这支牙膏快用完了。|Zhè zhī yágāo kuài yòngwán le.|Tuýp kem đánh răng này sắp dùng hết rồi.
肥皂|fei2 zao4|phì táo|noun|xà phòng; bánh xà bông|soap|洗手时请用肥皂。|Xǐshǒu shí qǐng yòng féizào.|Lúc rửa tay xin hãy dùng xà phòng.
梳子|shu1 zi5|sơ tử|noun|cái lược|comb|她正在用梳子梳头发。|Tā zhèngzài yòng shūzi shū tóufa.|Cô ấy đang dùng chiếc lược để chải tóc.
帽子|mao4 zi5|mạo tử|noun|cái mũ; nón|hat; cap|夏天出门记得戴帽子。|Xiàtiān chūmén jìde dài màozi.|Mùa hè ra ngoài nhớ đội mũ.
裤子|ku4 zi5|khố tử|noun|quần; cái quần|trousers; pants|这条裤子长短刚好合适。|Zhè tiáo kùzi chángduǎn gānghǎo héshì.|Chiếc quần này độ dài vừa vặn.
裙子|qun2 zi5|quần tử|noun|váy; chân váy|skirt; dress|她穿了一条红裙子。|Tā chuān le yì tiáo hóng qúnzi.|Cô ấy mặc một chiếc váy đỏ.
鞋|xie2|hài|noun|giày; đôi giày|shoes|进门前请脱鞋。|Jìnmén qián qǐng tuō xié.|Trước khi vào nhà xin hãy cởi giày.
袜子|wa4 zi5|ngoạt tử|noun|tất; vớ|socks|冬天穿厚袜子很暖和。|Dōngtiān chuān hòu wàzi hěn nuǎnhuo.|Mùa đông mang tất dày rất ấm áp.
眼镜|yan3 jing4|nhãn kính|noun|kính mắt; kính đeo|glasses; spectacles|爷爷看报纸时戴眼镜。|Yéye kàn bàozhǐ shí dài yǎnjìng.|Ông nội đeo kính khi đọc báo.
墨镜|mo4 jing4|mặc kính|noun|kính râm; kính mát|sunglasses|夏天在户外戴墨镜很舒服。|Xiàtiān zài hùwài dài mòjìng hěn shūfu.|Mùa hè ở ngoài trời đeo kính râm rất dễ chịu.
雨伞|yu3 san3|vũ tản|noun|cái ô đi mưa; dù che mưa|umbrella|今天出门一定要带雨伞。|Jīntiān chūmén yídìng yào dài yǔsǎn.|Hôm nay ra ngoài nhất định phải mang ô che mưa.
皮鞋|pi2 xie2|bì hài|noun|giày da|leather shoes|爸爸今天穿了一双新皮鞋。|Bàba jīntiān chuān le yì shuāng xīn píxié.|Hôm nay bố đi một đôi giày da mới.
衬衫|chen4 shan1|sấn sam|noun|áo sơ mi|shirt|这件白衬衫很干净。|Zhè jiàn bái chènshān hěn gānjìng.|Chiếc áo sơ mi trắng này rất sạch sẽ.
外套|wai4 tao4|ngoại sáo|noun|áo khoác; áo ngoài|coat; jacket|外面天冷，穿件外套吧。|Wàimiàn tiān lěng, chuān jiàn wàitào ba.|Bên ngoài trời lạnh, mặc thêm áo khoác vào đi.
大衣|da4 yi1|đại y|noun|áo măng tô; áo choàng|overcoat|冬天我喜欢穿黑色大衣。|Dōngtiān wǒ xǐhuan chuān hēisè dàyī.|Mùa đông tôi thích mặc áo khoác măng tô màu đen.
领带|ling3 dai4|lĩnh đới|noun|cà vạt|necktie|上班时他总是系领带。|Shàngbān shí tā zǒngshì jì lǐngdài.|Khi đi làm anh ấy luôn thắt cà vạt.
皮带|pi2 dai4|bì đới|noun|thắt lưng; dây nịt|belt|这条皮带质量非常好。|Zhè tiáo pídài zhìliàng fēicháng hǎo.|Chiếc thắt lưng da này chất lượng rất tốt.
手表带|shou3 biao3 dai4|thủ biểu đới|noun|dây đồng hồ đeo tay|watch strap|我的手表带旧了。|Wǒ de shǒubiǎodài jiù le.|Dây đồng hồ của tôi đã cũ rồi.
围巾|wei2 jin1|vi cân|noun|khăn quàng cổ|scarf|冬天戴围巾很暖和。|Dōngtiān dài wéijīn hěn nuǎnhuo.|Mùa đông quàng khăn rất ấm áp.
手套|shou3 tao4|thủ sáo|noun|găng tay; bao tay|gloves; mittens|骑车时请戴上手套。|Qí chē shí qǐng dài shang shǒutào.|Khi đi xe xin hãy đeo găng tay.
雨衣|yu3 yi1|vũ y|noun|áo mưa|raincoat|下大雨时穿雨衣比较方便。|Xià dàyǔ shí chuān yǔyī bǐjiào fāngbiàn.|Lúc trời mưa to mặc áo mưa tương đối tiện.
泳衣|yong3 yi1|dũng y|noun|đồ bơi; áo tắm|swimsuit|去海边游泳要带泳衣。|Qù hǎibiān yóuyǒng yào dài yǒngyī.|Đi bơi ở biển cần mang theo đồ bơi.
"""

# Batch 5 (50 items): Time, nature, environment, weather, measurement
BATCH_005 = """
季节|ji4 jie2|quý tiết|noun|mùa; mùa trong năm|season|一年有四个季节。|Yì nián yǒu sì ge jìjié.|Một năm có bốn mùa.
春天|chun1 tian1|xuân thiên|noun|mùa xuân|spring|春天花儿都开了。|Chūntiān huār dōu kāi le.|Mùa xuân hoa nở rộ khắp nơi.
夏天|xia4 tian1|hạ thiên|noun|mùa hè; mùa hạ|summer|夏天的天气非常热。|Xiàtiān de tiānqì fēicháng rè.|Thời tiết mùa hè vô cùng nóng.
秋天|qiu1 tian1|thu thiên|noun|mùa thu|autumn; fall|北京的秋天非常美丽。|Běijīng de qiūtiān fēicháng měilì.|Mùa thu Bắc Kinh vô cùng tươi đẹp.
冬天|dong1 tian1|đông thiên|noun|mùa đông|winter|冬天经常下雪。|Dōngtiān jīngcháng xià xuě.|Mùa đông thường hay có tuyết rơi.
太阳|tai4 yang2|thái dương|noun|mặt trời|sun|早晨太阳从东方升起。|Zǎochen tàiyáng cóng dōngfāng shēngqǐ.|Buổi sáng mặt trời mọc ở hướng đông.
月亮|yue4 liang5|nguyệt lượng|noun|mặt trăng|moon|今晚的月亮又大又圆。|Jīnwǎn de yuèliang yòu dà yòu yuán.|Mặt trăng tối nay vừa to vừa tròn.
星星|xing1 xing5|tinh tinh|noun|ngôi sao; sao trời|star|夜空中有许多亮星星。|Yèkōng zhōng yǒu xǔduō liàng xīngxing.|Trên bầu trời đêm có rất nhiều vì sao sáng.
风|feng1|phong|noun|gió|wind|今天风很大，出门小心。|Jīntiān fēng hěn dà, chūmén xiǎoxīn.|Hôm nay gió rất to, ra ngoài cẩn thận.
雪|xue3|tuyết|noun|tuyết|snow|外面下雪了，地上全是白的。|Wàimiàn xià xuě le, dì shang quán shì bái de.|Bên ngoài tuyết rơi rồi, dưới đất trắng xóa.
云|yun2|vân|noun|mây; đám mây|cloud|天上有几朵白云。|Tiān shang yǒu jǐ duǒ bái yún.|Trên trời có vài đám mây trắng.
空气|kong1 qi4|không khí|noun|không khí|air|森林里的空气很新鲜。|Sēnlín lǐ de kōngqì hěn xīnxiān.|Không khí trong rừng rất trong lành.
环境|huan2 jing4|hoàn cảnh|noun|môi trường|environment|我们要保护生活环境。|Wǒmen yào bǎohù shēnghuó huánjìng.|Chúng ta cần bảo vệ môi trường sống.
草|cao3|thảo|noun|cỏ; cây cỏ|grass|院子里长满了青草。|Yuànzi lǐ zhǎng mǎn le qīngcǎo.|Trong sân cỏ xanh mọc đầy.
树|shu4|thụ|noun|cây; cây cối|tree|这棵大树有一百年历史了。|Zhè kē dà shù yǒu yì bǎi nián lìshǐ le.|Cây cổ thụ này đã có lịch sử một trăm năm rồi.
花|hua1|hoa|noun|hoa; bông hoa|flower|花园里的花真香。|Huāyuán lǐ de huā zhēn xiāng.|Hoa trong vườn thật là thơm.
叶子|ye4 zi5|diệp tử|noun|lá cây; chiếc lá|leaf|秋天树上的叶子变黄了。|Qiūtiān shù shang de yèzi biàn huáng le.|Mùa thu lá cây trên cành chuyển sang màu vàng.
河|he2|hà|noun|con sông; sông|river|河水非常清澈。|Héshuǐ fēicháng qīngchè.|Nước sông vô cùng trong vắt.
湖|hu2|hồ|noun|hồ nước; cái hồ|lake|我们在湖边散步。|Wǒmen zài hú biān sànbù.|Chúng tôi đi dạo ven hồ.
海|hai3|hải|noun|biển; đại dương|sea; ocean|海边的风景真美丽。|Hǎibiān de fēngjǐng zhēn měilì.|Phong cảnh bên bờ biển thật đẹp.
山|shan1|sơn|noun|núi; ngọn núi|mountain; hill|那座高山终年积雪。|Nà zuò gāoshān zhōngnián jīxuě.|Ngọn núi cao kia tuyết phủ quanh năm.
森林|sen1 lin2|sâm lâm|noun|rừng rậm; rừng|forest|很多动物生活在森林里。|Hěn duō dòngwù shēnghuó zài sēnlín lǐ.|Rất nhiều loài động vật sinh sống trong rừng.
动物|dong4 wu4|động vật|noun|động vật; muông thú|animal|我们要爱护小动物。|Wǒmen yào àihù xiǎo dòngwù.|Chúng ta phải yêu quý các con vật nhỏ.
鸟|niao3|điểu|noun|con chim; chim|bird|小鸟在枝头欢快地唱歌。|Xiǎoniǎo zài zhītóu huānkuài de chànggē.|Chú chim nhỏ đang hót líu lo trên cành.
马|ma3|mã|noun|con ngựa; ngựa|horse|草地上有一匹大马。|Cǎodì shang yǒu yì pǐ dà mǎ.|Trên bãi cỏ có một con ngựa lớn.
牛|niu2|ngưu|noun|con bò; trâu|ox; cow|农民正在田里放牛。|Nóngmín zhèngzài tián lǐ fàng niú.|Người nông dân đang chăn bò ngoài đồng.
羊|yang2|dương|noun|con cừu; con dê|sheep; goat|山坡上有一群绵羊。|Shānpō shang yǒu yì qún miányáng.|Trên sườn núi có một đàn cừu.
熊猫|xiong2 mao1|hùng miêu|noun|gấu trúc|giant panda|大熊猫是中国国宝。|Dàxióngmāo shì Zhōngguó guóbǎo.|Gấu trúc lớn là quốc bảo của Trung Quốc.
公园|gong1 yuan2|công viên|noun|công viên|park|晚饭后全家人去公园散步。|Wǎnfàn hòu quánjiā rén qù gōngyuán sànbù.|Sau bữa tối cả nhà cùng đi công viên dạo bộ.
自然|zi4 ran2|tự nhiên|noun|thiên nhiên; tự nhiên|nature; natural|多接触大自然有益健康。|Duō jiēchù dàzìrán yǒuyì jiànkāng.|Tiếp xúc nhiều với thiên nhiên có lợi cho sức khỏe.
温度|wen1 du4|ôn độ|noun|nhiệt độ|temperature|今天水池的温度刚刚好。|Jīntiān shuǐchí de wēndù gānggāng hǎo.|Hôm nay nhiệt độ hồ nước vừa vặn.
气温|qi4 wen1|khí ôn|noun|nhiệt độ không khí|air temperature|明天北方的气温会下降。|Míngtiān běifāng de qìwēn huì xiàjiàng.|Ngày mai nhiệt độ không khí ở miền Bắc sẽ giảm.
度|du4|độ|classifier|độ (nhiệt độ, góc)|degree|今天最高气温三十度。|Jīntiān zuìgāo qìwēn sānshí dù.|Nhiệt độ cao nhất hôm nay là ba mươi độ.
米|mi3|mễ|classifier|mét|meter|操场长一百米。|Cāochǎng cháng yì bǎi mǐ.|Sân vận động dài một trăm mét.
千克|qian1 ke4|thiên khắc|classifier|ki-lô-gam; cân|kilogram|请给我称两千克苹果。|Qǐng gěi wǒ chēng liǎng qiānkè píngguǒ.|Xin hãy cân cho tôi hai ki-lô-gam táo.
斤|jin1|cân|classifier|cân (đơn vị đo Trung Quốc = 500g)|catty (500g)|这斤香蕉五块钱。|Zhè jīn xiāngjiāo wǔ kuài qián.|Nửa cân chuối này năm đồng.
克|ke4|khắc|classifier|gam|gram|这包茶叶有一百克。|Zhè bāo cháyè yǒu yì bǎi kè.|Gói trà này nặng một trăm gam.
公里|gong1 li3|công lý|classifier|ki-lô-mét; cây số|kilometer|从我家到学校有五公里。|Cóng wǒ jiā dào xuéxiào yǒu wǔ gōnglǐ.|Từ nhà tôi đến trường học có năm cây số.
段|duan4|đoạn|classifier|đoạn; quãng (thời gian, đường)|section; segment|这段路很难走。|Zhè duàn lù hěn nán zǒu.|Đoạn đường này rất khó đi.
层|ceng2|tầng|classifier|tầng (nhà); lớp|floor; layer|他住在教学楼三层。|Tā zhù zài jiàoxuélóu sān céng.|Anh ấy ở tầng ba tòa nhà giảng đường.
页|ye4|diệp|classifier|trang (sách)|page|请翻到书的第十页。|Qǐng fān dào shū de dì-shí yè.|Xin hãy giở đến trang thứ mười của cuốn sách.
套|tao4|sáo|classifier|bộ; căn (quần áo, nhà)|set; suite|他买了一套新西服。|Tā mǎi le yí tào xīn xīfú.|Anh ấy đã mua một bộ com-lê mới.
位|wei4|vị|classifier|vị; ngài (lượng từ lịch sự chỉ người)|classifier for persons (polite)|请问您是哪一位？|Qǐngwèn nín shì nǎ yí wèi?|Xin hỏi ngài là vị nào ạ?
把|ba3|bả|classifier|chiếc; cái (có tay cầm: ghế, ô, dao)|classifier for handled objects|房间里只有一把椅子。|Fángjiān lǐ zhǐyǒu yì bǎ yǐzi.|Trong phòng chỉ có một chiếc ghế.
头|tou2|đầu|classifier|con (gia súc lớn: bò, lợn)|classifier for big animals|农场里养着二十头牛。|Nóngchǎng lǐ yǎng zhe èrshí tou niú.|Trong trang trại nuôi hai mươi con bò.
匹|pi3|thất|classifier|con (ngựa); cuộn (vải)|classifier for horses or cloth|草原上奔跑着一匹骏马。|Cǎoyuán shang bēnpǎo zhe yì pǐ jùnmǎ.|Trên thảo nguyên có một tuấn mã đang phi nước đại.
棵|ke1|khóa|classifier|cây (lượng từ cho thực vật)|classifier for trees|院子里种着两棵桃树。|Yuànzi lǐ zhòng zhe liǎng kē táoshù.|Trong sân trồng hai cây đào.
辆|liang4|lượng|classifier|chiếc; cái (xe cộ)|classifier for vehicles|爸爸买了一辆新车。|Bàba mǎi le yí liàng xīn chē.|Bố đã mua một chiếc xe mới.
封|feng1|phong|classifier|bức; lá (thư)|classifier for letters|我收到了好朋友的一封信。|Wǒ shōudào le hǎo péngyou de yì fēng xìn.|Tôi đã nhận được một bức thư của bạn thân.
场|chang3|tràng|classifier|trận; buổi; cơn|classifier for events or rain|下午下了一场大雨。|Xiàwǔ xià le yì chǎng dàyǔ.|Buổi chiều đã đổ một cơn mưa to.
"""

# Let's fix duplicate items in BATCH_005: 公园 was already in Batch 003.
# Replace with: 气候|qi4 hou4|khí hậu|noun|khí hậu|climate|这里的气候非常宜人。|Zhèli de qìhòu fēicháng yírén.|Khí hậu ở đây rất dễ chịu.
BATCH_005_CLEAN = BATCH_005.replace(
    "公园|gong1 yuan2|công viên|noun|công viên|park|晚饭后全家人去公园散步。|Wǎnfàn hòu quánjiā rén qù gōngyuán sànbù.|Sau bữa tối cả nhà cùng đi công viên dạo bộ.",
    "气候|qi4 hou4|khí hậu|noun|khí hậu|climate|这里的气候非常宜人。|Zhèli de qìhòu fēicháng yírén.|Khí hậu ở đây rất dễ chịu."
)

# Batch 6 (50 items): Abstract concepts, communication, adverbs, conjunctions
BATCH_006 = """
意思|yi4 si5|ý tứ|noun|ý nghĩa; ý tứ|meaning; idea|这个词是什么意思？|Zhège cí shì shénme yìsi?|Từ này có ý nghĩa là gì?
意见|yi4 jian4|ý kiến|noun|ý kiến; bất đồng|opinion; view|大家对这项决定有什么意见？|Dàjiā duì zhè xiàng juédìng yǒu shénme yìjiàn?|Mọi người có ý kiến gì về quyết định này không?
办法|ban4 fa3|biện pháp|noun|biện pháp; cách thức|way; method|你想到了什么好办法吗？|Nǐ xiǎngdào le shénme hǎo bànfǎ ma?|Bạn đã nghĩ ra cách giải quyết nào hay chưa?
机会|ji1 hui4|cơ hội|noun|cơ hội; dịp|opportunity; chance|这是一次非常好的学习机会。|Zhè shì yí cì fēicháng hǎo de xuéxí jīhuì.|Đây là một cơ hội học tập vô cùng tốt.
水平|shui3 ping2|thủy bình|noun|trình độ; mực độ|level; standard|经过努力，他的汉语水平提高很快。|Jīngguò nǔlì, tā de hànyǔ shuǐpíng tígāo hěn kuài.|Qua nỗ lực, trình độ tiếng Trung của anh ấy nâng cao rất nhanh.
成绩|cheng2 ji4|thành tích|noun|thành tích; điểm số|result; grade|这次考试大家取得了优异的成绩。|Zhè cì kǎoshì dàjiā qǔdé le yōuyì de chéngjì.|Kỳ thi lần này mọi người đã đạt được thành tích xuất sắc.
经验|jing1 yan4|kinh nghiệm|noun|kinh nghiệm|experience|他有丰富的教学经验。|Tā yǒu fēngfù de jiàoxué jīngyàn.|Anh ấy có kinh nghiệm giảng dạy phong phú.
要求|yao1 qiu2|yêu cầu|noun|yêu cầu; đòi hỏi|requirement; demand|领导对我们提出了严格的要求。|Lǐngdǎo duì wǒmen tíchū le yángé de yāoqiú.|Lãnh đạo đã đưa ra yêu cầu nghiêm khắc với chúng tôi.
关系|guan1 xi5|quan hệ|noun|quan hệ; mối liên hệ|relationship|他和同事之间的关系很融洽。|Tā hé tóngshì zhījiān de guānxi hěn róngqià.|Mối quan hệ giữa anh ấy và đồng nghiệp rất hòa hợp.
新闻|xin1 wen2|tân văn|noun|tin tức; thời sự|news|爷爷每天晚上七点看新闻。|Yéye měitiān wǎnshang qī diǎn kàn xīnwén.|Ông nội mỗi tối bảy giờ đều xem tin tức thời sự.
故事|gu4 shi5|cố sự|noun|câu chuyện; chuyện|story; tale|妈妈在给孩子讲睡前故事。|Māma zài gěi háizi jiǎng shuìqián gùshi.|Mẹ đang kể chuyện trước khi ngủ cho con nghe.
历史|li4 shi3|lịch sử|noun|lịch sử|history|我对外语大学的历史很感兴趣。|Wǒ duì wàiyǔ dàxué de lìshǐ hěn gǎn xìngqù.|Tôi rất có hứng thú với lịch sử của trường đại học ngoại ngữ.
文化|wen2 hua4|văn hóa|noun|văn hóa|culture|留学生很喜欢体验中国传统文化。|Liúxuéshēng hěn xǐhuan tǐyàn Zhōngguó chuántǒng wénhuà.|Lưu học sinh rất thích trải nghiệm văn hóa truyền thống Trung Quốc.
节目|jie2 mu4|tiết mục|noun|tiết mục; chương trình|program; show|今晚电视台有一个精彩的晚会节目。|Jīnwǎn diànshìtái yǒu yí ge jīngcǎi de wǎnhuì jiémù.|Tối nay đài truyền hình có một chương trình dạ hội đặc sắc.
比赛|bi3 sai4|tỷ tái|noun|cuộc thi; trận đấu|competition; match|明天的足球比赛一定很精彩。|Míngtiān de zúqiú bǐsài yídìng hěn jīngcǎi.|Trận đấu bóng đá ngày mai nhất định rất đặc sắc.
音乐|yin1 yue4|âm nhạc|noun|âm nhạc|music|做作业时他喜欢听轻音乐。|Zuò zuòyè shí tā xǐhuan tīng qīngyīnyuè.|Lúc làm bài tập anh ấy thích nghe nhạc nhẹ.
声音|sheng1 yin1|thanh âm|noun|âm thanh; tiếng nói|sound; voice|老师的声音非常清楚动听。|Lǎoshī de shēngyīn fēicháng qīngchu dòngtīng.|Giọng nói của thầy giáo rất rõ ràng và êm tai.
词典|ci2 dian3|từ điển|noun|từ điển|dictionary|学外语要经常查词典。|Xué wàiyǔ yào jīngcháng chá cídiǎn.|Học ngoại ngữ phải thường xuyên tra từ điển.
句子|ju4 zi5|cú tử|noun|câu văn; câu|sentence|请用这个生词造一个完整的句子。|Qǐng yòng zhège shēngcí zào yí ge wánzhěng de jùzi.|Xin hãy dùng từ mới này đặt một câu hoàn chỉnh.
段落|duan4 luo4|đoạn lạc|noun|đoạn văn; phân đoạn|paragraph|请朗读课文的第一段落。|Qǐng lǎngdú kèwén de dì-yī duànluò.|Xin hãy đọc to đoạn văn đầu tiên của bài học.
信誉|xin4 yu4|tín dự|noun|uy tín; danh dự|credit; reputation|这家老字号商店信誉很好。|Zhè jiā lǎozìhào shāngdiàn xìnyù hěn hǎo.|Cửa hàng lâu đời này có uy tín rất tốt.
作用|zuo4 yong4|tác dụng|noun|tác dụng; hiệu quả|action; effect|规律运动对身体健康有很大作用。|Guīlǜ yùndòng duì shēntǐ jiànkāng yǒu hěn dà zuòyòng.|Tập thể dục điều độ có tác dụng lớn đối với sức khỏe.
原因|yuan2 yin1|nguyên nhân|noun|nguyên nhân; lý do|reason; cause|警察正在调查事故发生的原因。|Jǐngchá zhèngzài diàochá shìgù fāshēng de yuányīn.|Cảnh sát đang điều tra nguyên nhân xảy ra sự cố.
结果|jie2 guo3|kết quả|noun|kết quả|result; outcome|经过认真复习，考试有了好结果。|Jīngguò rènzhēn fùxí, kǎoshì yǒu le hǎo jiéguǒ.|Sau khi ôn tập kỹ càng, kỳ thi đã có kết quả tốt.
目的|mu4 di4|mục đích|noun|mục đích|purpose; goal|他出国留学的目的是为了学医。|Tā chūguó liúxué de mùdì shì wèile xué yī.|Mục đích đi du học của anh ấy là để học ngành y.
重点|zhong4 dian3|trọng điểm|noun|trọng điểm; điểm then chốt|key point; emphasis|复习时要注意把握课文的重点。|Fùxí shí yào zhùyì bǎwò kèwén de zhòngdiǎn.|Khi ôn tập cần chú ý nắm chắc trọng điểm bài học.
特点|te4 dian3|đặc điểm|noun|đặc điểm; nét đặc trưng|characteristic; feature|这座建筑最大的特点就是古朴。|Zhè zuò jiànzhù zuì dà de tèdiǎn jiù shì gǔpǔ.|Đặc điểm lớn nhất của công trình này chính là nét cổ kính.
优点|you1 dian3|ưu điểm|noun|ưu điểm; điểm mạnh|merit; advantage|每个人都有自己的优点。|Měi ge rén dōu yǒu zìjǐ de yōudiǎn.|Mỗi người đều có ưu điểm riêng của mình.
缺点|que1 dian3|khuyết điểm|noun|khuyết điểm; điểm yếu|shortcoming; flaw|我们要勇于改正自己的缺点。|Wǒmen yào yǒngyú gǎizhèng zìjǐ de quēdiǎn.|Chúng ta phải dũng cảm sửa đổi khuyết điểm của bản thân.
水平|shui3 ping2|thủy bình|noun|mức độ; chuẩn mực|level; proficiency|多听多说是提高口语水平的好方法。|Duō tīng duō shuō shì tígāo kǒuyǔ shuǐpíng de hǎo fāngfǎ.|Nghe nhiều nói nhiều là cách tốt để nâng cao trình độ nói.
其实|qi2 shi2|kỳ thực|adverb|kỳ thực; thực ra|actually; in fact|那道题其实没有想象中那么难。|Nà dào tí qíshí méiyǒu xiǎngxiàng zhōng nàme nán.|Câu hỏi đó thực ra không khó như tưởng tượng.
尤其|you2 qi2|ưu kỳ|adverb|đặc biệt là; nhất là|especially; particularly|他喜欢所有球类，尤其是足球。|Tā xǐhuan suǒyǒu qiúlèi, yóuqí shì zúqiú.|Anh ấy thích tất cả môn bóng, đặc biệt là bóng đá.
几乎|ji1 hu1|ki ha|adverb|hầu như; gần như|almost; nearly|他激动得几乎说不出话来。|Tā jīdòng de jīhū shuō bù chū huà lai.|Anh ấy xúc động đến mức hầu như không nói nên lời.
一共|yi2 gong4|nhất cộng|adverb|tổng cộng; tất cả|in total; altogether|这些书买下来一共需要一百块钱。|Zhèxiē shū mǎi xiàlai yígòng xūyào yì bǎi kuài qián.|Mua hết chỗ sách này tổng cộng cần một trăm đồng.
互相|hu4 xiang1|hỗ tương|adverb|lẫn nhau; qua lại|mutually; each other|同学之间要互相体谅与帮助。|Tóngxué zhījiān yào hùxiāng tǐliàng yǔ bāngzhù.|Bạn học cùng lớp nên thông cảm và giúp đỡ lẫn nhau.
经常|jing1 chang2|kinh thường|adverb|thường xuyên; hay|often; regularly|晚饭后他经常在小区散步。|Wǎnfàn hòu tā jīngcháng zài xiǎoqū sànbù.|Sau bữa tối anh ấy thường đi dạo trong khu dân cư.
突然|tu1 ran2|đột nhiên|adverb|đột nhiên; bất ngờ|suddenly; abruptly|刚才还好好的，天突然下起雨来。|Gāngcái hái hǎohāo de, tiān tūrán xià qǐ yǔ lai.|Vừa rồi trời vẫn đẹp, đột nhiên lại đổ mưa.
偶尔|ou3 er3|ngẫu nhĩ|adverb|thỉnh thoảng; đôi khi|occasionally; once in a while|周末他偶尔去钓鱼。|Zhōumò tā ǒu'ěr qù diàoyú.|Cuối tuần anh ấy thỉnh thoảng đi câu cá.
先|xian1|tiên|adverb|trước; đầu tiên|first; before|下班后我先去超市买些水果。|Xiàbān hòu wǒ xiān qù chāoshì mǎi xiē shuǐguǒ.|Tan làm tôi trước tiên đến siêu thị mua chút hoa quả.
终于|zhong1 yu2|chung vu|adverb|cuối cùng; rốt cuộc|finally; at last|经过长期努力，他终于通过了考试。|Jīngguò chángqī nǔlì, tā zhōngyú tōngguò le kǎoshì.|Qua thời gian dài nỗ lực, anh ấy cuối cùng đã vượt qua kỳ thi.
另外|ling4 wai4|lệnh ngoại|conjunction|ngoài ra; bên cạnh đó|besides; in addition|我还要买两本书，另外还需要一支笔。|Wǒ hái yào mǎi liǎng běn shū, lìngwài hái xūyào yì zhī bǐ.|Tôi còn muốn mua hai cuốn sách, ngoài ra còn cần một cây bút.
或者|huo4 zhe3|hoặc giả|conjunction|hoặc; hay là|or; either or|今天下午你可以看书或者听音乐。|Jīntiān xiàwǔ nǐ kěyǐ kàn shū huòzhě tīng yīnyuè.|Chiều nay bạn có thể đọc sách hoặc nghe nhạc.
不但|bu2 dan4|bất đãn|conjunction|không những; không chỉ|not only|他不但汉语说得好，而且会写书法。|Tā búdàn hànyǔ shuō de hǎo, érqiě huì xiě shūfǎ.|Anh ấy không những nói tiếng Trung giỏi mà còn biết viết thư pháp.
而且|er2 qie3|nhi thả|conjunction|mà còn; lại còn|and also; moreover|这家餐厅菜品味道好，而且价格合理。|Zhè jiā cāntīng càipǐn wèidao hǎo, érqiě jiàgé hélǐ.|Nhà hàng này món ăn ngon, mà giá cả lại hợp lý.
只要|zhi3 yao4|chỉ yếu|conjunction|chỉ cần|as long as; provided|只要坚持练习，口语就能大幅提升。|Zhǐyào jiānchí liànxí, kǒuyǔ jiù néng dàfú tíshēng.|Chỉ cần kiên trì luyện tập, khẩu ngữ sẽ tiến bộ rất nhanh.
只有|zhi3 you3|chỉ hữu|conjunction|chỉ có (mới)|only if; only|只有努力奋斗，才能实现美好的梦想。|Zhǐyǒu nǔlì fèndòu, cáinéng shíxiàn měihǎo de mèngxiǎng.|Chỉ có nỗ lực phấn đấu mới có thể thực hiện được ước mơ tươi đẹp.
为了|wei4 le5|vi liễu|preposition|để; vì mục đích|for; in order to|为了保持好身材，他每天坚持跑步。|Wèile bǎochí hǎo shēncái, tā měitiān jiānchí pǎobù.|Để giữ gìn vóc dáng đẹp, anh ấy kiên trì chạy bộ mỗi ngày.
除了|chu2 le5|trừ liễu|preposition|ngoài ra; ngoại trừ|except; besides|除了周日，图书馆每天都准时开门。|Chúle zhōurì, túshūguǎn měitiān dōu zhǔnshí kāimén.|Ngoại trừ chủ nhật, thư viện mỗi ngày đều mở cửa đúng giờ.
根据|gen1 ju4|căn cứ|preposition|căn cứ vào; dựa trên|according to; based on|医生根据详细检查结果开出了处方。|Yīshēng gēnjù xiángxì jiǎnchá jiéguǒ kāichū le chǔfāng.|Bác sĩ dựa trên kết quả kiểm tra chi tiết đã kê đơn thuốc.
关于|guan1 yu2|quan vu|preposition|về; liên quan đến|about; regarding|今天开会讨论关于举办活动的具体方案。|Jīntiān kāihuì tǎolùn guānyú jǔbàn huódòng de jùtǐ fāng'àn.|Hôm nay họp bàn về phương án cụ thể tổ chức hoạt động.
"""

# Let's clean line 30 of BATCH_006: 水平 was in line 5.
# Replace duplicate 水平 with 方式|fang1 shi4|phương thức|noun|phương thức; cách thức|way; fashion|阅读是获取知识的重要方式。|Yuèdú shì huòqǔ zhīshi de zhòngyào fāngshì.|Đọc sách là một phương thức quan trọng để tiếp thu tri thức.
BATCH_006_CLEAN = BATCH_006.replace(
    "水平|shui3 ping2|thủy bình|noun|mức độ; chuẩn mực|level; proficiency|多听多说是提高口语水平的好方法。|Duō tīng duō shuō shì tígāo kǒuyǔ shuǐpíng de hǎo fāngfǎ.|Nghe nhiều nói nhiều là cách tốt để nâng cao trình độ nói.",
    "方式|fang1 shi4|phương thức|noun|phương thức; cách thức|way; fashion|阅读是获取知识的重要方式。|Yuèdú shì huòqǔ zhīshi de zhòngyào fāngshì.|Đọc sách là một phương thức quan trọng để tiếp thu tri thức."
)


def main():
    batches = [
        (1, BATCH_001),
        (2, BATCH_002_CLEAN),
        (3, BATCH_003),
        (4, BATCH_004),
        (5, BATCH_005_CLEAN),
        (6, BATCH_006_CLEAN),
    ]

    for num, raw_text in batches:
        lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
        print(f"Building and validating Level 3 Batch {num:03d} (lines: {len(lines)})...")
        save_batch(level=3, batch_num=num, raw_lines=lines)

    print("Level 3 complete! Total 300 items across 6 batches.")


if __name__ == "__main__":
    main()

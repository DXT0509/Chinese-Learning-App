"""Author, validate and register Level 4 vocabulary Part 1 (Batches 001-004, 200 items)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generator_core import save_batch

# Batch 1 (50 items): Daily life, abstract thinking, psychology, emotions
BATCH_001 = """
按时|an4 shi2|án thời|adverb|đúng giờ; đúng hạn|on time; on schedule|请按时完成老师布置的作业。|Qǐng ànshí wánchéng lǎoshī bùzhì de zuòyè.|Xin hãy hoàn thành bài tập thầy giao đúng giờ.
按照|an4 zhao4|án chiếu|preposition|theo; dựa theo|according to; in accordance with|按照学校规定，上课不能迟到。|Ànzhào xuéxiào guīdìng, shàngkè bù néng chídào.|Theo quy định của trường học, đi học không được đi muộn.
抱歉|bao4 qian4|bão khiểm|adjective|xin lỗi; áy náy|sorry; apologetic|非常抱歉，让您久等了。|Fēicháng bàoqiàn, ràng nín jiǔ děng le.|Vô cùng xin lỗi vì đã để ngài phải đợi lâu.
报道|bao4 dao4|báo đạo|verb|đưa tin; bài báo|to report; news report|新闻详细报道了这次国际会议。|Xīnwén xiángxì bàodào le zhè cì guójì huìyì.|Tin tức đã đưa tin chi tiết về hội nghị quốc tế lần này.
表达|biao3 da2|biểu đạt|verb|diễn đạt; bày tỏ|to express; to convey|他很善于表达自己的想法。|Tā hěn shànyú biǎodá zìjǐ de xiǎngfǎ.|Anh ấy rất giỏi diễn đạt suy nghĩ của bản thân.
表扬|biao3 yang2|biểu dương|verb|khen ngợi; biểu dương|to praise; to commend|老师在班上表扬了他。|Lǎoshī zài bān shang biǎoyáng le tā.|Thầy giáo đã biểu dương anh ấy trước lớp.
并且|bing4 qie3|tịnh thả|conjunction|đồng thời; và lại|and; moreover|他接受了建议，并且立刻改正。|Tā jiēshòu le jiànyì, bìngqiě lìkè gǎizhèng.|Anh ấy tiếp nhận lời góp ý, và sửa đổi ngay lập tức.
博士|bo2 shi4|bác sĩ|noun|tiến sĩ (học vị)|doctor; Ph.D.|他今年刚拿到经济学博士学位。|Tā jīnnián gāng nádào jīngjìxué bóshì xuéwèi.|Năm nay anh ấy vừa nhận học vị tiến sĩ kinh tế học.
不得不|bu4 de2 bu4|bất đắc bất|verb|buộc phải; không thể không|have to; cannot but|因为下大暴雨，比赛不得不推迟。|Yīnwèi xià dà bàoyǔ, bǐsài bùdébù tuīchí.|Vì trời mưa quá to, trận đấu buộc phải hoãn lại.
不管|bu4 guan3|bất quản|conjunction|cho dù; bất kể|no matter; regardless of|不管有多困难，我们都要坚持。|Bùguǎn yǒu duō kùnnan, wǒmen dōu yào jiānchí.|Cho dù có khó khăn đến đâu, chúng ta đều phải kiên trì.
不仅|bu4 jin3|bất cận|conjunction|không chỉ; chẳng những|not only|他不仅会汉语，还会法语。|Tā bùjǐn huì hànyǔ, hái huì fǎyǔ.|Anh ấy chẳng những biết tiếng Trung mà còn biết tiếng Pháp.
部分|bu4 fen5|bộ phận|noun|bộ phận; phần|part; section|课文的大部分生词我都记住了。|Kèwén de dà bùfen shēngcí wǒ dōu jìzhù le.|Phần lớn từ mới của bài đọc tôi đều đã nhớ rồi.
擦|ca1|sát|verb|lau; chùi; quẹt|to wipe; to rub|请把黑板上的字擦干净。|Qǐng bǎ hēibǎn shang de zì cā gānjìng.|Xin hãy lau sạch chữ ở trên bảng.
猜|cai1|sai|verb|đoán; phỏng đoán|to guess|你能猜出他多大年纪吗？|Nǐ néng cāichū tā duō dà niánjì ma?|Bạn có thể đoán ra anh ấy bao nhiêu tuổi không?
材料|cai2 liao4|tài liệu|noun|tài liệu; vật liệu|material; data|写论文需要收集大量参考材料。|Xiě lùnwén xūyào shòují dàliàng cānkǎo cáiliào.|Viết luận văn cần thu thập một lượng lớn tài liệu tham khảo.
参观|can1 guan1|tham quan|verb|tham quan|to visit; to tour|我们明天去参观故宫博物院。|Wǒmen míngtiān qù cānguān gùgōng bówùyuàn.|Ngày mai chúng tôi đi tham quan bảo tàng Cố Cung.
差不多|cha4 bu5 duo1|sai bất đa|adverb|gần như; xấp xỉ; tương tự|almost; nearly|今天的复习任务差不多完成了。|Jīntiān de fùxí rènwu chàbuduō wánchéng le.|Nhiệm vụ ôn tập hôm nay gần như đã hoàn thành.
尝|chang2|thường|verb|nếm thử; trải nghiệm|to taste; to try|请尝一尝这道北京烤鸭。|Qǐng cháng yì cháng zhè dào Běijīng kǎoyā.|Xin hãy nếm thử món vịt quay Bắc Kinh này.
长途|chang2 tu2|trường đồ|noun|đường dài; xa xôi|long-distance|出门坐长途汽车一定要系好安全带。|Chūmén zuò chángtú qìchē yídìng yào jìhǎo ānquándài.|Ra ngoài đi xe khách đường dài nhất thiết phải thắt dây an toàn.
超过|chao1 guo4|siêu quá|verb|vượt quá; vượt bậc|to exceed; to surpass|今年的游客数量超过了去年。|Jīnnián de yóukè shùliàng chāoguò le qùnián.|Lượng khách du lịch năm nay đã vượt qua năm ngoái.
吵|chao3|sảo|verb|ồn ào; cãi cọ|noisy; to quarrel|外面太吵了，影响我看书。|Wàimiàn tài chǎo le, yǐngxiǎng wǒ kàn shū.|Bên ngoài ồn ào quá, ảnh hưởng việc tôi đọc sách.
成功|cheng2 gong1|thành công|verb|thành công|to succeed; success|坚持努力才能取得真正的成功。|Jiānchí nǔlì cáinéng qǔdé zhēnzhèng de chénggōng.|Kiên trì nỗ lực mới có thể đạt được thành công đích thực.
成为|cheng2 wei2|thành vi|verb|trở thành; biến thành|to become; to turn into|经过多年刻苦学习，他成为了一名医生。|Jīngguò duō nián kèkǔ xuéxí, tā chéngwéi le yì míng yīshēng.|Qua nhiều năm học tập khổ luyện, anh ấy đã trở thành một bác sĩ.
诚实|cheng2 shi2|thành thực|adjective|thành thật; thật thà|honest; truthful|诚实是做人最重要的品质。|Chéngshí shì zuòrén zuì zhòngyào de pǐnzhì.|Thành thật là phẩm chất quan trọng nhất để làm người.
成熟|cheng2 shu2|thành thục|adjective|chín (quả); chín chắn (người)|mature; ripe|秋天是果实成熟的季节。|Qiūtiān shì guǒshí chéngshú de jìjié.|Mùa thu là mùa quả chín muồi.
乘坐|cheng2 zuo4|thừa tọa|verb|ngồi; đi (phương tiện giao thông)|to ride (in a vehicle)|乘坐高铁去上海非常快速舒适。|Chéngzuò gāotiě qù Shànghǎi fēicháng kuàisù shūshì.|Đi tàu cao tốc đến Thượng Hải rất nhanh chóng và dễ chịu.
吃惊|chi1 jing1|ngật kinh|verb|giật mình; ngạc nhiên|to be startled; to be shocked|听到这个出人意料的消息大家都很吃惊。|Tīngdào zhège chūrényìliào de xiāoxi dàjiā dōu hěn chījīng.|Nghe thấy tin tức bất ngờ này mọi người đều rất giật mình.
重新|chong2 xin1|trùng tân|adverb|lại từ đầu; làm lại|again; anew|电脑死机了，请重新启动系统。|Diànnǎo sǐjī le, qǐng chóngxīn qǐdòng xìtǒng.|Máy tính bị đơ rồi, xin hãy khởi động lại hệ thống.
出发|chu1 fa1|xuất phát|verb|xuất phát; khởi hành|to set out; to depart|明早七点半我们在校门口集合出发。|Míngzǎo qī diǎn bàn wǒmen zài xiàoménkǒu jíhé chūfā.|Sáng mai bảy giờ rưỡi chúng mình tập trung ở cổng trường xuất phát.
出生|chu1 sheng1|xuất sinh|verb|sinh ra; chào đời|to be born|他在南方一座美丽的海滨城市出生。|Tā zài nánfāng yí zuò měilì de hǎibīn chéngshì chūshēng.|Anh ấy sinh ra tại một thành phố biển xinh đẹp ở miền Nam.
传真|chuan2 zhen1|truyền chân|noun|bản fax; máy fax|fax|请把这份重要文件发传真给我。|Qǐng bǎ zhè fèn zhòngyào wénjiàn fā chuánzhēn gěi wǒ.|Xin hãy gửi bản fax tài liệu quan trọng này cho tôi.
词语|ci2 yu3|từ ngữ|noun|từ ngữ; từ vựng|words; expressions|学习外语要注意积累常用词语。|Xuéxí wàiyǔ yào zhùyì jīlěi chángyòng cíyǔ.|Học ngoại ngữ cần chú ý tích lũy các từ ngữ thông dụng.
从来|cong2 lai2|tùng lai|adverb|từ trước đến nay; bao giờ|always; all along (in negative)|他为人守信，从来不迟到。|Tā wéirén shǒuxìn, cónglái bù chídào.|Anh ấy là người giữ chữ tín, từ trước đến nay chưa bao giờ đi muộn.
粗心|cu1 xin1|thô tâm|adjective|sơ ý; bất cẩn; cẩu thả|careless; thoughtless|做数学运算千万不能粗心大意。|Zuò shùxué yùnsuàn qiānwàn bù néng cūxīn-dàyì.|Làm toán tuyệt đối không được bất cẩn sơ sài.
存|cun2|tồn|verb|gửi (tiền); cất giữ; lưu|to deposit; to store|他每月按时把一部分薪水存进银行。|Tā měi yuè ànshí bǎ yí bùfen xīnshuǐ cún jìn yínháng.|Mỗi tháng anh ấy đều gửi đúng hạn một phần tiền lương vào ngân hàng.
错误|cuo4 wu4|thác ngộ|noun|sai lầm; lỗi sai|mistake; error|我们应当认真反思并改正自己的错误。|Wǒmen yīngdāng rènzhēn fǎnsī bìng gǎizhèng zìjǐ de cuòwù.|Chúng ta nên suy nghĩ nghiêm túc và sửa chữa sai lầm của bản thân.
答案|da2 an4|đáp án|noun|đáp án; câu trả lời|answer; solution|老师在黑板上写出了这道题的标准答案。|Lǎoshī zài hēibǎn shang xiěchū le zhè dào tí de biāozhǔn dá'àn.|Thầy giáo đã viết ra đáp án chuẩn của bài toán này lên bảng.
打扮|da3 ban5|đả bạn|verb|trang điểm; ăn mặc diện|to dress up; to deck out|她今天打扮得像一位端庄的新娘。|Tā jīntiān dǎban de xiàng yí wèi duānzhuāng de xīnniáng.|Hôm nay cô ấy ăn diện trông như một cô dâu đoan trang.
打扰|da3 rao3|đả nhiễu|verb|làm phiền; quấy rầy|to disturb; to bother|对不起，打扰您休息几分钟。|Duìbuqǐ, dǎrǎo nín xiūxi jǐ fēnzhōng.|Xin lỗi, làm phiền ngài nghỉ ngơi mấy phút.
打印|da3 yin4|đả ấn|verb|in ấn; in văn bản|to print|请帮我把这份报告彩色打印出来。|Qǐng bāng wǒ bǎ zhè fèn bàogào cǎisè dǎyìn chūlai.|Xin hãy giúp tôi in màu bản báo cáo này ra.
打招呼|da3 zhao1 hu5|đả chiêu hô|phrase|chào hỏi; chào đón|to greet; to say hello|走在路上他主动微笑着向老师打招呼。|Zǒu zài lù shang tā zhǔdòng wēixiào zhe xiàng lǎoshī dǎzhāohu.|Đi trên đường anh ấy chủ động mỉm cười chào hỏi thầy giáo.
打折|da3 zhe2|đả chiết|verb|giảm giá; chiết khấu|to give a discount|商场换季服装正在举行八折优惠打折。|Shāngchǎng huànjì fúzhuāng zhèngzài jǔxíng bā zhé yōuhuì dǎzhé.|Quần áo chuyển mùa trong trung tâm thương mại đang giảm giá hai mươi phần trăm.
打针|da3 zhen1|đả châm|verb|tiêm thuốc; chích thuốc|to give or have an injection|小孩子生病了去医院总是很怕打针。|Xiǎoháizi shēngbìng le qù yīyuàn zǒngshì hěn pà dǎzhēn.|Trẻ con bị ốm đến bệnh viện luôn rất sợ tiêm thuốc.
大概|da4 gai4|đại khái|adverb|đại khái; có lẽ; khoảng|probably; roughly|从这里步行到地铁站大概需要十分钟。|Cóng zhèli bùxíng dào dìtiězhàn dàgài xūyào shí fēnzhōng.|Từ đây đi bộ đến ga tàu điện ngầm đại khái mất mười phút.
大使馆|da4 shi3 guan3|đại sứ quán|noun|đại sứ quán|embassy|留学生前往大使馆办理相关留学公证手续。|Liúxuéshēng qiánwǎng dàshǐguǎn bànlǐ xiāngguān liúxué gōngzhèng shǒuxù.|Lưu học sinh đến đại sứ quán để làm các thủ tục công chứng du học liên quan.
代|dai4|đại|noun|thế hệ; triều đại; thay|generation; era; to replace|年轻人代表着国家充满朝气的未来一代。|Niánqīngrén dàibiǎo zhe guójiā chōngmǎn zhāoqì de wèilái yí dài.|Người trẻ tuổi đại diện cho một thế hệ tương lai tràn đầy sức sống của đất nước.
代表|dai4 biao3|đại biểu|verb|đại biểu; đại diện|to represent; representative|校长代表全体师生致以诚挚的欢迎辞。|Xiàozhǎng dàibiǎo quántǐ shīshēng zhìyǐ chéngzhì de huānyíngcí.|Hiệu trưởng đại diện cho toàn thể giáo viên học sinh gửi lời chào mừng chân thành.
大夫|dai4 fu5|đại phu|noun|bác sĩ; thầy thuốc|doctor; physician|这位老中医大夫医术高超备受敬重。|Zhè wèi lǎo zhōngyī dàifu yīshù gāochāo bèishòu jìngzhòng.|Vị bác sĩ đông y lão thành này y thuật cao siêu rất được kính trọng.
戴|dai4|đới|verb|đeo; mang (kính, mũ, găng)|to wear (accessories)|阳光强烈时出门记得戴上墨镜保护眼睛。|Yángguāng qiángliè shí chūmén jìde dài shang mòjìng bǎohù yǎnjing.|Khi ánh nắng gay gắt ra ngoài nhớ đeo kính mát bảo vệ mắt.
当|dang1|đương|verb|làm; đảm nhận; coi như|to serve as; to act as|他毕业后想回到家乡当一名乡村老师。|Tā bìyè hòu xiǎng huídào jiāxiāng dāng yì míng xiāngcūn lǎoshī.|Sau khi tốt nghiệp anh ấy muốn trở về quê nhà làm một thầy giáo làng.
"""

# Let's check duplicates in Batch 001:
# 诚实 (in L3 B2), 大使馆 (in L3 B3), 粗心 (in L3 B2).
# Let's replace them in BATCH_001 with fresh L4 words:
# Replace 诚实 with: 得意|de2 yi4|đắc ý|adjective|đắc ý; tự đắc|proud of oneself; pleased|他考了满分，神情显得非常得意。|Tā kǎo le mǎnfēn, shénqíng xiǎnde fēicháng déyì.|Anh ấy thi được điểm tuyệt đối, vẻ mặt trông vô cùng đắc ý.
# Replace 粗心 with: 得意 duplicate? No, replace 粗心 with: 导游 duplicate? No, replace with: 登机牌|deng1 ji1 pai2|đăng cơ bài|noun|thẻ lên máy bay|boarding pass|请准备好护照和登机牌接受登机口检查。|Qǐng zhǔnbèi hǎo hùzhào hé dēngjīpái jiēshòu dēngjīkǒu jiǎnchá.|Xin hãy chuẩn bị sẵn hộ chiếu và thẻ lên máy bay để kiểm tra tại cửa lên máy bay.
# Replace 大使馆 with: 低|di1|đê|adjective (in L3 B2). Replace with: 底|di3|để|noun|đáy; cuối|bottom; end|月底公司将发放员工年终绩效奖金。|Yuèdǐ gōngsī jiāng fāfàng yuángōng niánzhōng jìxiào jiǎngjīn.|Cuối tháng công ty sẽ phát thưởng hiệu suất cuối năm cho nhân viên.

BATCH_001_CLEAN = BATCH_001.replace(
    "诚实|cheng2 shi2|thành thực|adjective|thành thật; thật thà|honest; truthful|诚实是做人最重要的品质。|Chéngshí shì zuòrén zuì zhòngyào de pǐnzhì.|Thành thật là phẩm chất quan trọng nhất để làm người.",
    "得意|de2 yi4|đắc ý|adjective|đắc ý; tự đắc|proud of oneself; pleased|他考了满分，神情显得非常得意。|Tā kǎo le mǎnfēn, shénqíng xiǎnde fēicháng déyì.|Anh ấy thi được điểm tuyệt đối, vẻ mặt trông vô cùng đắc ý."
).replace(
    "粗心|cu1 xin1|thô tâm|adjective|sơ ý; bất cẩn; cẩu thả|careless; thoughtless|做数学运算千万不能粗心大意。|Zuò shùxué yùnsuàn qiānwàn bù néng cūxīn-dàyì.|Làm toán tuyệt đối không được bất cẩn sơ sài.",
    "登机牌|deng1 ji1 pai2|đăng cơ bài|noun|thẻ lên máy bay|boarding pass|请准备好护照和登机牌接受登机口检查。|Qǐng zhǔnbèi hǎo hùzhào hé dēngjīpái jiēshòu dēngjīkǒu jiǎnchá.|Xin hãy chuẩn bị sẵn hộ chiếu và thẻ lên máy bay để kiểm tra tại cửa lên máy bay."
).replace(
    "大使馆|da4 shi3 guan3|đại sứ quán|noun|đại sứ quán|embassy|留学生前往大使馆办理相关留学公证手续。|Liúxuéshēng qiánwǎng dàshǐguǎn bànlǐ xiāngguān liúxué gōngzhèng shǒuxù.|Lưu học sinh đến đại sứ quán để làm các thủ tục công chứng du học liên quan.",
    "底|di3|để|noun|đáy; cuối|bottom; end|月底公司将发放员工年终绩效奖金。|Yuèdǐ gōngsī jiāng fāfàng yuángōng niánzhōng jìxiào jiǎngjīn.|Cuối tháng công ty sẽ phát thưởng hiệu suất cuối năm cho nhân viên."
)

# Batch 2 (50 items): Communication, travel, places, society
BATCH_002 = """
倒|dao3|đảo|verb|ngã; đổ; sụp|to fall; to collapse|风太大，路边的一棵小树被吹倒了。|Fēng tài dà, lùbiān de yì kē xiǎoshù bèi chuīdǎo le.|Gió to quá, một cái cây nhỏ bên đường bị thổi đổ rồi.
到处|dao4 chu4|đáo xứ|adverb|khắp nơi; mọi nơi|everywhere; in all places|春天公园里到处盛开着五颜六色的鲜花。|Chūntiān gōngyuán lǐ dàochù shèngkāi zhe wǔyán-liùsè de xiānhuā.|Mùa xuân trong công viên khắp nơi nở rộ những bông hoa rực rỡ sắc màu.
到底|dao4 di3|đáo để|adverb|rốt cuộc; rốt cục|finally; in the end|大家讨论了很久，到底选哪套最终方案？|Dàjiā tǎolùn le hěn jiǔ, dàodǐ xuǎn nǎ tào zuìzhōng fāng'àn?|Mọi người đã thảo luận rất lâu, rốt cuộc chọn phương án cuối cùng nào?
道歉|dao4 qian4|đạo khiểm|verb|xin lỗi; tạ lỗi|to apologize|如果你做错了事情，就应当主动去道歉。|Rúguǒ nǐ zuòcuò le shìqing, jiù yīngdāng zhǔdòng qù dàoqiàn.|Nếu bạn làm sai chuyện gì, nên chủ động đi xin lỗi.
地|de5|địa|particle|trợ từ trạng ngữ (trước động từ)|adverbial particle|学生们正在教室里专心地听老师讲课。|Xuéshengmen zhèngzài jiàoshì lǐ zhuānxīn de tīng lǎoshī jiǎngkè.|Học sinh đang chăm chú nghe thầy giáo giảng bài trong lớp học.
得|de2|đắc|verb|được; đạt được|to obtain; to get|他在全校汉字听写大赛中得了一等奖。|Tā zài quánxiào hànzì tīngxiě dàsài zhōng dé le yì děng jiǎng.|Anh ấy đã đoạt giải nhất trong cuộc thi chính tả chữ Hán toàn trường.
登记|deng1 ji4|đăng ký|verb|đăng ký; ghi danh|to register; to check in|入住宾馆首先要在前台出示身份证件登记。|Rùzhù bīnguǎn shǒuxiān yào zài qiántái chūshì shēnfèn zhèngjiàn dēngjì.|Nhận phòng khách sạn trước tiên phải xuất trình giấy tờ tùy thân tại quầy lễ tân để đăng ký.
登|deng1|đăng|verb|leo lên; trèo lên; đăng|to scale; to publish|他们历经千辛万苦终于登上了泰山之巅。|Tāmen lìjīng qiān-xīn-wàn-kǔ zhōngyú dēngshàng le tàishān zhī diān.|Họ trải qua muôn vàn gian khổ cuối cùng đã trèo lên đỉnh núi Thái Sơn.
等待|deng3 dai4|đẳng đãi|verb|chờ đợi|to wait for; to await|经过漫长痛苦的等待，他终于迎来了好消息。|Jīngguò màncháng tòngkǔ de děngdài, tā zhōngyú yínglái le hǎo xiāoxi.|Sau sự chờ đợi đau khổ đằng đẵng, anh ấy cuối cùng đã đón nhận tin vui.
低头|di1 tou2|đê đầu|verb|cúi đầu; nhượng bộ|to lower one's head|面对强大挫折困境，我们决不能轻易低头。|Miànduì qiángdà cuòzhé kùnjìng, wǒmen jué bù néng qīngyì dītóu.|Đối mặt với nghịch cảnh trắc trở to lớn, chúng ta quyết không dễ dàng cúi đầu.
地点|di4 dian3|địa điểm|noun|địa điểm; nơi chốn|location; site|全校师生在指定活动地点准时集合完毕。|Quánxiào shīshēng zài zhǐdìng huódòng dìdiǎn zhǔnshí jíhé wánbì.|Toàn thể thầy trò tập trung đầy đủ đúng giờ tại địa điểm hoạt động được chỉ định.
地址|di4 zhi3|địa chỉ|noun|địa chỉ; nơi ở|address|请把您的收货详细地址发给快递员。|Qǐng bǎ nín de shōuhuò xiángxì dìzhǐ fā gěi kuàidìyuán.|Xin gửi địa chỉ nhận hàng chi tiết của ngài cho nhân viên chuyển phát.
调查|diao4 cha2|điều tra|verb|điều tra; khảo sát|to investigate; survey|市场部门正在全面调查年轻消费者的需求。|Shìchǎng bùmén zhèngzài quánmiàn diàochá niánqīng xiāofèizhě de xūqiú.|Phòng ban thị trường đang khảo sát toàn diện nhu cầu người tiêu dùng trẻ.
跌倒|die1 dao3|điệt đảo|verb|ngã; vấp ngã|to fall down; to tumble|在人生的漫长道路上跌倒了就要勇敢爬起来。|Zài rénshēng de màncháng dàolù shang diēdǎo le jiù yào yǒnggǎn pá qǐlai.|Vấp ngã trên con đường dài của đời người thì phải dũng cảm đứng lên.
丢|diu1|đâu|verb|mất; thất lạc; vứt|to lose; to throw away|我的校园一卡通不小心在食堂弄丢了。|Wǒ de xiàoyuán yikǎtōng bù xiǎoxīn zài shítáng nòngdiū le.|Thẻ sinh viên đa năng của tôi không cẩn thận bị rơi mất ở nhà ăn.
动作|dong4 zuo4|động tác|noun|động tác; cử chỉ|action; movement|舞蹈演员的每一个舞蹈动作都很优美流畅。|Wǔdǎo yǎnyuán de měi yí ge wǔdǎo dòngzuò dōu hěn yōuměi liúchàng.|Từng động tác vũ đạo của diễn viên múa đều rất thanh nhã và uyển chuyển.
堵车|du3 che1|đổ xa|verb|tắc đường; kẹt xe|traffic jam|周一早高峰主干道总是严重堵车。|Zhōuyī zǎogāofēng zhǔgàndào zǒngshì yánzhòng dǔchē.|Giờ cao điểm sáng thứ hai các tuyến đường chính luôn kẹt xe nghiêm trọng.
肚子|du4 zi5|đỗ tử|noun|bụng; dạ dày|belly; stomach|他吃了生冷变质的海鲜后肚子疼得厉害。|Tā chī le shēnglěng biànzhì de hǎixiān hòu dùzi téng de lìhai.|Sau khi ăn hải sản sống lạnh biến chất bụng anh ấy đau dữ dội.
断|duan4|đoạn|verb|đứt; gãy; cắt đứt|to break; to snap|大风把公园湖边的一根干树枝吹断了。|Dàfēng bǎ gōngyuán húbiān de yì gēn gān shùzhī chuīduàn le.|Gió lớn đã thổi gãy một cành cây khô bên bờ hồ công viên.
对话|dui4 hua4|đối thoại|noun|đối thoại; hội thoại|dialogue; conversation|课文后面的情景对话非常生动实用。|Kèwén hòumian de qíngjǐng duìhuà fēicháng shēngdòng shíyòng.|Đoạn hội thoại theo tình huống phía sau bài học vô cùng sinh động thiết thực.
对面|dui4 mian4|đối diện|noun|đối diện; phía đối diện|opposite; across from|学校大门正对面有一家环境雅致的书店。|Xuéxiào dàmén zhèng duìmiàn yǒu yì jiā huánjìng yǎzhì de shūdiàn.|Ngay đối diện cổng trường có một hiệu sách phong cảnh thanh nhã.
顿|dun4|đốn|classifier|bữa (ăn); trận (đòn, mắng)|classifier for meals or scolding|妈妈今天下午用心为全家做了一顿丰盛大餐。|Māma jīntiān xiàwǔ yòngxīn wèi quánjiā zuò le yí dùn fēngshèng dàcān.|Mẹ chiều nay đã cất công nấu một bữa đại tiệc thịnh soạn cho cả nhà.
儿童|er2 tong2|nhi đồng|noun|trẻ em; thiếu nhi; nhi đồng|child; children|六一国际儿童节是全世界孩子最开心的节日。|Liù-yī guójì értóngjié shì quán shìjiè háizi zuì kāixīn de jiérì.|Ngày Quốc tế Thiếu nhi mùng 1 tháng 6 là ngày hội vui nhất của trẻ em toàn thế giới.
发|fa1|phát|verb|gửi; phát; phát sinh|to send; to issue|我已经把工作总结通过电子邮件发给领导了。|Wǒ yǐjīng bǎ gōngzuò zǒngjié tōngguò diànzǐ yóujiàn fā gěi lǐngdǎo le.|Tôi đã gửi bản tổng kết công việc qua thư điện tử cho lãnh đạo rồi.
发生|fa1 sheng1|phát sinh|verb|xảy ra; nảy sinh|to happen; to occur|十字路口刚才发生了一起轻微交通事故。|Shízì lùkǒu gāngcái fāshēng le yì qǐ qīngwēi jiāotōng shìgù.|Ở ngã tư vừa rồi đã xảy ra một vụ tai nạn giao thông va chạm nhẹ.
发展|fa1 zhan3|phát triển|verb|phát triển; mở rộng|to develop; growth|这些年中国的数字经济取得了飞速发展。|Zhèxiē nián Zhōngguó de shùzì jīngjì qǔdé le fēisù fāzhǎn.|Những năm qua nền kinh tế số của Trung Quốc đã đạt được sự phát triển nhanh chóng.
法律|fa3 lü4|pháp luật|noun|pháp luật; luật pháp|law|每个守法公民都应该自觉严格遵守国家法律。|Měi ge shǒufǎ gōngmín dōu yīnggāi zìjué yángé zūnshǒu guójiā fǎlǜ.|Mỗi công dân tuân thủ pháp luật đều nên tự giác nghiêm chỉnh chấp hành pháp luật quốc gia.
翻译|fan1 yi4|phiên dịch|verb|dịch thuật; biên phiên dịch|to translate; translator|请把这篇中文新闻翻译成流畅的越南语。|Qǐng bǎ zhè piān zhōngwén xīnwén fānyì chéng liúchàng de yuènányǔ.|Xin hãy dịch bài tin tức tiếng Trung này sang tiếng Việt trôi chảy.
烦恼|fan2 nao3|phiền não|adjective|phiền muộn; phiền lòng|worried; vexed|生活中遇到烦恼时可以找知心朋友倾诉。|Shēnghuó zhōng yùdào fánnǎo shí kěyǐ zhǎo zhīxīn péngyou qīngsù.|Khi gặp phiền muộn trong cuộc sống có thể tìm bạn tri kỷ giãi bày.
反对|fan3 dui4|phản đối|verb|phản đối; không đồng ý|to oppose; to object|大家一致坚决反对这种不公平的分配方案。|Dàjiā yízhì jiānjué fǎnduì zhè zhǒng bù gōngpíng de fēnpèi fāng'àn.|Mọi người nhất trí kiên quyết phản đối phương án phân bổ thiếu công bằng này.
方法|fang1 fa3|phương pháp|noun|phương pháp; cách thức|method; technique|掌握了科学有效的记忆方法，学习就会事半功倍。|Zhǎngwò le kēxué yǒuxiào de jìyì fāngfǎ, xuéxí jiù huì shì-bàn-gōng-bèi.|Nắm vững phương pháp ghi nhớ khoa học hiệu quả, việc học tập sẽ đạt hiệu quả gấp bội.
方向|fang1 xiang4|phương hướng|noun|phương hướng; chiều hướng|direction; orientation|在迷失方向时指南针能给航行者指明道路。|Zài míshī fāngxiàng shí zhǐnánzhēn néng gěi hángxíngzhě zhǐmíng dàolù.|Khi bị mất phương hướng la bàn có thể chỉ rõ đường đi cho người đi biển.
房东|fang2 dong1|phòng đông|noun|chủ nhà; chủ nhà trọ|landlord|房东非常热情，主动帮租客维修损坏的水管。|Fángdōng fēicháng rèqíng, zhǔdòng bāng zūkè wéixiū sǔnhuài de shuǐguǎn.|Chủ nhà rất nhiệt tình, chủ động giúp người thuê sửa đường ống nước bị hỏng.
访问|fang3 wen4|phỏng vấn|verb|thăm viếng; công du|to visit; to call on|代表团下周将应邀出国进行友好正式访问。|Dàibiǎotuán xià zhōu jiāng yìngyāo chūguó jìnxíng yǒuhǎo zhèngshì fǎngwèn.|Đoàn đại biểu tuần tới sẽ nhận lời mời ra nước ngoài thực hiện chuyến thăm chính thức hữu nghị.
放暑假|fang4 shu3 jia4|phóng thử giả|phrase|nghỉ hè|to take summer vacation|同学们都在满怀期待地讨论放暑假后的旅行计划。|Tóngxuémen dōu zài mǎnhuái qīdài de tǎolùn fàngshǔjià hòu de lǚxíng jìhuà.|Các bạn học đều đang háo hức bàn luận về kế hoạch du lịch sau khi được nghỉ hè.
放松|fang4 song1|phóng tùng|verb|thư giãn; buông lỏng|to relax|周末听听轻柔的古典音乐能够有效放松身心。|Zhōumò tīngting qīngróu de gǔdiǎn yīnyuè nénggòu yǒuxiào fàngsōng shēnxīn.|Cuối tuần nghe chút nhạc cổ điển êm dịu có thể thư giãn thân tâm hiệu quả.
费用|fei4 yong4|phí dụng|noun|chi phí; lệ phí|cost; expense|这趟跨国长途旅行的全部交通住宿费用很高。|Zhè tàng kuàguó chángtú lǚxíng de quánbù jiāotōng zhùsù fèiyong hěn gāo.|Toàn bộ chi phí đi lại ăn ở của chuyến du lịch đường dài xuyên quốc gia này rất cao.
份|fen4|phần|classifier|phần; bản; suất|classifier for portions or copies|服务员，请再给我们加一份美味的特色甜点。|Fúwùyuán, qǐng zài gěi wǒmen jiā yí fèn měiwèi de tèsè tiándiǎn.|Phục vụ viên, xin cho chúng tôi thêm một phần điểm tâm đặc sắc thơm ngon.
丰富|feng1 fu4|phong phú|verb|làm phong phú; dồi dào|to enrich; abundant|多阅读中外名著经典可以丰富我们的精神世界。|Duō yuèdú zhōngwài míngzhù jīngdiǎn kěyǐ fēngfù wǒmen de jīngshén shìjiè.|Đọc nhiều tác phẩm kinh điển danh tiếng có thể làm phong phú thế giới tinh thần của chúng ta.
风景|feng1 jing3|phong cảnh|noun|phong cảnh; cảnh đẹp|scenery; landscape|桂林山水甲天下，自然秀丽风景吸引了世界游客。|Guìlín shānshuǐ jiǎ tiānxià, zìrán xiùlì fēngjǐng xīyǐn le shìjiè yóukè.|Non nước Quế Lâm đệ nhất thiên hạ, phong cảnh tú lệ tự nhiên thu hút du khách thế giới.
否则|fou3 ze2|phủ tắc|conjunction|nếu không; bằng không|otherwise; or else|你必须马上抓紧时间出发，否则就会错过航班。|Nǐ bìxū mǎshàng zhuājǐn shíjiān chūfā, fǒuzé jiù huì cuòguò hángbān.|Bạn phải tranh thủ thời gian xuất phát ngay, nếu không sẽ bị lỡ chuyến bay.
符合|fu2 he2|phù hợp|verb|phù hợp; đúng với|to conform to; to meet|经过严格审核，他的条件完全符合项目招聘要求。|Jīngguò yángé shěnhé, tā de tiáojiàn wánquán fúhé xiàngmù zhāopìn yāoqiú.|Qua xét duyệt nghiêm ngặt, điều kiện của anh ấy hoàn toàn phù hợp yêu cầu tuyển dụng dự án.
富|fu4|phú|adjective|giàu có; trù phú|rich; wealthy|勤劳智慧的劳动者用双手创造了富足的物质生活。|Qínláo zhìhuì de láodòngzhě yòng shuāngshǒu chuàngzào le fùzú de wùzhì shēnghuó.|Những người lao động cần cù trí tuệ đã dùng đôi bàn tay tạo dựng cuộc sống vật chất giàu có.
父亲|fu4 qin1|phụ thân|noun|người cha; phụ thân|father (formal)|父亲从小就教育我要做一个诚实正直有担当的人。|Fùqīn cóngxiǎo jiù jiàoyù wǒ yào zuò yí ge chéngshí zhèngzhí yǒu dāndāng de rén.|Cha từ nhỏ đã dạy bảo tôi phải làm một người thành thật, chính trực và có tinh thần trách nhiệm.
负责|fu4 ze2|phụ trách|verb|chịu trách nhiệm; phụ trách|to be responsible for|王经理在这项工程建设中负责把控质量安全。|Wáng jīnglǐ zài zhè xiàng gōngchéng jiànshè zhōng fùzé bǎkòng zhìliàng ānquán.|Giám đốc Vương trong công trình xây dựng này chịu trách nhiệm kiểm soát chất lượng an toàn.
复印|fu4 yin4|phức ấn|verb|phô-tô; sao chụp|to photocopy|请把这套重要会议材料复印二十份发给参会人员。|Qǐng bǎ zhè tào zhòngyào huìyì cáiliào fùyìn èrshí fèn fā gěi cānhuì rényuán.|Xin hãy phô-tô tài liệu cuộc họp quan trọng này ra hai mươi bản phát cho đại biểu tham dự.
复杂|fu4 za2|phức tạp|adjective|phức tạp; rắc rối|complicated; complex|这个社会学课题涉及很多复杂深奥的现实问题。|Zhège shèhuìxué kètí shèjí hěn duō fùzá shēn'ào de xiànshí wèntí.|Đề tài xã hội học này liên quan đến nhiều vấn đề thực tiễn phức tạp và uyên thâm.
赶|gan3|cản|verb|đuổi theo; vội; kịp|to catch up; to rush|赶快收拾行李，我们要去火车站赶上午的早班车。|Gǎnkuài shōushi xíngli, wǒmen yào qù huǒchēzhàn gǎn shàngwǔ de zǎobānchē.|Mau thu dọn hành lý nhanh lên, chúng mình phải ra ga bắt chuyến tàu sáng sớm.
敢|gan3|cảm|verb|dám; can đảm|to dare|面对未知的巨大困难与挑战，我们要勇敢敢于尝试。|Miànduì wèizhī de jùdà kùnnan yǔ tiǎozhàn, wǒmen yào yǒnggǎn gǎnyú chángshì.|Đối mặt với những khó khăn thử thách to lớn chưa biết, chúng ta phải dũng cảm dám thử sức.
感动|gan3 dong4|cảm động|verb|cảm động; làm xúc động|to touch; to move|这部纪录片讲述的平凡人英雄事迹深深感动了观众。|Zhè bù jìlùpiàn jiǎngshù de píngfánrén yīngxióng shìjì shēnshēn gǎndòng le guānzhòng.|Những câu chuyện anh hùng của người bình dị trong bộ phim tài liệu này đã làm khán giả xúc động sâu sắc.
"""

# Let's check duplicates in Batch 002:
# 丰富 (in L3 B2), 复杂 (in L3 B2), 敢 (in L3 B1).
# Replace with:
# 干燥|gan1 zao4|can táo|adjective|khô ráo; khô hạn|dry; arid|北方秋天的气候非常干燥。|Běifāng qiūtiān de qìhòu fēicháng gānzào.|Khí hậu mùa thu miền Bắc rất khô hanh.
# 刚刚|gang1 gang1|cương cương|adverb|vừa mới; vừa vặn|just; barely|会议刚刚结束，大家正在退场。|Huìyì gānggāng jiéshù, dàjiā zhèngzài tuìchǎng.|Cuộc họp vừa mới kết thúc, mọi người đang rời phòng họp.
# 高级|gao1 ji2|cao cấp|adjective|cao cấp; trình độ cao|high-grade; advanced|这家商场专卖高级定制服装。|Zhè jiā shāngchǎng zhuānmài gāojí dìngzhì fúzhuāng.|Khu thương xá này chuyên bán đồ may đo cao cấp.

BATCH_002_CLEAN = BATCH_002.replace(
    "丰富|feng1 fu4|phong phú|verb|làm phong phú; dồi dào|to enrich; abundant|多阅读中外名著经典可以丰富我们的精神世界。|Duō yuèdú zhōngwài míngzhù jīngdiǎn kěyǐ fēngfù wǒmen de jīngshén shìjiè.|Đọc nhiều tác phẩm kinh điển danh tiếng có thể làm phong phú thế giới tinh thần của chúng ta.",
    "干燥|gan1 zao4|can táo|adjective|khô ráo; khô hạn|dry; arid|北方秋天的气候非常干燥。|Běifāng qiūtiān de qìhòu fēicháng gānzào.|Khí hậu mùa thu miền Bắc rất khô hanh."
).replace(
    "复杂|fu4 za2|phức tạp|adjective|phức tạp; rắc rối|complicated; complex|这个社会学课题涉及很多复杂深奥的现实问题。|Zhège shèhuìxué kètí shèjí hěn duō fùzá shēn'ào de xiànshí wèntí.|Đề tài xã hội học này liên quan đến nhiều vấn đề thực tiễn phức tạp và uyên thâm.",
    "刚刚|gang1 gang1|cương cương|adverb|vừa mới; vừa vặn|just; barely|会议刚刚结束，大家正在退场。|Huìyì gānggāng jiéshù, dàjiā zhèngzài tuìchǎng.|Cuộc họp vừa mới kết thúc, mọi người đang rời phòng họp."
).replace(
    "敢|gan3|cảm|verb|dám; can đảm|to dare|面对未知的巨大困难与挑战，我们要勇敢敢于尝试。|Miànduì wèizhī de jùdà kùnnan yǔ tiǎozhàn, wǒmen yào yǒnggǎn gǎnyú chángshì.|Đối mặt với những khó khăn thử thách to lớn chưa biết, chúng ta phải dũng cảm dám thử sức.",
    "高级|gao1 ji2|cao cấp|adjective|cao cấp; trình độ cao|high-grade; advanced|这家商场专卖高级定制服装。|Zhè jiā shāngchǎng zhuānmài gāojí dìngzhì fúzhuāng.|Khu thương xá này chuyên bán đồ may đo cao cấp."
)

# Batch 3 (50 items): Lifestyle, work, cognition, adjectives
BATCH_003 = """
感觉|gan3 jue2|cảm giác|verb|cảm thấy; cảm giác|to feel; feeling|喝了一杯温开水，喉咙感觉舒服多了。|Hē le yì bēi wēn kāishuǐ, hóulóng gǎnjué shūfu duō le.|Uống một cốc nước ấm, cổ họng cảm thấy dễ chịu hơn nhiều rồi.
感情|gan3 qing2|cảm tình|noun|tình cảm; cảm xúc|feeling; emotion|他们夫妻结婚多年，感情一直非常深厚。|Tāmen fūqī jiéhūn duō nián, gǎnqíng yìzhí fēicháng shēnhòu.|Vợ chồng họ kết hôn nhiều năm, tình cảm luôn rất mặn nồng.
感谢|gan3 xie4|cảm tạ|verb|cảm tạ; cảm ơn chân thành|to thank; to be grateful|衷心感谢各位领导多年来给予的关心与指导。|Zhōngxīn gǎnxiè gèwèi lǐngdǎo duō nián lái jǐyǔ de guānxīn yǔ zhǐdǎo.|Chân thành cảm ơn các vị lãnh đạo trong nhiều năm qua đã quan tâm và chỉ đạo.
干|gan1|can|adjective|khô ráo; cạn nước|dry|晾在阳台上的衣服经过一天日晒已经干了。|Liàng zài yángtái shang de yīfu jīngguò yì tiān rìshài yǐjīng gān le.|Quần áo phơi ngoài ban công qua một ngày phơi nắng đã khô rồi.
干警|gan4 jing3|can cảnh|noun|cán bộ cảnh sát; công an|police cadre|人民干警夜以继日保护着市民的生命安全。|Rénmín gànjǐng yè-yǐ-jì-rì bǎohù zhe shìmín de shēngmìng ānquán.|Cán bộ chiến sĩ công an nhân dân ngày đêm bảo vệ an toàn tính mạng của người dân.
刚好|gang1 hao3|cương hảo|adverb|vừa hay; vừa đúng lúc|just; by chance|我走到地铁进站口，列车刚好进站。|Wǒ zǒu dào dìtiě jìnzhànkǒu, lièchē gānghǎo jìnzhàn.|Tôi vừa đi đến cửa vào ga tàu điện ngầm, đoàn tàu vừa đúng lúc vào ga.
钢铁|gang1 tie3|cương thiết|noun|gang thép; sắt thép|steel|现代城市摩天大楼建设需要大量坚硬钢铁。|Xiàndài chéngshì mótiān-dàlóu jiànshè xūyào dàliàng jiānyìng gāngtiě.|Việc xây dựng các tòa nhà chọc trời của thành phố hiện đại cần một lượng lớn sắt thép vững chắc.
高度|gao1 du4|cao độ|noun|chiều cao; độ cao|height; altitude|飞机航行巡航高度保持在一万米高空。|Fēijī hángxíng xúnháng gāodù bǎochí zài yì wàn mǐ gāokōng.|Máy bay bay đường dài duy trì ở độ cao một vạn mét trên bầu trời.
告别|gao4 bie2|cáo biệt|verb|từ biệt; cáo biệt|to bid farewell; to say goodbye|大学毕业典礼上，同学们依依不舍地告别。|Dàxué bìyè diǎnlǐ shang, tóngxuémen yīyī-bùshě de gàobié.|Trong lễ tốt nghiệp đại học, các bạn học bịn rịn không nỡ nói lời từ biệt.
格外|ge2 wai4|cách ngoại|adverb|đặc biệt; hết sức|exceptionally; especially|雨后初晴的空气显得格外清新宜人。|Yǔhòu chū qíng de kōngqì xiǎnde géwài qīngxīn yírén.|Không khí sau cơn mưa trời vừa hửng nắng trông đặc biệt trong lành dễ chịu.
各|ge4|các|pronoun|các; mỗi (riêng rẽ)|each; every|请各位代表在各自指定座位上有序就座。|Qǐng gèwèi dàibiǎo zài gèzì zhǐdìng zuòwèi shang yǒuxù jiùzuò.|Xin mời các vị đại biểu ngồi vào vị trí đã được chỉ định của mình một cách trật tự.
个子|ge4 zi5|cá tử|noun|vóc dáng; chiều cao người|height; stature|弟弟这两年长得飞快，个子已经超过了哥哥。|Dìdi zhè liǎng nián zhǎng de fēikuài, gèzi yǐjīng chāoguò le gēge.|Em trai hai năm nay cao lên rất nhanh, vóc dáng đã vượt qua cả anh trai.
给力|gei3 li4|cấp lực|adjective|tuyệt vời; mạnh mẽ; hết mình|awesome; cool; giving power|这次团队齐心协力表现得实在太给力了。|Zhè cì tuánduì qíxīn-xiélì biǎoxiàn de shízài tài gěilì le.|Lần này cả đội ngũ đồng lòng hợp lực thể hiện thực sự quá xuất sắc tuyệt vời.
根|gen1|căn|classifier|cây; chiếc; sợi (vật thon dài)|classifier for slender objects|他在纸上用铅笔画了一根笔直的长线。|Tā zài zhǐ shang yòng qiānbǐ huà le yì gēn bǐzhí de cháng xiàn.|Anh ấy dùng bút chì vẽ một đường thẳng tắp trên mặt giấy.
根本|gen1 ben3|căn bản|adverb|căn bản; hoàn toàn (phủ định)|at all; fundamental|这道奥数难题我从头到尾根本看不懂。|Zhè dào àoshù nántí wǒ cóngtóu-dàowěi gēnběn kàn bù dǒng.|Bài toán Olympic hóc búa này từ đầu đến cuối tôi căn bản nhìn không hiểu.
更加|geng4 jia1|cánh gia|adverb|càng thêm; càng|even more; furthermore|经过老师耐心辅导，他的学习信心更加足了。|Jīngguò lǎoshī nàixīn fǔdǎo, tā de xuéxí xìnxīn gèngjiā zú le.|Qua sự phụ đạo kiên trì của thầy giáo, lòng tự tin học tập của anh ấy càng thêm vững vàng.
公布|gong1 bu4|công bố|verb|công bố; ban bố|to announce; to publish|考试委员会今天正式向全校公布了录取结果。|Kǎoshì wěiyuánhuì jīntiān zhèngshì xiàng quánxiào gōngbù le lùqǔ jiéguǒ.|Hội đồng thi hôm nay đã chính thức công bố kết quả trúng tuyển ra toàn trường.
公平|gong1 ping2|công bình|adjective|công bằng; bình đẳng|fair; just|比赛裁判必须始终秉持公平公正的执裁原则。|Bǐsài cáipàn bìxū shǐzhōng bǐngchí gōngpíng gōngzhèng de zhícái yuánzé.|Trọng tài trận đấu bắt buộc phải luôn giữ vững nguyên tắc điều hành công bằng chính trực.
公里|gong1 li3|công lý|classifier|ki-lô-mét; cây số|kilometer|马拉松比赛的全程长达四十二公里多。|Mǎlāsōng bǐsài de quánchéng cháng dá sìshí'èr gōnglǐ duō.|Toàn bộ chặng đua ma-ra-tông dài hơn bốn mươi hai cây số.
功夫|gong1 fu5|công phu|noun|công phu; võ thuật; thời gian|kung fu; skill; effort|中国传统少林功夫名扬世界广受赞誉。|Zhōngguó chuántǒng shàolín gōngfu míngyáng shìjiè guǎng shòu zànyù.|Võ thuật Thiếu Lâm truyền thống Trung Hoa vang danh thế giới được khen ngợi rộng rãi.
工资|gong1 zi1|công tư|noun|tiền lương; thù lao|salary; wages|公司每个月十号准时向员工银行卡发放工资。|Gōngsī měi ge yuè shí hào zhǔnshí xiàng yuángōng yínhángkǎ fāfàng gōngzī.|Công ty ngày mười hàng tháng phát lương đúng hạn vào thẻ ngân hàng của nhân viên.
共同|gong4 tong2|cộng đồng|adjective|chung; cùng nhau|common; joint|保护地球生态环境是全人类共同肩负的责任。|Bǎohù dìqiú shēngtài huánjìng shì quán rénlèi gòngtóng jiānfù de zérèn.|Bảo vệ môi trường sinh thái địa cầu là trách nhiệm chung gánh vác của toàn nhân loại.
购物|gou4 wu4|cấu vật|verb|mua sắm; mua hàng|to shop; shopping|周末市中心大型商业广场吸引很多市民购物。|Zhōumò shìzhōngxīn dàxíng shāngyè guǎngchǎng xīyǐn hěn duō shìmín gòuwù.|Cuối tuần trung tâm thương mại lớn ở trung tâm thành phố thu hút đông đảo người dân mua sắm.
够|gou4|cấu|adverb|đủ; đạt mức|enough; sufficient|桌上准备了充足的水果点心，大家尽情吃够。|Zhuō shang zhǔnbèi le chōngzú de shuǐguǒ diǎnxin, dàjiā jìnqíng chī gòu.|Trên bàn đã chuẩn bị đầy đủ hoa quả điểm tâm, mọi người cứ thỏa thích ăn cho đủ.
估计|gu1 ji4|cô kế|verb|ước tính; ước lượng|to estimate; to reckon|我估计明天早晨八点左右列车能准时到达。|Wǒ gūjì míngtiān zǎochen bā diǎn zuǒyòu lièchē néng zhǔnshí dàodá.|Tôi ước tính khoảng tám giờ sáng mai đoàn tàu có thể đến đúng giờ.
鼓励|gu3 li4|cổ lệ|verb|khích lệ; động viên|to encourage; encouragement|老师常常鼓励基础薄弱的学生树立自信。|Lǎoshī chángcháng gǔlì jīchǔ bóruò de xuésheng shùlì zìxìn.|Thầy giáo thường xuyên khích lệ những học sinh còn yếu nền tảng tạo dựng sự tự tin.
故意|gu4 yi4|cố ý|adverb|cố ý; cố tình|intentionally; on purpose|对不起，刚才在走廊碰掉你的书绝不是故意的。|Duìbuqǐ, gāngcái zài zǒuláng pèngdiào nǐ de shū jué bú shì gùyì de.|Xin lỗi, vừa rồi va rơi sách của bạn ngoài hành lang hoàn toàn không phải cố ý đâu.
顾客|gu4 ke4|cố khách|noun|khách hàng; người mua|customer; client|优质周到的售后服务赢得了广大顾客的一致好评。|Yōuzhì zhōudào de shòuhòu fúwù yíngdé le guǎngdà gùkè de yízhì hǎopíng.|Dịch vụ hậu mãi chu đáo chất lượng đã chiếm được đánh giá tốt đồng lòng của đông đảo khách hàng.
挂号|gua4 hao4|quải hào|verb|lấy số; đăng ký khám bệnh|to register (at a hospital)|生病去大医院看病首先要去窗口挂号排队。|Shēngbìng qù dà yīyuàn kànbìng shǒuxiān yào qù chuāngkǒu guàhào páiduì.|Bị ốm đến bệnh viện lớn khám bệnh trước tiên phải đến quầy lấy số xếp hàng.
关键|guan1 jian4|quan kiện|noun|then chốt; mấu chốt|key; crucial point|认真细致是取得科学实验成功的关键所在。|Rènzhēn xìzhì shì qǔdé kēxué shíyàn chénggōng de guānjiàn suǒzài.|Cẩn thận tỉ mỉ chính là mấu chốt then chốt để đạt được thành công của thí nghiệm khoa học.
观众|guan1 zhong4|quan chúng|noun|khán giả; người xem|audience; spectator|全场观众被台上演员精湛绝伦的演技折服。|Quánchǎng guānzhòng bèi tái shang yǎnyuán jīngzhàn-juélún de yǎnjì zhéfú.|Toàn thể khán giả trong khán phòng bị chinh phục bởi diễn xuất tinh xảo tuyệt luân của diễn viên trên sân khấu.
管理|guan3 li3|quản lý|verb|quản lý; trông coi|to manage; management|这位新厂长善于科学高效管理现代企业。|Zhè wèi xīn chǎngzhǎng shànyú kēxué gāoxiào guǎnlǐ xiàndài qǐyè.|Vị giám đốc nhà máy mới này rất giỏi quản lý doanh nghiệp hiện đại một cách khoa học hiệu quả.
光|guang1|quang|adjective|sạch trơn; hết sạch; quang|light; empty; only|大家把桌上的饭菜吃得干干净净精光。|Dàjiā bǎ zhuō shang de fàncài chī de gāngān-jìngjìng jīngguāng.|Mọi người đã ăn sạch bóng cơm canh trên bàn ăn.
广播|guang3 bo1|quảng bá|noun|phát thanh; đài truyền thanh|broadcast; radio|早晨六点校园广播准时播放优美的晨曲。|Zǎochen liù diǎn xiàoyuán guǎngbō zhǔnshí bōfàng yōuměi de chénqǔ.|Sáu giờ sáng đài phát thanh của trường đúng giờ phát khúc nhạc ban mai êm dịu.
广告|guang3 gao4|quảng cáo|noun|quảng cáo|advertisement; commercial|电视黄金时间播放了一则公益环保广告。|Diànshì huángjīn shíjiān bōfàng le yì zé gōngyì huánbǎo guǎnggào.|Vào khung giờ vàng truyền hình đã phát một mẩu quảng cáo công ích bảo vệ môi trường.
逛|guang4|cuống|verb|dạo chơi; đi dạo phố|to stroll; to ramble|周末女孩们喜欢结伴去商业街逛街买衣服。|Zhōumò nǚháimen xǐhuan jiébàn qù shāngyèjiē guàngjiē mǎi yīfu.|Cuối tuần các cô gái thích rủ nhau đi dạo phố mua sắm quần áo ở phố thương mại.
规定|gui1 ding4|quy định|noun|quy định; điều lệ|regulation; rule|所有员工都必须严格遵守工厂的操作安全规定。|Suǒyǒu yuángōng dōu bìxū yángé zūnshǒu gōngchǎng de cāozuò ānquán guīdìng.|Tất cả nhân viên đều bắt buộc phải nghiêm chỉnh tuân thủ quy định an toàn thao tác của nhà xưởng.
国籍|guo2 ji2|quốc tịch|noun|quốc tịch|nationality|请在出入境登记表格上认真填写您的国籍。|Qǐng zài chūrùjìng dēngjì biǎogé shang rènzhēn tiánxiě nín de guójí.|Xin hãy điền cẩn thận quốc tịch của ngài vào mẫu đơn đăng ký xuất nhập cảnh.
国际|guo2 ji4|quốc tế|noun|quốc tế|international|北京明年将隆重举办一场大型国际体育盛会。|Běijīng míngnián jiāng lóngzhòng jǔbàn yì chǎng dàxíng guójì tǐyù shènghuì.|Bắc Kinh sang năm sẽ long trọng tổ chức một đại hội thể thao quốc tế quy mô lớn.
果汁|guo3 zhi1|quả trấp|noun|nước ép hoa quả|fruit juice|炎炎夏日喝一杯冰镇鲜榨西瓜果汁非常解暑。|Yányán xiàrì hē yì bēi bīngzhèn xiānzhà xīguā guǒzhī fēicháng jiěshǔ.|Mùa hè oi bức uống một cốc nước ép dưa hấu tươi ướp lạnh giải nhiệt rất tốt.
过程|guo4 cheng2|quá trình|noun|quá trình; tiến trình|process; course|科研人员在实验研发过程中克服了无数艰难险阻。|Kēyán rényuán zài shíyàn yánfā guòchéng zhōng kèfú le wúshù jiānnán-xiǎnzǔ.|Các cán bộ nghiên cứu khoa học trong quá trình thử nghiệm đã khắc phục vô vàn gian nan trắc trở.
海洋|hai3 yang2|hải dương|noun|đại dương; biển cả|ocean; sea|浩瀚无垠的海洋蕴藏着无穷无尽的生物资源。|Hàohàn-wúyín de hǎiyáng yùncáng zhe wúqióng-wújìn de shēngwù zīyuán.|Đại dương mênh mông vô tận ẩn chứa nguồn tài nguyên sinh vật vô cùng vô tận.
害羞|hai4 xiu1|hại tu|adjective|ngại ngùng; bẽn lẽn|shy; bashful|这个内向的小女孩在生人面前显得有些害羞。|Zhège nèixiàng de xiǎo nǚhái zài shēngrén miànqián xiǎnde yǒuxiē hàixiū.|Cô bé hướng nội này trước mặt người lạ tỏ ra có phần bẽn lẽn ngại ngùng.
寒假|han2 jia4|hàn giả|noun|kỳ nghỉ đông|winter vacation|放寒假时许多北方大学生纷纷回南方老家过年。|Fàng hánjià shí xǔduō běifāng dàxuéshēng fēnfēn huí nánfāng lǎojiā guònián.|Lúc được nghỉ đông nhiều sinh viên đại học miền Bắc nô nức về quê miền Nam ăn Tết.
汗|han4|hãn|noun|mồ hôi|sweat; perspiration|打完一场激烈的篮球赛后他全身出了很多汗。|Dǎwán yì chǎng jīliè de lánqiúsài hòu tā quánshēn chū le hěn duō hàn.|Sau khi chơi xong một trận bóng rổ kịch liệt toàn thân anh ấy toát ra rất nhiều mồ hôi.
好处|hao3 chu5|hảo xứ|noun|lợi ích; điểm tốt|benefit; advantage|经常参与户外慢跑锻炼对身体健康大有好处。|Jīngcháng cānyù hùwài mànpǎo duànliàn duì shēntǐ jiànkāng dàyǒu hǎochu.|Thường xuyên tham gia chạy bộ chậm ngoài trời có lợi ích to lớn đối với sức khỏe.
好像|hao3 xiang4|hảo tượng|adverb|dường như; hình như|as if; seem like|天边乌云密布沉沉压下来，好像马上要下大暴雨。|Tiānbiān wūyún-mìbù chénchén yā xiàlai, hǎoxiàng mǎshàng yào xià dà bàoyǔ.|Ven trời mây đen vần vũ đè nặng xuống, hình như sắp đổ mưa rào lớn.
号码|hao4 ma3|hào mã|noun|con số; số hiệu; số điện thoại|number|请留下您的手机号码，方便工作人员随时联系。|Qǐng liúxià nín de shǒujī hàomǎ, fāngbiàn gōngzuò rényuán suíshí liánxì.|Xin hãy để lại số điện thoại của ngài, thuận tiện cho nhân viên liên hệ bất cứ lúc nào.
合格|he2 ge2|hợp cách|adjective|đạt tiêu chuẩn; hợp lệ|qualified; eligible|这批工厂新产品全部经过严格检验并被评定为合格。|Zhè pī gōngchǎng xīn chǎnpǐn quánbù jīngguò yángé jiǎnyàn bìng bèi píngdìng wéi hégé.|Lô sản phẩm mới này của nhà máy đều qua kiểm định nghiêm ngặt và được đánh giá đạt tiêu chuẩn.
合适|he2 shi4|hợp thích|adjective|thích hợp; vừa vặn|suitable; fit|这件典雅的深色西装穿在他身上格外得体合适。|Zhè jiàn diǎnyǎ de shēnsè xīzhuāng chuān zài tā shēn shang géwài détǐ héshì.|Bộ com-lê sẫm màu trang nhã này mặc trên người anh ấy trông đặc biệt vừa vặn lịch thiệp.
"""

# Let's check duplicates in Batch 003:
# 公里 (in L3 B5), 顾客 (in L3 B3), 观众 (in L3 B3), 果汁 (in L3 B3), 害羞 (in L3 B2).
# Let's replace these 5 duplicates:
# 盒子|he2 zi5 (in L3 B4) -> 合资|he2 zi1|hợp tư|noun|liên doanh|joint venture|这是一家中外合资高新技术企业。|Zhè shì yì jiā zhōngwài hézī gāoxīn jìshù qǐyè.|Đây là một doanh nghiệp kỹ thuật công nghệ cao liên doanh Trung - ngoại.
# 盒子 replacement -> 盒|he2|hạp|classifier|hộp (lượng từ)|box of|我买了一盒巧克力。|Wǒ mǎi le yì hé qiǎokèlì.|Tôi đã mua một hộp sô-cô-la.
# Replace 公里 with: 共同体|gong4 tong2 ti3|cộng đồng thể|noun|cộng đồng; khối liên kết|community|世界各国是一个命运休戚与共的共同体。|Shìjiè gèguó shì yí ge mìngyùn xiūqī-yǔgòng de gòngtóngtǐ.|Các quốc gia trên thế giới là một cộng đồng chung vận mệnh gắn bó keo sơn.
# Replace 顾客 with: 孤独|gu1 du2|cô độc|adjective|cô đơn; cô độc|lonely; solitary|老人在远方独自生活难免感到孤独。|Lǎorén zài yuǎnfāng dúzì shēnghuó nánmiǎn gǎndào gūdú.|Người già sống một mình nơi phương xa khó tránh khỏi cảm thấy cô đơn.
# Replace 观众 with: 姑姑|gu1 gu5|cô cô|noun|cô; bác gái (chị em của bố)|aunt (father's sister)|姑姑寄来了一箱家乡特产酥饼。|Gūgu jì lái le yì xiāng jiāxiāng tèchǎn sūbǐng.|Cô gửi đến một thùng bánh giòn đặc sản quê hương.
# Replace 果汁 with: 股票|gu3 piao4|cổ phiếu|noun|cổ phiếu; chứng khoán|stock; share|投资股票市场需要保持理性严谨。|Tóuzī gǔpiào shìchǎng xūyào bǎochí lǐxìng yánjǐn.|Đầu tư vào thị trường chứng khoán cần phải duy trì tính lý trí cẩn trọng.
# Replace 害羞 with: 盒|he2|hạp|classifier|hộp (lượng từ)|box of|我买了一盒巧克力。|Wǒ mǎi le yì hé qiǎokèlì.|Tôi đã mua một hộp sô-cô-la.

BATCH_003_CLEAN = BATCH_003.replace(
    "公里|gong1 li3|công lý|classifier|ki-lô-mét; cây số|kilometer|马拉松比赛的全程长达四十二公里多。|Mǎlāsōng bǐsài de quánchéng cháng dá sìshí'èr gōnglǐ duō.|Toàn bộ chặng đua ma-ra-tông dài hơn bốn mươi hai cây số.",
    "共同体|gong4 tong2 ti3|cộng đồng thể|noun|cộng đồng; khối liên kết|community|世界各国是一个命运休戚与共的共同体。|Shìjiè gèguó shì yí ge mìngyùn xiūqī-yǔgòng de gòngtóngtǐ.|Các quốc gia trên thế giới là một cộng đồng chung vận mệnh gắn bó keo sơn."
).replace(
    "顾客|gu4 ke4|cố khách|noun|khách hàng; người mua|customer; client|优质周到的售后服务赢得了广大顾客的一致好评。|Yōuzhì zhōudào de shòuhòu fúwù yíngdé le guǎngdà gùkè de yízhì hǎopíng.|Dịch vụ hậu mãi chu đáo chất lượng đã chiếm được đánh giá tốt đồng lòng của đông đảo khách hàng.",
    "孤独|gu1 du2|cô độc|adjective|cô đơn; cô độc|lonely; solitary|老人在远方独自生活难免感到孤独。|Lǎorén zài yuǎnfāng dúzì shēnghuó nánmiǎn gǎndào gūdú.|Người già sống một mình nơi phương xa khó tránh khỏi cảm thấy cô đơn."
).replace(
    "观众|guan1 zhong4|quan chúng|noun|khán giả; người xem|audience; spectator|全场观众被台上演员精湛绝伦的演技折服。|Quánchǎng guānzhòng bèi tái shang yǎnyuán jīngzhàn-juélún de yǎnjì zhéfú.|Toàn thể khán giả trong khán phòng bị chinh phục bởi diễn xuất tinh xảo tuyệt luân của diễn viên trên sân khấu.",
    "姑姑|gu1 gu5|cô cô|noun|cô; bác gái (chị em của bố)|aunt (father's sister)|姑姑寄来了一箱家乡特产酥饼。|Gūgu jì lái le yì xiāng jiāxiāng tèchǎn sūbǐng.|Cô gửi đến một thùng bánh giòn đặc sản quê hương."
).replace(
    "果汁|guo3 zhi1|quả trấp|noun|nước ép hoa quả|fruit juice|炎炎夏日喝一杯冰镇鲜榨西瓜果汁非常解暑。|Yányán xiàrì hē yì bēi bīngzhèn xiānzhà xīguā guǒzhī fēicháng jiěshǔ.|Mùa hè oi bức uống một cốc nước ép dưa hấu tươi ướp lạnh giải nhiệt rất tốt.",
    "股票|gu3 piao4|cổ phiếu|noun|cổ phiếu; chứng khoán|stock; share|投资股票市场需要保持理性严谨。|Tóuzī gǔpiào shìchǎng xūyào bǎochí lǐxìng yánjǐn.|Đầu tư vào thị trường chứng khoán cần phải duy trì tính lý trí cẩn trọng."
).replace(
    "害羞|hai4 xiu1|hại tu|adjective|ngại ngùng; bẽn lẽn|shy; bashful|这个内向的小女孩在生人面前显得有些害羞。|Zhège nèixiàng de xiǎo nǚhái zài shēngrén miànqián xiǎnde yǒuxiē hàixiū.|Cô bé hướng nội này trước mặt người lạ tỏ ra có phần bẽn lẽn ngại ngùng.",
    "盒|he2|hạp|classifier|hộp (lượng từ)|box of|我买了一盒巧克力送给好朋友。|Wǒ mǎi le yì hé qiǎokèlì sòng gěi hǎo péngyou.|Tôi đã mua một hộp sô-cô-la tặng cho bạn tốt."
)

# Batch 4 (50 items): Daily actions, feelings, nature, society
BATCH_004 = """
盒子|he2 zi5|hạp tử|noun|cái hộp; hộp nhỏ|box; case|她把精致的首饰小心放回盒子里。|Tā bǎ jīngzhì de shǒushì xiǎoxīn fàng huí hézi lǐ.|Cô ấy cẩn thận cất lại món trang sức tinh xảo vào trong hộp.
猴子|hou2 zi5|hầu tử|noun|con khỉ; khỉ|monkey|几只调皮的小猴子在林间树枝上荡秋千。|Jǐ zhī tiáopí de xiǎo hóuzi zài línjiān shùzhī shang dàngqiūqiān.|Mấy chú khỉ con tinh nghịch đang đu dây trên cành cây giữa rừng.
厚|hou4|hậu|adjective|dày; đậm (tình cảm)|thick; deep|寒冬腊月出门请换上保暖的厚棉衣。|Hándōng-làyuè chūmén qǐng huàn shang bǎonuǎn de hòu miányī.|Những ngày đông lạnh giá ra ngoài xin hãy thay chiếc áo bông dày giữ ấm.
后悔|hou4 hui3|hậu hối|verb|hối hận; tiếc nuối|to regret; remorseful|如果不珍惜眼前的大好光阴，将来一定会后悔。|Rúguǒ bù zhēnxī yǎnqián de dàhǎo guāngyīn, jiānglái yídìng huì hòuhuǐ.|Nếu không trân trọng thời gian tươi đẹp trước mắt, tương lai nhất định sẽ hối hận.
后来|hou4 lai2|hậu lai|noun|về sau; sau này|later; afterwards|起初他们素不相识，后来渐渐成了无话不谈的挚友。|Qǐchū tāmen sùbùxiāngshí, hòulái jiànjiàn chéng le wúhuàbùtán de zhìyǒu.|Ban đầu họ không hề quen biết, về sau dần dần trở thành đôi bạn tri kỷ không chuyện gì không nói.
忽然|hu1 ran2|hốt nhiên|adverb|bỗng nhiên; đột nhiên|suddenly; all of a sudden|天空中电闪雷鸣，忽然间倾盆大雨倾泻而下。|Tiānkōng zhōng diànshǎn-léimíng, hūrán jiān qīngpén-dàyǔ qīngxiè ér xià.|Trên bầu trời chớp giật sấm rền, bỗng nhiên một cơn mưa rào trút nước như trút.
护士|hu4 shi5|hộ sĩ|noun|y tá|nurse|值班护士通宵达旦悉心照料病房里的重症患者。|Zhíbān hùshi tōngxiāo-dádàn xīxīn zhàoliào bìngfáng lǐ de zhòngzhèng huànzhě.|Cô y tá trực ca suốt đêm tận tình chăm sóc bệnh nhân nặng trong phòng bệnh.
互相|hu4 xiang1|hỗ tương|adverb|lẫn nhau; hỗ trợ|mutually; each other|真挚的友谊建立在彼此真诚理解与互相支持的基础之上。|Zhēnzhì de yǒuyì jiànlì zài bǐcǐ zhēnchéng lǐjiě yǔ hùxiāng zhīchí de jīchǔ zhī shàng.|Tình bạn chân chính được xây dựng trên nền tảng thấu hiểu chân thành và hỗ trợ lẫn nhau.
怀疑|huai2 yi2|hoài nghi|verb|hoài nghi; ngờ vực|to doubt; to suspect|警方经过严密侦查，初步怀疑案件有预谋作案的可能。|Jǐngfāng jīngguò yánmì zhēnchá, chūbù huáiyí ànjiàn yǒu yùmóu zuò'àn de kěnéng.|Cảnh sát qua điều tra kỹ càng, bước đầu hoài nghi vụ án có khả năng được lên kế hoạch từ trước.
回忆|hui2 yi4|hồi ức|verb|hồi tưởng; ký ức|to recall; memory|漫步在故乡的老街上，童年往事涌上心头令人无限回忆。|Mànbù zài gùxiāng de lǎojiē shang, tóngnián wǎngshì yǒngshàng xīntóu lìng rén wúxiàn huíyì.|Dạo bước trên con phố cổ quê hương, chuyện xưa thời thơ ấu ùa về khiến lòng người khôn nguôi hồi tưởng.
活动|huo2 dong4|hoạt động|noun|hoạt động; sự kiện|activity; event|学生会这周将隆重组织一场校园环保植树公益活动。|Xuéshēnghuì zhè zhōu jiāng lóngzhòng zǔzhī yì chǎng xiàoyuán huánbǎo zhíshù gōngyì huódòng.|Hội sinh viên tuần này sẽ long trọng tổ chức một hoạt động công ích trồng cây xanh bảo vệ môi trường trường học.
活泼|huo2 po5|hoạt bát|adjective|hoạt bát; hồn nhiên|lively; vivacious|那群天真烂漫的小学生在操场上欢快活泼地奔跑嬉戏。|Nà qún tiānzhēn-lànmàn de xiǎoxuéshēng zài cāochǎng shang huānkuài huópo de bēnpǎo xīxì.|Đám học sinh tiểu học ngây thơ hồn nhiên đang tung tăng hoạt bát chạy nhảy nô đùa trên sân trường.
火|huo3|hỏa|noun|lửa; cơn giận|fire; anger|冬天的壁炉里燃烧着温暖明亮的红火。|Dōngtiān de bìlú lǐ ránshāo zhe wēnnuǎn míngliàng de hónghuǒ.|Trong lò sưởi mùa đông đang bập bùng ngọn lửa đỏ ấm áp sáng ngời.
基础|ji1 chu3|cơ sở|noun|nền tảng; cơ sở|foundation; base|学好任何一门外语都必须下苦功夫打牢语音语法基础。|Xuéhǎo rèn hé yì mén wàiyǔ dōu bìxū xià kǔ gōngfu dǎláo yǔyīn yǔfǎ jīchǔ.|Học tốt bất kỳ môn ngoại ngữ nào đều phải bỏ công sức xây đắp nền tảng ngữ âm ngữ pháp vững chắc.
激动|ji1 dong4|kích động|adjective|xúc động; kích động|excited; stirred|当听到祖国队夺得冠军喜讯时，所有球迷都激动地跳了起来。|Dāng tīngdào zǔguóduì duóde guànjūn xǐxùn shí, suǒyǒu qiúmí dōu jīdòng de tiào le qǐlai.|Khi nghe tin vui đội nhà đoạt chức vô địch, tất cả người hâm mộ đều xúc động nhảy cẫng lên.
积极|ji1 ji2|tích cực|adjective|tích cực; chủ động|positive; active|青年一代应该以积极阳光的心态面对生活中的种种艰难挫折。|Qīngnián yídài yīnggāi yǐ jījí yángguāng de xīntài miànduì shēnghuó zhōng de zhǒngzhǒng jiānnán-cuòzhé.|Thế hệ thanh niên nên dùng tâm thế tích cực rạng rỡ để đối diện với muôn vàn gian nan trắc trở trong cuộc sống.
积累|ji1 lei3|tích lũy|verb|tích lũy; gom góp|to accumulate; accumulation|阅读优秀文学作品是积累优美词汇和写作素材的最佳途径。|Yuèdú yōuxiù wénxué zuòpǐn shì jīlěi yōuměi cíhuì hé xiězuò sùcái de zuìjiā tújìng.|Đọc tác phẩm văn học xuất sắc là con đường tốt nhất để tích lũy vốn từ vựng trau chuốt và chất liệu viết văn.
及时|ji2 shi2|kịp thời|adverb|kịp thời; đúng lúc|timely; in time|多亏医生及时展开抢救，病人才顺利脱离了生命危险。|Duōkuī yīshēng jíshí zhǎnkāi qiǎngjiù, bìngrén cái shùnlì tuōlí le shēngmìng wēixiǎn.|May nhờ bác sĩ kịp thời cấp cứu, bệnh nhân mới thuận lợi thoát khỏi nguy hiểm tính mạng.
即使|ji2 shi3|tức sử|conjunction|cho dù; dẫu rằng|even if; even though|即使通往成功的道路布满荆棘坎坷，我也绝不会轻易放弃梦想。|Jíshǐ tōngwǎng chénggōng de dàolù bùmǎn jīngjí-kǎnkě, wǒ yě jué bú huì qīngyì fàngqì mèngxiǎng.|Cho dù con đường đi đến thành công đầy rẫy chông gai trắc trở, tôi cũng tuyệt đối không dễ dàng từ bỏ ước mơ.
寄信|ji4 xin4|ký tín|verb|gửi thư|to send a letter|走过街角邮局时我顺便帮室友把两封家信寄信投递出去。|Zǒuguò jiējiǎo yóujú shí wǒ shùnbiàn bāng shìyǒu bǎ liǎng fēng jiāxìn jìxìn tóudì chūqù.|Lúc đi qua bưu điện góc phố tôi tiện tay giúp bạn cùng phòng gửi chuyển phát hai lá thư nhà.
计划|ji4 hua4|kế hoạch|noun|kế hoạch; dự định|plan; project|制定好科学合理的复习计划后，就要不折不扣认真执行落实。|Zhìdìng hǎo kēxué hélǐ de fùxí jìhuà hòu, jiù yào bù-zhé-bù-kòu rènzhēn zhíxíng luòshí.|Sau khi lập kế hoạch ôn tập khoa học hợp lý, cần phải nghiêm chỉnh thực hiện triệt để không thoái thác.
技术|ji4 shu4|kỹ thuật|noun|kỹ thuật; tay nghề|technology; skill|这家研发制造企业引进了世界领先的自动化生产高新技术。|Zhè jiā yánfā zhìzào qǐyè yǐnjìn le shìjiè lǐngxiān de zìdònghuà shēngchǎn gāoxīn jìshù.|Doanh nghiệp nghiên cứu và chế tạo này đã du nhập kỹ thuật công nghệ cao sản xuất tự động hàng đầu thế giới.
既然|ji4 ran2|ký nhiên|conjunction|nếu đã; một khi đã|since; as|既然大家都一致赞同这项提议，那我们就立刻着手组织实施。|Jìrán dàjiā dōu yízhì zàntóng zhè xiàng tíyì, nà wǒmen jiù lìkè zhuóshǒu zǔzhī shíshī.|Nếu đã mọi người đều nhất trí tán thành đề xuất này, vậy chúng ta lập tức bắt tay vào tổ chức thực thi.
继续|ji4 xu4|kế tục|verb|tiếp tục; duy trì|to continue; to go on|短暂的课间休息十分钟之后，大家回到教室继续专心听讲。|Duǎnzàn de kèjiān xiūxi shí fēnzhōng zhīhòu, dàjiā huídào jiàoxuéshì jìxù zhuānxīn tīngjiǎng.|Sau mười phút giải lao ngắn ngủi giữa giờ, mọi người trở lại lớp học tiếp tục chăm chú nghe giảng.
寄托|ji4 tuo1|ký thác|verb|gửi gắm; ký thác|to entrust; to place (hope)|这首优美的抒情诗寄托了游子对故乡亲人深深的思念与牵挂。|Zhè shǒu yōuměi de shūqíngshī jìtuō le yóuzǐ duì gùxiāng qīnrén shēnshēn de sīniàn yǔ qiānguà.|Bài thơ trữ tình tuyệt đẹp này gửi gắm nỗi nhớ thương sâu sắc và sự vương vấn của người lữ thứ đối với người thân nơi quê nhà.
记者|ji4 zhe3|ký giả|noun|nhà báo; phóng viên|journalist; reporter|新闻发布会现场坐满了来自世界各大知名媒体的随行记者。|Xīnwén fābùhuì xiànchǎng zuòmǎn le láizì shìjiè gè dà zhīmíng méitǐ de suíxíng jìzhě.|Hiện trường buổi họp báo tin tức ngồi kín các phóng viên tháp tùng đến từ các cơ quan truyền thông danh tiếng thế giới.
加油站|jia1 you2 zhan4|gia du trạm|noun|trạm xăng; cây xăng|gas station; petrol station|汽车在高速公路上长途行驶前请务必在加油站把汽油加满。|Qìchē zài gāosù gōnglù shang chángtú xíngshǐ qián qǐng wùbì zài jiāyóuzhàn bǎ qìyóu jiāmǎn.|Trước khi xe chạy đường dài trên đường cao tốc xin nhất thiết hãy đổ đầy xăng tại cây xăng.
家具|jia1 ju4|gia cụ|noun|đồ nội thất; đồ gỗ|furniture|新搬进公寓后他们特地购置了一套现代北欧风格的简约家具。|Xīn bānjìn gōngyù hòu tāmen tēdì gòuzhì le yí tào xiàndài běi'ōu fēnggé de jiǎnyuē jiājù.|Sau khi mới chuyển vào căn hộ họ đã đặc biệt mua sắm một bộ đồ nội thất tối giản mang phong cách Bắc Âu hiện đại.
假|jia3|giả|adjective|giả mạo; giả tạo|fake; false|出门在外防范网络电信诈骗，千万不要轻信来历不明的假消息。|Chūmén zàiwài fángfàn wǎngluò diànxìn zhàpiàn, qiānwàn bú yào qīngxìn láilì-bùmíng de jiǎ xiāoxi.|Ra ngoài cần đề phòng lừa đảo viễn thông mạng, tuyệt đối không được nhẹ dạ tin vào tin giả không rõ nguồn gốc.
价格|jia4 ge2|giá cách|noun|giá cả; giá tiền|price; cost|这家社区生鲜超市的有机蔬菜水果物美价廉，价格非常亲民。|Zhè jiā shèqū shēngxiān chāoshì de yǒujī shūcài shuǐguǒ wùměi-jiàlián, jiàgé fēicháng qīnmín.|Rau quả hữu cơ của siêu thị thực phẩm tươi sống khu dân cư này phẩm chất tốt giá hời, giá cả vô cùng bình dân.
坚持|jian1 chi2|kiên trì|verb|kiên trì; bền bỉ|to persist; to persevere|无论刮风下雨他都天天坚持早起晨跑，锻炼出了强健体魄。|Wúlùn guāfēng-xiàyǔ tā dōu tiāntiān jiānchí zǎoqǐ chénpǎo, duànliàn chū le qiángjiàn tǐpò.|Bất luận mưa gió ngày nào anh ấy cũng kiên trì dậy sớm chạy bộ buổi sáng, rèn luyện được một thể phách cường tráng.
减肥|jian3 fei2|giảm phì|verb|giảm béo; giảm cân|to lose weight|科学合理的减肥需要均衡控制饮食并配合持之以恒的有氧运动。|Kēxué hélǐ de jiǎnféi xūyào jìnhéng kòngzhì yǐnshí bìng pèihé chízhīyǐhéng de yǒuyǎng yùndòng.|Giảm cân khoa học hợp lý đòi hỏi phải kiểm soát chế độ ăn uống cân bằng và phối hợp với các bài tập thể dục hiếu khí kiên trì bền bỉ.
减少|jian3 shao3|giảm thiểu|verb|giảm bớt; giảm thiểu|to reduce; to decrease|倡导绿色低碳出行有助于有效减少城市汽车尾气碳排放污染。|Chàngdǎo lǜsè dītàn chūxíng yǒuzhùyú yǒuxiào jiǎnshǎo chéngshì qìchē wěiqì tànpáifàng wūrǎn.|Cổ vũ việc đi lại xanh ít carbon góp phần giảm thiểu hiệu quả lượng khí thải carbon từ ống xả ô tô thành phố.
建议|jian4 yi4|kiến nghị|verb|góp ý; kiến nghị|to suggest; proposal|老师建议基础薄弱的同学平时课下多花时间反复精读教材。|Lǎoshī jiànyì jīchǔ bóruò de tóngxué píngshí kèxià duō huā shíjiān fǎnfù jīngdú jiàocái.|Thầy giáo góp ý những bạn học sinh có nền tảng còn yếu thường ngày sau giờ học nên dành nhiều thời gian đọc kỹ giáo trình.
将来|jiang1 lai2|tương lai|noun|tương lai; mai sau|future|努力学好各门专业课本领，将来才能在社会上施展宏伟抱负。|Nǔlì xuéhǎo gè mén zhuānyèkè běnlǐng, jiānglái cáinéng zài shèhuì shang shīzhǎn hóngwěi bàofù.|Nỗ lực học tốt bản lĩnh các môn chuyên ngành, tương lai mới có thể thi thố hoài bão to lớn ngoài xã hội.
奖金|jiang3 jin1|tưởng kim|noun|tiền thưởng; thưởng|bonus; monetary award|经过一整年夜以继日的辛勤奋斗，团队年终拿到了丰厚奖金。|Jīngguò yì zhěng nián yè-yǐ-jì-rì de xīnqín fèndòu, tuánduì niánzhōng nádào le fēnghòu jiǎngjīn.|Qua một năm ròng rã phấn đấu cần cù ngày đêm, toàn đội ngũ cuối năm đã nhận được khoản tiền thưởng hậu hĩnh.
降低|jiang4 di1|hàng đê|verb|hạ thấp; giảm sút|to reduce; to drop|工厂采用先进节能环保工艺后，综合生产能耗大幅降低。|Gōngchǎng cǎiyòng xiānjìn jiénéng huánbǎo gōngyì hòu, zōnghé shēngchǎn nénghào dàfú jiàngdī.|Nhà xưởng sau khi áp dụng quy trình công nghệ bảo vệ môi trường tiết kiệm năng lượng tiên tiến, mức tiêu hao năng lượng sản xuất tổng hợp đã giảm mạnh.
降落|jiang4 luo4|hàng lạc|verb|hạ cánh; đáp xuống|to land; to touch down|飞机平稳降落在跑道上，机舱广播响起了热情的问候音乐。|Fēijī píngwěn jiàngluò zài pǎodào shang, jīcāng guǎngbō xiǎngqǐ le rèqíng de wènhòu yīnyuè.|Máy bay hạ cánh êm ả xuống đường băng, đài phát thanh khoang máy bay vang lên bản nhạc chào hỏi ấm áp.
交|jiao1|giao|verb|nộp; giao; kết bạn|to hand over; to make friends|下课铃声响了，请课代表把全班的汉语作业本收齐交上来。|Xiàkè língshēng xiǎng le, qǐng kèdàibiǎo bǎ quánbān de hànyǔ zuòyèběn shōuqí jiāo shànglai.|Chuông tan học reo rồi, xin cán sự lớp thu đủ vở bài tập tiếng Trung của cả lớp nộp lên.
交流|jiao1 liu2|giao lưu|verb|giao lưu; trao đổi|to communicate; to exchange|国际文化交流活动能够极大促进不同民族之间的相互理解。|Guójì wénhuà jiāoliú huódòng nénggòu jídà cùjìn bùtóng mínzú zhījiān de xiānghù lǐjiě.|Các hoạt động giao lưu văn hóa quốc tế có thể thúc đẩy to lớn sự thấu hiểu lẫn nhau giữa các dân tộc khác nhau.
交通|jiao1 tong1|giao thông|noun|giao thông; đi lại|traffic; transportation|这座新兴科技园周边地铁公交网络发达，日常公共交通非常便利。|Zhè zuò xīnxīng kējìyuán zhōubiān dìtiě gōngjiāo wǎngluò fādá, rìcháng gōnggòng jiāotōng fēicháng biànlì.|Xung quanh khu công viên khoa học kỹ thuật mới nổi này mạng lưới tàu điện ngầm xe buýt phát triển, giao thông công cộng hàng ngày rất thuận tiện.
郊区|jiao1 qu1|giao khu|noun|ngoại ô; vùng ven|suburbs; outskirts|周末不少市民喜欢自驾前往空气清新的近郊区踏青游玩。|Zhōumò bùshǎo shìmín xǐhuan zìjià qiánwǎng kōngqì xīnxīan de jìn jiāoqū tàqīng yóuwán.|Cuối tuần không ít người dân thích tự lái xe đến vùng ngoại ô gần có không khí trong lành để du xuân ngắm cảnh.
骄傲|jiao1 ao4|kiêu ngạo|adjective|tự hào; kiêu ngạo|proud; arrogant|他在国际顶级学科竞赛中荣获金奖，全校师生都为他感到无比骄傲。|Tā zài guójì dǐngjí xuékē jìngsài zhōng rónghuò jīnjiǎng, quánxiào shīshēng dōu wèi tā gǎndào wúbǐ jiāo'ào.|Anh ấy đoạt giải vàng trong kỳ thi học thuật đỉnh cao quốc tế, toàn thể thầy trò đều cảm thấy vô cùng tự hào về anh ấy.
饺子|jiao3 zi5|giảo tử|noun|bánh chẻo; sủi cảo|dumpling|每逢中国农历除夕佳节，家家户户围坐在一起热热闹闹包饺子。|Měiféng Zhōngguó nónglì chúxī jiājié, jiājiā-hùhù wéizuò zài yìqǐ rèrenaonao bāo jiǎozi.|Mỗi dịp Tết Giao thừa âm lịch Trung Quốc, các nhà đều quây quần bên nhau náo nhiệt gói bánh sủi cảo.
教授|jiao4 shou4|giáo thụ|noun|giáo sư (học hàm)|professor|这位享誉海内外的著名数学教授正在给研究生讲授高等代数。|Zhè wèi xiǎngyù hǎinèiwài de zhùmíng shùxué jiàoshòu zhèngzài gěi yánjiūshēng jiǎngshòu gāoděng dàishù.|Vị giáo sư toán học lừng danh trong và ngoài nước này đang giảng dạy môn đại số cao cấp cho nghiên cứu sinh.
教育|jiao4 yu4|giáo dục|noun|giáo dục|education|百年大计教育为本，国家始终把优先发展全民优质教育放在战略首位。|Bǎinián-dàjì jiàoyù wéi běn, guójiā shǐzhōng bǎ yōuxiān fāzhǎn quánmín yōuzhì jiàoyù fàng zài zhànlüè shǒuwèi.|Kế sách trăm năm giáo dục là gốc, quốc gia luôn đặt việc ưu tiên phát triển nền giáo dục chất lượng toàn dân lên vị trí chiến lược hàng đầu.
接受|jie1 shou4|tiếp thụ|verb|tiếp nhận; chấp nhận|to accept; to receive|虚心接受他人中肯的批评建议，才能在日常学习和工作中不断取得新进步。|Xūxīn jiēshòu tārén zhòngkěn de pīpíng jiànyì, cáinéng zài rìcháng xuéxí hé gōngzuò zhōng búduàn qǔdé xīn jìnbù.|Khiêm tốn tiếp nhận những lời phê bình góp ý xác đáng của người khác mới có thể không ngừng đạt được tiến bộ mới trong học tập và công việc hàng ngày.
接着|jie1 zhe5|tiếp trước|adverb|tiếp theo; liền sau đó|then; afterward|听完了前半部分详细报告，大家接着就具体执行细节展开深入探讨。|Tīngwán le qiánbàn bùfen xiángxì bàogào, dàjiā jiēzhe jiù jùtǐ zhíxíng xìjié zhǎnkāi shēnrù tàntǎo.|Nghe xong phần đầu bản báo cáo chi tiết, mọi người liền sau đó đi sâu thảo luận về các chi tiết thực thi cụ thể.
节|jie2|tiết|classifier|tiết (học); khúc; toa|classifier for classes or sections|今天上午九点开始我们要连着上两节难度颇高的现代汉语语法课。|Jīntiān shàngwǔ jiǔ diǎn kāishǐ wǒmen yào lián zhe shàng liǎng jié nándù pō gāo de xiàndài hànyǔ yǔfǎkè.|Chín giờ sáng nay bắt đầu chúng tôi phải học liền hai tiết ngữ pháp tiếng Hán hiện đại có độ khó khá cao.
节约|jie2 yue1|tiết ước|verb|tiết kiệm|to save; to economize|节约每一度电每一滴水是全社会倡导的良好公民道德习惯。|Jiéyuē měi yí dù diàn měi yì dī shuǐ shì quán shèhuì chàngdǎo de liánghǎo gōngmín dàodé xíguàn.|Tiết kiệm từng số điện từng giọt nước là thói quen đạo đức công dân tốt đẹp được toàn xã hội cổ vũ.
"""

# Let's check duplicates in Batch 004:
# 盒子 (in L3 B4), 互相 (in L3 B6), 活泼 (in L3 B2), 记者 (in L3 B3), 骄傲 (in L3 B2), 饺子 (in L2 B3).
# Replace these 6 duplicates:
# 结账|jie2 zhang4|kết trượng|verb|thanh toán; thanh toán hóa đơn|to pay the bill|吃完饭后请服务员过来结账。|Chīwán fàn hòu qǐng fúwùyuán guòlai jiézhàng.|Ăn cơm xong gọi phục vụ viên đến thanh toán hóa đơn.
# 结束 (in L3 B1). Instead: 结实|jie1 shi5|kết thực|adjective|vững chắc; chắc nịch|sturdy; solid|这张实木书桌做工十分结实。|Zhè zhāng shímù shūzhuō zuògōng shífēn jiēshi.|Chiếc bàn học bằng gỗ thịt này đóng vô cùng chắc chắn.
# 结合|jie2 he2|kết hợp|verb|kết hợp; gắn kết|to combine; to integrate|学习理论知识要紧密结合实际操作。|Xuéxí lǐlùn zhīshi yào jǐnmì jiéhé shíjì cāozuò.|Học tập tri thức lý luận cần gắn kết chặt chẽ với thao tác thực tế.
# 结论|jie2 lun4|kết luận|noun|kết luận|conclusion|经过严密论证，专家得出了科学结论。|Jīngguò yánmì lùnzhèng, zhuānjiā déchū le kēxué jiélùn.|Sau khi lập luận chặt chẽ, chuyên gia đã đưa ra kết luận khoa học.
# 解释|jie3 shi4|giải thích|verb|giải thích; thanh minh|to explain; explanation|请你向大家详细解释一下这个词的含义。|Qǐng nǐ xiàng dàjiā xiángxì jiěshì yíxià zhège cí de hányì.|Xin bạn hãy giải thích chi tiết cho mọi người ý nghĩa của từ này.
# 尽管|jin3 guan3|tẫn quản|conjunction|dù cho; dẫu rằng|although; even though|尽管外面雨雪纷飞，战士们依然坚守岗位。|Jǐnguǎn wàimiàn yǔxuě-fēnfēi, zhànshìmen yīrán jiānshǒu gǎngwèi.|Dù cho bên ngoài mưa tuyết mịt mù, các chiến sĩ vẫn kiên định bám trụ vị trí.

BATCH_004_CLEAN = BATCH_004.replace(
    "盒子|he2 zi5|hạp tử|noun|cái hộp; hộp nhỏ|box; case|她把精致的首饰小心放回盒子里。|Tā bǎ jīngzhì de shǒushì xiǎoxīn fàng huí hézi lǐ.|Cô ấy cẩn thận cất lại món trang sức tinh xảo vào trong hộp.",
    "结账|jie2 zhang4|kết trượng|verb|thanh toán; thanh toán hóa đơn|to pay the bill|吃完饭后请服务员过来结账。|Chīwán fàn hòu qǐng fúwùyuán guòlai jiézhàng.|Ăn cơm xong gọi phục vụ viên đến thanh toán hóa đơn."
).replace(
    "互相|hu4 xiang1|hỗ tương|adverb|lẫn nhau; hỗ trợ|mutually; each other|真挚的友谊建立在彼此真诚理解与互相支持的基础之上。|Zhēnzhì de yǒuyì jiànlì zài bǐcǐ zhēnchéng lǐjiě yǔ hùxiāng zhīchí de jīchǔ zhī shàng.|Tình bạn chân chính được xây dựng trên nền tảng thấu hiểu chân thành và hỗ trợ lẫn nhau.",
    "结实|jie1 shi5|kết thực|adjective|vững chắc; chắc nịch|sturdy; solid|这张实木书桌做工十分结实。|Zhè zhāng shímù shūzhuō zuògōng shífēn jiēshi.|Chiếc bàn học bằng gỗ thịt này đóng vô cùng chắc chắn."
).replace(
    "活泼|huo2 po5|hoạt bát|adjective|hoạt bát; hồn nhiên|lively; vivacious|那群天真烂漫的小学生在操场上欢快活泼地奔跑嬉戏。|Nà qún tiānzhēn-lànmàn de xiǎoxuéshēng zài cāochǎng shang huānkuài huópo de bēnpǎo xīxì.|Đám học sinh tiểu học ngây thơ hồn nhiên đang tung tăng hoạt bát chạy nhảy nô đùa trên sân trường.",
    "结合|jie2 he2|kết hợp|verb|kết hợp; gắn kết|to combine; to integrate|学习理论知识要紧密结合实际操作。|Xuéxí lǐlùn zhīshi yào jǐnmì jiéhé shíjì cāozuò.|Học tập tri thức lý luận cần gắn kết chặt chẽ với thao tác thực tế."
).replace(
    "记者|ji4 zhe3|ký giả|noun|nhà báo; phóng viên|journalist; reporter|新闻发布会现场坐满了来自世界各大知名媒体的随行记者。|Xīnwén fābùhuì xiànchǎng zuòmǎn le láizì shìjiè gè dà zhīmíng méitǐ de suíxíng jìzhě.|Hiện trường buổi họp báo tin tức ngồi kín các phóng viên tháp tùng đến từ các cơ quan truyền thông danh tiếng thế giới.",
    "结论|jie2 lun4|kết luận|noun|kết luận|conclusion|经过严密论证，专家得出了科学结论。|Jīngguò yánmì lùnzhèng, zhuānjiā déchū le kēxué jiélùn.|Sau khi lập luận chặt chẽ, chuyên gia đã đưa ra kết luận khoa học."
).replace(
    "骄傲|jiao1 ao4|kiêu ngạo|adjective|tự hào; kiêu ngạo|proud; arrogant|他在国际顶级学科竞赛中荣获金奖，全校师生都为他感到无比骄傲。|Tā zài guójì dǐngjí xuékē jìngsài zhōng rónghuò jīnjiǎng, quánxiào shīshēng dōu wèi tā gǎndào wúbǐ jiāo'ào.|Anh ấy đoạt giải vàng trong kỳ thi học thuật đỉnh cao quốc tế, toàn thể thầy trò đều cảm thấy vô cùng tự hào về anh ấy.",
    "解释|jie3 shi4|giải thích|verb|giải thích; thanh minh|to explain; explanation|请你向大家详细解释一下这个词的含义。|Qǐng nǐ xiàng dàjiā xiángxì jiěshì yíxià zhège cí de hányì.|Xin bạn hãy giải thích chi tiết cho mọi người ý nghĩa của từ này."
).replace(
    "饺子|jiao3 zi5|giảo tử|noun|bánh chẻo; sủi cảo|dumpling|每逢中国农历除夕佳节，家家户户围坐在一起热热闹闹包饺子。|Měiféng Zhōngguó nónglì chúxī jiājié, jiājiā-hùhù wéizuò zài yìqǐ rèrenaonao bāo jiǎozi.|Mỗi dịp Tết Giao thừa âm lịch Trung Quốc, các nhà đều quây quần bên nhau náo nhiệt gói bánh sủi cảo.",
    "尽管|jin3 guan3|tẫn quản|conjunction|dù cho; dẫu rằng|although; even though|尽管外面雨雪纷飞，战士们依然坚守岗位。|Jǐnguǎn wàimiàn yǔxuě-fēnfēi, zhànshìmen yīrán jiānshǒu gǎngwèi.|Dù cho bên ngoài mưa tuyết mịt mù, các chiến sĩ vẫn kiên định bám trụ vị trí."
)


def main():
    batches = [
        (1, BATCH_001_CLEAN),
        (2, BATCH_002_CLEAN),
        (3, BATCH_003_CLEAN),
        (4, BATCH_004_CLEAN),
    ]

    for num, raw_text in batches:
        lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
        print(f"Building and validating Level 4 Batch {num:03d} (lines: {len(lines)})...")
        save_batch(level=4, batch_num=num, raw_lines=lines)

    print("Level 4 Part 1 complete! Total 200 items across 4 batches.")


if __name__ == "__main__":
    main()

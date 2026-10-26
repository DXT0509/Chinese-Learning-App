import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

replacements = {
    "尽管": '紧迫|jin3 po4|khẩn bách|adjective|cấp bách; khẩn trương|urgent; pressing|当前救灾形势十分紧迫，需要立即调集物资。|Dāngqián jiùzāi xíngshì shífēn jǐnpò, xūyào lìjí diàojí wùzī.|Tình hình cứu trợ hiện tại vô cùng cấp bách, cần lập tức điều động vật tư.',
    "精彩": '敬礼|jing4 li3|kính lễ|verb|chào; chào kính cẩn|to salute; greet respectfully|少先队员们面向国旗庄严敬礼。|Shàoxiānduìyuánmen miànxiàng guóqí zhuāngyán jìnglǐ.|Các đội viên Đội thiếu niên tiền phong hướng về quốc kỳ trang nghiêm chào cẩn thận.',
    "经验": '经营|jing1 ying2|kinh doanh|verb|kinh doanh; quản lý|to manage; operate|这家百年老字号一直由家族用心经营。|Zhè jiā bǎinián lǎozìhao yìzhí yóu jiāzú yòngxīn jīngyíng.|Cửa hiệu lâu đời trăm năm này luôn được gia tộc dốc lòng kinh doanh.',
    "警察": '警告|jing3 gao4|cảnh cáo|verb|cảnh cáo; nhắc nhở|to warn; caution|气象台向沿海地区发布了暴风雨蓝色警告。|Qìxiàngtái xiàng yánhǎi dìqū fābù le bàofēngyǔ lánsè jǐnggào.|Đài khí tượng đã phát đi cảnh báo bão màu xanh lam tới các vùng ven biển.',
    "棵": '颗|ke1|khóa|classifier|hạt; hòn; viên; ngôi (sao)|classifier for small round things or stars|天空中闪烁着一颗耀眼的北极星。|Tiānkōng zhōng shǎnshuò zhe yì kē yàoyǎn de Běijíxīng.|Trên bầu trời lấp lánh một ngôi sao Bắc Cực sáng ngời chói mắt.',
    "空气": '空间|kong1 jian1|không gian|noun|không gian; chỗ trống|space; room|我们为新购入的书架预留了足够的摆放空间。|Wǒmen wèi xīn gòurù de shūjià yùliú le zúgòu de bǎifàng kōngjiān.|Chúng tôi đã chừa đủ không gian sắp đặt cho chiếc giá sách mới mua.',
    "苦": '苦恼|ku3 nao3|khổ não|adjective|phiền muộn; khổ sở|distressed; vexed|由于找不到合适的论文选题，他内心十分苦恼。|Yóuyú zhǎobudào héshì de lùnwén xuǎntí, tā nèixīn shífēn kǔnǎo.|Do không tìm được đề tài luận văn phù hợp, trong lòng anh ấy vô cùng phiền muộn.',
    "困": '枯燥|ku1 zao4|khô táo|adjective|khô khan; tẻ nhạt|dry; dull; boring|原本枯燥的理论知识被老师讲得生动有趣。|Yuánběn kūzào de lǐlùn zhīshi bèi lǎoshī jiǎng de shēngdòng-yǒuqù.|Kiến thức lý thuyết vốn khô khan đã được thầy giáo giảng giải sinh động thú vị.',
    "辣": '蜡烛|la4 zhu2|lạp chúc|noun|cây nến; nến|candle|生日聚会上大家点燃了插在蛋糕上的彩色蜡烛。|Shēngrì jùhuì shang dàjiā diǎnrán le chā zài dàngāo shang de cǎisè làzhú.|Trong bữa tiệc sinh nhật mọi người đã thắp sáng những cây nến nhiều màu cắm trên bánh kem.',

    "律师": '旅馆|lü3 guan3|lữ quán|noun|nhà trọ; khách sạn nhỏ|inn; small hotel|我们在古城中心预订了一家古色古香的青年旅馆。|Wǒmen zài gǔchéng zhōngxīn yùdìng le yì jiā gǔsè-gǔxiāng de qīngnián lǚguǎn.|Chúng tôi đã đặt một nhà trọ thanh niên mang phong cách cổ kính ở trung tâm phố cổ.',
    "农村": '农业|nong2 ye4|nông nghiệp|noun|nông nghiệp|agriculture|现代科学技术正在深刻改变传统农业生产方式。|Xiàndài kēxué jìshù zhèngzài shēnkè gǎibiàn chuántǒng nóngyè shēngchǎn fāngshì.|Khoa học kỹ thuật hiện đại đang làm thay đổi sâu sắc phương thức sản xuất nông nghiệp truyền thống.',
    "暖和": '暖气|nuan3 qi4|noãn khí|noun|hệ thống sưởi; hơi sưởi|heating; central heating|北方冬天的室内安装了暖气，感觉格外温暖舒适。|Běifāng dōngtiān de shìnèi ānzhuāng le nuǎnqì, gǎnjué géwài wēnnuǎn shūshì.|Mùa đông phương bắc trong phòng lắp hệ thống sưởi, cảm thấy đặc biệt ấm áp dễ chịu.',
    "偶尔": '偶然|ou3 ran2|ngẫu nhiên|adjective|ngẫu nhiên; tình cờ|accidental; incidental|他们两人在图书馆偶然相遇，从此成了知心好友。|Tāmen liǎng rén zài túshūguǎn ǒurán xiāngyù, cóngcǐ chéng le zhīxīn hǎoyǒu.|Hai người họ tình cờ gặp nhau ở thư viện, từ đó trở thành bạn thân tri kỷ.',
    "瓶子": '平常|ping2 chang2|bình thường|adjective|bình thường; giản dị|ordinary; usual|他是一个性格非常朴素平常的普通劳动者。|Tā shì yí ge xìnggé fēicháng pǔsù píngcháng de pǔtōng láodòngzhě.|Bác ấy là một người lao động bình dị mang tính cách vô cùng mộc mạc.',
    "气候": '气氛|qi4 fen1|khí phân|noun|bầu không khí; không khí|atmosphere; ambiance|除夕夜全家团圆的晚宴气氛极其喜庆热烈。|Chúxīyè quánjiā tuányuán de wǎnyàn qìfēn jíqí xǐqìng-rèliè.|Bầu không khí bữa tiệc đoàn viên cả nhà đêm giao thừa hết sức vui vẻ náo nhiệt.',

    "缺点": '缺陷|que1 xian4|khuyết hãm|noun|khuyết điểm; nhược điểm; thiếu sót|defect; flaw; shortcoming|产品在出厂检测中被发现存在细微的设计缺陷。|Chǎnpǐn zài chūchǎng jiǎncè zhōng bèi fāxiàn cúnzài xìwēi de shèjì quēxiàn.|Sản phẩm trong đợt kiểm tra xuất xưởng bị phát hiện có lỗi thiết kế nhỏ.',
    "热闹": '热心|re4 xin1|nhiệt tâm|adjective|nhiệt tình; tốt bụng|enthusiastic; warm-hearted|社区里有许多热心市民自愿参加环保宣传活动。|Shèqū lǐ yǒu xǔduō rèxīn shìmín zìyuàn cānjiā huánbǎo xuānchuán huódòng.|Trong khu dân cư có nhiều người dân nhiệt tình tình nguyện tham gia hoạt động tuyên truyền bảo vệ môi trường.',
    "散步": '散发|san4 fa1|tản phát|verb|tỏa ra; phát tán|to emit; give off|雨后花园里的各色花朵散发出淡淡的清香。|Yǔhòu huāyuán lǐ de gèsè huāduǒ sànfā chū dàndàn de qīngxiāng.|Những bông hoa đủ màu trong vườn sau cơn mưa tỏa ra hương thơm thoang thoảng.',
    "森林": '沙漠|sha1 mo4|sa mạc|noun|sa mạc|desert|绿化团队正在沙漠边缘大力种植防风固沙林。|Lǜhuà tuánduì zhèngzài shāmò biānyuán dàlì zhòngzhí fángfēng-gùshālín.|Đội ngũ phủ xanh đang nỗ lực trồng rừng chắn gió giữ cát ở rìa sa mạc.',
    "勺子": '舍不得|she3 bu5 de5|xả bất đắc|verb|không nỡ; quyến luyến|to hate to part with|大学毕业离校之际，同学们彼此依依舍不得分开。|Dàxué bìyè líxiào zhī jì, tóngxuémen bǐcǐ yīyī shěbude fēnkāi.|Khoảnh khắc tốt nghiệp đại học rời trường, các bạn học bịn rịn quyến luyến không nỡ chia xa.',
    "社会": '设施|she4 shi1|thiết thi|noun|cơ sở vật chất; tiện ích|facilities; installations|新居民小区配备了完善的文体与休闲健身设施。|Xīn jūmín xiǎoqū pèibèi le wánshàn de wéntǐ yǔ xiūxián jiànshēn shèshī.|Khu dân cư mới được trang bị đầy đủ cơ sở vật chất văn thể và rèn luyện giải trí.',
    "市场": '市区|shi4 qu1|thị khu|noun|nội thành; khu đô thị|downtown; urban district|早高峰期间通往市区的主干道经常发生交通拥堵。|Zǎogāofēng qījiān tōngwǎng shìqū de zhǔgàndào jīngcháng fāshēng jiāotōng yōngdǔ.|Trong giờ cao điểm buổi sáng tuyến đường chính dẫn vào nội thành thường xảy ra ùn tắc giao thông.',

    "顺利": '硕士|shuo4 shi4|thạc sĩ|noun|thạc sĩ|master degree|他经过两年的刻苦学习顺利获得了工程硕士学位。|Tā jīngguò liǎng nián de kèkǔ xuéxí shùnlì huòdé le gōngchéng shuòshì xuéwèi.|Sau hai năm học tập chăm chỉ anh ấy đã thuận lợi nhận bằng thạc sĩ kỹ thuật.',
    "酸": '随时|sui2 shi2|tùy thời|adverb|bất cứ lúc nào|at any time; whenever|如果使用过程中遇到任何问题，欢迎随时联系客服人员。|Rúguǒ shǐyòng guòchéng zhōng yùdào rènhé wèntí, huānyíng suíshí liánxì kèfù rényuán.|Nếu gặp bất kỳ vấn đề nào trong quá trình sử dụng, hoan nghênh bạn liên hệ nhân viên chăm sóc khách hàng bất cứ lúc nào.',
    "算": '所谓|suo3 wei4|sở vị|adjective|cái gọi là|so-called|不要盲目相信网络上所谓专家推荐的各种偏方。|Bú yào mángmù xiāngxìn wǎngluò shang suǒwèi zhuānjiā tuījiàn de gè zhǒng piānfāng.|Đừng tin tưởng mù quáng vào các phương thuốc dân gian của cái gọi là chuyên gia giới thiệu trên mạng.',
    "汤": '谈判|tan2 pan4|đàm phán|verb|đàm phán; thương lượng|to negotiate; negotiation|两国代表团就双边贸易合作协定举行了深入谈判。|Liǎng guó dàibiǎotuán jiù shuāngbiān màoyì hézuò xiédìng jǔxíng le shēnrù tánpàn.|Đoàn đại biểu hai nước đã tiến hành đàm phán sâu sắc về hiệp định hợp tác thương mại song phương.',
    "套": '特殊|te4 shu1|đặc thù|adjective|đặc biệt; đặc thù|special; particular|由于天气原因这一特殊情况，航班不得不临时改降邻近机场。|Yóuyú tiānqì yuányīn zhè yì tèshū qíngkuàng, hángbān bùdébù línshí gǎijiàng línjìn jīchǎng.|Do nguyên nhân thời tiết là tình huống đặc biệt này, chuyến bay buộc phải chuyển sang hạ cánh tạm thời ở sân bay lân cận.',
    "特点": '提纲|ti2 gang1|đề cương|noun|dàn ý; đề cương|outline; synopsis|动笔写作长篇报告之前应当先列出清晰的内容提纲。|Dòngbǐ xiězuò chángpiān bàogào zhīqián yīngdāng xiān liè chū qīngxī de nèiróng tígāng.|Trước khi đặt bút viết bản báo cáo dài cần liệt kê ra đề cương nội dung rõ ràng trước.',
    "危险": '危机|wei1 ji1|nguy cơ|noun|nguy cơ; khủng hoảng|crisis|企业在面临突发公关危机时需要迅速采取有效应对措施。|Qǐyè zài miànlín tūfā gōngguān wēijī shí xūyào xùnsù cǎiqǔ yǒuxiào yìngduì cuòshī.|Doanh nghiệp khi đối mặt khủng hoảng quan hệ công chúng bất ngờ cần nhanh chóng áp dụng biện pháp ứng phó hiệu quả.',
    "温度": '吻合|wen3 he2|vẫn hợp|verb|trùng khớp; ăn khớp|to match; coincide|实验室得出的最新测试数据与理论计算结果高度吻合。|Shíyànshì déchū de zuìxīn cèshì shùjù yǔ lǐlùn jìsuàn jiéguǒ gāodù wěnhé.|Dữ liệu kiểm tra mới nhất của phòng thí nghiệm hoàn toàn trùng khớp với kết quả tính toán lý thuyết.',
}

target_file = ROOT / "build_level_4_part2.py"
lines = target_file.read_text(encoding="utf-8").splitlines(keepends=True)

new_lines = []
replaced = 0
for line in lines:
    matched = False
    for k, v in replacements.items():
        if line.startswith(f"{k}|"):
            new_lines.append(v + "\n")
            replaced += 1
            matched = True
            break
    if not matched:
        new_lines.append(line)

target_file.write_text("".join(new_lines), encoding="utf-8")
print(f"Replaced {replaced} lines successfully.")

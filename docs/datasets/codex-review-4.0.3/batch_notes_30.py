"""Actual L5-B010 linguistic review; corrections re-read before validation."""
from record_batch import record

record("L5-B010", """
降雨量 jiàngyǔliàng rainfall; six-hour precipitation example aligned.
降水 jiàngshuǐ precipitation including snow; forecast accurate.
交代 jiāodài explain/entrust; repair redundant physical 交代交接 with instructions to successor.
焦点 jiāodiǎn focus; AI ethics summit discussion aligned.
焦急 jiāojí anxious; waiting outside operating room natural.
交接 jiāojiē hand over; nominal 防务交接 also requires noun POS.
娇气 jiāoqi delicate/pampered; toughened graduates example coherent, full-toned example variant valid.
狡猾 jiǎohuá cunning; fraudster aliases and evasion aligned.
缴费 jiǎofèi pay fees; mobile utility payments natural.
教学楼 jiàoxuélóu teaching building; school construction example correct.
阶层 jiēcéng social stratum; income distribution example aligned.
皆大欢喜 jiēdàhuānxǐ everyone satisfied; neighbor mediation natural.
接连 jiēlián in succession; research awards example correct.
接收 jiēshōu receive; evacuation reception example aligned.
揭露 jiēlù expose; chemical food adulteration investigation correct.
结晶 jiéjīng crystallization/fruit; bridge as collective wisdom correct metaphor.
竭尽全力 jiéjìnquánlì do utmost; flood rescue example aligned.
截止 jiézhǐ close at deadline; remove prepositional by/as-of meaning belonging to 截至.
截然不同 jiéránbùtóng utterly different; philosophical positions contrasted correctly.
解脱 jiětuō release; nominal relief after 获得 requires noun POS too.
解析 jiěxī analyze; examination problem analysis aligned, 压轴 pronunciation variant retained.
借口 jièkǒu pretext; correct 干部 gànbù transcription.
戒备 jièbèi guard against/alertness; remove 高峰峰会 duplication, include nominal state.
届时 jièshí at that time; exhibition opening and companies attending aligned.
津贴 jīntiē allowance; remote-region specialist subsidy aligned.
紧密 jǐnmì close; regional cooperation example accurate.
紧急 jǐnjí urgent; flood emergency response aligned.
谨慎 jǐnshèn cautious; cross-border investment diligence natural.
尽力 jìnlì do best; example incorrect jīnlì corrected to fourth tone.
近视 jìnshì myopia; student vision example aligned.
进取 jìnqǔ enterprising; positive initiative and spirit correct.
进化 jìnhuà evolve/evolution; include noun and correct 进一步 transcription.
浸透 jìntòu soak through; remove redundant 湿透浸透 and overrestricted sweat gloss.
经久不衰 jīngjiǔbùshuāi enduring; classic popularity appropriate.
经贸 jīngmào economy/trade; economic exchange example aligned.
精密 jīngmì precision; instrument description correct.
精简 jīngjiǎn streamline; management reduction example coherent.
精确 jīngquè precise; correct 辨 biàn and Vietnamese inverse inference rendering, avoid absolute gloss.
精髓 jīngsuǐ essence; central cultural substance aligned.
警惕 jǐngtì vigilant; cảnh dịch conventional reading, usage aligned.
净利 jìnglì net profit; earnings growth example aligned.
境地 jìngdì predicament; bankruptcy situation natural.
救济 jiùjì provide relief/relief; include nominal 生活救济 use.
救助 jiùzhù rescue; remove duplicated 专业 and redundant wind phrase using clear rescue sentence.
就职 jiùzhí take office; inaugural address correct.
居高不下 jūgāobùxià remain high; energy prices example accurate.
拘束 jūshù constrained; youth camp relaxation appropriate.
局限 júxiàn limit; not restricted to book learning correct.
聚精会神 jùjīnghuìshén concentrate; correct 等待 děngdài versus source děngdào.
捐献 juānxiàn donate; teacher donating savings aligned. All stable keys and level retained.
""", [
 (3,"Remove redundant handover construction.",{"example":{"simplified":"老站长向接任者交代了观测工作的注意事项。","pinyin":"Lǎo zhànzhǎng xiàng jiērènzhě jiāodài le guāncè gōngzuò de zhùyì shìxiàng.","vietnamese":"Bác trạm trưởng già dặn dò người kế nhiệm những điều cần chú ý trong công việc quan sát."}}),
 (6,"Nominal handover use.",{"part_of_speech":"verb, noun"}),
 (18,"Distinguish 截止 from 截至.",{"vietnamese_meanings":["hết hạn","chấm dứt vào thời điểm quy định"],"english_meanings":["to end","to close (at a deadline)"]}),
 (20,"Nominal release use.",{"part_of_speech":"verb, noun"}),
 (22,"干部 gànbù.",{"example":{"pinyin":"Duìdài rìcháng zǔzhī jìlǜ yāoqiú yǔ gōngzuò zhízé, dǎngyuán gànbù bìxū yányúlìjǐ jìnzhí-jìnzé, jué bù néng xúnzhǎo rènhé kèguān jièkǒu tuīwěi tuōyán."}}),
 (23,"Remove duplicated peak and capture alertness noun.",{"part_of_speech":"verb, noun","example":{"simplified":"峰会期间，安保人员始终保持高度戒备。","pinyin":"Fēnghuì qījiān, ānbǎo rényuán shǐzhōng bǎochí gāodù jièbèi.","vietnamese":"Trong thời gian hội nghị thượng đỉnh, nhân viên an ninh luôn duy trì cảnh giác cao độ."}}),
 (29,"尽力 fourth tone.",{"example":{"pinyin":"Wúlùn miànduì duōme fùzá de kēyán gōngguān tiǎozhàn, quántǐ jìshù gǔgàn dōu juéxīn háowú-bǎoliú jìnlì-érwéi, shìbǎo guójiā zhòngdà hángtiān fāshè rènwu yuánmǎn chénggōng."}}),
 (32,"Evolution noun and 进 fourth tone.",{"part_of_speech":"verb, noun","example":{"pinyin":"Gǔshēngwù kǎogǔ xuézhě tōngguò duì shàng yì nián bǎocún wánhǎo de shǐzǔniǎo huàshí de yánjiū, jìnyíbù jiēshì le gǔdài kǒnglóng xiàng niǎolèi jìnhuà de guānjiàn guòdù xíngtài lìchéng."}}),
 (33,"Natural soaking construction and broader gloss.",{"vietnamese_meanings":["thấm đẫm","thấm qua toàn bộ"],"example":{"simplified":"工人的工作服被汗水浸透了。","pinyin":"Gōngrén de gōngzuòfú bèi hànshuǐ jìntòu le.","vietnamese":"Quần áo làm việc của công nhân bị mồ hôi thấm ướt đẫm."}}),
 (38,"辨 biàn; inverse inference Vietnamese; precision not necessarily absolute.",{"vietnamese_meanings":["chuẩn xác","chính xác"],"example":{"pinyin":"Gāofēnbiànlǜ qìxiàng yáogǎn léidá nénggòu jíqí jīngquè de shíshí fǎnyǎn bìng cèdìng tèdà qiáng duìliú bàoyǔ yúntuán de yídòng guǐjì yǔ jiàngshuǐ héxīn fēnbù.","vietnamese":"Radar khí tượng viễn thám có độ phân giải cao có thể suy ra từ dữ liệu đo và xác định theo thời gian thực, với độ chính xác cao, quỹ đạo di chuyển cùng phân bố vùng mưa chính của các đám mây gây mưa lớn đối lưu mạnh."}}),
 (43,"Relief nominal use.",{"part_of_speech":"verb, noun"}),
 (44,"Remove repeated 专业 and wind redundancy.",{"example":{"simplified":"海上搜救直升机大队顶着强风，成功救助了货轮上的十名被困船员。","pinyin":"Hǎishàng sōujiù zhíshēngjī dàduì dǐngzhe qiángfēng, chénggōng jiùzhù le huòlún shang de shí míng bèikùn chuányuán.","vietnamese":"Đội trực thăng tìm kiếm cứu nạn trên biển đã vượt gió mạnh, cứu thành công mười thủy thủ mắc kẹt trên tàu hàng."}}),
 (49,"等待 děngdài not 等到 děngdào.",{"example":{"pinyin":"Quántǐ kēyán jìshù gōngguān rényuán jùjīng-huìshén de níngshì zhe fāshè cèkòng zhǐhuī zhōngxīn de zhǔ xiǎnshì dà píngmù, bǐngxī-níngshén děngdài zhe yùnzài huǒjiàn shùnlì diǎnhuǒ shēngkōng de jīdòng-rénxīn lìshǐ shūnjiān."}}),
])

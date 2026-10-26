"""Actual L5-B023 specialist vocabulary review; two incorrect keys held."""
from record_batch import record, rows
r=rows("L5-B023")
def py(i,a,b):
 p=r[i-1].examples[0].pinyin
 assert a in p
 return {"example":{"pinyin":p.replace(a,b)}}
record("L5-B023", """
暗物质 ànwùzhì dark matter; 高精度 exact transcription corrected.
靶向药 bǎxiàngyào targeted drug; drug not therapy itself; replace universal response claim with precise research example.
半导体 bàndǎotǐ semiconductor; wide-bandgap materials context aligned.
超级计算机 chāojíjìsuànjī supercomputer; exascale 百亿亿 and simulations aligned.
超导材料 chāodǎocáiliào superconducting material; zero resistance/diamagnetism appropriate properties.
等离子体 děnglízǐtǐ plasma; 离 lí not lǐ in example.
电磁波 diàncíbō electromagnetic wave; 解调 jiětiáo not jiějiào.
分子生物学 fēnzǐshēngwùxué molecular biology; molecular structure/life research aligned.
基因工程 jīyīngōngchéng genetic engineering; crop breeding context aligned.
核聚变 héjùbiàn fusion; 竭 jié not jié? Source bùjié correct; retain.
红外光谱 hóngwàiguāngpǔ infrared spectrum; functional group bond vibrations aligned.
激光雷达 jīguāngléidá LiDAR; 高精度 not 高精密 in pinyin.
量子通信 liàngzǐtōngxìn quantum communication; remove physically guaranteed absolute implementation security claim.
纳米材料 nàmǐcáiliào nanomaterial; surface area/catalysis aligned.
脑机接口 nǎojījiēkǒu brain-computer interface; motor intention robotic control example coherent.
逆向工程 nìxiànggōngchéng reverse engineering; structure/algorithm analysis aligned.
人工心脏 réngōngxīnzàng artificial heart; circulatory support narrative aligned.
神经元 shénjīngyuán neuron; chemical synapse signaling appropriate.
深空探测 shēnkōngtàncè deep space exploration; 返回 fǎnhuí not huíhuán.
生物反应器 shēngwùfǎnyìngqì bioreactor; recombinant protein manufacture aligned.
石墨烯 shímòxī graphene; carbon single layer/honeycomb aligned.
太阳能电池 tàiyángnéngdiànchí solar cell; 钙 gài not gǎi.
碳纤维 tànxiānwéi carbon fiber; 模量 móliàng missing tone repaired; modulus not electrical module in Vietnamese.
外骨骼 wàigǔgé exoskeleton; duplicate robot in Vietnamese repaired.
微纳制造 wēinàzhìzào micro/nano manufacture; MEMS lithography/etching aligned.
无线充电 wúxiànchōngdiàn wireless charging; resonant coupling appropriate.
云计算 yúnjìsuàn cloud computing; dangling 依托 subject repaired.
载人航天 zàirénhángtiān crewed spaceflight; space laboratory narrative aligned.
质子治疗 requires zhìzǐzhìliáo; stable key zhi3 incorrect. Hold identity; replace false nanoscale targeted explosion claim with proton beam irradiation.
重力波 zhònglìbō gravitational wave attested Taiwan usage (Academia Sinica); clarify regional sense and replace malformed binary-black-hole/detector claim.
合成生物学 héchéngshēngwùxué synthetic biology; designed genetic circuits appropriate.
低温超导 dīwēnchāodǎo low-temperature superconductivity; liquid helium coils aligned.
单克隆抗体 dānkèlóngkàngtǐ monoclonal antibody; malignant autoimmune/express-after-purify wording repaired.
粒子物理 lìzǐwùlǐ particle physics; lạp tử not lập tử.
热力学 rèlìxué thermodynamics; isolated-system entropy example aligned.
拓扑绝缘体 tuòpūjuéyuántǐ topological insulator; clarify bulk insulation/surface conduction rather than universally dissipationless current.
微流控 wēiliúkòng microfluidics; 指甲盖 zhǐjiǎgài and 皮升 píshēng corrected.
光伏发电 guāngfúfādiàn photovoltaic generation; transmission of 度 electricity in kWh Vietnamese.
量子比特 liàngzǐbǐtè qubit; superconducting entanglement manipulation aligned.
数字孪生 shùzìluánshēng digital twin; 流域 liúyù and 高精度 corrected.
生物信息学 requires shēngwùxìnxīxué; immutable key xin1 should xin4. Hold identity; example already xìn correct.
干细胞 gànxìbāo stem cell; induced pluripotent not totipotent, Vietnamese refined.
深海潜器 shēnhǎiqiánqì deep submersible; sample collection aligned.
超燃冲压 chāoránchōngyā scramjet propulsion; 难题 nántí correct.
自适应控制 zìshìyìngkòngzhì adaptive control; autonomous landing response coherent.
机器学习 jīqìxuéxí machine learning; 高质量 exact pinyin corrected.
工业互联网 gōngyèhùliánwǎng industrial internet; networked manufacturing appropriate.
固态电池 gùtàidiànchí solid-state battery; 电解质 diànjiězhì not diànjiězì.
空间站 kōngjiānzhàn space station; orbital experiments context aligned.
智能驾驶 zhìnéngjiàshǐ intelligent driving; distinguish assistance from unconditional autonomy in every scenario, repair example/gloss. Stable keys retained.
""", [
 (1,"高精度 exact transcription.",py(1,"gāo jīngmì","gāo jīngdù")),
 (2,"Drug not therapy; precise nonuniversal example.",{"english_meanings":["targeted drug","molecularly targeted medicine"],"example":{"simplified":"研究人员正在评估这种靶向药对特定肿瘤的作用。","pinyin":"Yánjiū rényuán zhèngzài pínggū zhè zhǒng bǎxiàngyào duì tèdìng zhǒngliú de zuòyòng.","vietnamese":"Các nhà nghiên cứu đang đánh giá tác dụng của thuốc điều trị đích này đối với một loại khối u cụ thể."}}),
 (6,"离 lí.",py(6,"děnglǐzǐtǐ","děnglízǐtǐ")),
 (7,"解调 jiětiáo.",py(7,"jiějiào","jiětiáo")),
 (12,"高精度 exact transcription.",py(12,"gāo jīngmì","gāo jīngdù")),
 (13,"No absolute implementation security guarantee.",{"example":{"simplified":"量子通信研究利用量子态传递信息的方法。","pinyin":"Liàngzǐ tōngxìn yánjiū lìyòng liàngzǐtài chuándì xìnxī de fāngfǎ.","vietnamese":"Truyền thông lượng tử nghiên cứu phương pháp dùng trạng thái lượng tử để truyền thông tin."}}),
 (19,"返回 fǎnhuí.",py(19,"qǔyàng huíhuán","qǔyàng fǎnhuí")),
 (22,"钙 gài.",py(22,"gǎitài","gàitài")),
 (23,"Modulus tone and terminology.",{"example":{"pinyin":r[22].examples[0].pinyin.replace("moliàng","móliàng"),"vietnamese":r[22].examples[0].vietnamese.replace("mô-đun siêu cao","mô đun đàn hồi siêu cao")}}),
 (24,"Remove Vietnamese duplicate robot.",{"example":{"vietnamese":r[23].examples[0].vietnamese.replace("Robot khung trợ lực robot bộ khung xương ngoài","Robot khung xương ngoài trợ lực")}}),
 (27,"Restore grammatical subject.",{"example":{"simplified":"云计算平台为企业提供可按需扩展的计算资源。","pinyin":"Yúnjìsuàn píngtái wèi qǐyè tígōng kě ànxū kuòzhǎn de jìsuàn zīyuán.","vietnamese":"Nền tảng điện toán đám mây cung cấp cho doanh nghiệp tài nguyên tính toán có thể mở rộng theo nhu cầu."}}),
 (29,"Proton beam irradiation not nanoscale explosion; identity still held.",{"example":{"simplified":"质子治疗使用质子束照射肿瘤。","pinyin":"Zhìzǐ zhìliáo shǐyòng zhìzǐshù zhàoshè zhǒngliú.","vietnamese":"Xạ trị proton sử dụng chùm hạt proton để chiếu xạ khối u."}}),
 (30,"Attested regional terminology clearly labeled.",{"vietnamese_meanings":["sóng hấp dẫn (cách gọi trong thiên văn học Đài Loan)"],"english_meanings":["gravitational wave (Taiwan astronomical terminology)"],"example":{"simplified":"在台湾的天文学文献中，引力波也称为重力波。","pinyin":"Zài Táiwān de tiānwénxué wénxiàn zhōng, yǐnlìbō yě chēngwéi zhònglìbō.","vietnamese":"Trong tài liệu thiên văn học Đài Loan, sóng hấp dẫn (引力波) cũng được gọi là 重力波."}}),
 (33,"Remove malignant autoimmune classification and reversed manufacturing verbs.",{"example":{"simplified":"研究团队正在开发针对特定蛋白质的单克隆抗体。","pinyin":"Yánjiū tuánduì zhèngzài kāifā zhēnduì tèdìng dànbáizhì de dānkèlóng kàngtǐ.","vietnamese":"Nhóm nghiên cứu đang phát triển kháng thể đơn dòng nhắm vào một protein cụ thể."}}),
 (34,"粒 lạp.",{"sino_vietnamese":"lạp tử vật lý"}),
 (36,"Basic property without overgeneralizing dissipationless spin current.",{"example":{"simplified":"拓扑绝缘体的内部绝缘，而表面可以导电。","pinyin":"Tuòpū juéyuántǐ de nèibù juéyuán, ér biǎomiàn kěyǐ dǎodiàn.","vietnamese":"Bên trong chất cách điện tô-pô có tính cách điện, còn bề mặt có thể dẫn điện."}}),
 (37,"甲 jiǎ and pico 皮 pí.",{"example":{"pinyin":r[36].examples[0].pinyin.replace("zhǐjiagai","zhǐjiǎgài").replace("pīshēngjí","píshēngjí")}}),
 (38,"度 electrical unit kWh.",{"example":{"vietnamese":r[37].examples[0].vietnamese.replace("hàng trăm triệu độ điện năng","hàng trăm triệu kWh điện năng")}}),
 (40,"流域 and 高精度 exact syllables.",{"example":{"pinyin":r[39].examples[0].pinyin.replace("kuàliùyù","kuàliúyù").replace("gāo jīngmì","gāo jīngdù")}}),
 (42,"Pluripotent đa năng rather than totipotent vạn năng.",{"example":{"vietnamese":r[41].examples[0].vietnamese.replace("tế bào gốc vạn năng cảm ứng","tế bào gốc đa năng cảm ứng")}}),
 (44,"难题 tí.",py(44,"nándí","nántí")),
 (46,"高质量 exact transcription.",py(46,"gāo pǐnzhì","gāo zhìliàng")),
 (48,"质 zhì.",py(48,"diànjiězì","diànjiězhì")),
 (50,"Intelligent assistance not blanket all-scenario autonomy.",{"vietnamese_meanings":["lái xe thông minh","công nghệ hỗ trợ lái xe thông minh"],"english_meanings":["intelligent driving","intelligent driving assistance"],"example":{"simplified":"智能驾驶系统利用多种传感器感知车辆周围的环境。","pinyin":"Zhìnéng jiàshǐ xìtǒng lìyòng duō zhǒng chuángǎnqì gǎnzhī chēliàng zhōuwéi de huánjìng.","vietnamese":"Hệ thống lái xe thông minh sử dụng nhiều loại cảm biến để nhận biết môi trường xung quanh xe."}}),
], pending={
 29:{"reason":"Incorrect stable pronunciation identity 质子治疗|zhi3 zi3 zhi4 liao2: 质 must zhi4 (zhì). Example corrected and rechecked, but lexical key cannot be silently renamed. Excluded pending explicit identity resolution.","linguistic_uncertainty":True},
 41:{"reason":"Incorrect stable pronunciation identity 生物信息学|sheng1 wu4 xin1 xi1 xue2: 信 must xin4 (xìn), already correct in example. Preserve immutable key and hold pending explicit identity resolution.","linguistic_uncertainty":True},
}, sources=["https://www.cancer.gov/about-cancer/treatment/types/targeted-therapies","https://www.cancer.gov/about-cancer/treatment/types/radiation-therapy/external-beam","https://www.asiaa.sinica.edu.tw/IAAQ/pdf/2018Q1.pdf","https://www.nist.gov/cybersecurity-and-privacy/what-quantum-cryptography"])

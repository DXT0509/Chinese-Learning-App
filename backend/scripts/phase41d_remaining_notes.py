"""Individually authored after reading all 242 checkpoint entries and source examples.

Each line pins checkpoint index AND written form. The serializer binds the full
pronunciation identity/version/checksum, and never infers decisions from a label.
Contexts below are new assessment sentences, not edits to published examples.
"""

NOTES = """0|一帆风顺|predicate|事情并非一帆风顺。|Describes the course of events as the predicative core; not a noun label.
1|一点儿|quantity_phrase|请给我一点儿水。|Indefinite quantity phrase denotes a small amount of water; it is not a classifier or an invented numeral.
2|一目了然|predicate|图中的关系一目了然。|The relationship is immediately clear; the expression predicates its state.
3|一窍不通|predicate|他对这门技术一窍不通。|States lack of understanding after a topic/subject; no free adjective/verb guess.
4|一脉相承|predicate|这两种风格一脉相承。|Predicates continuity of the two styles, consistent with the source.
5|一览无余|predicate|站在山顶，全城景色一览无余。|Predicates complete visibility of the panorama.
6|一诺千金|subject|一诺千金是他的原则。|The quoted commitment principle is the subject, not an invariant idiom POS.
7|一鼓作气|adverbial|大家一鼓作气完成了任务。|Modifies the manner of completing the task, as in the source construction.
8|万古长青|predicate|愿我们的友谊万古长青。|Predicates enduring flourishing of friendship in a wish clause.
9|万象更新|attribute|这是一个万象更新的春天。|The expression before de modifies spring; internal subject-predicate structure is not being graded.
10|三言两语|object|这件事不能只用三言两语说明。|Nominal expression is the object of instrumental yong; includes preposition objects.
11|下情上达|predicate|这样才能下情上达。|Predicates the upward communication of grassroots concerns after the modal.
12|不会|verb|我不会游泳。|Negated modal-verb phrase expresses lack of ability; the whole phrase has verbal function, not adverb POS inferred from its negative component.
13|不可以|verb|这里不可以拍照。|Negated permission auxiliary is a modal-verb phrase; preserves the source's explicit modal classification.
14|不可思议|predicate|这个结果不可思议。|Describes the result as incredible in an unambiguous predicative use.
15|不屈不挠|attribute|他表现出了不屈不挠的精神。|The de phrase modifies spirit, retaining the source sense of unyielding courage.
16|不是|verb|我不是老师。|Negated copular verb phrase has verbal function; it is not the POS of the negative adverb alone.
17|不用|verb|你不用等我。|Negated necessity auxiliary has modal-verbal function in the actual source example.
18|不相上下|predicate|两队的实力不相上下。|Predicates comparable strength rather than an independent action.
19|不能|verb|这里不能停车。|Negated possibility/permission modal-verb phrase scopes over parking; source modal identity retained.
20|不要|verb|请不要在这里吸烟。|Prohibitive modal-verb phrase scopes over smoking; whole-phrase verbal function is distinguished from the initial negative word.
21|世外桃源|object|游客们向往世外桃源。|Names the idyllic place as the object of yearning.
22|两全其美|attribute|这是一个两全其美的方案。|Modifies the plan through de; both benefits are preserved.
23|严于律己|predicate|我们应当严于律己。|The modal introduces the predicated practice of strict self-discipline.
24|中流砥柱|subject|中流砥柱能够支撑大局。|The metaphorical mainstay names the subject, not a new adjective class.
25|为民造福|predicate|干部应当为民造福。|Action of benefiting the people is the predicate after the modal.
26|举一反三|predicate|学生应该举一反三。|Predicates generalizing from a learned example.
27|举世瞩目|attribute|他们取得了举世瞩目的成就。|Modifies achievements attracting worldwide attention.
28|乐善好施|attribute|他是一位乐善好施的医生。|Modifies the doctor by charitable disposition in a de phrase.
29|买东西|verb|我去超市买东西。|Verb-object phrase has verbal function; explicit source verb-phrase metadata is reliable.
30|予人口实|predicate|这种做法会予人口实。|Predicates giving others a pretext to criticize; no synonym is accepted.
31|互利共赢|attribute|双方开展互利共赢的合作。|Modifies cooperation; modern fixed expression need not be forced into a classical idiom POS.
32|今|bound_morpheme|今天是星期一。|In this modern source example the character is inside the compound for today; classical independent uses are outside scope.
33|今天晚上|noun|今天晚上我在家。|Temporal noun phrase names tonight; an NP used as a time adverbial is not thereby a lexical adverb. Question explicitly asks phrase class rather than sentence position.
34|价廉物美|predicate|这里的商品价廉物美。|Predicates low price and good quality of the goods.
35|任重道远|predicate|我们依然任重道远。|Predicates the remaining burden and long journey.
36|众望所归|attribute|他是一位众望所归的候选人。|De phrase modifies the widely supported candidate, avoiding ambiguous copular analysis.
37|优势互补|predicate|两地可以优势互补。|Predicates complementary advantages after the modal; contemporary collocation is retained as a fixed expression.
38|你好|greeting|你好！|Conventional greeting formula is assessed by communicative function, not a fabricated word POS.
39|供不应求|predicate|这种商品供不应求。|Predicates demand exceeding supply for the product.
40|依法治国|predicate|我们要依法治国。|Verbal policy expression predicates governing according to law.
41|保家卫国|predicate|战士们要保家卫国。|Predicates protecting home and country after the modal.
42|入木三分|predicate|这篇评论入木三分。|Predicates penetrating insight of the commentary, not literal penetration of wood.
43|再接再厉|predicate|我们应当再接再厉。|Predicates renewed effort; the source exhortation sense is maintained.
44|再见|farewell|再见！|Independent leave-taking formula; no arbitrary lexical adjective is assigned.
45|凤毛麟角|subject|凤毛麟角值得珍惜。|Rare people or objects are the subject in this explicitly nominal use.
46|出神入化|attribute|他展示了出神入化的技艺。|The de phrase modifies artistic skill at a sublime level.
47|别出心裁|predicate|这个设计别出心裁。|Predicates originality of the design.
48|刻骨铭心|attribute|这是一段刻骨铭心的记忆。|Modifies an unforgettable memory, matching the source figurative sense.
49|前所未有|attribute|我们遇到了前所未有的机会。|The de phrase modifies opportunities as unprecedented.
50|力所能及|attribute|他做了一些力所能及的工作。|Modifies work within his ability; the internal clause is not a lexical POS answer.
51|勤能补拙|independent_clause|勤能补拙，所以我们要坚持练习。|Complete maxim forms the first independent clause before the explicit consequence.
52|匠心独运|predicate|这座园林的布局匠心独运。|Predicates ingenious craftsmanship of the layout.
53|十全十美|predicate|没有哪个方案十全十美。|Predicates perfection under negation.
54|千方百计|adverbial|他们千方百计寻找水源。|Manner phrase modifies searching by every possible means.
55|午|bound_morpheme|中午我们在家吃饭。|The target is the time-related morpheme inside the compound for noon, not an invented independent POS.
56|协和万邦|attribute|他们秉持协和万邦的理念。|The de phrase modifies the principle of harmonious relations.
57|卓尔不群|attribute|他展现出卓尔不群的风范。|Modifies outstanding bearing in the source sense.
58|博古通今|predicate|这位学者博古通今。|Predicates wide knowledge spanning past and present.
59|博大精深|predicate|中华文化博大精深。|Predicates breadth and depth of culture.
60|卧薪尝胆|predicate|他们卧薪尝胆，终于取得突破。|Predicates sustained hardship and preparation before success.
61|压倒一切|attribute|安全是压倒一切的重要任务。|De phrase modifies task by overriding priority; lexical transitivity is not confused with contextual role.
62|厚积薄发|predicate|青年学者应该厚积薄发。|Predicates accumulating deeply before measured achievement.
63|反腐倡廉|attribute|大家支持反腐倡廉的措施。|Modern coordinated action expression modifies measures through de.
64|合情合理|attribute|委员会作出了合情合理的裁决。|Modifies the ruling as reasonable and fair.
65|同舟共济|predicate|大家应当同舟共济。|Predicates cooperating through shared difficulty.
66|名列前茅|predicate|这所学校的成绩名列前茅。|Predicates the ranking of results.
67|名副其实|attribute|这是一座名副其实的智慧农场。|Modifies the farm by correspondence between name and reality.
68|后顾之忧|object|保障制度消除了后顾之忧。|Names worries as the direct object of eliminating them.
69|和衷共济|predicate|大家和衷共济，终于渡过难关。|Predicates united cooperative action before overcoming difficulty.
70|咬文嚼字|predicate|讨论时不要咬文嚼字。|Predicates excessive textual quibbling under a prohibition.
71|喜出望外|predicate|听到消息，大家喜出望外。|Predicates unexpected delight of the people.
72|喜闻乐见|attribute|这是一场喜闻乐见的演出。|The de phrase modifies an enjoyable performance; no overt relative-clause subject changes the requested span.
73|因地制宜|adverbial|各地因地制宜发展特色产业。|Modifies development according to local conditions, matching the source construction.
74|垂头丧气|predicate|他没有垂头丧气。|Predicates dejection under negation.
75|墨守成规|predicate|我们不能墨守成规。|Predicates rigid adherence to old rules under a modal.
76|大公无私|predicate|这位干部大公无私。|Predicates impartiality and selflessness.
77|天下为公|independent_clause|天下为公，这是一个崇高的理想。|The complete proposition is the first independent assertion before a comment.
78|天伦之乐|object|老人享受着天伦之乐。|Names family happiness as the direct object of enjoying it.
79|天衣无缝|complement|他们配合得天衣无缝。|Expression follows the structural complement marker de and evaluates the degree of coordination.
80|如饥似渴|adverbial|学生们如饥似渴地阅读经典。|The di phrase modifies the manner of reading.
81|妙笔生花|predicate|这位作家妙笔生花。|Predicates literary virtuosity in a simple independent clause.
82|始料未及|attribute|这是始料未及的结果。|Modifies an unforeseen result, avoiding an ambiguous complement after a mental verb.
83|安邦定国|predicate|贤明的治理者应当安邦定国。|Predicates securing peace and stability of the country.
84|实干兴邦|independent_clause|实干兴邦，因此我们要踏实工作。|A complete subject-predicate maxim precedes its consequence; not every slogan is an adjective.
85|寓情于景|predicate|作者在文章中寓情于景。|Predicates embedding emotion in scenery.
86|对不起|apology|对不起！|Independent apology formula is assessed by speech act rather than an unsupported dictionary POS.
87|层出不穷|predicate|新的应用层出不穷。|Predicates continuous emergence of applications.
88|居高不下|predicate|能源价格一直居高不下。|Predicates persistently high prices.
89|床上|noun|猫在床上睡觉。|Locative noun phrase combines bed and a localizer; as object of zai it retains nominal function, rather than being a preposition itself.
90|开卷有益|independent_clause|开卷有益，所以我们应该多读书。|The complete assertion about reading is an independent clause preceding a consequence.
91|开源节流|predicate|各单位必须开源节流。|Predicates increasing revenue and reducing expenditure.
92|开玩笑|verb|他只是开玩笑。|The verb-object expression has verbal function meaning to joke; no standalone noun sense is required here.
93|异想天开|predicate|这个想法简直异想天开。|Predicates fanciful impracticality of the idea.
94|得天独厚|attribute|这里拥有得天独厚的自然条件。|Modifies favorable natural conditions through de.
95|得意洋洋|predicate|他不应该得意洋洋。|Predicates smug satisfaction under a modal negation.
96|循序渐进|adverbial|我们循序渐进地学习。|The di phrase modifies the manner of learning step by step.
97|循规蹈矩|predicate|他做事总是循规蹈矩。|Predicates rule-bound behavior; no unsupported global POS is asserted.
98|微不足道|predicate|这些小事微不足道。|Predicates insignificance of the small matters.
99|微言大义|object|读者体会到了微言大义。|Names subtle profound meaning as the direct object of understanding.
100|心力交瘁|predicate|连续工作后，他已经心力交瘁。|Predicates mental and physical exhaustion.
101|心满意足|attribute|老人露出了心满意足的笑容。|Modifies a satisfied smile through de.
102|心甘情愿|adverbial|他心甘情愿地去乡村支教。|The di phrase modifies volunteering willingly.
103|忠于职守|attribute|大家敬佩忠于职守的交警。|Modern fixed expression modifies conscientious traffic police through de.
104|忠贞不渝|predicate|他们对这项事业忠贞不渝。|Predicates enduring loyalty to the cause.
105|急功近利|predicate|做研究不能急功近利。|Predicates shortsighted pursuit of quick gains under a negated modal.
106|总揽全局|predicate|负责人必须总揽全局。|Transitive action phrase predicates taking an overall view.
107|您好|greeting|您好！|Polite greeting formula; the honorific pronunciation identity is preserved.
108|情不自禁|adverbial|观众情不自禁地流下热泪。|The di phrase modifies crying involuntarily.
109|惩恶扬善|predicate|司法应当惩恶扬善。|Predicates punishing evil and promoting good.
110|想方设法|adverbial|队员们想方设法恢复通信。|Modifies restoring communications by devising every means.
111|意气用事|predicate|处理分歧不能意气用事。|Predicates acting from impulse under prohibition.
112|成千上万|attribute|成千上万的游客来到这里。|Quantifying expression modifies tourists through de; not a classifier.
113|截然不同|attribute|他们提出了截然不同的观点。|Modifies opinions as entirely different.
114|打招呼|verb|他向老师打招呼。|Verb-object phrase denotes the act of greeting someone, unlike a standalone greeting formula.
115|打电话|verb|他在打电话。|Verb-object phrase denotes making a telephone call and supports progressive use.
116|打篮球|verb|下午我们打篮球。|Verb-object phrase denotes playing basketball, not the basketball noun alone.
117|投机倒把|attribute|执法人员查处了投机倒把的商贩。|De phrase modifies profiteering traders; not an assertion that its lexical POS is adjective.
118|拍案叫绝|predicate|观众们无不拍案叫绝。|Predicates enthusiastic praise and table-slapping.
119|拾金不昧|attribute|大家赞扬拾金不昧的品德。|De phrase modifies the virtue of returning lost valuables.
120|持之以恒|predicate|学习外语必须持之以恒。|Predicates maintaining sustained effort after a modal; no automatic adjective mapping.
121|指手画脚|predicate|外人不应对这件事指手画脚。|Predicates unsolicited interference directed at the matter.
122|推陈出新|predicate|创作者应该推陈出新。|Predicates creative renewal of inherited artistic material.
123|提心吊胆|predicate|走过悬崖时，他一直提心吊胆。|Predicates fearful anxiety rather than literal bodily actions.
124|放暑假|verb|学校下周放暑假。|Verb-object phrase denotes taking or beginning summer vacation; not the vacation noun alone.
125|政通人和|attribute|这里呈现出政通人和的景象。|De phrase modifies a scene of orderly government and public harmony.
126|文以载道|independent_clause|文以载道，这是一种传统文学观念。|The complete literary proposition forms the first assertion, not a fabricated nominal POS.
127|文质彬彬|attribute|他是一位文质彬彬的青年。|De phrase modifies a refined, well-mannered young person.
128|斩钉截铁|adverbial|发言人斩钉截铁地作出回应。|Di phrase modifies responding decisively.
129|无与伦比|attribute|古城展现出无与伦比的魅力。|De phrase modifies unrivaled charm.
130|无为而治|attribute|他研究无为而治的思想。|The governance expression modifies the idea through de; internal verbal structure is not its contextual role.
131|无动于衷|predicate|面对困难，他不能无动于衷。|Predicates indifference under a negated modal.
132|无微不至|attribute|她给予孩子无微不至的关爱。|De phrase modifies meticulous care.
133|日新月异|predicate|城市的面貌日新月异。|Predicates rapid continuing change of the city.
134|日积月累|object|本领来自日积月累。|The gradual accumulation process is the object of deriving from; nominalization does not invent a permanent noun POS.
135|昨|bound_morpheme|我昨天去了学校。|The target is inside the modern compound for yesterday; no free-standing modern POS is fabricated.
136|显而易见|predicate|科技创新的作用显而易见。|Predicates obviousness of the role of innovation.
137|晚安|wish|晚安，明天见！|Conventional goodnight wish is assessed by communicative function, not assumed to be a noun or adjective.
138|朋|bound_morpheme|他是我的朋友。|The reviewed modern example uses the character within the compound for friend.
139|未雨绸缪|predicate|面对风险，我们要未雨绸缪。|Predicates preparing in advance before risk materializes.
140|本固枝荣|independent_clause|本固枝荣，所以我们要重视基础。|Complete paired assertion about roots and branches precedes an explicit consequence.
141|标新立异|predicate|设计师敢于标新立异。|Predicates proposing novel designs after an attitude/modal-like verb.
142|标本兼治|predicate|治理污染必须标本兼治。|Predicates addressing symptoms and root causes together.
143|死心塌地|adverbial|他死心塌地地追随自己的理想。|Di phrase modifies unwavering pursuit; source fidelity sense is retained.
144|民为邦本|independent_clause|民为邦本，因此应当保障民生。|A complete political proposition precedes its consequence; not an idiom-only answer.
145|民熙物阜|attribute|这里出现了民熙物阜的景象。|De phrase modifies the scene of prosperous people and abundant goods.
146|求真务实|attribute|大家提倡求真务实的作风。|De phrase modifies an evidence-seeking practical working style.
147|沧海一粟|object|他把个人的荣辱看作沧海一粟。|The metaphorical tiny grain is the object of the comparison verb kanzuo.
148|流连忘返|predicate|游客们在枫林中流连忘返。|Predicates lingering and reluctance to leave.
149|海晏河清|attribute|古人向往海晏河清的盛世。|De phrase modifies an era of peace; literal river/sea clauses are not graded separately.
150|海纳百川|attribute|文明需要海纳百川的胸怀。|De phrase modifies an inclusive broad mind.
151|润物无声|predicate|良好的教育润物无声。|Predicates quiet, unobtrusive nurturing in the source metaphorical sense.
152|深谋远虑|attribute|他提出了深谋远虑的规划。|De phrase modifies a far-sighted plan.
153|游刃有余|predicate|这位医生在手术中游刃有余。|Predicates confident ease in performing the procedure.
154|源远流长|attribute|我们珍惜源远流长的文化。|De phrase modifies culture with a long enduring history.
155|潜移默化|attribute|家风产生了潜移默化的影响。|De phrase modifies a gradual unobtrusive influence; not automatically an adverb outside context.
156|炉火纯青|attribute|他展示了炉火纯青的技艺。|De phrase modifies highly perfected skill.
157|独树一帜|predicate|这位画家在画坛独树一帜。|Predicates establishing a distinctive artistic style.
158|玩忽职守|predicate|公职人员不能玩忽职守。|Predicates neglecting official duties under a modal prohibition.
159|珠联璧合|predicate|这两种艺术形式珠联璧合。|Predicates a harmonious excellent combination of the two arts, without inventing marriage-only meaning.
160|理所当然|adverbial|我们理所当然应当尊老爱幼。|Modifies the obligation as a matter of course in the source construction.
161|琳琅满目|attribute|展厅里陈列着琳琅满目的商品。|De phrase modifies an abundance of attractive goods.
162|琼浆玉液|object|他仿佛尝到了琼浆玉液。|Names superb liquor as the direct object of tasting.
163|瑕不掩瑜|independent_clause|瑕不掩瑜，这项成果仍然十分出色。|The complete concession statement is an independent clause before the evaluation.
164|百家争鸣|attribute|他们研究百家争鸣的历史。|De phrase modifies the history of diverse intellectual debate.
165|百废俱兴|attribute|灾区迎来了百废俱兴的新局面。|De phrase modifies the new scene of rebuilding and renewal.
166|皆大欢喜|attribute|双方达成了皆大欢喜的和解。|De phrase modifies an agreement satisfying everyone.
167|直截了当|adverbial|他直截了当地指出了问题。|Di phrase modifies pointing out the problem directly.
168|相提并论|predicate|这两种产品不能相提并论。|Predicates comparing on equal terms under negation.
169|真知灼见|object|学者们提出了真知灼见。|Names insightful views as the object of proposing them.
170|知足常乐|independent_clause|知足常乐，因此他不追求奢华。|A complete maxim precedes its consequence; an explicit clausal context removes other contextual readings.
171|空前绝后|attribute|他们创造了空前绝后的奇迹。|De phrase modifies an unparalleled achievement.
172|立党为公|attribute|他们强调立党为公的宗旨。|Modern political expression modifies the stated founding purpose through de.
173|竭尽全力|adverbial|救援队竭尽全力搜救群众。|Modifies rescue efforts as using every available effort.
174|粗制滥造|attribute|市场上不能出售粗制滥造的商品。|De phrase modifies poorly made goods; lexical action versus contextual modifier is separated.
175|精益求精|attribute|工匠秉持精益求精的精神。|De phrase modifies the spirit of continual refinement.
176|繁荣昌盛|predicate|我们祝愿祖国繁荣昌盛。|Predicates prosperity of the country inside the wish clause.
177|纵横捭阖|predicate|谋士们在列国之间纵横捭阖。|Predicates diplomatic maneuvering rather than an unsupported nominal class.
178|经世致用|attribute|他坚持经世致用的治学宗旨。|De phrase modifies a scholarly purpose of practical application.
179|经久不衰|attribute|作品展现出经久不衰的魅力。|De phrase modifies lasting artistic appeal.
180|络绎不绝|predicate|前来参观的车队络绎不绝。|Predicates continuous arrival of vehicles.
181|统筹兼顾|predicate|政府在规划时必须统筹兼顾。|Predicates coordinated overall consideration after a modal.
182|继往开来|attribute|他们肩负着继往开来的使命。|De phrase modifies the mission of carrying tradition forward.
183|群策群力|predicate|面对困难，大家群策群力。|Predicates combining collective thought and effort.
184|耐人寻味|attribute|这是一部耐人寻味的作品。|De phrase modifies a work inviting reflection.
185|耳闻目睹|predicate|他耳闻目睹了家乡的变化。|Perfective le and the following object anchor the predicative eyewitness use.
186|聚精会神|adverbial|科研人员聚精会神地观察屏幕。|Di phrase modifies observing attentively.
187|脚踏实地|adverbial|青年应当脚踏实地地工作。|Di phrase modifies working steadily and practically.
188|脱颖而出|predicate|这支年轻的团队最终脱颖而出。|Predicates emerging conspicuously from a competition.
189|自力更生|attribute|我们发扬自力更生的精神。|De phrase modifies the spirit of relying on one's own efforts.
190|自始至终|adverbial|他自始至终坚守岗位。|Temporal range expression modifies remaining at the post throughout.
191|自强不息|attribute|我们弘扬自强不息的精神。|De phrase modifies the spirit of persistent self-improvement; avoids the source's two-occurrence ambiguity.
192|至关重要|attribute|这是至关重要的任务。|De phrase modifies a task of crucial importance.
193|若无其事|adverbial|他若无其事地继续工作。|Di phrase modifies continuing as if nothing had happened.
194|茅塞顿开|predicate|听完解释，他茅塞顿开。|Predicates sudden understanding after an explanation.
195|莫名其妙|predicate|这件事莫名其妙。|Predicates inexplicability of the event in a simple evaluative construction.
196|蔚为大观|predicate|连绵的峰林蔚为大观。|Predicates forming a magnificent spectacle.
197|薪火相传|predicate|优秀的文化代代薪火相传。|Predicates intergenerational transmission of cultural tradition.
198|虚实相生|attribute|戏曲营造了虚实相生的舞台空间。|De phrase modifies a stage space interweaving real and imagined elements.
199|虚无缥缈|attribute|他不相信虚无缥缈的幻想。|De phrase modifies unreal illusory fantasies.
200|融会贯通|predicate|这些知识必须融会贯通。|Predicates integrating knowledge coherently after a modal.
201|血气方刚|attribute|这些血气方刚的青年充满热情。|De phrase modifies vigorous young people.
202|见义勇为|attribute|他是一位见义勇为的市民。|De phrase modifies a citizen acting courageously for justice.
203|言传身教|predicate|老师应该言传身教。|Predicates teaching through speech and personal example after a modal.
204|言简意赅|attribute|他作了言简意赅的汇报。|De phrase modifies a concise and meaningful report.
205|言行一致|predicate|他始终言行一致。|Predicates consistency between speech and conduct.
206|讳疾忌医|predicate|面对缺点不能讳疾忌医。|Predicates hiding faults and refusing correction under modal negation.
207|诗情画意|object|古镇充满了诗情画意。|Names poetic/pictorial charm as the object of being filled with it.
208|谈笑风生|predicate|队员们围坐在篝火旁谈笑风生。|Predicates lively conversation by the campfire.
209|谢谢|verb|谢谢你！|Thanking verb takes ni as its object in the source; reliable verbal function makes a speech-act fallback unnecessary.
210|责无旁贷|attribute|保护环境是我们责无旁贷的义务。|De phrase modifies an obligation that cannot be shifted to others.
211|费尽心机|adverbial|骗子费尽心机伪造文件。|Modifies forging documents through elaborate scheming.
212|赖以生存|attribute|我们保护赖以生存的环境。|Modern relative expression modifies the environment on which life depends.
213|踢足球|verb|我们去踢足球吧。|Verb-object phrase has verbal function, denoting playing football in the serial-verb construction.
214|轩然大波|object|这条消息掀起了轩然大波。|Names the uproar as the direct object of causing it.
215|迎刃而解|predicate|这些难题将会迎刃而解。|Predicates ready resolution of the problems after a modal.
216|返璞归真|attribute|他追求返璞归真的生活。|De phrase modifies a life returning to natural simplicity.
217|还没|adverb|我还没吃饭。|Adverbial phrase combines still and not yet, modifying eating; explicit source adverb annotation is preserved rather than confused with an ability modal.
218|远近闻名|predicate|这座古村远近闻名。|Predicates widespread fame of the village.
219|迫不及待|adverbial|运动员迫不及待地走出基地。|Di phrase modifies leaving eagerly without delay.
220|追本溯源|predicate|研究人员应该追本溯源。|Predicates tracing origins after a modal.
221|适得其反|predicate|这样做的结果适得其反。|Predicates an outcome opposite to the intention.
222|逢年过节|adverbial|志愿者逢年过节都会来看老人。|Temporal expression modifies visiting on holidays; no numeral or noun POS is invented.
223|遵纪守法|predicate|每个公民都应当遵纪守法。|Predicates observing discipline and law.
224|量入为出|predicate|安排预算必须量入为出。|Predicates budgeting expenditure according to income.
225|针锋相对|attribute|代表团作出了针锋相对的回应。|De phrase modifies a directly opposing response.
226|闲情逸致|object|他难得有闲情逸致。|Names leisurely refined enjoyment as the object of having it.
227|防微杜渐|predicate|管理人员必须防微杜渐。|Predicates preventing small beginnings from growing into harm.
228|防患未然|predicate|化工园区应该防患未然。|Predicates prevention before an accident arises.
229|除暴安良|attribute|警察履行除暴安良的职责。|De phrase modifies the duty to eliminate violence and protect good people.
230|随心所欲|adverbial|人们不能随心所欲地损害公共利益。|Di phrase modifies damaging public interests arbitrarily; negation does not change the target's role.
231|难能可贵|predicate|这种坚守难能可贵。|Predicates rarity and value of the persistence.
232|雅俗共赏|attribute|这是一部雅俗共赏的作品。|De phrase modifies a work enjoyed by different audiences.
233|集思广益|predicate|制定规划时应当集思广益。|Predicates drawing on collective ideas after a modal.
234|雨后春笋|object|新企业如雨后春笋般涌现。|Nominal image is the object of comparative ru; the larger comparison phrase is the adverbial.
235|雪中送炭|attribute|这是一场雪中送炭的救助。|De phrase modifies timely help in hardship.
236|革故鼎新|attribute|我们需要革故鼎新的精神。|De phrase modifies the spirit of thorough renewal.
237|风雨同舟|predicate|面对困难，我们要风雨同舟。|Predicates sharing hardship together.
238|飞禽走兽|subject|飞禽走兽需要保护。|Names animals as the subject; no adjective or verb class is assigned to the nominal idiom.
239|饮水思源|predicate|富裕之后更应该饮水思源。|Predicates remembering the source of benefits after a modal.
240|高山仰止|predicate|他的品格令人高山仰止。|Target is the predicate of the caused person in the causative construction, as in the actual source.
241|齐心协力|adverbial|大家齐心协力完成了任务。|Modifies completing the task through united effort, as in the source action sequence.
"""
